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
        const { query } = req.query;
        console.log("QUERYsearchPhotos: " + query)
        if (!query || typeof query !== 'string') {
            throw { statusCode: 400, message: 'Search query is required' };
        }
        const photos = await photoService.searchPhotos(query);
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

        // const description = "this is a photo description";
        const description = await openaiService.generateImageDescription(req.file.path);

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