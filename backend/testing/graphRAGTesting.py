from flask import Flask, request, jsonify
import os
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

load_dotenv()

app = Flask(__name__)


class PhotoGraphRAG:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PhotoGraphRAG, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.graph = Neo4jGraph()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings()

        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_username = os.getenv("NEO4J_USERNAME")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Initialize vector store connection
        try:
            self.vector_store = Neo4jVector.from_existing_index(
                OpenAIEmbeddings(),
                url=self.neo4j_uri,
                username=self.neo4j_username,
                password=self.neo4j_password,
                index_name="photo_vectors",
            )
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
            self.vector_store = None

        self._initialized = True

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
                self.graph.query(
                    "CALL db.index.fulltext.drop('photo_keywords')")
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
                "NaturalFeature",  # Natural elements
                "TimeContext",     # Temporal aspects
                "Atmosphere",      # Mood/ambiance
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
        if not hasattr(self, 'retrieval_chain'):
            template = """Given the following structured and unstructured search results about photos, 
            analyze both the direct content and the relationships between elements to find the most relevant photos.

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

            Only choose photos that are directly relevent, be less photos the better. 

            Provide your response in this format:
            Filename: [<chosen_filename1>, <chosen_filename2>, ....]
            Primary Match Factors:
            - [List 2-3 key elements that strongly match the query]
            Detailed Reasoning: [Explain how the chosens photo's elements, relationships, and atmosphere align with the query]

            """
#             Alternative Considerations: [Briefly mention why this photo was chosen over other potential matches]

            prompt = ChatPromptTemplate.from_template(template)

            def retriever(query: str) -> str:
                # Get results from vector similarity search
                vector_results = [
                    f"Photo {doc.metadata['filename']}: {doc.page_content}"
                    for doc in self.vector_store.similarity_search(query, k=3)
                ]

                # Get results from graph pattern matching
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


# Create PhotoGraphRAG instance
photo_rag = PhotoGraphRAG()


@app.route('/build_knowledge_graph', methods=['POST'])
def build_graph():
    """
    Endpoint to build the knowledge graph from photo descriptions
    Expected JSON format:
    {
        "photos": {
            "1.jpg": "A desert sand storm...",
            "2.jpg": "A serene mountain lake..."
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'photos' not in data:
            return jsonify({"error": "No photo data provided"}), 400

        photo_descriptions = data['photos']
        start_time = time.time()

        photo_rag.build_knowledge_graph(photo_descriptions)

        end_time = time.time()
        return jsonify({
            "message": "Knowledge graph built successfully",
            "time_taken": f"{end_time - start_time:.2f} seconds"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search_photos', methods=['POST'])
def search_photos():
    """
    Endpoint to search photos based on a query
    Expected JSON format:
    {
        "query": "Busy downtown"
    }
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400

        query = data['query']
        print("SEARCH PHOTOS HAS BEEN CALLED")
        print("QUERY: " + query)

        # Ensure retrieval chain is set up
        # photo_rag.setup_retrieval_chain()

        start_time = time.time()
        result = photo_rag.search_photos(query)
        end_time = time.time()

        return jsonify({
            "result": result,
            "time_taken": f"{end_time - start_time:.2f} seconds"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "neo4j_connected": photo_rag.graph is not None,
        "vector_store_initialized": photo_rag.vector_store is not None
    })


