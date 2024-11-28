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
                <img
                    src={selectedPhoto.url}
                    // alt={selectedPhoto.description}
                    className="w-full h-auto"
                />
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