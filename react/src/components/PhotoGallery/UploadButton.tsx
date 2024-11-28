import React from 'react';
import { Paper, Typography, CircularProgress } from '@mui/material';
import { CloudUpload } from 'lucide-react';

interface UploadButtonProps {
    handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
    isUploading: boolean;
}

export const UploadButton: React.FC<UploadButtonProps> = ({
    handleFileUpload,
    isUploading
}) => {
    return (
        <>
            <input
                type="file"
                accept="image/*"
                id="upload-button"
                className="hidden"
                onChange={handleFileUpload}
            />
            <label htmlFor="upload-button">
                <Paper
                    className="mb-8 p-4 cursor-pointer flex items-center justify-center transition-all hover:bg-gray-50"
                >
                    {isUploading ? (
                        <CircularProgress size={24} />
                    ) : (
                        <>
                            <CloudUpload className="h-6 w-6 mr-2" />
                            <Typography>Upload New Photo</Typography>
                        </>
                    )}
                </Paper>
            </label>
        </>
    );
};