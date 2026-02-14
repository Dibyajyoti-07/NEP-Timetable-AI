import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import logo from '../../assets/APP LOGO (1).svg';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Schedule,
  School,
  Settings,
  Psychology,
  AccountCircle,
  ExitToApp,
  ArrowBack as ArrowBackIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material';
import { useNavigate, Routes, Route, useLocation } from 'react-router-dom';
import Dashboard from '../pages/Dashboard.tsx';
import Timetables from '../pages/Timetables.tsx';
import Programs from '../pages/Programs.tsx';
import Constraints from '../pages/Constraints.tsx';
import AIOptimization from '../pages/AIOptimization.tsx';
import CreateTimetable from '../pages/CreateTimetable.tsx';
import LoginPage from '../pages/Login.tsx';
import Signup from '../pages/Signup.tsx';
import { useAuthStore } from '../../store/authStore';

const drawerWidth = 240;

const MainLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuthStore();

  // Check if we're on a timetable create/edit page
  const isTimetablePage = location.pathname.includes('/timetables/create') || location.pathname.includes('/timetables/edit') || location.pathname.match(/\/timetables\/[^\/]+$/);
  const timetableName = 'CSE AI & ML'; // This could come from route params or state in the future

  const handleBackToTimetables = () => {
    navigate('/timetables');
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/login');
  };

  // If not authenticated, show login/signup routes
  if (!isAuthenticated) {
    return (
      <Box sx={{ 
        minHeight: '100vh', 
        width: '100%',
        backgroundColor: 'background.default',
        margin: 0,
        padding: 0
      }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<LoginPage />} />
        </Routes>
      </Box>
    );
  }

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Timetables', icon: <Schedule />, path: '/timetables' },
    { text: 'Programs', icon: <School />, path: '/programs' },
    { text: 'Constraints', icon: <Settings />, path: '/constraints' },
    { text: 'AI Optimization', icon: <Psychology />, path: '/ai' },
  ];

  const drawer = (
    <Box>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <img src={logo} alt="VINYASA" style={{ height: '64px', width: 'auto' }} />
            <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'white' }}>
              VINYASA
            </Typography>
          </Box>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => {
                navigate(item.path);
                if (isMobile) setMobileOpen(false);
              }}
            >
              <ListItemIcon sx={{ color: 'primary.main' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  if (!isAuthenticated) {
    // This shouldn't happen now since routing is handled at App level
    // Temporarily disabled for development - return null;
  }

  return (
    <>
      {/* Conditional wrapper: Box only for non-timetable pages */}
      {!isTimetablePage ? (
        <Box sx={{ 
          display: 'flex', 
          minHeight: '100vh',
          width: '100%',
          backgroundColor: 'background.default',
          margin: 0,
          padding: 0
        }}>
          <AppBar
            position="fixed"
            elevation={0}
            sx={{
              width: { md: `calc(100% - ${drawerWidth}px)` },
              ml: { md: `${drawerWidth}px` },
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { md: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                VINYASA - AI Timetable System
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <IconButton onClick={handleProfileMenuOpen} color="inherit">
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                    {user?.name?.charAt(0) || 'U'}
                  </Avatar>
                </IconButton>
              </Box>
            </Toolbar>
          </AppBar>

          <Box
            component="nav"
            sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
          >
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={handleDrawerToggle}
              ModalProps={{
                keepMounted: true,
              }}
              sx={{
                display: { xs: 'block', md: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', md: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>

          {/* Main content area only for non-timetable pages */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { md: `calc(100% - ${drawerWidth}px)` },
              minHeight: '100vh',
              backgroundColor: 'background.default',
            }}
          >
            <Toolbar />
            <Box sx={{ 
              minHeight: 'calc(100vh - 64px)', 
              display: 'flex', 
              flexDirection: 'column' 
            }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/timetables" element={<Timetables />} />
                <Route path="/programs" element={<Programs />} />
                <Route path="/constraints" element={<Constraints />} />
                <Route path="/ai" element={<AIOptimization />} />
              </Routes>
            </Box>
          </Box>
        </Box>
      ) : (
        /* Timetable pages without sidebar - full width */
        <>
          <AppBar
            position="fixed"
            elevation={0}
            sx={{
              width: '100%', // Full width for timetable pages
              ml: 0, // No margin left
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                onClick={handleBackToTimetables}
                sx={{ mr: 2 }}
              >
                <ArrowBackIcon />
              </IconButton>
              <CalendarIcon sx={{ mr: 0.25, color: 'primary.main' }} />
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, textAlign: 'left' }}>
                VINYASA - Edit Timetable - {timetableName}
              </Typography>
              
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <IconButton onClick={handleProfileMenuOpen} color="inherit">
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                    {user?.name?.charAt(0) || 'U'}
                  </Avatar>
                </IconButton>
              </div>
            </Toolbar>
          </AppBar>

          {/* Timetable content without sidebar, with proper top margin */}
          <Box sx={{ 
            marginTop: '64px', 
            width: '100%', 
            minHeight: 'calc(100vh - 64px)',
            backgroundColor: 'background.default'
          }}>
            <Routes>
              <Route path="/timetables/create" element={<CreateTimetable />} />
              <Route path="/timetables/edit/:id" element={<CreateTimetable />} />
              <Route path="/timetables/:id" element={<CreateTimetable />} />
            </Routes>
          </Box>
        </>
      )}

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon>
            <AccountCircle fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Profile" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <ExitToApp fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </MenuItem>
      </Menu>
    </>
  );
};

export default MainLayout;
