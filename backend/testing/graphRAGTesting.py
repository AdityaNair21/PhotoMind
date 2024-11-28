import os
from typing import Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.docstore.document import Document


class PhotoGraphRAG:
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_username: str,
        neo4j_password: str,
        openai_api_key: str
    ):
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["NEO4J_URI"] = neo4j_uri
        os.environ["NEO4J_USERNAME"] = neo4j_username
        os.environ["NEO4J_PASSWORD"] = neo4j_password

        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4")
        self.embeddings = OpenAIEmbeddings()

    def build_knowledge_graph(self, photo_descriptions: Dict[str, str]):
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

        # Extract entities and relationships using LLM
        llm_transformer = LLMGraphTransformer(
            llm=self.llm,
            node_properties=["type", "description"],
            relationship_properties=["description"]
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

        def retriever(query: str) -> str:
            # Get results from vector similarity search
            vector_results = [
                f"Photo {doc.metadata['filename']}: {doc.page_content}"
                for doc in self.vector_store.similarity_search(query, k=3)
            ]

            # Get results from graph pattern matching
            # This query finds photos connected to entities that match keywords in the query
            graph_results = self.graph.query(f"""
                CALL db.index.fulltext.queryNodes("photo_keywords", $query) YIELD node
                MATCH (node)<-[:MENTIONS|IN_PHOTO]-(photo:Document)
                RETURN DISTINCT photo.filename AS filename, photo.page_content AS description
                LIMIT 3
            """, {"query": query})

            final_context = f"""
            Vector Search Results:
            {' '.join(vector_results)}
            
            Graph Search Results:
            {graph_results}
            """
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
    photo_rag = PhotoGraphRAG(
        neo4j_uri="bolt://44.201.130.123:7687",
        neo4j_username="neo4j",
        neo4j_password="authorization-hunk-curve",
        openai_api_key="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"
    )

    photo_descriptions = {
        "beach_sunset.jpg": "A stunning sunset over a tropical beach with palm trees silhouetted against an orange sky. The waves are gently lapping at the shore.",
        "mountain_lake.jpg": "A serene mountain lake surrounded by snow-capped peaks. The water is crystal clear and reflects the mountains like a mirror.",
    }

    # Build knowledge graph
    photo_rag.build_knowledge_graph(photo_descriptions)

    # Search for photos
    result = photo_rag.search_photos(
        "Picture with peaceful nature scenes with water")
    print(result)
