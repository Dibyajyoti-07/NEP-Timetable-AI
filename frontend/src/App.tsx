import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import MainLayout from './components/layout/MainLayout';
import { AuthGuard } from './components/AuthGuard';
import './App.css';

// Create a custom off-white theme with faded deep blue accents
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
    action: {
      hover: 'rgba(33, 150, 243, 0.08)',
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
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          '&.faculty-style': {
            background: 'linear-gradient(45deg, #1976d2, #1565c0)',
            color: 'white',
            padding: '8px 24px',
            fontWeight: 600,
            boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
            '&:hover': {
              background: 'linear-gradient(45deg, #1565c0, #1976d2)',
              boxShadow: '0 6px 16px rgba(25, 118, 210, 0.4)',
            },
          },
        },
        contained: {
          background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
          boxShadow: '0 3px 10px rgba(33, 150, 243, 0.3)',
          '&:hover': {
            background: 'linear-gradient(45deg, #1976d2 30%, #1cb5e0 90%)',
            boxShadow: '0 6px 20px rgba(33, 150, 243, 0.4)',
          },
        },
        outlined: {
          borderColor: 'rgba(33, 150, 243, 0.5)',
          '&:hover': {
            borderColor: '#2196f3',
            background: 'rgba(33, 150, 243, 0.08)',
          },
        },
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
          background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
          border: '1px solid rgba(33, 150, 243, 0.3)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
          border: '1px solid rgba(33, 150, 243, 0.3)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(135deg, rgba(26,26,26,0.95) 0%, rgba(18,18,18,0.95) 100%)',
          borderRight: '1px solid rgba(33, 150, 243, 0.3)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
          borderBottom: '1px solid rgba(33, 150, 243, 0.3)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
        },
      },
    },
    MuiToolbar: {
      styleOverrides: {
        root: {
          background: 'transparent',
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          background: 'transparent',
        },
      },
    },

    MuiIconButton: {
      styleOverrides: {
        root: {
          '&:hover': {
            background: 'rgba(33, 150, 243, 0.08)',
          },
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          '&.faculty-header': {
            color: 'white',
            fontWeight: 700,
            fontSize: '2rem',
            position: 'relative',
            zIndex: 1,
          },
          '&.faculty-subtitle': {
            color: 'white',
            opacity: 0.9,
            fontSize: '1.1rem',
            position: 'relative',
            zIndex: 1,
          },
          '&.faculty-stats': {
            color: 'white',
            fontWeight: 700,
            fontSize: '2.5rem',
            position: 'relative',
            zIndex: 1,
          },
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
