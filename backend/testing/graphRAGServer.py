import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import time
from typing import Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.docstore.document import Document
from functools import wraps

load_dotenv()

class PhotoGraphRAG:
    def __init__(self):
        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings()

        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_username = os.getenv("NEO4J_USERNAME")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize LLM transformer with common configuration
        self.llm_transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=[
                "Scene", "Landscape", "Building", "Person", "Activity",
                "NaturalFeature", "TimeContext", "Atmosphere", "Object",
                "Weather", "Location"
            ],
            allowed_relationships=[
                "CONTAINS", "HAS_FEATURE", "LOCATED_IN", "NEXT_TO",
                "PART_OF", "INTERACTS_WITH", "CREATES", "INFLUENCES",
                "USED_IN", "EXPERIENCES"
            ],
            node_properties=[
                "type", "description", "color", "atmosphere",
                "time_of_day", "weather", "activity_level", "importance"
            ],
            relationship_properties=[
                "description", "spatial", "temporal", "impact", "strength"
            ],
            strict_mode=True
        )

    # [Previous PhotoGraphRAG methods remain the same]
    def reset_knowledge_graph(self):
        """Reset the Neo4j database by clearing all nodes, relationships, and indexes"""
        print("Resetting Neo4j database...")
        try:
            self.graph.query("MATCH (n) DETACH DELETE n")
            
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

    def create_new_graph(self, photo_descriptions: Dict[str, str]):
        """Creates a completely new knowledge graph from scratch"""
        start_time = time.time()
        self.reset_knowledge_graph()
        documents = [
            Document(page_content=description, metadata={"filename": filename})
            for filename, description in photo_descriptions.items()
        ]
        graph_documents = self.llm_transformer.convert_to_graph_documents(documents)
        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True
        )
        self.vector_store = Neo4jVector.from_documents(
            documents,
            self.embeddings,
            index_name="photo_vectors",
            keyword_index_name="photo_keywords",
            search_type="hybrid"
        )
        end_time = time.time()
        print(f"New knowledge graph created in {end_time - start_time:.2f} seconds")

    def query_existing_graph(self, query: str) -> str:
        """Queries an existing graph without modifying it"""
        self.vector_store = Neo4jVector.from_existing_index(
            self.embeddings,
            url=self.neo4j_uri,
            username=self.neo4j_username,
            password=self.neo4j_password,
            index_name="photo_vectors",
        )
        if not hasattr(self, 'retrieval_chain'):
            self.setup_retrieval_chain()
        return self.retrieval_chain.invoke(query)

    def add_single_photo(self, filename: str, description: str):
        """Adds a single new photo to an existing graph"""
        start_time = time.time()
        document = Document(
            page_content=description,
            metadata={"filename": filename}
        )
        graph_documents = self.llm_transformer.convert_to_graph_documents([document])
        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True
        )
        self.vector_store = Neo4jVector.from_existing_index(
            self.embeddings,
            url=self.neo4j_uri,
            username=self.neo4j_username,
            password=self.neo4j_password,
            index_name="photo_vectors",
        )
        self.vector_store.add_documents([document])
        end_time = time.time()
        print(f"Added new photo in {end_time - start_time:.2f} seconds")

    def setup_retrieval_chain(self):
        """Set up the hybrid retrieval chain"""
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

        def generateContext(query: str) -> str:
            vector_results = [
                f"Photo {doc.metadata['filename']}: {doc.page_content}"
                for doc in self.vector_store.similarity_search(query, k=3)
            ]
            graph_results = self.graph.query("""
                CALL db.index.fulltext.queryNodes("photo_keywords", $query) YIELD node
                MATCH (node)<-[:MENTIONS|IN_PHOTO]-(photo:Document)
                RETURN DISTINCT photo.filename AS filename, photo.page_content AS description
                LIMIT 3
            """, {"query": query})

            return f"""
            Vector Search Results:
            {' '.join(vector_results)}
            
            Graph Search Results:
            {graph_results}
            """

        self.retrieval_chain = (
            {"context": generateContext, "query": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

# Initialize Flask app
app = Flask(__name__)

# Initialize PhotoGraphRAG instance
photo_rag = PhotoGraphRAG()

def error_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500
    return wrapper

def timing_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        if isinstance(result, tuple):
            response, status_code = result
        else:
            response, status_code = result, 200
            
        if isinstance(response, dict):
            response['execution_time'] = f"{end_time - start_time:.2f} seconds"
        
        return response, status_code
    return wrapper

@app.route('/api/graph/create', methods=['POST'])
@error_handler
@timing_decorator
def create_graph():
    data = request.get_json()
    
    if not data or 'photos' not in data:
        return jsonify({
            "error": "Missing 'photos' in request body",
            "status": "error"
        }), 400
        
    photos = data['photos']
    if not isinstance(photos, dict):
        return jsonify({
            "error": "Photos must be provided as a dictionary",
            "status": "error"
        }), 400
    
    photo_rag.create_new_graph(photos)
    
    return jsonify({
        "message": "Knowledge graph created successfully",
        "photo_count": len(photos),
        "status": "success"
    })

@app.route('/api/graph/search', methods=['POST'])
@error_handler
@timing_decorator
def search_graph():
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({
            "error": "Missing 'query' in request body",
            "status": "error"
        }), 400
    
    query = data['query']
    result = photo_rag.query_existing_graph(query)
    
    return jsonify({
        "result": result,
        "status": "success"
    })

@app.route('/api/graph/add-photo', methods=['POST'])
@error_handler
@timing_decorator
def add_photo():
    data = request.get_json()
    
    if not data or 'filename' not in data or 'description' not in data:
        return jsonify({
            "error": "Missing required fields: 'filename' and 'description'",
            "status": "error"
        }), 400
    
    filename = data['filename']
    description = data['description']
    
    photo_rag.add_single_photo(filename, description)
    
    return jsonify({
        "message": f"Photo {filename} added successfully",
        "status": "success"
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PhotoGraphRAG API"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
