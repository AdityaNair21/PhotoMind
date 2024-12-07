import React from 'react';
import { Dialog, DialogContent, IconButton, Box, Typography } from '@mui/material';
import { CircleX } from 'lucide-react';
import { Photo } from '../../types/types';

interface PhotoPreviewProps {
    selectedPhoto: Photo | null;
    onClose: () => void;
}

export const PhotoPreview: React.FC<PhotoPreviewProps> = ({
    selectedPhoto,
    onClose
}) => {
    if (!selectedPhoto) return null;

    return (
        <Dialog
            open={!!selectedPhoto}
            onClose={onClose}
            maxWidth="md"
            fullWidth
        >
            <DialogContent className="relative p-0">
                <IconButton
                    onClick={onClose}
                    className="absolute top-2 right-2 bg-white/80 hover:bg-white"
                >
                    <CircleX className="h-5 w-5" />
                </IconButton>
                <Box
                    sx={{
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        overflow: 'hidden',
                        maxHeight: '80vh', // Constrain the image height within viewport height
                    }}
                >
                    <img
                        src={selectedPhoto.url}
                        alt={selectedPhoto.description || "Photo preview"}
                        style={{
                            maxWidth: '100%', // Image won't exceed container width
                            maxHeight: '80vh', // Constrain image height to viewport
                            objectFit: 'contain', // Maintain aspect ratio within bounds
                        }}
                    />
                </Box>
                <Box className="p-4">
                    <Typography variant="body2" className="text-gray-600">
                        {new Date(selectedPhoto.date).toLocaleDateString()}
                    </Typography>
                    <Typography>{selectedPhoto.description}</Typography>
                </Box>
            </DialogContent>
        </Dialog>
    );
};