def test_graphrag():
    """
    Test function to verify PhotoGraphRAG functionality directly without Flask
    Comment out when deploying the server
    """
    print("Running PhotoGraphRAG tests\n")

    try:
        # Initialize PhotoGraphRAG
        start_time = time.time()
        photo_rag = PhotoGraphRAG()
        end_time = time.time()
        print(
            f"PhotoGraphRAG Instantiated in {end_time - start_time:.2f} seconds\n")

        # Test data
        photo_descriptions = {
            "supercar.jpg": "The image showcases a striking green sports car, prominently displayed with its unique butterfly doors wide open, creating a dramatic effect. The car features a sleek and aerodynamic design, characterized by sharp lines and an aggressive front end. It is parked on a winding road, surrounded by a scenic landscape of lush greenery and rocky formations, suggesting a mountainous or coastal setting. The sunlight bathes the scene, enhancing the car's glossy finish and highlighting its features. The combination of the car's modern design and the natural surroundings creates a visually appealing contrast. The scene captures a sense of luxury and performance, inviting admiration for both the vehicle and its picturesque environment. Notable details include the intricate wheel design and the sophisticated interior visible through the open door, emphasizing the car's high",
            "chicken_fight.jpg": "The image captures a dynamic scene of two fighting roosters engaged in a fierce bout. Each bird is in mid-air, showcasing their powerful wings and muscular bodies. The rooster on the left has dark plumage with a glossy sheen, while the rooster on the right displays vibrant orange and brown feathers, emphasizing their contrasting appearances. The setting appears to be a dirt arena, likely outdoor, with a slightly blurred, indistinct background suggesting trees or foliage. Dust can be seen rising from the ground, adding to the intensity of the action. The focus on the birds highlights their aggressive postures, with each bird aiming to outmaneuver the other. Their spurs are prominently visible, indicating the competitive nature of this scene. Overall, the image conveys",
            "stone_ape.jpg": "The image features a surreal, cosmic scene centered around the profile of a large, expressive chimpanzee. It holds a mushroom in one hand, cleverly suggesting themes of growth, evolution, and consciousness. The chimp's gaze is directed towards a swirl of abstract shapes and symbols that cascade from its head, hinting at thoughts and ideas. Surrounding the chimp are various elements that depict the evolution of humanity and knowledge. We see iconic representations of human figures in various stages of development, alongside mathematical equations, musical notes, and references to science and space exploration, illustrating the journey from primitive to advanced thought. In the background, geometric and ageless symbols create a mystical backdrop, while the horizon features pyramids and a stylized cityscape, implying a",
            "city-lights.jpeg": "The image captures a breathtaking view of a sprawling cityscape at twilight, showcasing Hong Kong's iconic skyline. Towering skyscrapers dominate the foreground, their windows aglow with warm lights, creating a vibrant urban atmosphere. The city is nestled against the backdrop of lush green hills, contrasting the natural landscape with the densely packed buildings. In the distance, the shimmering waters of Victoria Harbour reflect the colorful lights of the city, enhancing the scene's beauty. Notable structures such as the International Commerce Centre and the HSBC Building can be seen, further emphasizing Hong Kong's status as a financial hub. The sky transitions from soft pinks and purples to deeper blues as night approaches, adding to the overall tranquility of the moment. The entire composition conveys a sense of",
            "beach_sunset.jpg": "The image captures a serene beach scene during sunset. The foreground features soft, sandy textures with gentle undulations, suggesting a relaxed atmosphere. The shoreline curves gracefully where the light golden sand meets the calm ocean water. The backdrop showcases a vibrant sky filled with a palette of warm hues—soft oranges, pinks, and yellows blending seamlessly with cool blues. Wispy clouds scatter across the sky, illuminated by the fading sunlight, creating a dramatic yet peaceful ambiance. As the sun dips toward the horizon, a shimmering reflection dances on the water's surface, adding a touch of sparkles to the serene scene. Small waves gently lap against the shore, enhancing the tranquility, while the overall composition evokes a sense of calm and natural beauty, making it a perfect",
            "curved_road.jpg": "The image depicts a winding road on a hillside, characterized by its smooth, newly paved asphalt. In the foreground, there's a gravel shoulder where the ground transitions from pavement to dirt, with small rocky patches and sparse vegetation. To the left, a metal guardrail provides safety along the curve of the road, with yellow and black hazard markings indicating a sharp turn ahead. A vehicle, likely an SUV, is seen navigating the bend, moving into the distance. The landscape features dry, golden grass and a rocky hillside, suggesting a warm climate. In the background, rolling hills are visible, fading into a clearer sky. The overall atmosphere conveys a sense of rural tranquility, with open space and scenic views typical of a mountainous or hilly region.",
            "gentlemen.jpeg": "The image features four men standing confidently next to a silver minivan parked in a residential area during the evening. They are dressed in formal attire, with suits and sunglasses, giving a stylish and sophisticated impression. The man on the left wears a blue suit with a patterned tie, exuding a confident demeanor. Next to him, a man in a gray plaid suit stands with his hands clasped, showcasing a more reserved posture. The third individual is dressed in a black suit with a white shirt and a dark tie, while the fourth man, on the far right, sports a black suit with a striped tie and has a subtle badge on his lapel. In the background, the setting includes a well-maintained house with a garage door, and",
            "family-dinner.jpg": "The image features a lively group of five people gathered around a wooden dining table, sharing a meal. The setting is bright and inviting, with natural light streaming through large windows, revealing a modern, airy interior. At the center of the table is a large platter of spaghetti, complemented by pieces of bread on a cutting board. Each person has a plate with pasta, and there are glasses of water in front of them. The group consists of three women and two men, all displaying cheerful expressions and engaged in animated conversation. One woman, wearing a pink top, is gesturing with her hand as she speaks, adding warmth to the interaction. The others, dressed in casual attire, seem equally involved, with smiles and laughter contributing to a joyful atmosphere",
            "coffee-shop.jpeg": "The image depicts a lively café atmosphere with a modern and inviting design. The interior features large windows that allow natural light to flood the space, highlighting the stylish furnishings and décor. On the left side, several patrons are seated at wooden tables, absorbed in work or conversation. A woman in a red sweater appears to be using her laptop, while another individual leans back, seemingly deep in thought. To the right, a barista is working behind the counter, preparing beverages, with an additional staff member assisting. The counter is neatly arranged with coffee-making equipment and colorful dishware, emphasizing the café's focus on quality service. The décor includes minimalist shelving adorned with various items, including decorative vases and potentially local art, contributing to the café's",
            "mountain-hike.jpeg": "The image depicts a scenic mountain hiking trail with a hiker as the main subject. The hiker, carrying a large backpack, is seen walking along a narrow dirt path that winds through lush greenery and flowering shrubbery. This path is bordered by tall coniferous trees on either side, adding to the natural beauty of the setting. In the background, majestic snow-capped mountains rise dramatically, their peaks piercing the blue sky, which is scattered with a few wispy clouds. The vibrant colors of the surrounding foliage juxtapose beautifully with the rugged mountain terrain and clear, bright sky. The hiker appears focused on the trail ahead, using trekking poles to aid their ascent. This image captures a moment of solitude and adventure in a breathtaking outdoor environment,",
            "puppies.jpg": "The image features a delightful scene of eight adorable puppies nestled in a wicker basket. The puppies vary in color, with some having predominantly white fur and others showcasing shades of gray and black. Their expressions are curious and playful, capturing the innocence and charm typical of young dogs. The setting is a lush, green outdoor space with soft grass beneath the basket, suggesting a warm and inviting day. In the background, hints of foliage, possibly bushes or small trees, add depth to the scene, creating a vibrant, natural ambiance. Notable details include the various positions of the puppies—some are sitting upright, others are leaning against each other, displaying their playful nature. The basket itself is light brown with a natural weave pattern, contributing to the overall cozy and",
            "kittens.jpg": "The image features a group of six adorable kittens, gathered closely together on a colorful patchwork quilt. The kittens predominantly display a mix of black and white fur, with some having distinctive black markings on their faces and bodies. Their large, expressive eyes—ranging from green to blue—create a sense of curiosity and playfulness. The setting is cozy and inviting, with the vibrant quilt showcasing various patterns and colors, adding to the cheerful atmosphere. The kittens appear to be in a playful mood, with their ears perked up and whiskers twitching, as if they are eager to explore their surroundings or engage in playful antics with each other. The composition captures their youthful energy perfectly, making it an endearing and heartwarming scene.",
            "chickfila.jpg": "The image depicts a Chick-fil-A restaurant, showcasing its distinctive exterior design. The building features a combination of brick and bright red panels, with the Chick-fil-A logo prominently displayed on the roof. Large windows line the front, allowing a view of the menu and interior. In the foreground, there is a paved parking area, which is clean and well-maintained. The landscaping includes some low shrubs, contributing to an inviting atmosphere. A drive-thru sign is visible, indicating the restaurant's services, while additional signage promotes menu items and specials. The clear blue sky above suggests a sunny day, enhancing the vibrant appearance of the establishment. Overall, the setting conveys a sense of accessibility and modernity, typical of fast-casual dining experiences.",
            "the_amish.jpg": "The image features a group of five individuals posed outdoors in a scenic setting with greenery in the background. They appear to be dressed in attire reminiscent of traditional or perhaps Amish style clothing. On the left, a woman in a long, teal dress with a white apron and a cap smiles at the camera. Next to her stands a young boy wearing a gray shirt and black vest, with his hands in his pockets, giving a relaxed stance. Beside him, a teenage boy wears a blue shirt and a black vest, also with his hands in his pockets, suggesting a casual vibe. In the center, another young boy is dressed in a green shirt with a black vest and shorts, embodying a playful appearance. To the right stands another woman dressed",
            "eiffel_tower.jpg": "The image showcases the iconic Eiffel Tower rising majestically against a vibrant sunset sky, characterized by a palette of oranges, pinks, and blues. Below the tower, you can see a tranquil water feature reflecting the stunning colors of the sky. The area features lush green lawns with neatly trimmed hedges and a variety of trees, their leaves glowing with the warm hues of dusk. In the foreground, a series of modern, curved structures and fountains create an elegant, artistic display. To the right, a carousel can be spotted, adding a playful touch to the scene. People are leisurely walking and enjoying the surroundings, contributing to the lively yet serene atmosphere of this famous Parisian landmark. The overall composition captures a beautiful blend of architecture, nature, and urban",
            "gym_bro.jpg": "In the image, a muscular man is seated on a bench press within a gym setting, preparing for a lift. He is wearing a sleeveless workout shirt that showcases his well-defined arms and shoulders, paired with athletic shorts. His focused expression indicates he's concentrating on the task ahead. Behind him, a woman stands as a spotter, providing support and encouragement. She is dressed in a black zip-up jacket and fitted leggings, with a black mask covering her face. The gym environment is characterized by a spacious layout, equipped with various weightlifting equipment in the background, and has a moody, industrial aesthetic, highlighted by darker walls and subtle lighting. Notable details include the heavy weights on the barbell, indicating a challenging lift, and",
            "desert.jpg": "The image captures a vast desert landscape characterized by rolling sand dunes with intricate ripples in the sand, showcasing patterns created by the wind. The dunes rise and fall in gentle waves, reflecting golden hues under sunlight against a bright blue sky dotted with wispy clouds.",
            "tesla.jpg": "The image depicts a sleek silver Tesla car parked on a winding road through a picturesque landscape with rolling hills and mountains. The setting is illuminated by sunset's warm glow, with the car's shiny body reflecting sunlight, emphasizing its modern design and clean lines.",
            "prius.jpg": "The image features a sleek, modern silver car, possibly a hybrid or electric model, navigating an open road. The vehicle is positioned dynamically, suggesting motion and speed, with a streamlined design that highlights its aerodynamic shape."
            }

        # Test building knowledge graph
        print("Testing knowledge graph construction...")
        start_time = time.time()
        try:
            photo_rag.build_knowledge_graph(photo_descriptions)
            end_time = time.time()
            print(
                f"Knowledge graph built in {end_time - start_time:.2f} seconds\n")
        except Exception as e:
            print(f"Error building knowledge graph: {str(e)}")
            raise e

        # Test photo search
        print("Testing photo search...")
        start_time = time.time()
        result = photo_rag.search_photos("Busy downtown")
        end_time = time.time()
        print(
            f"Photo search completed in {end_time - start_time:.2f} seconds\n")

        print("Search Result:")
        print(result)

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    # Uncomment the relevant section based on your needs

    # For testing PhotoGraphRAG functionality directly:
    test_graphrag()

    # For running the Flask server:
    port = int(os.getenv("PORT", 7500))
    app.run(host='0.0.0.0', port=port)
