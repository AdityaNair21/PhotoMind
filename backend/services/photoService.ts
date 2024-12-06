import { Photo } from '../types/types';

// Add interface for Flask API response
interface FlaskSearchResponse {
    result: string;
    time_taken: string;
}

// In-memory storage for demo purposes
// In production, use a proper database
let photos: Photo[] = [
    {
        id: 1,
        url: '/images/supercar.jpg',
        date: '2024-12-06',
        description: "The image showcases a striking green sports car, prominently displayed with its unique butterfly doors wide open, creating a dramatic effect. The car features a sleek and aerodynamic design, characterized by sharp lines and an aggressive front end. It is parked on a winding road, surrounded by a scenic landscape of lush greenery and rocky formations, suggesting a mountainous or coastal setting. The sunlight bathes the scene, enhancing the car's glossy finish and highlighting its features. The combination of the car's modern design and the natural surroundings creates a visually appealing contrast. The scene captures a sense of luxury and performance, inviting admiration for both the vehicle and its picturesque environment. Notable details include the intricate wheel design and the sophisticated interior visible through the open door, emphasizing the car's high"
    },
    {
        id: 2,
        url: '/images/chicken_fight.jpg',
        date: '2024-12-06',
        description: "The image captures a dynamic scene of two fighting roosters engaged in a fierce bout. Each bird is in mid-air, showcasing their powerful wings and muscular bodies. The rooster on the left has dark plumage with a glossy sheen, while the rooster on the right displays vibrant orange and brown feathers, emphasizing their contrasting appearances. The setting appears to be a dirt arena, likely outdoor, with a slightly blurred, indistinct background suggesting trees or foliage. Dust can be seen rising from the ground, adding to the intensity of the action. The focus on the birds highlights their aggressive postures, with each bird aiming to outmaneuver the other. Their spurs are prominently visible, indicating the competitive nature of this scene. Overall, the image conveys"
    },
    {
        id: 3,
        url: '/images/stone_ape.jpg',
        date: '2024-12-06',
        description: "The image features a surreal, cosmic scene centered around the profile of a large, expressive chimpanzee. It holds a mushroom in one hand, cleverly suggesting themes of growth, evolution, and consciousness. The chimp's gaze is directed towards a swirl of abstract shapes and symbols that cascade from its head, hinting at thoughts and ideas. Surrounding the chimp are various elements that depict the evolution of humanity and knowledge. We see iconic representations of human figures in various stages of development, alongside mathematical equations, musical notes, and references to science and space exploration, illustrating the journey from primitive to advanced thought. In the background, geometric and ageless symbols create a mystical backdrop, while the horizon features pyramids and a stylized cityscape, implying a"
    },
    {
        id: 4,
        url: '/images/city-lights.jpeg',
        date: '2024-12-06',
        description: "The image captures a breathtaking view of a sprawling cityscape at twilight, showcasing Hong Kong's iconic skyline. Towering skyscrapers dominate the foreground, their windows aglow with warm lights, creating a vibrant urban atmosphere. The city is nestled against the backdrop of lush green hills, contrasting the natural landscape with the densely packed buildings. In the distance, the shimmering waters of Victoria Harbour reflect the colorful lights of the city, enhancing the scene's beauty. Notable structures such as the International Commerce Centre and the HSBC Building can be seen, further emphasizing Hong Kong's status as a financial hub. The sky transitions from soft pinks and purples to deeper blues as night approaches, adding to the overall tranquility of the moment. The entire composition conveys a sense of"
    },
    {
        id: 5,
        url: '/images/beach_sunset.jpg',
        date: '2024-12-06',
        description: "The image captures a serene beach scene during sunset. The foreground features soft, sandy textures with gentle undulations, suggesting a relaxed atmosphere. The shoreline curves gracefully where the light golden sand meets the calm ocean water. The backdrop showcases a vibrant sky filled with a palette of warm hues—soft oranges, pinks, and yellows blending seamlessly with cool blues. Wispy clouds scatter across the sky, illuminated by the fading sunlight, creating a dramatic yet peaceful ambiance. As the sun dips toward the horizon, a shimmering reflection dances on the water's surface, adding a touch of sparkles to the serene scene. Small waves gently lap against the shore, enhancing the tranquility, while the overall composition evokes a sense of calm and natural beauty, making it a perfect"
    },
    {
        id: 6,
        url: '/images/curved_road.jpg',
        date: '2024-12-06',
        description: "The image depicts a winding road on a hillside, characterized by its smooth, newly paved asphalt. In the foreground, there's a gravel shoulder where the ground transitions from pavement to dirt, with small rocky patches and sparse vegetation. To the left, a metal guardrail provides safety along the curve of the road, with yellow and black hazard markings indicating a sharp turn ahead. A vehicle, likely an SUV, is seen navigating the bend, moving into the distance. The landscape features dry, golden grass and a rocky hillside, suggesting a warm climate. In the background, rolling hills are visible, fading into a clearer sky. The overall atmosphere conveys a sense of rural tranquility, with open space and scenic views typical of a mountainous or hilly region."
    },
    {
        id: 7,
        url: '/images/gentlemen.jpeg',
        date: '2024-12-06',
        description: "The image features four men standing confidently next to a silver minivan parked in a residential area during the evening. They are dressed in formal attire, with suits and sunglasses, giving a stylish and sophisticated impression. The man on the left wears a blue suit with a patterned tie, exuding a confident demeanor. Next to him, a man in a gray plaid suit stands with his hands clasped, showcasing a more reserved posture. The third individual is dressed in a black suit with a white shirt and a dark tie, while the fourth man, on the far right, sports a black suit with a striped tie and has a subtle badge on his lapel. In the background, the setting includes a well-maintained house with a garage door, and"
    },
    {
        id: 8,
        url: '/images/family-dinner.jpg',
        date: '2024-12-06',
        description: "The image features a lively group of five people gathered around a wooden dining table, sharing a meal. The setting is bright and inviting, with natural light streaming through large windows, revealing a modern, airy interior. At the center of the table is a large platter of spaghetti, complemented by pieces of bread on a cutting board. Each person has a plate with pasta, and there are glasses of water in front of them. The group consists of three women and two men, all displaying cheerful expressions and engaged in animated conversation. One woman, wearing a pink top, is gesturing with her hand as she speaks, adding warmth to the interaction. The others, dressed in casual attire, seem equally involved, with smiles and laughter contributing to a joyful atmosphere"
    },
    {
        id: 9,
        url: '/images/coffee-shop.jpeg',
        date: '2024-12-06',
        description: "The image depicts a lively café atmosphere with a modern and inviting design. The interior features large windows that allow natural light to flood the space, highlighting the stylish furnishings and décor. On the left side, several patrons are seated at wooden tables, absorbed in work or conversation. A woman in a red sweater appears to be using her laptop, while another individual leans back, seemingly deep in thought. To the right, a barista is working behind the counter, preparing beverages, with an additional staff member assisting. The counter is neatly arranged with coffee-making equipment and colorful dishware, emphasizing the café's focus on quality service. The décor includes minimalist shelving adorned with various items, including decorative vases and potentially local art, contributing to the café's"
    },
    {
        id: 10,
        url: '/images/mountain-hike.jpeg',
        date: '2024-12-06',
        description: "The image depicts a scenic mountain hiking trail with a hiker as the main subject. The hiker, carrying a large backpack, is seen walking along a narrow dirt path that winds through lush greenery and flowering shrubbery. This path is bordered by tall coniferous trees on either side, adding to the natural beauty of the setting. In the background, majestic snow-capped mountains rise dramatically, their peaks piercing the blue sky, which is scattered with a few wispy clouds. The vibrant colors of the surrounding foliage juxtapose beautifully with the rugged mountain terrain and clear, bright sky. The hiker appears focused on the trail ahead, using trekking poles to aid their ascent. This image captures a moment of solitude and adventure in a breathtaking outdoor environment,"
    },
    {
        id: 11,
        url: '/images/puppies.jpg',
        date: '2024-12-06',
        description: "The image features a delightful scene of eight adorable puppies nestled in a wicker basket. The puppies vary in color, with some having predominantly white fur and others showcasing shades of gray and black. Their expressions are curious and playful, capturing the innocence and charm typical of young dogs. The setting is a lush, green outdoor space with soft grass beneath the basket, suggesting a warm and inviting day. In the background, hints of foliage, possibly bushes or small trees, add depth to the scene, creating a vibrant, natural ambiance. Notable details include the various positions of the puppies—some are sitting upright, others are leaning against each other, displaying their playful nature. The basket itself is light brown with a natural weave pattern, contributing to the overall cozy and"
    },
    {
        id: 12,
        url: '/images/kittens.jpg',
        date: '2024-12-06',
        description: "The image features a group of six adorable kittens, gathered closely together on a colorful patchwork quilt. The kittens predominantly display a mix of black and white fur, with some having distinctive black markings on their faces and bodies. Their large, expressive eyes—ranging from green to blue—create a sense of curiosity and playfulness. The setting is cozy and inviting, with the vibrant quilt showcasing various patterns and colors, adding to the cheerful atmosphere. The kittens appear to be in a playful mood, with their ears perked up and whiskers twitching, as if they are eager to explore their surroundings or engage in playful antics with each other. The composition captures their youthful energy perfectly, making it an endearing and heartwarming scene."
    },
    {
        id: 13,
        url: '/images/chickfila.jpg',
        date: '2024-12-06',
        description: "The image depicts a Chick-fil-A restaurant, showcasing its distinctive exterior design. The building features a combination of brick and bright red panels, with the Chick-fil-A logo prominently displayed on the roof. Large windows line the front, allowing a view of the menu and interior. In the foreground, there is a paved parking area, which is clean and well-maintained. The landscaping includes some low shrubs, contributing to an inviting atmosphere. A drive-thru sign is visible, indicating the restaurant's services, while additional signage promotes menu items and specials. The clear blue sky above suggests a sunny day, enhancing the vibrant appearance of the establishment. Overall, the setting conveys a sense of accessibility and modernity, typical of fast-casual dining experiences."
    },
    {
        id: 14,
        url: '/images/the_amish.jpg',
        date: '2024-12-06',
        description: "The image features a group of five individuals posed outdoors in a scenic setting with greenery in the background. They appear to be dressed in attire reminiscent of traditional or perhaps Amish style clothing. On the left, a woman in a long, teal dress with a white apron and a cap smiles at the camera. Next to her stands a young boy wearing a gray shirt and black vest, with his hands in his pockets, giving a relaxed stance. Beside him, a teenage boy wears a blue shirt and a black vest, also with his hands in his pockets, suggesting a casual vibe. In the center, another young boy is dressed in a green shirt with a black vest and shorts, embodying a playful appearance. To the right stands another woman dressed"
    },
    {
        id: 15,
        url: '/images/eiffel_tower.jpg',
        date: '2024-12-06',
        description: "The image showcases the iconic Eiffel Tower rising majestically against a vibrant sunset sky, characterized by a palette of oranges, pinks, and blues. Below the tower, you can see a tranquil water feature reflecting the stunning colors of the sky. The area features lush green lawns with neatly trimmed hedges and a variety of trees, their leaves glowing with the warm hues of dusk. In the foreground, a series of modern, curved structures and fountains create an elegant, artistic display. To the right, a carousel can be spotted, adding a playful touch to the scene. People are leisurely walking and enjoying the surroundings, contributing to the lively yet serene atmosphere of this famous Parisian landmark. The overall composition captures a beautiful blend of architecture, nature, and urban"
    },
    {
        id: 16,
        url: '/images/gym_bro.jpg',
        date: '2024-12-06',
        description: "In the image, a muscular man is seated on a bench press within a gym setting, preparing for a lift. He is wearing a sleeveless workout shirt that showcases his well-defined arms and shoulders, paired with athletic shorts. His focused expression indicates he's concentrating on the task ahead. Behind him, a woman stands as a spotter, providing support and encouragement. She is dressed in a black zip-up jacket and fitted leggings, with a black mask covering her face. The gym environment is characterized by a spacious layout, equipped with various weightlifting equipment in the background, and has a moody, industrial aesthetic, highlighted by darker walls and subtle lighting. Notable details include the heavy weights on the barbell, indicating a challenging lift, and"
    }
];

