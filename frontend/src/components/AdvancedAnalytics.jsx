import React, { useState, useEffect } from 'react';
import {
        Card,
        CardContent,
        CardDescription,
        CardHeader,
        CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
        LineChart,
        Line,
        XAxis,
        YAxis,
        CartesianGrid,
        Tooltip,
        ResponsiveContainer,
        BarChart,
        Bar,
        PieChart,
        Pie,
        Cell
} from 'recharts';
import {
        TrendingUp,
        Users,
        Brain,
        Target,
        AlertCircle,
        CheckCircle,
        Clock,
        BarChart3
} from 'lucide-react';

const AdvancedAnalytics = () => {
        const [prediction, setPrediction] = useState(null);
        const [cohortAnalysis, setCohortAnalysis] = useState([]);
        const [realTimeAdjustments, setRealTimeAdjustments] = useState(null);
        const [analyticsStatus, setAnalyticsStatus] = useState(null);
        const [loading, setLoading] = useState(false);
        const [selectedCourse, setSelectedCourse] = useState(1);

        // Fetch analytics status on component mount
        useEffect(() => {
                fetchAnalyticsStatus();
        }, []);

        const fetchAnalyticsStatus = async () => {
                try {
                        const response = await fetch('/api/advanced-analytics/analytics-status', {
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });
                        if (response.ok) {
                                const data = await response.json();
                                setAnalyticsStatus(data);
                        }
                } catch (error) {
                        console.error('Error fetching analytics status:', error);
                }
        };

        const fetchPrediction = async (courseId) => {
                setLoading(true);
                try {
                        const response = await fetch(`/api/advanced-analytics/predict-outcome/${courseId}`, {
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });
                        if (response.ok) {
                                const data = await response.json();
                                setPrediction(data);
                        }
                } catch (error) {
                        console.error('Error fetching prediction:', error);
                } finally {
                        setLoading(false);
                }
        };

        const fetchCohortAnalysis = async (cohortType = 'learning_style') => {
                setLoading(true);
                try {
                        const response = await fetch(`/api/advanced-analytics/cohort-analysis?cohort_type=${cohortType}`, {
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });
                        if (response.ok) {
                                const data = await response.json();
                                setCohortAnalysis(data);
                        }
                } catch (error) {
                        console.error('Error fetching cohort analysis:', error);
                } finally {
                        setLoading(false);
                }
        };

        const simulateRealTimeEvent = async () => {
                const eventData = {
                        session_id: `session_${Date.now()}`,
                        event_data: {
                                event_type: 'content_interaction',
                                interaction_type: 'quiz_completion',
                                score: Math.random(),
                                time_spent: Math.floor(Math.random() * 300) + 60,
                                difficulty_level: Math.random()
                        }
                };

                try {
                        const response = await fetch('/api/advanced-analytics/real-time-event', {
                                method: 'POST',
                                headers: {
                                        'Content-Type': 'application/json',
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                },
                                body: JSON.stringify(eventData)
                        });
                        if (response.ok) {
                                const data = await response.json();
                                setRealTimeAdjustments(data);
                        }
                } catch (error) {
                        console.error('Error processing real-time event:', error);
                }
        };

        const PredictionCard = () => (
                <Card>
                        <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                        <Brain className="h-5 w-5" />
                                        Learning Outcome Prediction
                                </CardTitle>
                                <CardDescription>
                                        AI-powered prediction of your learning success
                                </CardDescription>
                        </CardHeader>
                        <CardContent>
                                <div className="space-y-4">
                                        <div className="flex gap-2">
                                                <Button
                                                        onClick={() => fetchPrediction(selectedCourse)}
                                                        disabled={loading}
                                                >
                                                        {loading ? 'Analyzing...' : 'Get Prediction'}
                                                </Button>
                                                <select
                                                        value={selectedCourse}
                                                        onChange={(e) => setSelectedCourse(e.target.value)}
                                                        className="px-3 py-1 border rounded"
                                                >
                                                        <option value={1}>Course 1</option>
                                                        <option value={2}>Course 2</option>
                                                        <option value={3}>Course 3</option>
                                                </select>
                                        </div>

                                        {prediction && (
                                                <div className="space-y-4">
                                                        <div className="flex items-center justify-between">
                                                                <span className="text-sm font-medium">Success Probability</span>
                                                                <Badge variant={prediction.predicted_value > 0.7 ? 'success' : 'warning'}>
                                                                        {Math.round(prediction.predicted_value * 100)}%
                                                                </Badge>
                                                        </div>

                                                        <Progress value={prediction.predicted_value * 100} className="w-full" />

                                                        <div className="flex items-center justify-between">
                                                                <span className="text-sm font-medium">Confidence</span>
                                                                <span className="text-sm text-gray-600">
                                                                        {Math.round(prediction.confidence * 100)}%
                                                                </span>
                                                        </div>

                                                        <div className="space-y-2">
                                                                <h4 className="text-sm font-medium">Key Factors</h4>
                                                                {Object.entries(prediction.factors).slice(0, 3).map(([factor, importance]) => (
                                                                        <div key={factor} className="flex items-center justify-between text-sm">
                                                                                <span className="capitalize">{factor.replace('_', ' ')}</span>
                                                                                <Progress value={importance * 100} className="w-20" />
                                                                        </div>
                                                                ))}
                                                        </div>

                                                        <div className="space-y-2">
                                                                <h4 className="text-sm font-medium">Recommendations</h4>
                                                                <ul className="text-sm space-y-1">
                                                                        {prediction.recommendations.slice(0, 3).map((rec, index) => (
                                                                                <li key={index} className="flex items-start gap-2">
                                                                                        <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                                                        {rec}
                                                                                </li>
                                                                        ))}
                                                                </ul>
                                                        </div>
                                                </div>
                                        )}
                                </div>
                        </CardContent>
                </Card>
        );

        const CohortAnalysisCard = () => (
                <Card>
                        <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                        <Users className="h-5 w-5" />
                                        Cohort Analysis
                                </CardTitle>
                                <CardDescription>
                                        Learning patterns across user groups
                                </CardDescription>
                        </CardHeader>
                        <CardContent>
                                <div className="space-y-4">
                                        <div className="flex gap-2">
                                                <Button
                                                        onClick={() => fetchCohortAnalysis('learning_style')}
                                                        disabled={loading}
                                                        size="sm"
                                                >
                                                        By Learning Style
                                                </Button>
                                                <Button
                                                        onClick={() => fetchCohortAnalysis('engagement_level')}
                                                        disabled={loading}
                                                        size="sm"
                                                        variant="outline"
                                                >
                                                        By Engagement
                                                </Button>
                                        </div>

                                        {cohortAnalysis.length > 0 && (
                                                <div className="space-y-4">
                                                        {cohortAnalysis.slice(0, 2).map((cohort, index) => (
                                                                <div key={index} className="border rounded-lg p-4">
                                                                        <div className="flex items-center justify-between mb-3">
                                                                                <h4 className="font-medium capitalize">
                                                                                        {cohort.cohort_name.replace('_', ' ')}
                                                                                </h4>
                                                                                <Badge variant="outline">
                                                                                        {cohort.cohort_size} users
                                                                                </Badge>
                                                                        </div>

                                                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                                                                <div>
                                                                                        <span className="text-gray-600">Avg Completion</span>
                                                                                        <div className="font-medium">
                                                                                                {Math.round(cohort.performance_metrics.avg_completion_rate * 100)}%
                                                                                        </div>
                                                                                </div>
                                                                                <div>
                                                                                        <span className="text-gray-600">Avg Engagement</span>
                                                                                        <div className="font-medium">
                                                                                                {Math.round(cohort.performance_metrics.avg_engagement_score * 100)}%
                                                                                        </div>
                                                                                </div>
                                                                        </div>

                                                                        {cohort.retention_rates && (
                                                                                <div className="mt-3">
                                                                                        <span className="text-sm text-gray-600">Retention Trend</span>
                                                                                        <div className="flex gap-1 mt-1">
                                                                                                {Object.entries(cohort.retention_rates).slice(0, 4).map(([week, rate]) => (
                                                                                                        <div key={week} className="flex-1">
                                                                                                                <Progress value={rate * 100} className="h-2" />
                                                                                                                <span className="text-xs text-gray-500">{week}</span>
                                                                                                        </div>
                                                                                                ))}
                                                                                        </div>
                                                                                </div>
                                                                        )}
                                                                </div>
                                                        ))}
                                                </div>
                                        )}
                                </div>
                        </CardContent>
                </Card>
        );

        const RealTimePersonalizationCard = () => (
                <Card>
                        <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                        <Target className="h-5 w-5" />
                                        Real-Time Personalization
                                </CardTitle>
                                <CardDescription>
                                        Live learning session adjustments
                                </CardDescription>
                        </CardHeader>
                        <CardContent>
                                <div className="space-y-4">
                                        <Button
                                                onClick={simulateRealTimeEvent}
                                                className="w-full"
                                        >
                                                Simulate Learning Event
                                        </Button>

                                        {realTimeAdjustments && (
                                                <div className="space-y-4">
                                                        <div className="flex items-center justify-between">
                                                                <span className="text-sm font-medium">Adjustment Confidence</span>
                                                                <Badge variant="success">
                                                                        {Math.round(realTimeAdjustments.confidence * 100)}%
                                                                </Badge>
                                                        </div>

                                                        <div className="space-y-2">
                                                                <h4 className="text-sm font-medium">Triggered Events</h4>
                                                                <div className="flex flex-wrap gap-1">
                                                                        {realTimeAdjustments.trigger_events.map((event, index) => (
                                                                                <Badge key={index} variant="outline" className="text-xs">
                                                                                        {event.replace('_', ' ')}
                                                                                </Badge>
                                                                        ))}
                                                                </div>
                                                        </div>

                                                        <div className="space-y-2">
                                                                <h4 className="text-sm font-medium">Adjustments</h4>
                                                                {Object.entries(realTimeAdjustments.adjustments).map(([type, adjustments]) => (
                                                                        <div key={type} className="border rounded p-3">
                                                                                <h5 className="text-sm font-medium capitalize mb-2">
                                                                                        {type.replace('_', ' ')}
                                                                                </h5>
                                                                                <ul className="text-sm space-y-1">
                                                                                        {Object.entries(adjustments).map(([key, value]) => (
                                                                                                <li key={key} className="flex items-center gap-2">
                                                                                                        {value === true ? (
                                                                                                                <CheckCircle className="h-3 w-3 text-green-500" />
                                                                                                        ) : (
                                                                                                                <AlertCircle className="h-3 w-3 text-yellow-500" />
                                                                                                        )}
                                                                                                        <span className="capitalize">
                                                                                                                {key.replace('_', ' ')}: {value.toString()}
                                                                                                        </span>
                                                                                                </li>
                                                                                        ))}
                                                                                </ul>
                                                                        </div>
                                                                ))}
                                                        </div>
                                                </div>
                                        )}
                                </div>
                        </CardContent>
                </Card>
        );

        const StatusCard = () => (
                <Card>
                        <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                        <BarChart3 className="h-5 w-5" />
                                        Analytics Status
                                </CardTitle>
                                <CardDescription>
                                        System status and capabilities
                                </CardDescription>
                        </CardHeader>
                        <CardContent>
                                {analyticsStatus && (
                                        <div className="space-y-4">
                                                <div className="grid grid-cols-1 gap-4">
                                                        <div className="border rounded p-3">
                                                                <h4 className="text-sm font-medium mb-2">Predictive Models</h4>
                                                                <div className="flex items-center gap-2">
                                                                        {analyticsStatus.predictive_models.completion_predictor ? (
                                                                                <CheckCircle className="h-4 w-4 text-green-500" />
                                                                        ) : (
                                                                                <AlertCircle className="h-4 w-4 text-red-500" />
                                                                        )}
                                                                        <span className="text-sm">
                                                                                {analyticsStatus.predictive_models.completion_predictor ? 'Trained' : 'Not Trained'}
                                                                        </span>
                                                                </div>
                                                        </div>

                                                        <div className="border rounded p-3">
                                                                <h4 className="text-sm font-medium mb-2">Real-Time Sessions</h4>
                                                                <div className="flex items-center gap-2">
                                                                        <Clock className="h-4 w-4 text-blue-500" />
                                                                        <span className="text-sm">
                                                                                {analyticsStatus.real_time_personalization.active_sessions} active
                                                                        </span>
                                                                </div>
                                                        </div>

                                                        <div className="border rounded p-3">
                                                                <h4 className="text-sm font-medium mb-2">Cohort Types</h4>
                                                                <div className="flex flex-wrap gap-1">
                                                                        {analyticsStatus.cohort_analysis.supported_cohort_types.map((type, index) => (
                                                                                <Badge key={index} variant="outline" className="text-xs">
                                                                                        {type.replace('_', ' ')}
                                                                                </Badge>
                                                                        ))}
                                                                </div>
                                                        </div>
                                                </div>
                                        </div>
                                )}
                        </CardContent>
                </Card>
        );

        return (
                <div className="container mx-auto p-6 space-y-6">
                        <div className="flex items-center justify-between">
                                <div>
                                        <h1 className="text-3xl font-bold">Advanced Analytics</h1>
                                        <p className="text-gray-600">
                                                AI-powered insights and real-time personalization
                                        </p>
                                </div>
                        </div>

                        <Tabs defaultValue="predictions" className="space-y-6">
                                <TabsList className="grid w-full grid-cols-4">
                                        <TabsTrigger value="predictions">Predictions</TabsTrigger>
                                        <TabsTrigger value="cohorts">Cohorts</TabsTrigger>
                                        <TabsTrigger value="realtime">Real-Time</TabsTrigger>
                                        <TabsTrigger value="status">Status</TabsTrigger>
                                </TabsList>

                                <TabsContent value="predictions" className="space-y-6">
                                        <PredictionCard />
                                </TabsContent>

                                <TabsContent value="cohorts" className="space-y-6">
                                        <CohortAnalysisCard />
                                </TabsContent>

                                <TabsContent value="realtime" className="space-y-6">
                                        <RealTimePersonalizationCard />
                                </TabsContent>

                                <TabsContent value="status" className="space-y-6">
                                        <StatusCard />
                                </TabsContent>
                        </Tabs>
                </div>
        );
};

export default AdvancedAnalytics;