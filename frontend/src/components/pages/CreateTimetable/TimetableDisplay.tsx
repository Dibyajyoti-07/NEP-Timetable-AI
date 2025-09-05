import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Stack,
  Chip,
  Card,
  CardContent,
  Grid,
  Divider,
} from '@mui/material';
import {
  Download as DownloadIcon,
  PictureAsPdf as PdfIcon,
  TableChart as CsvIcon,
} from '@mui/icons-material';

interface TimetableEntry {
  day: string;
  time: string;
  course_name: string;
  course_code: string;
  group: string;
  room: string;
  faculty: string;
  is_lab: boolean;
  duration: number;
}

interface TimetableDisplayProps {
  timetableData: any;
  onExport: (format: 'csv' | 'pdf') => void;
}

const TimetableDisplay: React.FC<TimetableDisplayProps> = ({ timetableData, onExport }) => {
  // Time slots for the timetable (matching your image format)
  const timeSlots = [
    '10:00 - 10:50',
    '10:50 - 11:40', 
    '11:40 - 12:30',
    '12:30 - 1:00', // Break
    '1:00 - 1:50',
    '1:50 - 2:40',
    '2:40 - 3:30',
    '3:30 - 4:20',
    '4:20 - 5:10',
    '5:10 - 6:00'
  ];

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  // Process the timetable data into a grid format
  const processScheduleData = () => {
    const scheduleGrid: { [key: string]: { [key: string]: TimetableEntry | null } } = {};
    
    // Initialize empty grid
    days.forEach(day => {
      scheduleGrid[day] = {};
      timeSlots.forEach(slot => {
        scheduleGrid[day][slot] = null;
      });
    });

    // Fill the grid with actual data
    if (timetableData?.timetable?.metadata?.schedule_details) {
      timetableData.timetable.metadata.schedule_details.forEach((entry: any) => {
        const timeSlot = `${entry.start_time} - ${entry.end_time}`;
        if (scheduleGrid[entry.day] && scheduleGrid[entry.day].hasOwnProperty(timeSlot)) {
          scheduleGrid[entry.day][timeSlot] = {
            day: entry.day,
            time: timeSlot,
            course_name: entry.course_name,
            course_code: entry.course_code || entry.course_name,
            group: entry.group,
            room: entry.room,
            faculty: entry.faculty || 'TBD',
            is_lab: entry.is_lab || false,
            duration: entry.duration || 50
          };
        }
      });
    }

    return scheduleGrid;
  };

  const scheduleGrid = processScheduleData();

  // Extract course information for the summary table
  const extractCourseInfo = () => {
    const courses: { [key: string]: any } = {};
    
    if (timetableData?.timetable?.metadata?.schedule_details) {
      timetableData.timetable.metadata.schedule_details.forEach((entry: any) => {
        const courseCode = entry.course_code || entry.course_name;
        if (!courses[courseCode]) {
          courses[courseCode] = {
            name: entry.course_name,
            code: courseCode,
            periods: 0,
            faculty: entry.faculty || 'TBD',
            type: entry.is_lab ? 'Lab' : 'Theory'
          };
        }
        courses[courseCode].periods += 1;
      });
    }

    return Object.values(courses);
  };

  const courseInfo = extractCourseInfo();

  // Get cell content with proper styling
  const getCellContent = (entry: TimetableEntry | null, isBreak: boolean = false) => {
    if (isBreak) {
      return (
        <Box sx={{ 
          textAlign: 'center', 
          py: 1, 
          backgroundColor: '#f5f5f5',
          color: '#666',
          fontWeight: 'bold'
        }}>
          BREAK
        </Box>
      );
    }

    if (!entry) {
      return <Box sx={{ height: 40 }}></Box>;
    }

    const isLab = entry.is_lab;
    const backgroundColor = isLab ? '#fff3cd' : '#ffffff';
    const borderColor = isLab ? '#ffc107' : '#dee2e6';

    return (
      <Box sx={{ 
        p: 1, 
        backgroundColor,
        border: `1px solid ${borderColor}`,
        borderRadius: 1,
        minHeight: 40,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.75rem' }}>
          {entry.course_code}
        </Typography>
        {entry.group && (
          <Typography variant="caption" sx={{ color: '#666', fontSize: '0.7rem' }}>
            {entry.group} [{entry.room}]
          </Typography>
        )}
      </Box>
    );
  };

  const handleExport = (format: 'csv' | 'pdf') => {
    onExport(format);
  };

  return (
    <Box sx={{ width: '100%', mb: 4 }}>
      {/* Header */}
      <Card sx={{ mb: 3, backgroundColor: '#1a1a1a' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
                B. Tech. CSE - AI-ML (Odd) Fifth Semester Class Routine
              </Typography>
              <Typography variant="subtitle1" sx={{ color: '#b0b0b0' }}>
                Theory Class Room - N-009 | Academic Year: {timetableData?.timetable?.academic_year || '2025-2026'}
              </Typography>
            </Box>
            
            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                startIcon={<CsvIcon />}
                onClick={() => handleExport('csv')}
                sx={{ backgroundColor: '#4CAF50' }}
              >
                Export CSV
              </Button>
              <Button
                variant="contained"
                startIcon={<PdfIcon />}
                onClick={() => handleExport('pdf')}
                sx={{ backgroundColor: '#f44336' }}
              >
                Export PDF
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {/* Main Timetable */}
      <TableContainer component={Paper} sx={{ mb: 3, backgroundColor: '#1a1a1a' }}>
        <Table size="small" sx={{ minWidth: 1000 }}>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#2a2a2a' }}>
              <TableCell sx={{ color: 'white', fontWeight: 'bold', width: 100, border: '1px solid #444' }}>
                Day
              </TableCell>
              {timeSlots.map((slot) => (
                <TableCell 
                  key={slot} 
                  sx={{ 
                    color: 'white', 
                    fontWeight: 'bold', 
                    textAlign: 'center',
                    border: '1px solid #444',
                    minWidth: 120,
                    fontSize: '0.75rem'
                  }}
                >
                  {slot}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {days.map((day) => (
              <TableRow key={day} sx={{ backgroundColor: '#1a1a1a' }}>
                <TableCell sx={{ 
                  color: 'white', 
                  fontWeight: 'bold',
                  border: '1px solid #444',
                  backgroundColor: '#2a2a2a'
                }}>
                  {day}
                </TableCell>
                {timeSlots.map((slot) => (
                  <TableCell 
                    key={`${day}-${slot}`} 
                    sx={{ 
                      border: '1px solid #444',
                      p: 0.5,
                      verticalAlign: 'middle'
                    }}
                  >
                    {slot === '12:30 - 1:00' ? 
                      getCellContent(null, true) : 
                      getCellContent(scheduleGrid[day][slot])
                    }
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Course Information Table */}
      <Card sx={{ backgroundColor: '#1a1a1a' }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: 'white', mb: 2, fontWeight: 'bold' }}>
            Course Information
          </Typography>
          
          <TableContainer component={Paper} sx={{ backgroundColor: '#2a2a2a' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold', border: '1px solid #444' }}>
                    Paper Name
                  </TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold', border: '1px solid #444' }}>
                    Paper Code
                  </TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold', border: '1px solid #444' }}>
                    Periods
                  </TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold', border: '1px solid #444' }}>
                    Faculty Name
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {courseInfo.map((course: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell sx={{ color: 'white', border: '1px solid #444' }}>
                      {course.name}
                    </TableCell>
                    <TableCell sx={{ color: 'white', border: '1px solid #444' }}>
                      {course.code}
                    </TableCell>
                    <TableCell sx={{ color: 'white', border: '1px solid #444' }}>
                      {course.periods}
                    </TableCell>
                    <TableCell sx={{ color: 'white', border: '1px solid #444' }}>
                      {course.faculty}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Generation Statistics */}
      {timetableData?.generation_details && (
        <Card sx={{ mt: 3, backgroundColor: '#1a1a1a' }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: 'white', mb: 2, fontWeight: 'bold' }}>
              Generation Statistics
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                    {timetableData.generation_details.score || 'N/A'}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Optimization Score
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ color: '#2196F3', fontWeight: 'bold' }}>
                    {timetableData.generation_details.statistics?.total_sessions || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Total Sessions
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ color: '#FF9800', fontWeight: 'bold' }}>
                    {timetableData.generation_details.statistics?.lab_sessions || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Lab Sessions
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#2a2a2a', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ color: '#9C27B0', fontWeight: 'bold' }}>
                    {timetableData.generation_details.statistics?.theory_sessions || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Theory Sessions
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TimetableDisplay;