export class PhotoService {
    private flaskApiUrl: string;

    constructor() {
        // Configure your Flask API URL here
        this.flaskApiUrl = process.env.FLASK_API_URL || 'http://localhost:7500';
    }

    async getAllPhotos(): Promise<Photo[]> {
        return photos.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    }

    async searchPhotos(query: string): Promise<Photo[]> {
        try {

            console.log("QUERY: " + query)
            // Make request to Flask API
            const response = await fetch(`${this.flaskApiUrl}/search_photos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });

            if (!response.ok) {
                throw new Error(`Flask API error: ${response.statusText}`);
            }

            const data: FlaskSearchResponse = await response.json();

            // Parse the result from Flask
            // The result is in format:
            // Filename: <filename>
            // Primary Match Factors: ...
            // Detailed Reasoning: ...
            // Alternative Considerations: ...
            const resultLines = data.result.split('\n');
            const filename = resultLines[0].split(': ')[1].trim();

            // First try to find the exact photo
            const matchedPhoto = photos.find(p => p.url.includes(filename));
            if (matchedPhoto) {
                return [matchedPhoto];
            }

            // Fallback to traditional text search if no match found
            const lowercaseQuery = query.toLowerCase();
            return photos.filter(photo =>
                photo.description.toLowerCase().includes(lowercaseQuery)
            );

        } catch (error) {
            console.error('Error searching photos via Flask:', error);
            // Fallback to basic text search on error
            const lowercaseQuery = query.toLowerCase();
            return photos.filter(photo =>
                photo.description.toLowerCase().includes(lowercaseQuery)
            );
        }
    }

    async savePhoto(photoData: Omit<Photo, 'id'>): Promise<Photo> {
        const newPhoto = {
            id: Date.now(),
            ...photoData,
            url: `/images/${photoData.url.split('/').pop()}`
        };
        photos.unshift(newPhoto);

        try {
            // Update the knowledge graph with the new photo
            // await fetch(`${this.flaskApiUrl}/build_knowledge_graph`, {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify({
            //         photos: {
            //             [newPhoto.url]: newPhoto.description
            //         }
            //     })
            // });
        } catch (error) {
            console.error('Error updating knowledge graph:', error);
            // Continue even if knowledge graph update fails
            // The photo is still saved in local storage
        }

        return newPhoto;
    }
}