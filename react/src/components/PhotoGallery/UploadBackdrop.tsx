import React from 'react';
import { Backdrop, CircularProgress } from '@mui/material';

interface UploadBackdropProps {
    open: boolean;
}

export const UploadBackdrop: React.FC<UploadBackdropProps> = ({ open }) => {
    return (
        <Backdrop open={open} className="z-50">
            <CircularProgress color="inherit" />
        </Backdrop>
    );
};