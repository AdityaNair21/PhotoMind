// photoRoutes.ts
import express from 'express';
import { getPhotos, searchPhotos, uploadPhoto } from '../controllers/photoController.js';
import { Multer } from 'multer';

export const photoRoutes = (upload: Multer) => {
    const router = express.Router();

    router.get('/', getPhotos);
    router.get('/search', searchPhotos);
    router.post('/upload', upload.single('photo'), uploadPhoto);

    return router;
};
