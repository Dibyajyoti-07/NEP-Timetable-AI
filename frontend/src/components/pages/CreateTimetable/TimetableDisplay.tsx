import React, { useState, useEffect } from 'react';
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
import { timetableService } from '../../../services/timetableService';
import { useTimetableContext } from '../../../contexts/TimetableContext';

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
  console.log('🔍 TimetableDisplay component rendered with data:', timetableData);
  console.log('🔍 TimetableData keys:', Object.keys(timetableData || {}));
  console.log('🔍 TimetableData.entries:', timetableData?.entries);
  console.log('🔍 TimetableData.timetable?.entries:', timetableData?.timetable?.entries);
  console.log('🔍 TimetableData structure check:', {
    hasEntries: !!timetableData?.entries,
    hasTimetableEntries: !!timetableData?.timetable?.entries,
    entriesLength: timetableData?.entries?.length || 0,
    timetableEntriesLength: timetableData?.timetable?.entries?.length || 0
  });
  const { formData } = useTimetableContext();
  const [courses, setCourses] = useState<{ [key: string]: any }>({});
  const [faculty, setFaculty] = useState<{ [key: string]: any }>({});
  const [loading, setLoading] = useState(true);

  // Generate time slots dynamically from context data
  const generateTimeSlots = () => {
    const { time_slots } = formData;
    const slots: string[] = [];
    
    // Parse start and end times
    const startTime = time_slots.start_time;
    const endTime = time_slots.end_time;
    const slotDuration = time_slots.slot_duration || 50;
    const breakDuration = time_slots.break_duration || 10;
    
    // Convert time string to minutes
    const timeToMinutes = (timeStr: string) => {
      const [hours, minutes] = timeStr.split(':').map(Number);
      return hours * 60 + minutes;
    };
    
    // Convert minutes to time string
    const minutesToTime = (minutes: number) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    };
    
    let currentTime = timeToMinutes(startTime);
    const endTimeMinutes = timeToMinutes(endTime);
    const lunchStartMinutes = time_slots.lunch_break ? timeToMinutes(time_slots.lunch_start) : null;
    const lunchEndMinutes = time_slots.lunch_break ? timeToMinutes(time_slots.lunch_end) : null;
    
    while (currentTime + slotDuration <= endTimeMinutes) {
      const slotStart = minutesToTime(currentTime);
      const slotEnd = minutesToTime(currentTime + slotDuration);
      
      // Skip lunch break time
      if (lunchStartMinutes && lunchEndMinutes && 
          currentTime < lunchEndMinutes && currentTime + slotDuration > lunchStartMinutes) {
        currentTime = lunchEndMinutes;
        continue;
      }
      
      slots.push(`${slotStart} - ${slotEnd}`);
      currentTime += slotDuration + breakDuration;
    }
    
    return slots;
  };

  // Generate working days dynamically from context data
  const generateWorkingDays = () => {
    const { working_days } = formData;
    const dayMapping = {
      monday: 'Monday',
      tuesday: 'Tuesday',
      wednesday: 'Wednesday',
      thursday: 'Thursday',
      friday: 'Friday',
      saturday: 'Saturday',
      sunday: 'Sunday'
    };
    
    return Object.entries(working_days)
      .filter(([_, enabled]) => enabled)
      .map(([day, _]) => dayMapping[day as keyof typeof dayMapping])
      .filter(Boolean);
  };

  // Generate fallback time slots and days
  const fallbackTimeSlots = generateTimeSlots();
  const days = generateWorkingDays();
  
  // Debug logging
  console.log('📅 Generated working days:', days);
  console.log('📊 Form data time_slots:', formData.time_slots);
  console.log('📊 Timetable data:', timetableData);

  // Map backend day names to frontend day names (comprehensive mapping)
  const dayNameMapping: { [key: string]: string } = {
    'Mon': 'Monday',
    'Tue': 'Tuesday', 
    'Wed': 'Wednesday',
    'Thu': 'Thursday',
    'Fri': 'Friday',
    'Sat': 'Saturday',
    'Sun': 'Sunday',
    'Monday': 'Monday',
    'Tuesday': 'Tuesday',
    'Wednesday': 'Wednesday', 
    'Thursday': 'Thursday',
    'Friday': 'Friday',
    'Saturday': 'Saturday',
    'Sunday': 'Sunday'
  };

  // Fetch courses and faculty data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch courses
        const coursesData = await timetableService.getCourses();
        const coursesMap: { [key: string]: any } = {};
        coursesData.forEach((course: any) => {
          // Handle both id and _id fields for backward compatibility
          const courseId = course.id || course._id;
          if (courseId) {
            coursesMap[courseId] = course;
            // Also map by _id if it exists and is different
            if (course._id && course._id !== courseId) {
              coursesMap[course._id] = course;
            }
          }
        });
        setCourses(coursesMap);
        
        // Fetch faculty
        const facultyData = await timetableService.getFaculty();
        const facultyMap: { [key: string]: any } = {};
        facultyData.forEach((member: any) => {
          // Handle both id and _id fields for backward compatibility
          const facultyId = member.id || member._id;
          if (facultyId) {
            facultyMap[facultyId] = member;
            // Also map by _id if it exists and is different
            if (member._id && member._id !== facultyId) {
              facultyMap[member._id] = member;
            }
          }
        });
        setFaculty(facultyMap);
        
        console.log('📚 Loaded courses:', coursesMap);
        console.log('👨‍🏫 Loaded faculty:', facultyMap);
        console.log('🔍 Course IDs available:', Object.keys(coursesMap));
        console.log('🔍 Faculty IDs available:', Object.keys(facultyMap));
        
      } catch (error) {
        console.error('❌ Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Helper functions to get names from IDs
  const getCourseName = (courseId: string) => {
    const course = courses[courseId];
    if (course) {
      return course.name || course.code || courseId;
    }
    // If not found, try to find by matching _id or id field
    const foundCourse = Object.values(courses).find((c: any) => c._id === courseId || c.id === courseId);
    return foundCourse?.name || foundCourse?.code || courseId;
  };

  const getCourseCode = (courseId: string) => {
    const course = courses[courseId];
    if (course) {
      return course.code || courseId;
    }
    // If not found, try to find by matching _id or id field
    const foundCourse = Object.values(courses).find((c: any) => c._id === courseId || c.id === courseId);
    return foundCourse?.code || courseId;
  };

  const getFacultyName = (facultyId: string) => {
    const facultyMember = faculty[facultyId];
    if (facultyMember) {
      return facultyMember.name || facultyId;
    }
    // If not found, try to find by matching _id or id field
    const foundFaculty = Object.values(faculty).find((f: any) => f._id === facultyId || f.id === facultyId);
    return foundFaculty?.name || facultyId;
  };

  const getCourseType = (courseId: string) => {
    const course = courses[courseId];
    if (course) {
      return course.type || course.course_type || 'Theory';
    }
    // If not found, try to find by matching _id or id field
    const foundCourse = Object.values(courses).find((c: any) => c._id === courseId || c.id === courseId);
    return foundCourse?.type || foundCourse?.course_type || 'Theory';
  };

  // Process the timetable data into a grid format
  const processScheduleData = (): { scheduleGrid: { [key: string]: { [key: string]: TimetableEntry | null } }, actualTimeSlots: string[] } => {
    const scheduleGrid: { [key: string]: { [key: string]: TimetableEntry | null } } = {};
    const actualTimeSlots = new Set<string>();
    
    // First pass: collect all actual time slots from the data
    let entries = null;
    if (timetableData?.entries) {
      entries = timetableData.entries;
      console.log('🔍 Found entries in timetableData.entries:', entries.length);
    } else if (timetableData?.timetable?.entries) {
      entries = timetableData.timetable.entries;
      console.log('🔍 Found entries in timetableData.timetable.entries:', entries.length);
    } else {
      console.log('❌ No entries found in either location');
      console.log('🔍 Available timetableData keys:', Object.keys(timetableData || {}));
    }
    
    if (entries) {
      console.log('🔍 Sample entry structure:', entries[0]);
      entries.forEach((entry: any) => {
        const timeSlot = `${entry.time_slot.start_time} - ${entry.time_slot.end_time}`;
        actualTimeSlots.add(timeSlot);
      });
    }
    
    // Use actual time slots if available, otherwise fall back to generated ones
    const slotsToUse: string[] = actualTimeSlots.size > 0 ? Array.from(actualTimeSlots).sort() : fallbackTimeSlots;
    console.log('🕐 Using time slots:', slotsToUse);
    
    // Initialize empty grid with actual time slots
    days.forEach(day => {
      scheduleGrid[day] = {};
      slotsToUse.forEach((slot: string) => {
        scheduleGrid[day][slot] = null;
      });
    });

    // Fill the grid with actual data from entries array (new backend structure)
    // Check for genetic algorithm response structure first (entries directly in response)
    if (entries) {
      console.log('🔍 Processing timetable entries:', entries.length);
      console.log('🔍 Available courses data:', Object.keys(courses).length, 'courses loaded');
      console.log('🔍 Available faculty data:', Object.keys(faculty).length, 'faculty loaded');
      console.log('🔍 Sample courses:', Object.keys(courses).slice(0, 3));
      console.log('🔍 Sample faculty:', Object.keys(faculty).slice(0, 3));
      entries.forEach((entry: any) => {
        const timeSlot = `${entry.time_slot.start_time} - ${entry.time_slot.end_time}`;
        const backendDay = entry.time_slot.day;
        const day = dayNameMapping[backendDay] || backendDay; // Map backend day to frontend day
        
        console.log(`📅 Processing entry: ${day} ${timeSlot} - Course ID: ${entry.course_id}, Faculty ID: ${entry.faculty_id}`);
        console.log(`🔍 Course lookup result:`, courses[entry.course_id]);
        console.log(`🔍 Faculty lookup result:`, faculty[entry.faculty_id]);
        console.log(`📚 Course name resolved: ${getCourseName(entry.course_id)}`);
        console.log(`👨‍🏫 Faculty name resolved: ${getFacultyName(entry.faculty_id)}`);
        
        // Initialize day if it doesn't exist
        if (!scheduleGrid[day]) {
          scheduleGrid[day] = {};
        }
        
        // Always add the entry with its actual time slot (don't restrict to predefined slots)
        console.log(`✅ Successfully placed: ${day} ${timeSlot}`);
        scheduleGrid[day][timeSlot] = {
          day: day,
          time: timeSlot,
          course_name: getCourseName(entry.course_id),
          course_code: getCourseCode(entry.course_id),
          group: entry.group_id || 'Default',
          room: entry.room_id,
          faculty: getFacultyName(entry.faculty_id) || 'TBD',
          is_lab: getCourseType(entry.course_id) === 'Lab',
          duration: entry.time_slot.duration_minutes || 50
        };
      });
    }
    // Fallback: Check for old metadata structure for backward compatibility
    else if (timetableData?.timetable?.metadata?.schedule_details) {
      console.log('⚠️ No timetable entries found, using fallback metadata structure');
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

    console.log('📊 Final schedule grid:', scheduleGrid);
    return { scheduleGrid, actualTimeSlots: slotsToUse };
  };

  // Process the schedule data to get actual time slots and grid
  const { scheduleGrid, actualTimeSlots: displayTimeSlots }: { scheduleGrid: { [key: string]: { [key: string]: TimetableEntry | null } }, actualTimeSlots: string[] } = processScheduleData();
  
  // Use actual time slots if available, otherwise fallback to generated ones
  const timeSlots: string[] = displayTimeSlots.length > 0 ? displayTimeSlots : fallbackTimeSlots;
  
  // Log the final schedule grid for debugging
  console.log('📊 Final schedule grid:', scheduleGrid);
  console.log('🕐 Actual time slots from data:', displayTimeSlots);
  console.log('⏰ Final time slots used:', timeSlots);

  // Log the timetable data structure for debugging
  console.log('🔍 TimetableData structure:', timetableData);

  // Extract course information for the summary table
  const extractCourseInfo = () => {
    const courses: { [key: string]: any } = {};
    
    // Extract from entries structure (handle both genetic algorithm and simple timetable responses)
    let entries = null;
    if (timetableData?.entries) {
      entries = timetableData.entries;
    } else if (timetableData?.timetable?.entries) {
      entries = timetableData.timetable.entries;
    }
    
    if (entries) {
      entries.forEach((entry: any) => {
        const courseCode = entry.course_id;
        const facultyName = getFacultyName(entry.faculty_id);
        
        console.log(`🔍 Course Info Debug - Course ID: ${entry.course_id}, Faculty ID: ${entry.faculty_id}, Faculty Name: ${facultyName}`);
        
        if (!courses[courseCode]) {
          courses[courseCode] = {
            name: entry.course_name || getCourseName(entry.course_id),
            code: entry.course_code || getCourseCode(entry.course_id),
            periods: 0,
            faculty: facultyName || 'TBD',
            type: getCourseType(entry.course_id),
            facultySet: new Set([entry.faculty_id]) // Track all faculty IDs for this course
          };
        } else {
          // If course already exists, add faculty to the set
          courses[courseCode].facultySet.add(entry.faculty_id);
          // Update faculty display if we have multiple faculty for same course
          const allFacultyNames = Array.from(courses[courseCode].facultySet as Set<string>)
            .map(fId => getFacultyName(fId))
            .filter(name => name && name !== 'TBD') // Filter out unresolved names
            .join(', ');
          courses[courseCode].faculty = allFacultyNames || 'TBD';
        }
        courses[courseCode].periods += 1;
      });
    }
    // Fallback: Extract from old metadata structure
    else if (timetableData?.timetable?.metadata?.schedule_details) {
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

    // Clean up facultySet before returning
    const result = Object.values(courses).map(course => {
      const { facultySet, ...cleanCourse } = course;
      return cleanCourse;
    });
    
    console.log('📊 Final course info:', result);
    return result;
  };

  const courseInfo = extractCourseInfo();

  // Show loading state while fetching data
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Typography variant="h6" color="text.secondary">
          Loading course and faculty data...
        </Typography>
      </Box>
    );
  }

  // Get cell content with proper styling
  const getCellContent = (entry: TimetableEntry | null, isBreak: boolean = false) => {
    if (isBreak) {
      return (
        <Box sx={{ 
          textAlign: 'center', 
          py: 1, 
          background: 'linear-gradient(45deg, rgba(255,193,7,0.2), rgba(255,152,0,0.2))',
          color: '#ffb74d',
          fontWeight: 'bold',
          border: '1px solid rgba(255,193,7,0.3)',
          borderRadius: 1
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
        minHeight: 60,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.75rem', lineHeight: 1.2 }}>
          {entry.course_name}
        </Typography>
        <Typography variant="caption" sx={{ color: '#666', fontSize: '0.65rem', lineHeight: 1.1 }}>
          {entry.course_code}
        </Typography>
        {entry.faculty && (
          <Typography variant="caption" sx={{ color: '#444', fontSize: '0.65rem', fontWeight: 'medium', lineHeight: 1.1 }}>
            {entry.faculty}
          </Typography>
        )}
        {entry.group && (
          <Typography variant="caption" sx={{ color: '#666', fontSize: '0.65rem', lineHeight: 1.1 }}>
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
      <Card sx={{ 
        mb: 3, 
        background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        borderRadius: 3
      }}>
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
                sx={{ 
                  background: 'linear-gradient(45deg, #4CAF50, #66BB6A)',
                  boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #66BB6A, #4CAF50)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 6px 16px rgba(76, 175, 80, 0.4)'
                  }
                }}
              >
                Export CSV
              </Button>
              <Button
                variant="contained"
                startIcon={<PdfIcon />}
                onClick={() => handleExport('pdf')}
                sx={{ 
                  background: 'linear-gradient(45deg, #f44336, #ef5350)',
                  boxShadow: '0 4px 12px rgba(244, 67, 54, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #ef5350, #f44336)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 6px 16px rgba(244, 67, 54, 0.4)'
                  }
                }}
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
              {timeSlots.map((slot: string) => (
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
                {timeSlots.map((slot: string) => (
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
                      getCellContent(scheduleGrid[day]?.[slot] || null)
                    }
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Course Information Table */}
      <Card sx={{ 
        background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        borderRadius: 3
      }}>
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
        <Card sx={{ 
          mt: 3, 
          background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          borderRadius: 3
        }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: 'white', mb: 2, fontWeight: 'bold' }}>
              Generation Statistics
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2, 
                  background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(255,255,255,0.1)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 'bold' }}>
                    {timetableData.generation_details.score || 'N/A'}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Optimization Score
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2, 
                  background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(255,255,255,0.1)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: '#2196F3', fontWeight: 'bold' }}>
                    {timetableData.generation_details.statistics?.total_sessions || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Total Sessions
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2, 
                  background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(255,255,255,0.1)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: '#FF9800', fontWeight: 'bold' }}>
                    {timetableData.generation_details.statistics?.lab_sessions || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Lab Sessions
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2, 
                  background: 'linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(18,18,18,0.95) 100%)',
                  borderRadius: 2,
                  border: '1px solid rgba(255,255,255,0.1)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                }}>
                  <Typography variant="h4" sx={{ color: '#9C27B0', fontWeight: 'bold' }}>
                    {timetableData.generation_details.statistics?.theory_sessions || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#b0b0b0' }}>
                    Theory Sessions
                  </Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TimetableDisplay;
