import React, { useRef } from 'react';
import { CloudUpload } from 'lucide-react';
import {
    Button,
    CircularProgress,
    Typography,
    Box,
    styled
} from '@mui/material';

interface UploadButtonProps {
    handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
    isUploading: boolean;
}

const UploadBox = styled(Button)(({ theme }) => ({
    width: '500px',  // Set the width to 500px
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2),  // Adjust padding for better visual balance
    minHeight: 64,
    borderRadius: '999px',  // Make it pill-shaped
    border: `1px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.background.paper,
    transition: theme.transitions.create([
        'background-color',
        'box-shadow',
        'border-color'
    ], {
        duration: theme.transitions.duration.short,
    }),
    '&:hover': {
        backgroundColor: theme.palette.action.hover,
        borderColor: theme.palette.primary.main,
        boxShadow: theme.shadows[1],
    },
    '&.Mui-disabled': {
        backgroundColor: theme.palette.action.disabledBackground,
        borderColor: theme.palette.action.disabled,
    }
}));

export const UploadButton: React.FC<UploadButtonProps> = ({
    handleFileUpload,
    isUploading
}) => {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center',   // Centers horizontally
                alignItems: 'center',       // Centers vertically
                // minHeight: '100vh',          // Ensures the full screen height is used
            }}
        >
            <Box>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    disabled={isUploading}
                    style={{ display: 'none' }}
                />
                <UploadBox
                    onClick={handleClick}
                    disabled={isUploading}
                    variant="text"
                    disableElevation
                >
                    {isUploading ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <CircularProgress size={24} />
                            <Typography
                                variant="body1"
                                color="text.secondary"
                                sx={{ fontWeight: 500 }}
                            >
                                Uploading...
                            </Typography>
                        </Box>
                    ) : (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CloudUpload
                                className="h-6 w-6"
                                color="primary"
                            />
                            <Typography
                                variant="body1"
                                sx={{
                                    fontWeight: 500,
                                    color: (theme) => theme.palette.text.primary
                                }}
                            >
                                Upload New Photo
                            </Typography>
                        </Box>
                    )}
                </UploadBox>
            </Box>
        </Box>
    );
};

export default UploadButton;
