import React from 'react';
import { Snackbar, Alert } from '@mui/material';
import { NotificationState } from '../../types/types';

interface NotificationSnackbarProps {
    notification: NotificationState;
    onClose: () => void;
}

export const NotificationSnackbar: React.FC<NotificationSnackbarProps> = ({
    notification,
    onClose
}) => {
    return (
        <Snackbar
            open={notification.open}
            autoHideDuration={4000}
            onClose={onClose}
        >
            <Alert severity={notification.severity} onClose={onClose}>
                {notification.message}
            </Alert>
        </Snackbar>
    );
};