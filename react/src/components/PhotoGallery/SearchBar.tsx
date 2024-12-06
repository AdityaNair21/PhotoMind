import React from 'react';
import {
    Paper,
    InputBase,
    IconButton,
    CircularProgress,
    alpha,
    styled
} from '@mui/material';
import { Search as SearchIcon } from 'lucide-react';

interface SearchBarProps {
    searchQuery: string;
    setSearchQuery: (query: string) => void;
    handleSearch: (e: React.FormEvent) => Promise<void>;
    isSearching: boolean;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 50,
    backgroundColor: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    height: '64px', // Fixed height for better layout calculation
    display: 'flex',
    alignItems: 'center'
}));

const SearchContainer = styled('div')(({ theme }) => ({
    maxWidth: '1200px', // Increased max-width to match gallery
    width: '100%',
    margin: '0 auto',
    padding: '0 24px',
}));

const SearchForm = styled('form')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    width: '100%',
    backgroundColor: alpha('#000', 0.04),
    borderRadius: '8px',
    padding: '4px 8px',
    transition: 'all 0.2s ease',
    '&:hover': {
        backgroundColor: alpha('#000', 0.06),
    },
    '&:focus-within': {
        backgroundColor: '#fff',
        boxShadow: '0 0 0 2px #2196f3',
    }
}));

export const SearchBar: React.FC<SearchBarProps> = ({
    searchQuery,
    setSearchQuery,
    handleSearch,
    isSearching
}) => {
    return (
        <StyledPaper elevation={0}>
            <SearchContainer>
                <SearchForm onSubmit={handleSearch}>
                    <IconButton
                        sx={{ p: '8px' }}
                        disabled={isSearching}
                    >
                        {isSearching ? (
                            <CircularProgress size={20} />
                        ) : (
                            <SearchIcon size={20} />
                        )}
                    </IconButton>
                    <InputBase
                        value={searchQuery}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                            setSearchQuery(e.target.value)
                        }
                        placeholder="Search your photos..."
                        disabled={isSearching}
                        sx={{
                            ml: 1,
                            flex: 1,
                            fontSize: '15px',
                            '& .MuiInputBase-input': {
                                padding: '6px 0',
                            }
                        }}
                    />
                    {searchQuery && (
                        <IconButton
                            type="submit"
                            sx={{
                                p: '6px',
                                bgcolor: 'primary.main',
                                color: 'white',
                                '&:hover': {
                                    bgcolor: 'primary.dark',
                                },
                                '&.Mui-disabled': {
                                    bgcolor: 'primary.light',
                                    color: 'white',
                                }
                            }}
                            disabled={isSearching}
                        >
                            <SearchIcon size={18} />
                        </IconButton>
                    )}
                </SearchForm>
            </SearchContainer>
        </StyledPaper>
    );
};

export default SearchBar;