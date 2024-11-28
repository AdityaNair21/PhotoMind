import React from 'react';
import { Paper, InputBase, IconButton, CircularProgress } from '@mui/material';
import { Search } from 'lucide-react';

interface SearchBarProps {
    searchQuery: string;
    setSearchQuery: (query: string) => void;
    handleSearch: (e: React.FormEvent) => Promise<void>;
    isSearching: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
    searchQuery,
    setSearchQuery,
    handleSearch,
    isSearching
}) => {
    return (
        <Paper
            component="form"
            onSubmit={handleSearch}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 w-full max-w-2xl mx-auto flex items-center px-4 py-2 z-10 shadow-lg"
        >
            <InputBase
                className="flex-grow ml-2"
                placeholder="Search your photos (e.g., 'beach vacation' or 'family dinner')"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
            {isSearching ? (
                <CircularProgress size={24} className="mx-2" />
            ) : (
                <IconButton type="submit">
                    <Search className="h-5 w-5" />
                </IconButton>
            )}
        </Paper>
    );
};