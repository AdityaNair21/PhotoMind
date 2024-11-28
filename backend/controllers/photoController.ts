import { Request, Response, NextFunction } from 'express';
import { PhotoService } from '../services/photoService.js';
import { OpenAIService } from '../services/openaiService.js';

const photoService = new PhotoService();
const openaiService = new OpenAIService();

export const getPhotos = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const photos = await photoService.getAllPhotos();
        res.json(photos);
    } catch (error) {
        next(error);
    }
};

export const searchPhotos = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { q } = req.query;
        if (!q || typeof q !== 'string') {
            throw { statusCode: 400, message: 'Search query is required' };
        }

        const photos = await photoService.searchPhotos(q);
        res.json(photos);
    } catch (error) {
        next(error);
    }
};

export const uploadPhoto = async (req: Request, res: Response, next: NextFunction) => {
    try {
        if (!req.file) {
            throw { statusCode: 400, message: 'No file uploaded' };
        }

        console.log('Uploaded file:', req.file); // Debug log

        const description = "this is a photo description";

        // Construct the URL path relative to the /images endpoint
        const photoUrl = `/images/${req.file.filename}`;

        const photo = await photoService.savePhoto({
            url: photoUrl,
            description,
            date: new Date().toISOString()
        });

        res.status(201).json(photo);
    } catch (error) {
        console.error('Upload error:', error); // Debug log
        next(error);
    }
};