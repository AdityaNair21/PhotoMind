export interface Photo {
    id: number;
    url: string;
    date: string;
    description: string;
}

export interface NotificationState {
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
}

export interface ExtendedPhoto extends Photo {
    localUrl?: string;
}