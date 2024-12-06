import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import multer, { Multer } from 'multer';
import { errorHandler } from './middleware/errorHandler.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import path from 'path';

// Import controllers
import { getPhotos, searchPhotos, uploadPhoto } from './controllers/photoController.js';

// Helper variables for paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to frontend public folder (adjust this path based on your project structure)
const FRONTEND_PUBLIC_PATH = path.join(__dirname, '../react/public/images');

dotenv.config();

const app = express();
const PORT = 3001;

// Configure multer for file uploads to frontend public folder
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        // Create directory if it doesn't exist
        import('fs').then(fs => {
            fs.mkdir(FRONTEND_PUBLIC_PATH, { recursive: true }, (err) => {
                if (err) {
                    console.error('Error creating directory:', err);
                }
                cb(null, FRONTEND_PUBLIC_PATH);
            });
        });
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + path.extname(file.originalname));
    }
});

const upload: Multer = multer({ storage: storage });

// Middleware
app.use(cors());
app.use(express.json());

// Routes
const photoRoutes = (upload: Multer) => {
    const router = express.Router();

    router.get('/', getPhotos);
    router.get('/search', searchPhotos);
    router.post('/upload', upload.single('photo'), uploadPhoto);

    return router;
};

app.use('/api/photos', photoRoutes(upload));

// Error handling
app.use(errorHandler);

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Saving files to: ${FRONTEND_PUBLIC_PATH}`);
});
