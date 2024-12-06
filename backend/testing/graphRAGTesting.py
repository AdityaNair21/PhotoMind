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
        # os.environ["OPENAI_API_KEY"] = openai_api_key
        # os.environ["NEO4J_URI"] = neo4j_uri
        # os.environ["NEO4J_USERNAME"] = neo4j_username
        # os.environ["NEO4J_PASSWORD"] = neo4j_password

        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings()

        self.neo4j_uri = os.getenv("NEO4J_URI"),
        self.neo4j_username = os.getenv("NEO4J_USERNAME"),
        self.neo4j_password = os.getenv("NEO4J_PASSWORD"),
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

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

        print("\nPhoto Descriptions:")
        print(photo_descriptions)

        """
        Build knowledge graph from photo descriptions using LLM extraction
        """
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
            node_properties=["type", "description"],
            relationship_properties=["description"]
        )

        # Convert to graph documents
        graph_documents = llm_transformer.convert_to_graph_documents(documents)

        # Store these created graph documents in Neo4j
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
        # Template for generating final response
        template = """Given the following structured and unstructured search results about photos, 
        determine the most relevant photo filename and explain why it best matches the query.

        Context:
        {context}

        Query: {query}

        Return your response in the format:
        Filename: <chosen_filename>
        Reasoning: <explanation>
        """

        prompt = ChatPromptTemplate.from_template(template)

        def generateContext(query: str) -> str:
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

            print("\.Final Context:")
            print(final_context + "\n\n\n")

            return final_context

        # Build the chain
        self.retrieval_chain = (
            {"context": generateContext, "query": RunnablePassthrough()}
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

    start_time = time.time()
    photo_rag = PhotoGraphRAG()
    end_time = time.time()
    print(
        f"PhotoGraphRAG Instantiated in {end_time - start_time:.2f} seconds\n")

    photo_descriptions = {
        "11111.jpg": "A dry desert sand storm, a barren wasteland. The sky is blue and it looks very hot. There are hills of sand that seem to go endlessly.",
        "122222.jpg": "A serene mountain lake surrounded by snow-capped peaks. The water is crystal clear and reflects the mountains like a mirror.",
        "1333333.jpg": "A bustling cityscape at sunset, with skyscrapers silhouetted against a vibrant orange sky. Lights are starting to glow in the windows.",
        "234535.jpg": "A lively birthday party with balloons, a colorful cake, and kids playing games. Everyone looks happy and excited to celebrate.",
        "2344323.jpg": "A modern office with rows of desks and computers. The room is bright, with large windows letting in natural light.",
        "2353255.jpg": "A quiet forest trail surrounded by tall trees. The ground is covered with leaves, and sunlight filters through the branches above.",
        "83573.jpg": "A stark, gray prison building with high walls and barbed wire. The yard is empty, and the atmosphere is somber.",
        "234762.jpg": "A sunny beach with families enjoying a picnic. There are umbrellas, blankets, and kids building sandcastles by the shore.",
        "6463236.jpg": "A cozy log cabin covered in snow. Smoke is rising from the chimney, and the surrounding forest is blanketed in white.",
        "72342.jpg": "A busy city street with cars stuck in traffic. Pedestrians walk briskly along the sidewalks under a cloudy sky.",
        "824562234.jpg": "A local soccer game with players in colorful jerseys. The field is green, and a crowd of spectators is cheering from the sidelines.",
        "654365.jpg": "A grand museum hall with marble floors and tall columns. There are paintings and sculptures displayed along the walls.",
        "263234623.jpg": "A bustling airport terminal with travelers walking past gates. Large windows show planes on the tarmac outside.",
        "2354.jpg": "A well-stocked grocery store aisle with rows of colorful produce. Shoppers are picking fruits and vegetables for their carts.",
        "1347.jpg": "A packed music concert with a crowd waving their hands. The stage is brightly lit, and the band is performing energetically.",
        "689785.jpg": "A lush jungle with dense greenery and a small waterfall. The area is humid, and exotic birds can be seen flying overhead.",
        "13525235.jpg": "A peaceful farmland with a red barn and rows of crops. A tractor is parked nearby, and the sky is clear and blue.",
        "12652351.jpg": "A vibrant city street at night with neon signs and bustling crowds. The atmosphere is lively, with music and chatter filling the air.",
        "763.jpg": "A clean hospital room with a single bed and medical equipment. The walls are white, and the environment feels calm and clinical.",
        "8465487.jpg": "A quiet library with rows of bookshelves and study tables. Students are reading and taking notes under warm lighting.",
        "2135123513.jpg": "A snowy mountain slope with skiers gliding downhill. The air is crisp, and the scene is full of action and energy.",
        "634226.jpg": "A warm family dinner with a table full of dishes. Everyone is gathered around, smiling and enjoying a hearty meal together.",
        "26234616.jpg": "A lively park with children playing near a large fountain. The water sparkles in the sunlight, and flowers are blooming nearby.",
    }

    # print("About to call get knowledge graphs\n")
    # # Pull knowledge graph
    # photo_rag.get_knowledge_graph()

    print("About to call build knowledge graphs\n")
    start_time = time.time()
    photo_rag.build_knowledge_graph(photo_descriptions)
    end_time = time.time()
    print(f"Knowledge graph built in {end_time - start_time:.2f} seconds\n")

    print("About to search for photos\n")
    start_time = time.time()
    result = photo_rag.search_photos("Busy downtown")
    end_time = time.time()
    print(f"Photo search completed in {end_time - start_time:.2f} seconds\n")

    print("Search Result:")
    print(result)
