
import os
from dotenv import load_dotenv
import time

# Load environment variables from the .env file
from typing import Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.docstore.document import Document

load_dotenv()


class PhotoGraphRAG:
    def __init__(
        self,
    ):
        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings()

        self.neo4j_uri = os.getenv("NEO4J_URI"),
        self.neo4j_username = os.getenv("NEO4J_USERNAME"),
        self.neo4j_password = os.getenv("NEO4J_PASSWORD"),
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def reset_knowledge_graph(self):
        """
        Reset the Neo4j database by clearing all nodes, relationships, and indexes
        """
        print("Resetting Neo4j database...")
        try:
            # Clear all nodes and relationships
            self.graph.query("""
                MATCH (n)
                DETACH DELETE n
            """)
            
            # Drop existing indexes if they exist
            try:
                self.graph.query("CALL db.index.fulltext.drop('photo_keywords')")
            except:
                print("No photo_keywords index to drop")
                
            try:
                self.graph.query("CALL db.index.vector.drop('photo_vectors')")
            except:
                print("No photo_vectors index to drop")
                
            print("Database reset complete")
        except Exception as e:
            print(f"Error during reset: {str(e)}")
            raise e

    def get_knowledge_graph(self):
        print("TESTING")
        print(self.llm)
        print("TESTINGDONE")
        store = Neo4jVector.from_existing_index(
            OpenAIEmbeddings(),
            url=self.neo4j_uri,
            username=self.neo4j_username,
            password=self.neo4j_password,
            index_name="photo_vectors",
        )

    def build_knowledge_graph(self, photo_descriptions: Dict[str, str]):
        """
        Build knowledge graph from photo descriptions using LLM extraction
        """
        # Reset the database first
        print("\nResetting existing knowledge graph...")
        start_time = time.time()
        self.reset_knowledge_graph()
        end_time = time.time()
        print(f"Reset completed in {end_time - start_time:.2f} seconds")

        print("\nPhoto Descriptions:")
        print(photo_descriptions)

        # Convert photo descriptions to documents
        documents = []
        for filename, description in photo_descriptions.items():
            doc = Document(
                page_content=description,
                metadata={"filename": filename}
            )
            documents.append(doc)

        print("\nDocuments:")
        print(documents)

        # Extract entities and relationships using LLM
        llm_transformer = LLMGraphTransformer(
            llm=self.llm,
                allowed_nodes=[
                    "Scene",           # Overall scene type
                    "Landscape",       # Natural landscapes
                    "Building",        # Built structures
                    "Person",          # People
                    "Activity",        # Activities
                    "NaturalFeature", # Natural elements
                    "TimeContext",    # Temporal aspects
                    "Atmosphere",     # Mood/ambiance
                    "Object",         # Physical objects
                    "Weather",        # Weather conditions
                    "Location"        # Specific locations
                ],
                allowed_relationships=[
                    "CONTAINS",           # Basic containment
                    "HAS_FEATURE",        # Scene features
                    "LOCATED_IN",         # Spatial location
                    "NEXT_TO",           # Adjacent relationships
                    "PART_OF",           # Component relationships
                    "INTERACTS_WITH",    # General interactions
                    "CREATES",           # Causal relationships
                    "INFLUENCES",        # Impact relationships
                    "USED_IN",          # Object usage
                    "EXPERIENCES"        # Experiential relationships
                ],
                node_properties=[
                    "type",
                    "description",
                    "color",
                    "atmosphere",
                    "time_of_day",
                    "weather",
                    "activity_level",
                    "importance"         # Added to help prioritize key elements
                ],
                relationship_properties=[
                    "description",
                    "spatial",
                    "temporal",
                    "impact",
                    "strength"          # Added to indicate relationship strength
                ],
                strict_mode=True
        )

        # Convert to graph documents and store in Neo4j
        graph_documents = llm_transformer.convert_to_graph_documents(documents)
        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True
        )

        # Vector embeddings
        self.vector_store = Neo4jVector.from_documents(
            documents,
            self.embeddings,
            index_name="photo_vectors",
            keyword_index_name="photo_keywords",
            search_type="hybrid"
        )

    def setup_retrieval_chain(self):
        """
        Set up the hybrid retrieval chain combining graph and vector search
        """
        template = """Given the following structured and unstructured search results about photos, 
        analyze both the direct content and the relationships between elements to find the most relevant photo.

        Consider these aspects when matching:
        1. Primary elements and objects in the scene
        2. Atmosphere and mood
        3. Activities and interactions
        4. Time of day and lighting
        5. Spatial relationships and scene composition
        6. Weather and environmental conditions
        7. Overall scene type and setting

        Context:
        {context}

        Query: {query}

        Provide your response in this format:
        Filename: <chosen_filename>
        Primary Match Factors:
        - [List 2-3 key elements that strongly match the query]
        Detailed Reasoning: [Explain how the photo's elements, relationships, and atmosphere align with the query]
        Alternative Considerations: [Briefly mention why this photo was chosen over other potential matches]
        """

        prompt = ChatPromptTemplate.from_template(template)

        def retriever(query: str) -> str:
            # Get results from vector similarity search
            vector_results = [
                f"Photo {doc.metadata['filename']}: {doc.page_content}"
                for doc in self.vector_store.similarity_search(query, k=3)
            ]

            print("\nVector Results:")
            print(vector_results)

            # Get results from graph pattern matching
            # This query finds photos connected to entities that match keywords in the query
            graph_results = self.graph.query(f"""
                CALL db.index.fulltext.queryNodes("photo_keywords", $query) YIELD node
                MATCH (node)<-[:MENTIONS|IN_PHOTO]-(photo:Document)
                RETURN DISTINCT photo.filename AS filename, photo.page_content AS description
                LIMIT 3
            """, {"query": query})

            print("\nGraph Results:")
            print(graph_results)

            final_context = f"""
            Vector Search Results:
            {' '.join(vector_results)}
            
            Graph Search Results:
            {graph_results}
            """

            print("\nFinal Context:")
            print(final_context + "\n\n\n")

            return final_context

        # Build the chain
        self.retrieval_chain = (
            {"context": retriever, "query": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def search_photos(self, query: str) -> str:
        """
        Search for most relevant photo given a natural language query
        """
        if not hasattr(self, 'retrieval_chain'):
            self.setup_retrieval_chain()

        return self.retrieval_chain.invoke(query)


if __name__ == "__main__":
    print("Running main\n")

    try:
        start_time = time.time()
        photo_rag = PhotoGraphRAG()
        end_time = time.time()
        print(f"PhotoGraphRAG Instantiated in {end_time - start_time:.2f} seconds\n")

        photo_descriptions = {
            "1.jpg": "A dry desert sand storm, a barren wasteland. The sky is blue and it looks very hot. There are hills of sand that seem to go endlessly.",
            "2.jpg": "A serene mountain lake surrounded by snow-capped peaks. The water is crystal clear and reflects the mountains like a mirror.",
            "3.jpg": "A bustling cityscape at sunset, with skyscrapers silhouetted against a vibrant orange sky. Lights are starting to glow in the windows.",
            "4.jpg": "A lively birthday party with balloons, a colorful cake, and kids playing games. Everyone looks happy and excited to celebrate.",
            "5.jpg": "A modern office with rows of desks and computers. The room is bright, with large windows letting in natural light.",
            "6.jpg": "A quiet forest trail surrounded by tall trees. The ground is covered with leaves, and sunlight filters through the branches above.",
            "7.jpg": "A stark, gray prison building with high walls and barbed wire. The yard is empty, and the atmosphere is somber.",
            "8.jpg": "A sunny beach with families enjoying a picnic. There are umbrellas, blankets, and kids building sandcastles by the shore.",
        }

        print("About to call build knowledge graphs\n")
        start_time = time.time()
        try:
            photo_rag.build_knowledge_graph(photo_descriptions)
            end_time = time.time()
            print(f"Knowledge graph built in {end_time - start_time:.2f} seconds\n")
        except Exception as e:
            print(f"Error building knowledge graph: {str(e)}")
            raise e

        print("About to search for photos\n")
        start_time = time.time()
        result = photo_rag.search_photos("A group of people gathered together for a special occasion.")
        end_time = time.time()
        print(f"Photo search completed in {end_time - start_time:.2f} seconds\n")

        print("Search Result:")
        print(result)

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        exit(1)