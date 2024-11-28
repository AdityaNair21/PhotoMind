import { Photo } from '../types/types';

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
    async getAllPhotos(): Promise<Photo[]> {
        return photos.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    }

    async searchPhotos(query: string): Promise<Photo[]> {
        const lowercaseQuery = query.toLowerCase();
        return photos.filter(photo =>
            photo.description.toLowerCase().includes(lowercaseQuery)
        );
    }

    // photoService.ts
    async savePhoto(photoData: Omit<Photo, 'id'>): Promise<Photo> {
        const newPhoto = {
            id: Date.now(),
            ...photoData,
            // Just use the filename part since it will be served from frontend public
            url: `/images/${photoData.url.split('/').pop()}`
        };
        photos.unshift(newPhoto);
        return newPhoto;
    }
}