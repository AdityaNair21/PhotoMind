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
        url: '/images/beach-sunset.jpg',
        date: '2024-03-15',
        description: 'A beautiful beach sunset with waves crashing on the shore'
    },
    {
        id: 2,
        url: '/images/family-dinner.jpg',
        date: '2024-03-14',
        description: 'Family gathered around a dinner table sharing a meal'
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