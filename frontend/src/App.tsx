import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import MainLayout from './components/layout/MainLayout';
import { AuthGuard } from './components/AuthGuard';
import './App.css';

// Create a custom dark theme with smaller fonts
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3', // Blue primary
      light: '#64b5f6',
      dark: '#1976d2',
    },
    secondary: {
      main: '#2196f3',
    },
    background: {
      default: '#0a0a0a', // Very dark background
      paper: '#1a1a1a', // Slightly lighter for cards
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b0b0',
    },
    divider: '#2196f3',
    action: {
      hover: '#1a1a1a',
    }
  },
  typography: {
    fontSize: 12, // Smaller base font size
    h1: { fontSize: '1.75rem' },
    h2: { fontSize: '1.5rem' },
    h3: { fontSize: '1.25rem' },
    h4: { fontSize: '1.1rem' },
    h5: { fontSize: '1rem' },
    h6: { fontSize: '0.9rem' },
    body1: { fontSize: '0.8rem' },
    body2: { fontSize: '0.75rem' },
    button: { 
      fontSize: '0.75rem',
      textTransform: 'none'
    },
    caption: { fontSize: '0.65rem' },
  },
  components: {
    MuiTextField: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiButton: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiSelect: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiFormControl: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiInputLabel: {
      defaultProps: {
        shrink: true,
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: '#2196f3',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#64b5f6',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#2196f3',
          },
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        input: {
          fontSize: '0.8rem',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          fontSize: '0.75rem',
          padding: '6px 8px',
        },
        head: {
          fontSize: '0.8rem',
          fontWeight: 600,
          padding: '8px',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontSize: '0.7rem',
          height: '24px',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontSize: '0.75rem',
          minHeight: '40px',
          padding: '6px 12px',
          // Remove the white border/outline on focus and active states
          '&:focus': {
            outline: 'none',
          },
          '&:focus-visible': {
            outline: 'none',
          },
          '&.Mui-focusVisible': {
            outline: 'none',
            backgroundColor: 'transparent',
          },
          '&.Mui-selected': {
            outline: 'none',
          },
          '&.Mui-selected:focus': {
            outline: 'none',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          // Remove focus outline from the tabs container
          '&:focus': {
            outline: 'none',
          },
          '&:focus-visible': {
            outline: 'none',
          },
        },
        flexContainer: {
          // Ensure no outline on the flex container
          '&:focus': {
            outline: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: '#1a1a1a',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: '#1a1a1a',
          borderRight: '1px solid #2196f3',
        },
      },
    },
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Box sx={{ 
            width: '100%', 
            minHeight: '100vh', 
            margin: 0, 
            padding: 0, 
            backgroundColor: 'background.default'
          }}>
            <Router>
              <AuthGuard>
                <MainLayout />
              </AuthGuard>
            </Router>
          </Box>
        </LocalizationProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
