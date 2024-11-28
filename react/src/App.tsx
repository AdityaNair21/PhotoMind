import React from 'react';

import { PhotoGallery } from './components/PhotoGallery/PhotoGallery';
import { Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';

const theme = createTheme({
  palette: {
    background: {
      default: '#f5f5f5',
    },
  },
});

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box className="min-h-screen">
        <PhotoGallery />
      </Box>
    </ThemeProvider>
  );
};

export default App;