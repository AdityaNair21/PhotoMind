import React, { useState, useEffect } from 'react';
import { Box, Container } from '@mui/material';
import { Photo, ExtendedPhoto, NotificationState } from '../../types/types';
import { api } from '../../utils/api';
import { SearchBar } from './SearchBar';
import { UploadButton } from './UploadButton';
import { PhotoGrid } from './PhotoGrid';
import { PhotoPreview } from './PhotoPreview';
import { NotificationSnackbar } from './NotificationSnackbar';
import { UploadBackdrop } from './UploadBackdrop';


export const PhotoGallery = () => {
    const [photos, setPhotos] = useState<ExtendedPhoto[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [notification, setNotification] = useState<NotificationState>({
        open: false,
        message: '',
        severity: 'success'
    });
    const [selectedPhoto, setSelectedPhoto] = useState<Photo | null>(null);

    useEffect(() => {
        loadPhotos();
    }, []);

    const loadPhotos = async () => {
        try {
            const data = await api.getPhotos();
            setPhotos(data);
        } catch (error) {
            showNotification('Error loading photos', 'error');
        }
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setIsSearching(true);
        try {
            const results = await api.searchPhotos(searchQuery);
            setPhotos(results);
            showNotification(`Found ${results.length} matching photos`, 'success');
        } catch (error) {
            showNotification('Error searching photos', 'error');
        } finally {
            setIsSearching(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const response = await api.uploadPhoto(file);
            const localUrl = URL.createObjectURL(file);

            const newPhoto: ExtendedPhoto = {
                ...response,
                localUrl
            };

            // Add to photos array with local URL
            setPhotos(prev => [newPhoto, ...prev]);

            // Preload the image
            const img = new Image();
            img.onload = () => {
                // Once the server image is loaded, update the photo to use the server URL
                setPhotos(prev =>
                    prev.map(photo =>
                        photo.id === newPhoto.id
                            ? { ...photo, localUrl: undefined }
                            : photo
                    )
                );
                URL.revokeObjectURL(localUrl); // Clean up the local URL
            };
            img.src = newPhoto.url;

            showNotification('Photo uploaded successfully', 'success');
        } catch (error) {
            showNotification('Error uploading photo', 'error');
        } finally {
            setIsUploading(false);
        }
    };

    // Clean up local URLs when component unmounts
    useEffect(() => {
        return () => {
            photos.forEach(photo => {
                if (photo.localUrl) {
                    URL.revokeObjectURL(photo.localUrl);
                }
            });
        };
    }, []);

    const showNotification = (message: string, severity: NotificationState['severity']) => {
        setNotification({ open: true, message, severity });
    };

    return (
        <Box className="min-h-screen bg-gray-100">
            <SearchBar
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                handleSearch={handleSearch}
                isSearching={isSearching}
            />

            {/* Main content container with proper spacing */}
            <Container
                maxWidth="xl"
                sx={{
                    pt: '84px', // 64px (header height) + 20px padding
                    pb: 4,
                    px: { xs: 2, sm: 3, md: 4 } // Responsive padding
                }}
            >
                {/* Upload button container */}
                <Box sx={{ mb: 3 }}>
                    <UploadButton
                        handleFileUpload={handleFileUpload}
                        isUploading={isUploading}
                    />
                </Box>

                {/* Photo grid with proper spacing */}
                <Box sx={{ mt: 2 }}>
                    <PhotoGrid
                        photos={photos}
                        onPhotoClick={setSelectedPhoto}
                    />
                </Box>
            </Container>

            <PhotoPreview
                selectedPhoto={selectedPhoto}
                onClose={() => setSelectedPhoto(null)}
            />

            <UploadBackdrop open={isUploading} />

            <NotificationSnackbar
                notification={notification}
                onClose={() => setNotification({ ...notification, open: false })}
            />
        </Box>
    );
};


