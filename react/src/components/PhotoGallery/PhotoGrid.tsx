import React from 'react';
import { Masonry } from '@mui/lab';
import { Paper, Box, Typography } from '@mui/material';
import { Photo, ExtendedPhoto } from '../../types/types';

interface PhotoGridProps {
    photos: ExtendedPhoto[];
    onPhotoClick: (photo: ExtendedPhoto) => void;
}

export const PhotoGrid: React.FC<PhotoGridProps> = ({ photos, onPhotoClick }) => {
    return (
        <Masonry columns={{ xs: 1, sm: 2, md: 3, lg: 4 }} spacing={2}>
            {photos.map((photo) => (
                <Paper
                    key={photo.id}
                    className="break-inside-avoid cursor-pointer transition-transform hover:scale-[1.02]"
                    onClick={() => onPhotoClick(photo)}
                    sx={{ borderRadius: 2, overflow: 'hidden' }}
                >
                    <Box sx={{ position: 'relative', width: '100%', height: 0, paddingBottom: '56.25%' }}>
                        <img
                            src={photo.localUrl || photo.url}
                            alt={photo.description}
                            style={{
                                objectFit: 'cover',
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%',
                                borderRadius: '8px 8px 0 0',
                            }}
                        />
                    </Box>

                    <Box sx={{ p: 2 }}>
                        <Typography variant="caption" color="textSecondary">
                            {new Date(photo.date).toLocaleDateString()}
                        </Typography>
                    </Box>
                </Paper>
            ))}
        </Masonry>
    );
};

