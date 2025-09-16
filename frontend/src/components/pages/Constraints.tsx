import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Stack,
  Tooltip,
  Snackbar,
  Switch,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  PlaylistAddCheck as ValidateIcon,
  Flag as PriorityIcon,
  Rule as RuleIcon,
  ExpandMore as ExpandMoreIcon,
  School as SchoolIcon,
  Person as PersonIcon,
  Room as RoomIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

// Types based on backend models
interface Constraint {
  _id: string;
  name: string;
  type: string;
  description?: string;
  parameters: Record<string, any>;
  priority: number;
  is_active: boolean;
  program_id?: string;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

interface ConstraintType {
  key: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  parameters: ParameterDefinition[];
}

interface ParameterDefinition {
  name: string;
  label: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'multiselect' | 'time' | 'json';
  required?: boolean;
  options?: string[];
  min?: number;
  max?: number;
  default?: any;
}

interface ValidationResult {
  constraint_id: string;
  constraint_type: string;
  is_valid: boolean;
  message: string;
}

const CONSTRAINT_TYPES: ConstraintType[] = [
  {
    key: 'faculty_availability',
    name: 'Faculty Availability',
    description: 'Defines when faculty members are available',
    icon: <PersonIcon />,
    parameters: [
      { name: 'faculty_id', label: 'Faculty ID', type: 'text', required: true },
      { name: 'available_days', label: 'Available Days', type: 'multiselect', options: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] },
      { name: 'start_time', label: 'Start Time', type: 'time' },
      { name: 'end_time', label: 'End Time', type: 'time' },
    ]
  },
  {
    key: 'room_capacity',
    name: 'Room Capacity',
    description: 'Ensures room capacity matches course requirements',
    icon: <RoomIcon />,
    parameters: [
      { name: 'room_id', label: 'Room ID', type: 'text' },
      { name: 'min_capacity', label: 'Minimum Capacity', type: 'number', min: 1 },
      { name: 'max_capacity', label: 'Maximum Capacity', type: 'number', min: 1 },
    ]
  },
  {
    key: 'time_preference',
    name: 'Time Preference',
    description: 'Faculty or institutional time preferences',
    icon: <ScheduleIcon />,
    parameters: [
      { name: 'preferred_times', label: 'Preferred Time Slots', type: 'multiselect', options: ['11:00-12:00', '12:00-13:00', '14:00-15:00', '15:00-16:00', '16:00-16:30'] },
    { name: 'avoid_times', label: 'Times to Avoid', type: 'multiselect', options: ['11:00-12:00', '12:00-13:00', '14:00-15:00', '15:00-16:00', '16:00-16:30'] },
    ]
  },
  {
    key: 'faculty_workload',
    name: 'Faculty Workload',
    description: 'Limits on faculty teaching hours',
    icon: <PersonIcon />,
    parameters: [
      { name: 'faculty_id', label: 'Faculty ID', type: 'text', required: true },
      { name: 'max_hours_per_day', label: 'Max Hours per Day', type: 'number', min: 1, max: 12 },
      { name: 'max_hours_per_week', label: 'Max Hours per Week', type: 'number', min: 1, max: 40 },
    ]
  },
  {
    key: 'room_type_requirement',
    name: 'Room Type Requirement',
    description: 'Specific room type needs (lab, lecture hall)',
    icon: <RoomIcon />,
    parameters: [
      { name: 'course_id', label: 'Course ID', type: 'text' },
      { name: 'required_room_type', label: 'Required Room Type', type: 'select', options: ['Lecture Hall', 'Laboratory', 'Seminar Room', 'Computer Lab', 'Workshop'] },
    ]
  },
  {
    key: 'block_scheduling',
    name: 'Block Scheduling',
    description: 'Teaching practice and field work blocks',
    icon: <SchoolIcon />,
    parameters: [
      { name: 'block_duration', label: 'Block Duration (hours)', type: 'number', min: 1, max: 8 },
      { name: 'consecutive_days', label: 'Consecutive Days', type: 'number', min: 1, max: 7 },
    ]
  },
  {
    key: 'gap_minimization',
    name: 'Gap Minimization',
    description: 'Minimize gaps in schedules',
    icon: <ScheduleIcon />,
    parameters: [
      { name: 'max_gap_hours', label: 'Maximum Gap (hours)', type: 'number', min: 0, max: 4 },
      { name: 'apply_to', label: 'Apply To', type: 'select', options: ['Faculty', 'Students', 'Both'] },
    ]
  },
  {
    key: 'consecutive_classes',
    name: 'Consecutive Classes',
    description: 'Required consecutive class scheduling',
    icon: <ScheduleIcon />,
    parameters: [
      { name: 'course_ids', label: 'Course IDs (comma-separated)', type: 'text' },
      { name: 'must_be_consecutive', label: 'Must be Consecutive', type: 'boolean', default: true },
    ]
  },
  {
    key: 'nep_compliance',
    name: 'NEP Compliance',
    description: 'NEP 2020 guideline adherence',
    icon: <RuleIcon />,
    parameters: [
      { name: 'compliance_type', label: 'Compliance Type', type: 'select', options: ['Credit Distribution', 'Multidisciplinary', 'Flexibility', 'Assessment'] },
      { name: 'requirement_details', label: 'Requirement Details', type: 'json' },
    ]
  },
];

