import { Photo } from '../types/types';
import axios from 'axios';

const BASE_URL = 'http://localhost:3001/api';

export const api = {
    getPhotos: async (): Promise<Photo[]> => {
        try {
            const response = await axios.get(`${BASE_URL}/photos`);
            return response.data.sort((a: Photo, b: Photo) => {
                const dateA = new Date(a.date).getTime();
                const dateB = new Date(b.date).getTime();
                return dateB - dateA;
            });
        } catch (error) {
            console.error('Error fetching photos:', error);
            throw error;
        }
    },

    searchPhotos: async (query: string): Promise<Photo[]> => {
        try {
            const response = await axios.get(`${BASE_URL}/photos/search`, {
                params: { query }
            });
            return response.data;
        } catch (error) {
            console.error('Error searching photos:', error);
            throw error;
        }
    },

    uploadPhoto: async (file: File): Promise<Photo> => {
        try {
            // Create a copy of the file with a cleaned-up name
            const cleanFileName = file.name.toLowerCase().replace(/\s+/g, '-');
            const newFile = new File([file], cleanFileName, { type: file.type });

            const formData = new FormData();
            formData.append('photo', newFile);

            // Send the cleaned filename as a separate field
            formData.append('desiredPath', `/images/${cleanFileName}`);

            // Create a local URL for immediate display
            const localUrl = URL.createObjectURL(file);

            const response = await axios.post(`${BASE_URL}/photos/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                }
            });


            // Return both the server response and the local URL
            return {
                ...response.data,
                localUrl
            };

        } catch (error) {
            console.error('Error uploading photo:', error);
            throw error;
        }
    }
};