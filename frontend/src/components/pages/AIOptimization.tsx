import React, { useState } from 'react';
import {
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  Snackbar,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Psychology as AIIcon,
  TrendingUp as OptimizeIcon,
  Analytics as AnalysisIcon,
  Lightbulb as SuggestIcon,
  Chat as QueryIcon,
  CheckCircle as ValidateIcon,
  Speed as EfficiencyIcon,
  School as ComplianceIcon,
  AutoAwesome as MagicIcon,
  ExpandMore as ExpandMoreIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
  PlayArrow as RunIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

// Types for AI features
interface OptimizationResult {
  timetable_id: string;
  optimization_result: string;
  optimized: boolean;
  timestamp: string;
  efficiency_improvement?: number;
  conflicts_resolved?: number;
}

interface Suggestion {
  title: string;
  description: string;
  impact_level: 'high' | 'medium' | 'low';
  implementation_difficulty: 'easy' | 'medium' | 'hard';
  expected_benefit: string;
  category?: string;
}

interface AnalysisResult {
  timetable_id: string;
  analysis_type: string;
  efficiency_score: number;
  analysis_details: string;
  analyzed_at: string;
  metrics?: {
    faculty_workload: number;
    room_utilization: number;
    student_satisfaction: number;
    conflict_count: number;
  };
}

interface ComplianceResult {
  timetable_id: string;
  nep_compliance_score: number;
  compliance_details: string;
  validation_date: string;
  recommendations: string[];
  issues?: Array<{
    category: string;
    severity: 'high' | 'medium' | 'low';
    description: string;
  }>;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ai-tabpanel-${index}`}
      aria-labelledby={`ai-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AIOptimization: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedTimetable, setSelectedTimetable] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Optimization states
  const [optimizationGoals, setOptimizationGoals] = useState({
    efficiency: true,
    conflicts: true,
    workload: true,
    nep_compliance: true,
  });
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [optimizationProgress, setOptimizationProgress] = useState(0);

  // Suggestions states
  const [focusAreas, setFocusAreas] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  // Analysis states
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  // Natural Language Query states
  const [query, setQuery] = useState('');
  const [queryResponse, setQueryResponse] = useState('');
  const [queryHistory, setQueryHistory] = useState<Array<{query: string, response: string}>>([]);

  // Compliance states
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);

  // Mock timetables
  const mockTimetables = [
    { id: '1', name: 'CSE Semester 1 - 2024', program: 'Computer Science' },
    { id: '2', name: 'B.Ed Semester 2 - 2024', program: 'Education' },
    { id: '3', name: 'FYUP Year 1 - 2024', program: 'Multidisciplinary' },
    { id: '4', name: 'CSE AI&ML 5TH sem timetable', program: 'Computer Science - AI & ML' },
  ];

  // Focus areas for suggestions
  const availableFocusAreas = [
    'Faculty Workload',
    'Room Utilization',
    'Student Gaps',
    'NEP Compliance',
    'Resource Optimization',
    'Conflict Resolution',
  ];

  // Run optimization
  const runOptimization = async () => {
    if (!selectedTimetable) {
      setError('Please select a timetable to optimize');
      return;
    }

    setLoading(true);
    setOptimizationProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setOptimizationProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 500);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const mockResult: OptimizationResult = {
        timetable_id: selectedTimetable,
        optimization_result: JSON.stringify({
          analysis: "Current timetable shows 73% efficiency with 12 scheduling conflicts identified.",
          suggestions: [
            "Redistribute Prof. Smith's workload to reduce from 24 to 18 hours/week",
            "Move CSE101 lab sessions to Room B-202 for better capacity utilization",
            "Adjust break timings to minimize student gaps between classes"
          ],
          priorities: ["High: Resolve faculty workload conflicts", "Medium: Optimize room allocation"],
          nep_compliance_score: 82,
          estimated_improvement_percentage: 27
        }, null, 2),
        optimized: true,
        timestamp: new Date().toISOString(),
        efficiency_improvement: 27,
        conflicts_resolved: 8,
      };

      setOptimizationResult(mockResult);
      setOptimizationProgress(100);
      setSuccess('Timetable optimization completed successfully!');
    } catch (err) {
      setError('Optimization failed. Please try again.');
    } finally {
      setLoading(false);
      clearInterval(progressInterval);
    }
  };

  // Get suggestions
  const getSuggestions = async () => {
    if (!selectedTimetable) {
      setError('Please select a timetable for suggestions');
      return;
    }

    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockSuggestions: Suggestion[] = [
        {
          title: "Optimize Faculty Workload Distribution",
          description: "Redistribute teaching hours to prevent faculty overload and ensure balanced workload across all faculty members.",
          impact_level: "high",
          implementation_difficulty: "medium",
          expected_benefit: "25% improvement in faculty satisfaction and teaching quality",
          category: "Faculty Management"
        },
        {
          title: "Improve Room Utilization",
          description: "Reschedule classes to maximize room occupancy during peak hours and reduce underutilized spaces.",
          impact_level: "medium",
          implementation_difficulty: "easy",
          expected_benefit: "30% better room utilization efficiency",
          category: "Resource Optimization"
        },
        {
          title: "Minimize Student Schedule Gaps",
          description: "Reorganize class timings to reduce gaps between consecutive classes for better student experience.",
          impact_level: "high",
          implementation_difficulty: "medium",
          expected_benefit: "Improved student satisfaction and campus efficiency",
          category: "Student Experience"
        },
        {
          title: "Enhance NEP 2020 Compliance",
          description: "Adjust curriculum delivery to better align with NEP 2020 guidelines for multidisciplinary learning.",
          impact_level: "high",
          implementation_difficulty: "hard",
          expected_benefit: "Full compliance with national education policy",
          category: "Compliance"
        }
      ];

      setSuggestions(mockSuggestions);
      setSuccess('AI suggestions generated successfully!');
    } catch (err) {
      setError('Failed to generate suggestions');
    } finally {
      setLoading(false);
    }
  };

  // Run analysis
  const runAnalysis = async () => {
    if (!selectedTimetable) {
      setError('Please select a timetable to analyze');
      return;
    }

    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const mockAnalysis: AnalysisResult = {
        timetable_id: selectedTimetable,
        analysis_type: analysisType,
        efficiency_score: 78,
        analysis_details: "Comprehensive analysis reveals good overall structure with room for improvement in resource allocation and conflict resolution.",
        analyzed_at: new Date().toISOString(),
        metrics: {
          faculty_workload: 82,
          room_utilization: 67,
          student_satisfaction: 75,
          conflict_count: 12,
        }
      };

      setAnalysisResult(mockAnalysis);
      setSuccess('Analysis completed successfully!');
    } catch (err) {
      setError('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // Process natural language query
  const processQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResponse = `Based on your query "${query}", I can help you understand that effective timetable scheduling requires balancing multiple factors including faculty availability, room capacity, and student needs. For NEP 2020 compliance, ensure multidisciplinary courses are properly integrated and flexible credit options are available. Would you like me to analyze a specific aspect of your timetable?`;
      
      setQueryResponse(mockResponse);
      setQueryHistory(prev => [...prev, { query, response: mockResponse }]);
      setQuery('');
      setSuccess('Query processed successfully!');
    } catch (err) {
      setError('Query processing failed');
    } finally {
      setLoading(false);
    }
  };

  // Validate NEP compliance
  const validateCompliance = async () => {
    if (!selectedTimetable) {
      setError('Please select a timetable to validate');
      return;
    }

    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      const mockCompliance: ComplianceResult = {
        timetable_id: selectedTimetable,
        nep_compliance_score: 85,
        compliance_details: "Good compliance with NEP 2020 guidelines. Strong multidisciplinary integration and flexible credit structure.",
        validation_date: new Date().toISOString(),
        recommendations: [
          "Increase interdisciplinary course offerings by 15%",
          "Add more flexible time slots for research activities",
          "Include additional skill development sessions",
          "Enhance continuous assessment integration"
        ],
        issues: [
          {
            category: "Multidisciplinary Learning",
            severity: "medium",
            description: "Could benefit from more cross-departmental course integration"
          },
          {
            category: "Research Time",
            severity: "low",
            description: "Consider allocating more time for student research projects"
          }
        ]
      };

      setComplianceResult(mockCompliance);
      setSuccess('NEP compliance validation completed!');
    } catch (err) {
      setError('Compliance validation failed');
    } finally {
      setLoading(false);
    }
  };

  const getImpactColor = (level: string) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'hard': return 'error';
      case 'medium': return 'warning';
      case 'easy': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <AIIcon color="primary" />
          AI Optimization
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Leverage AI to optimize timetables, analyze efficiency, and ensure NEP 2020 compliance
        </Typography>
      </Box>

      {/* Timetable Selection */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
          <FormControl sx={{ minWidth: 300 }}>
            <InputLabel>Select Timetable</InputLabel>
            <Select
              value={selectedTimetable}
              label="Select Timetable"
              onChange={(e) => setSelectedTimetable(e.target.value)}
            >
              {mockTimetables.map(tt => (
                <MenuItem key={tt.id} value={tt.id}>
                  <Box>
                    <Typography variant="body1">{tt.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {tt.program}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Chip 
            label={selectedTimetable ? "Timetable Selected" : "No Timetable Selected"}
            color={selectedTimetable ? "success" : "default"}
            icon={selectedTimetable ? <CheckCircleIcon /> : <InfoIcon />}
          />
        </Stack>
      </Paper>

      {/* Main Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<OptimizeIcon />} label="Optimize" />
          <Tab icon={<SuggestIcon />} label="Suggestions" />
          <Tab icon={<AnalysisIcon />} label="Analysis" />
          <Tab icon={<QueryIcon />} label="AI Chat" />
          <Tab icon={<ValidateIcon />} label="NEP Compliance" />
        </Tabs>
      </Paper>

      {/* Optimize Tab */}
      <TabPanel value={activeTab} index={0}>
        <Stack spacing={3}>
          {/* Optimization Goals */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <SettingsIcon />
                Optimization Goals
              </Typography>
              <Stack spacing={2}>
                <Stack direction="row" spacing={2} flexWrap="wrap">
                  {Object.entries(optimizationGoals).map(([key, value]) => (
                    <Chip
                      key={key}
                      label={key.replace('_', ' ').toUpperCase()}
                      color={value ? 'primary' : 'default'}
                      onClick={() => setOptimizationGoals(prev => ({...prev, [key]: !prev[key as keyof typeof prev]}))}
                      clickable
                    />
                  ))}
                </Stack>
              </Stack>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <RunIcon />}
                onClick={runOptimization}
                disabled={loading || !selectedTimetable}
                size="large"
              >
                {loading ? 'Optimizing...' : 'Run AI Optimization'}
              </Button>
            </CardActions>
          </Card>

          {/* Progress */}
          {loading && optimizationProgress > 0 && (
            <Card>
              <CardContent>
                <Typography variant="body2" gutterBottom>
                  Optimization Progress: {optimizationProgress}%
                </Typography>
                <LinearProgress variant="determinate" value={optimizationProgress} />
              </CardContent>
            </Card>
          )}

          {/* Optimization Results */}
          {optimizationResult && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MagicIcon />
                  Optimization Results
                </Typography>
                <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mb: 2 }}>
                  <Paper sx={{ p: 2, textAlign: 'center', flex: 1 }}>
                    <Typography variant="h3" color="success.main">
                      {optimizationResult.efficiency_improvement}%
                    </Typography>
                    <Typography variant="body2">Efficiency Improvement</Typography>
                  </Paper>
                  <Paper sx={{ p: 2, textAlign: 'center', flex: 1 }}>
                    <Typography variant="h3" color="primary.main">
                      {optimizationResult.conflicts_resolved}
                    </Typography>
                    <Typography variant="body2">Conflicts Resolved</Typography>
                  </Paper>
                </Stack>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Detailed Results</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                      {optimizationResult.optimization_result}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
              <CardActions>
                <Button startIcon={<DownloadIcon />}>Download Report</Button>
                <Button startIcon={<RefreshIcon />} onClick={runOptimization}>
                  Re-optimize
                </Button>
              </CardActions>
            </Card>
          )}
        </Stack>
      </TabPanel>

      {/* Suggestions Tab */}
      <TabPanel value={activeTab} index={1}>
        <Stack spacing={3}>
          {/* Focus Areas Selection */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Focus Areas</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {availableFocusAreas.map(area => (
                  <Chip
                    key={area}
                    label={area}
                    color={focusAreas.includes(area) ? 'primary' : 'default'}
                    onClick={() => setFocusAreas(prev => 
                      prev.includes(area) 
                        ? prev.filter(a => a !== area)
                        : [...prev, area]
                    )}
                    clickable
                  />
                ))}
              </Stack>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SuggestIcon />}
                onClick={getSuggestions}
                disabled={loading || !selectedTimetable}
              >
                {loading ? 'Generating...' : 'Get AI Suggestions'}
              </Button>
            </CardActions>
          </Card>

          {/* Suggestions List */}
          {suggestions.length > 0 && (
            <Stack spacing={2}>
              {suggestions.map((suggestion, index) => (
                <Card key={index}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="start" sx={{ mb: 1 }}>
                      <Typography variant="h6">{suggestion.title}</Typography>
                      <Stack direction="row" spacing={1}>
                        <Chip 
                          label={`Impact: ${suggestion.impact_level}`}
                          color={getImpactColor(suggestion.impact_level) as any}
                          size="small"
                        />
                        <Chip 
                          label={`Difficulty: ${suggestion.implementation_difficulty}`}
                          color={getDifficultyColor(suggestion.implementation_difficulty) as any}
                          size="small"
                        />
                      </Stack>
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {suggestion.description}
                    </Typography>
                    <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                      Expected Benefit: {suggestion.expected_benefit}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          )}
        </Stack>
      </TabPanel>

      {/* Analysis Tab */}
      <TabPanel value={activeTab} index={2}>
        <Stack spacing={3}>
          {/* Analysis Configuration */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Analysis Configuration</Typography>
              <FormControl fullWidth>
                <InputLabel>Analysis Type</InputLabel>
                <Select
                  value={analysisType}
                  label="Analysis Type"
                  onChange={(e) => setAnalysisType(e.target.value)}
                >
                  <MenuItem value="comprehensive">Comprehensive Analysis</MenuItem>
                  <MenuItem value="efficiency">Efficiency Focus</MenuItem>
                  <MenuItem value="compliance">Compliance Focus</MenuItem>
                  <MenuItem value="resource">Resource Utilization</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <AnalysisIcon />}
                onClick={runAnalysis}
                disabled={loading || !selectedTimetable}
              >
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </Button>
            </CardActions>
          </Card>

          {/* Analysis Results */}
          {analysisResult && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <EfficiencyIcon />
                  Analysis Results
                </Typography>
                
                {/* Score Display */}
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <Typography variant="h2" color="primary.main">
                    {analysisResult.efficiency_score}%
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    Overall Efficiency Score
                  </Typography>
                </Box>

                {/* Metrics */}
                {analysisResult.metrics && (
                  <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
                    {Object.entries(analysisResult.metrics).map(([key, value]) => (
                      <Paper key={key} sx={{ p: 2, textAlign: 'center', minWidth: 120, flex: 1 }}>
                        <Typography variant="h5" color="secondary.main">
                          {key === 'conflict_count' ? value : `${value}%`}
                        </Typography>
                        <Typography variant="caption">
                          {key.replace('_', ' ').toUpperCase()}
                        </Typography>
                      </Paper>
                    ))}
                  </Stack>
                )}

                <Typography variant="body1">
                  {analysisResult.analysis_details}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Stack>
      </TabPanel>

      {/* AI Chat Tab */}
      <TabPanel value={activeTab} index={3}>
        <Stack spacing={3}>
          {/* Query Input */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <QueryIcon />
                Ask AI Assistant
              </Typography>
              <Stack direction="row" spacing={2}>
                <TextField
                  fullWidth
                  placeholder="Ask me about timetable optimization, NEP 2020 compliance, or scheduling best practices..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !loading && processQuery()}
                  multiline
                  rows={3}
                />
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                  onClick={processQuery}
                  disabled={loading || !query.trim()}
                  sx={{ minWidth: 120 }}
                >
                  {loading ? 'Processing...' : 'Send'}
                </Button>
              </Stack>
            </CardContent>
          </Card>

          {/* Current Response */}
          {queryResponse && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>AI Response</Typography>
                <Paper sx={{ p: 2, backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', color: 'text.primary' }}>
                    {queryResponse}
                  </Typography>
                </Paper>
              </CardContent>
            </Card>
          )}

          {/* Query History */}
          {queryHistory.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Recent Conversations</Typography>
                <Stack spacing={2} sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {queryHistory.slice(-5).reverse().map((item, index) => (
                    <Box key={index}>
                      <Paper sx={{ p: 2, backgroundColor: 'primary.main', color: 'primary.contrastText', border: '1px solid', borderColor: 'primary.dark' }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          You: {item.query}
                        </Typography>
                      </Paper>
                      <Paper sx={{ p: 2, mt: 1, backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                        <Typography variant="body2" sx={{ color: 'text.primary' }}>
                          AI: {item.response}
                        </Typography>
                      </Paper>
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          )}
        </Stack>
      </TabPanel>

      {/* NEP Compliance Tab */}
      <TabPanel value={activeTab} index={4}>
        <Stack spacing={3}>
          {/* Validation Control */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ComplianceIcon />
                NEP 2020 Compliance Validation
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Validate your timetable against National Education Policy 2020 guidelines
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <ValidateIcon />}
                onClick={validateCompliance}
                disabled={loading || !selectedTimetable}
                size="large"
              >
                {loading ? 'Validating...' : 'Validate NEP Compliance'}
              </Button>
            </CardActions>
          </Card>

          {/* Compliance Results */}
          {complianceResult && (
            <Stack spacing={2}>
              {/* Score Card */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Compliance Score</Typography>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h2" color="primary.main">
                      {complianceResult.nep_compliance_score}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      NEP 2020 Compliance Level
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={complianceResult.nep_compliance_score} 
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>

              {/* Issues */}
              {complianceResult.issues && complianceResult.issues.length > 0 && (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Compliance Issues</Typography>
                    <List>
                      {complianceResult.issues.map((issue, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            {issue.severity === 'high' ? (
                              <ErrorIcon color="error" />
                            ) : issue.severity === 'medium' ? (
                              <WarningIcon color="warning" />
                            ) : (
                              <InfoIcon color="info" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={issue.category}
                            secondary={issue.description}
                          />
                          <Chip 
                            label={issue.severity.toUpperCase()} 
                            color={
                              issue.severity === 'high' ? 'error' :
                              issue.severity === 'medium' ? 'warning' : 'info'
                            }
                            size="small"
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              )}

              {/* Recommendations */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Recommendations</Typography>
                  <List>
                    {complianceResult.recommendations.map((rec, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <SuggestIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={rec} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Stack>
          )}
        </Stack>
      </TabPanel>

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

export default AIOptimization;