const Constraints: React.FC = () => {
  const [constraints, setConstraints] = useState<Constraint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  
  // Filtering
  const [filterType, setFilterType] = useState<string>('');
  const [filterActive, setFilterActive] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  // Dialogs
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [validateDialogOpen, setValidateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  // Selected constraint
  const [selectedConstraint, setSelectedConstraint] = useState<Constraint | null>(null);
  const [validationResults, setValidationResults] = useState<ValidationResult[]>([]);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    description: '',
    parameters: {} as Record<string, any>,
    priority: 5,
    is_active: true,
    program_id: '',
  });

  // Load constraints
  const loadConstraints = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: (page * rowsPerPage).toString(),
        limit: rowsPerPage.toString(),
        is_active: filterActive.toString(),
      });
      
      if (filterType) params.append('constraint_type', filterType);
      
      // Note: In real implementation, you'd use your API service
      const mockConstraints: Constraint[] = [
        {
          _id: '1',
          name: 'Dr. Smith Availability',
          type: 'faculty_availability',
          description: 'Dr. Smith is available Monday to Friday, 9 AM to 5 PM',
          parameters: {
            faculty_id: 'FAC001',
            available_days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            start_time: '11:00',
      end_time: '16:30'
          },
          priority: 8,
          is_active: true,
          program_id: '1',
          created_by: 'USER001',
          created_at: new Date().toISOString(),
        },
        {
          _id: '2',
          name: 'Lab Room Capacity',
          type: 'room_capacity',
          description: 'Computer lab must accommodate at least 30 students',
          parameters: {
            room_id: 'LAB01',
            min_capacity: 30,
            max_capacity: 35
          },
          priority: 9,
          is_active: true,
          created_by: 'USER001',
          created_at: new Date().toISOString(),
        },
      ];
      
      setConstraints(mockConstraints);
      setTotal(mockConstraints.length);
    } catch (err) {
      setError('Failed to load constraints');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConstraints();
  }, [page, rowsPerPage, filterType, filterActive]);

  // Handle form changes
  const handleFormChange = (field: string, value: any) => {
    if (field.startsWith('param_')) {
      const paramName = field.replace('param_', '');
      setFormData(prev => ({
        ...prev,
        parameters: {
          ...prev.parameters,
          [paramName]: value,
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value,
      }));
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      type: '',
      description: '',
      parameters: {},
      priority: 5,
      is_active: true,
      program_id: '',
    });
  };

  // Get constraint type info
  const getConstraintType = (typeKey: string): ConstraintType | undefined => {
    return CONSTRAINT_TYPES.find(t => t.key === typeKey);
  };

  // Create constraint
  const handleCreate = async () => {
    try {
      console.log('Creating constraint:', formData);
      setSuccess('Constraint created successfully');
      setCreateDialogOpen(false);
      resetForm();
      loadConstraints();
    } catch (err) {
      setError('Failed to create constraint');
    }
  };

  // Edit constraint
  const handleEdit = (constraint: Constraint) => {
    setSelectedConstraint(constraint);
    setFormData({
      name: constraint.name,
      type: constraint.type,
      description: constraint.description || '',
      parameters: constraint.parameters,
      priority: constraint.priority,
      is_active: constraint.is_active,
      program_id: constraint.program_id || '',
    });
    setEditDialogOpen(true);
  };

  // Update constraint
  const handleUpdate = async () => {
    try {
      console.log('Updating constraint:', selectedConstraint?._id, formData);
      setSuccess('Constraint updated successfully');
      setEditDialogOpen(false);
      resetForm();
      setSelectedConstraint(null);
      loadConstraints();
    } catch (err) {
      setError('Failed to update constraint');
    }
  };

  // Validate constraints
  const handleValidate = async () => {
    try {
      setValidationResults([
        { constraint_id: '1', constraint_type: 'faculty_availability', is_valid: true, message: 'Faculty availability validated successfully' },
        { constraint_id: '2', constraint_type: 'room_capacity', is_valid: false, message: 'Room capacity exceeds available space' },
      ]);
      setValidateDialogOpen(true);
    } catch (err) {
      setError('Failed to validate constraints');
    }
  };

  // Delete constraint
  const handleDelete = async () => {
    try {
      if (!selectedConstraint) return;
      console.log('Deleting constraint:', selectedConstraint._id);
      setSuccess('Constraint deleted successfully');
      setDeleteDialogOpen(false);
      setSelectedConstraint(null);
      loadConstraints();
    } catch (err) {
      setError('Failed to delete constraint');
    }
  };

  // Render parameter input
  const renderParameterInput = (param: ParameterDefinition, value: any) => {
    const fieldName = `param_${param.name}`;
    
    switch (param.type) {
      case 'boolean':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={value || param.default || false}
                onChange={(e) => handleFormChange(fieldName, e.target.checked)}
              />
            }
            label={param.label}
          />
        );
      
      case 'number':
        return (
          <TextField
            fullWidth
            label={param.label}
            type="number"
            value={value || param.default || ''}
            onChange={(e) => handleFormChange(fieldName, parseInt(e.target.value))}
            inputProps={{ min: param.min, max: param.max }}
            required={param.required}
          />
        );
      
      case 'select':
        return (
          <FormControl fullWidth required={param.required}>
            <InputLabel>{param.label}</InputLabel>
            <Select
              value={value || param.default || ''}
              label={param.label}
              onChange={(e) => handleFormChange(fieldName, e.target.value)}
            >
              {param.options?.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      
      case 'multiselect':
        return (
          <FormControl fullWidth required={param.required}>
            <InputLabel>{param.label}</InputLabel>
            <Select
              multiple
              value={value || param.default || []}
              label={param.label}
              onChange={(e) => handleFormChange(fieldName, e.target.value)}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {(selected as string[]).map((val) => (
                    <Chip key={val} label={val} size="small" />
                  ))}
                </Box>
              )}
            >
              {param.options?.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      
      case 'time':
        return (
          <TextField
            fullWidth
            label={param.label}
            type="time"
            value={value || param.default || ''}
            onChange={(e) => handleFormChange(fieldName, e.target.value)}
            InputLabelProps={{ shrink: true }}
            required={param.required}
          />
        );
      
      case 'json':
        return (
          <TextField
            fullWidth
            label={param.label}
            multiline
            rows={3}
            value={typeof value === 'object' ? JSON.stringify(value, null, 2) : value || ''}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                handleFormChange(fieldName, parsed);
              } catch {
                handleFormChange(fieldName, e.target.value);
              }
            }}
            placeholder="Enter JSON object"
            required={param.required}
          />
        );
      
      default:
        return (
          <TextField
            fullWidth
            label={param.label}
            value={value || param.default || ''}
            onChange={(e) => handleFormChange(fieldName, e.target.value)}
            required={param.required}
          />
        );
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon color="primary" />
          Constraints Management
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage scheduling constraints for timetable generation with NEP 2020 compliance
        </Typography>
      </Box>

      {/* Action Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack spacing={2} direction={{ xs: 'column', md: 'row' }} alignItems={{ md: 'center' }}>
          <Box sx={{ flex: '1 1 300px' }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search constraints..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Box>
          <Box sx={{ flex: '0 1 200px' }}>
            <FormControl fullWidth size="small">
              <InputLabel>Constraint Type</InputLabel>
              <Select
                value={filterType}
                label="Constraint Type"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="">All Types</MenuItem>
                {CONSTRAINT_TYPES.map(type => (
                  <MenuItem key={type.key} value={type.key}>{type.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ flex: '0 1 150px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={filterActive}
                  onChange={(e) => setFilterActive(e.target.checked)}
                />
              }
              label="Active Only"
            />
          </Box>
          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateDialogOpen(true)}
            >
              Add Constraint
            </Button>
            <Button
              variant="outlined"
              startIcon={<ValidateIcon />}
              onClick={() => handleValidate()}
            >
              Validate
            </Button>
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={loadConstraints}
            >
              Refresh
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {/* Constraints Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Constraint</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Program</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {constraints.map((constraint) => {
                  const constraintType = getConstraintType(constraint.type);
                  return (
                    <TableRow key={constraint._id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {constraintType?.icon}
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                              {constraint.name}
                            </Typography>
                            {constraint.description && (
                              <Typography variant="caption" color="text.secondary">
                                {constraint.description.substring(0, 50)}...
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={constraintType?.name || constraint.type}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <PriorityIcon fontSize="small" color={
                            constraint.priority >= 8 ? 'error' :
                            constraint.priority >= 5 ? 'warning' : 'success'
                          } />
                          <Typography variant="body2">{constraint.priority}/10</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {constraint.program_id ? (
                          <Chip label="Program Specific" size="small" color="secondary" />
                        ) : (
                          <Chip label="Global" size="small" color="default" />
                        )}
                      </TableCell>
                      <TableCell>
                        {constraint.is_active ? (
                          <Chip
                            icon={<CheckCircleIcon />}
                            label="Active"
                            size="small"
                            color="success"
                          />
                        ) : (
                          <Chip
                            icon={<CancelIcon />}
                            label="Inactive"
                            size="small"
                            color="error"
                          />
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={0.5} justifyContent="center">
                          <Tooltip title="Edit Constraint">
                            <IconButton
                              size="small"
                              onClick={() => handleEdit(constraint)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Constraint">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedConstraint(constraint);
                                setDeleteDialogOpen(true);
                              }}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={total}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </Paper>
      )}

      {/* Create Constraint Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Constraint</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <TextField
                fullWidth
                label="Constraint Name"
                value={formData.name}
                onChange={(e) => handleFormChange('name', e.target.value)}
                required
              />
              <FormControl fullWidth required>
                <InputLabel>Constraint Type</InputLabel>
                <Select
                  value={formData.type}
                  label="Constraint Type"
                  onChange={(e) => handleFormChange('type', e.target.value)}
                >
                  {CONSTRAINT_TYPES.map(type => (
                    <MenuItem key={type.key} value={type.key}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {type.icon}
                        {type.name}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>

            <TextField
              fullWidth
              label="Description"
              multiline
              rows={2}
              value={formData.description}
              onChange={(e) => handleFormChange('description', e.target.value)}
            />

            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <Box sx={{ flex: 1 }}>
                <Typography gutterBottom>Priority: {formData.priority}/10</Typography>
                <Slider
                  value={formData.priority}
                  onChange={(_, value) => handleFormChange('priority', value)}
                  min={1}
                  max={10}
                  marks
                  step={1}
                  valueLabelDisplay="auto"
                />
              </Box>
              <FormControl sx={{ flex: 1 }}>
                <InputLabel>Program (Optional)</InputLabel>
                <Select
                  value={formData.program_id}
                  label="Program (Optional)"
                  onChange={(e) => handleFormChange('program_id', e.target.value)}
                >
                  <MenuItem value="">Global Constraint</MenuItem>
                  <MenuItem value="1">Computer Science Engineering</MenuItem>
                  <MenuItem value="2">Bachelor of Education</MenuItem>
                </Select>
              </FormControl>
            </Stack>

            {formData.type && (
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Constraint Parameters</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={2}>
                    {getConstraintType(formData.type)?.parameters.map(param => (
                      <Box key={param.name}>
                        {renderParameterInput(param, formData.parameters[param.name])}
                      </Box>
                    ))}
                  </Stack>
                </AccordionDetails>
              </Accordion>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>
            Create Constraint
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Constraint Dialog - Similar to Create but with different title and action */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Constraint</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <TextField
                fullWidth
                label="Constraint Name"
                value={formData.name}
                onChange={(e) => handleFormChange('name', e.target.value)}
                required
              />
              <FormControl fullWidth required>
                <InputLabel>Constraint Type</InputLabel>
                <Select
                  value={formData.type}
                  label="Constraint Type"
                  onChange={(e) => handleFormChange('type', e.target.value)}
                >
                  {CONSTRAINT_TYPES.map(type => (
                    <MenuItem key={type.key} value={type.key}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {type.icon}
                        {type.name}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>

            <TextField
              fullWidth
              label="Description"
              multiline
              rows={2}
              value={formData.description}
              onChange={(e) => handleFormChange('description', e.target.value)}
            />

            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <Box sx={{ flex: 1 }}>
                <Typography gutterBottom>Priority: {formData.priority}/10</Typography>
                <Slider
                  value={formData.priority}
                  onChange={(_, value) => handleFormChange('priority', value)}
                  min={1}
                  max={10}
                  marks
                  step={1}
                  valueLabelDisplay="auto"
                />
              </Box>
              <FormControl sx={{ flex: 1 }}>
                <InputLabel>Program (Optional)</InputLabel>
                <Select
                  value={formData.program_id}
                  label="Program (Optional)"
                  onChange={(e) => handleFormChange('program_id', e.target.value)}
                >
                  <MenuItem value="">Global Constraint</MenuItem>
                  <MenuItem value="1">Computer Science Engineering</MenuItem>
                  <MenuItem value="2">Bachelor of Education</MenuItem>
                </Select>
              </FormControl>
            </Stack>

            {formData.type && (
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Constraint Parameters</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Stack spacing={2}>
                    {getConstraintType(formData.type)?.parameters.map(param => (
                      <Box key={param.name}>
                        {renderParameterInput(param, formData.parameters[param.name])}
                      </Box>
                    ))}
                  </Stack>
                </AccordionDetails>
              </Accordion>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdate}>
            Update Constraint
          </Button>
        </DialogActions>
      </Dialog>

      {/* Validation Results Dialog */}
      <Dialog
        open={validateDialogOpen}
        onClose={() => setValidateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Constraint Validation Results</DialogTitle>
        <DialogContent>
          <List>
            {validationResults.map((result, index) => (
              <React.Fragment key={result.constraint_id}>
                <ListItem>
                  <ListItemIcon>
                    {result.is_valid ? 
                      <CheckCircleIcon color="success" /> : 
                      <WarningIcon color="error" />
                    }
                  </ListItemIcon>
                  <ListItemText
                    primary={result.constraint_type}
                    secondary={result.message}
                  />
                </ListItem>
                {index < validationResults.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setValidateDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the constraint "{selectedConstraint?.name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDelete}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbars */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess('')}
      >
        <Alert severity="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
      >
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Constraints;
