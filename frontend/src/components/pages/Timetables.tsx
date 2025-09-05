import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  Stack,
  CardActions,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckCircleIcon,
  Drafts as DraftIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material';
import { timetableService } from '../../services/timetableService';
import { useAuthStore } from '../../store/authStore';
import type { Timetable } from '../../services/timetableService';

const Timetables: React.FC = () => {
  console.log('🚀 TIMETABLES COMPONENT LOADING!');
  
  const navigate = useNavigate();
  const { user, token, isAuthenticated } = useAuthStore();
  
  console.log('🔍 Auth values from store:', { 
    hasUser: !!user, 
    hasToken: !!token, 
    isAuthenticated,
    userEmail: user?.email 
  });
  
  // Immediate console log to test if component is loading
  console.log('🚀 Timetables component loaded!');
  
  // Debug authentication state
  useEffect(() => {
    console.log('🔄 useEffect triggered for auth debugging');
    
    // Check localStorage directly
    const authStorage = localStorage.getItem('auth-storage');
    console.log('📱 Raw localStorage auth-storage:', authStorage);
    
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        console.log('📱 Parsed auth storage:', parsed);
      } catch (e) {
        console.error('📱 Failed to parse auth storage:', e);
      }
    }
    
    console.log('🔐 Timetables - Authentication state:', {
      isAuthenticated,
      hasUser: !!user,
      hasToken: !!token,
      token: token ? `${token.substring(0, 20)}...` : 'None',
      user: user ? { id: user.id, email: user.email, is_admin: user.is_admin } : 'None'
    });
  }, [isAuthenticated, user, token]);

  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    timetable: Timetable | null;
  }>({ open: false, timetable: null });
  const [deleting, setDeleting] = useState(false);

  // Load timetables and programs from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check authentication first
        if (!isAuthenticated) {
          console.log('User not authenticated - redirecting to login');
          navigate('/login');
          return;
        }

        setLoading(true);
        setError(null);
        
        // Test authentication by calling /users/me endpoint
        console.log('🧪 Testing authentication with /users/me endpoint...');
        try {
          const userResponse = await fetch('http://localhost:8000/api/v1/users/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          
          console.log('🧪 /users/me response status:', userResponse.status);
          if (userResponse.ok) {
            const userData = await userResponse.json();
            console.log('🧪 /users/me response data:', userData);
          } else {
            const errorData = await userResponse.text();
            console.log('🧪 /users/me error:', errorData);
          }
        } catch (testError) {
          console.error('🧪 /users/me test failed:', testError);
        }
        
        try {
          // Try to fetch from backend first
          const timetablesData = await timetableService.getAllTimetables();
          console.log('📦 Fetched timetables data:', timetablesData);
          console.log('🔍 First timetable structure:', timetablesData[0]);
          setTimetables(timetablesData);
          
        } catch (backendError) {
          console.warn('Backend not available, using mock data:', backendError);
          
          // Fallback to mock data if backend is not available
          const mockTimetables: Timetable[] = [];
          setTimetables(mockTimetables);
        }
      } catch (err: any) {
        console.error('Error fetching data:', err);
        setError(err.response?.data?.detail || 'Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, navigate, token]);

  // Handler functions
  const handleEdit = (timetable: Timetable) => {
    const timetableId = timetable.id || (timetable as any)._id;
    navigate(`/timetables/edit/${timetableId}`);
  };

  const handleView = (timetable: Timetable) => {
    const timetableId = timetable.id || (timetable as any)._id;
    navigate(`/timetables/${timetableId}`);
  };

  const handleDeleteClick = (timetable: Timetable) => {
    setDeleteDialog({ open: true, timetable });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteDialog.timetable) return;
    
    // Get the correct ID (handle both id and _id for compatibility)
    const timetableId = deleteDialog.timetable.id || (deleteDialog.timetable as any)._id;
    
    if (!timetableId) {
      console.error('❌ No timetable ID found:', deleteDialog.timetable);
      setError('Invalid timetable ID');
      return;
    }
    
    console.log('🗑️ Deleting timetable with ID:', timetableId);
    
    setDeleting(true);
    try {
      await timetableService.deleteTimetable(timetableId);
      
      // Refresh the timetables list
      const updatedTimetables = await timetableService.getAllTimetables();
      setTimetables(updatedTimetables);
      
      setDeleteDialog({ open: false, timetable: null });
    } catch (err: any) {
      console.error('Error deleting timetable:', err);
      setError(err.response?.data?.detail || 'Failed to delete timetable');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialog({ open: false, timetable: null });
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading timetables...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
            <CalendarIcon color="primary" />
            Timetables
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage and organize academic timetables
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/timetables/create')}
          size="large"
        >
          Create New Timetable
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Timetables Grid */}
      <Stack spacing={2}>
        {timetables.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <CalendarIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No timetables found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Create your first timetable to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/timetables/create')}
            >
              Create New Timetable
            </Button>
          </Paper>
        ) : (
          timetables.map((timetable) => (
            <Card key={timetable.id} sx={{ p: 2, border: '1px solid', borderColor: 'divider' }}>
              <CardContent sx={{ pb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {timetable.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {timetable.academic_year} - Semester {timetable.semester}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      Created: {formatDate(timetable.created_at)}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      size="small"
                      icon={timetable.is_draft ? <DraftIcon /> : <CheckCircleIcon />}
                      label={timetable.is_draft ? 'Draft' : 'Complete'}
                      color={timetable.is_draft ? 'warning' : 'success'}
                      variant={timetable.is_draft ? 'outlined' : 'filled'}
                    />
                  </Box>
                </Box>

                {/* Additional details */}
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 1 }}>
                  {timetable.validation_status && (
                    <Typography variant="caption" color="text.secondary">
                      Status: {timetable.validation_status}
                    </Typography>
                  )}
                  {timetable.optimization_score && (
                    <Typography variant="caption" color="text.secondary">
                      Score: {timetable.optimization_score.toFixed(1)}
                    </Typography>
                  )}
                </Box>
              </CardContent>

              <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                <Tooltip title="View Details">
                  <IconButton 
                    size="small" 
                    onClick={() => handleView(timetable)}
                    color="info"
                  >
                    <ViewIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Edit Timetable">
                  <IconButton 
                    size="small" 
                    onClick={() => handleEdit(timetable)}
                    color="primary"
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Delete Timetable">
                  <IconButton 
                    size="small" 
                    onClick={() => handleDeleteClick(timetable)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          ))
        )}
      </Stack>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={handleDeleteCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete Timetable</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{deleteDialog.timetable?.title}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleting}
            startIcon={deleting ? <CircularProgress size={16} /> : <DeleteIcon />}
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Timetables;
