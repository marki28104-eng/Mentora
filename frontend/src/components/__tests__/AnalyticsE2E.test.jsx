/**
 * End-to-end tests for analytics components integration
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import UmamiTracker, { useUmamiTracker } from '../UmamiTracker';
import LearningAnalytics from '../LearningAnalytics';
import PersonalizedRecommendations from '../PersonalizedRecommendations';

// Mock API services
jest.mock('../../api/dashboardService', () => ({
        getLearningAnalytics: jest.fn(),
        getPersonalizedRecommendations: jest.fn(),
}));

jest.mock('../../api/baseApi', () => ({
        get: jest.fn(),
        post: jest.fn(),
}));

// Mock translation hook
jest.mock('react-i18next', () => ({
        useTranslation: () => ({
                t: (key) => key,
        }),
}));

// Mock Umami
const mockUmami = {
        track: jest.fn()
};

// Test wrapper component
const TestWrapper = ({ children }) => {
        const queryClient = new QueryClient({
                defaultOptions: {
                        queries: { retry: false },
                        mutations: { retry: false },
                },
        });

        return (
                <BrowserRouter>
                        <MantineProvider>
                                <QueryClientProvider client={queryClient}>
                                        {children}
                                </QueryClientProvider>
                        </MantineProvider>
                </BrowserRouter>
        );
};

// Test component that simulates a complete learning session
const LearningSessionSimulator = () => {
        const {
                trackCourseStart,
                trackChapterComplete,
                trackAssessmentComplete,
                trackContentInteraction,
                trackTimeSpent,
                trackEngagementMetrics
        } = useUmamiTracker();

        const simulateCompleteSession = async () => {
                // Simulate course start
                trackCourseStart('course-123', 'intermediate');

                // Simulate content interactions
                trackContentInteraction('course-123', 'video', 300, { quality: 'HD' });
                trackContentInteraction('course-123', 'text', 180, { difficulty: 'medium' });

                // Simulate time spent
                trackTimeSpent('course-123', 'chapter-1', 480, 'mixed');

                // Simulate chapter completion
                trackChapterComplete('course-123', 'chapter-1', 480);

                // Simulate assessment
                trackAssessmentComplete('course-123', 'quiz-1', 85, 240);

                // Simulate engagement metrics
                trackEngagementMetrics({
                        sessionDuration: 720,
                        interactionCount: 15,
                        scrollDepth: 85,
                        clickCount: 12
                });
        };

        return (
                <div>
                        <button onClick={simulateCompleteSession}>
                                Simulate Learning Session
                        </button>
                        <LearningAnalytics userId="test-user-123" courseId="course-123" />
                        <PersonalizedRecommendations userId="test-user-123" />
                </div>
        );
};

describe('Analytics E2E Integration', () => {
        let mockGetLearningAnalytics;
        let mockGetPersonalizedRecommendations;

        beforeEach(() => {
                // Clear mocks
                jest.clearAllMocks();
                delete window.umami;

                // Setup API mocks
                const { getLearningAnalytics, getPersonalizedRecommendations } = require('../../api/dashboardService');
                mockGetLearningAnalytics = getLearningAnalytics;
                mockGetPersonalizedRecommendations = getPersonalizedRecommendations;

                // Mock successful API responses
                mockGetLearningAnalytics.mockResolvedValue({
                        timeSpent: 3600,
                        completionRate: 0.75,
                        engagementScore: 0.8,
                        averageScore: 85,
                        learningStyle: 'visual',
                        preferredDifficulty: 'intermediate',
                        strongTopics: ['mathematics', 'physics'],
                        challengingTopics: ['chemistry'],
                        preferredContentTypes: ['video', 'interactive'],
                        sessionLength: 45,
                        progressData: [
                                { date: '2024-01-01', value: 20 },
                                { date: '2024-01-02', value: 35 },
                                { date: '2024-01-03', value: 50 },
                        ]
                });

                mockGetPersonalizedRecommendations.mockResolvedValue({
                        recommendedCourses: [
                                {
                                        id: 1,
                                        title: 'Advanced Mathematics',
                                        difficulty: 'intermediate',
                                        estimatedDuration: 120,
                                        matchScore: 0.9
                                },
                                {
                                        id: 2,
                                        title: 'Physics Fundamentals',
                                        difficulty: 'intermediate',
                                        estimatedDuration: 90,
                                        matchScore: 0.85
                                }
                        ],
                        adaptedContent: {
                                difficulty: 'intermediate',
                                contentFormat: 'visual',
                                pacing: 'normal'
                        }
                });
        });

        it('completes full analytics tracking and display cycle', async () => {
                // Setup Umami mock
                window.umami = mockUmami;

                render(
                        <TestWrapper>
                                <UmamiTracker websiteId="test-website" />
                                <LearningSessionSimulator />
                        </TestWrapper>
                );

                // Simulate learning session
                const simulateButton = screen.getByText('Simulate Learning Session');
                fireEvent.click(simulateButton);

                // Verify tracking calls were made
                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'course_start',
                        course_id: 'course-123',
                        difficulty: 'intermediate'
                }));

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'content_interaction',
                        course_id: 'course-123',
                        content_type: 'video',
                        time_spent: 300
                }));

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'chapter_complete',
                        course_id: 'course-123',
                        chapter_id: 'chapter-1',
                        time_spent: 480
                }));

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'assessment_complete',
                        course_id: 'course-123',
                        assessment_id: 'quiz-1',
                        score: 85,
                        time_spent: 240
                }));

                expect(mockUmami.track).toHaveBeenCalledWith('engagement_metrics', expect.objectContaining({
                        session_duration: 720,
                        interaction_count: 15,
                        scroll_depth: 85,
                        click_count: 12
                }));

                // Wait for analytics to load and display
                await waitFor(() => {
                        expect(screen.getByText('Learning Analytics')).toBeInTheDocument();
                });

                // Verify analytics data is displayed
                expect(screen.getByText('TIME SPENT')).toBeInTheDocument();
                expect(screen.getByText('COMPLETION RATE')).toBeInTheDocument();
                expect(screen.getByText('ENGAGEMENT SCORE')).toBeInTheDocument();

                // Wait for recommendations to load
                await waitFor(() => {
                        expect(screen.getByText('Advanced Mathematics')).toBeInTheDocument();
                });

                // Verify API calls were made
                expect(mockGetLearningAnalytics).toHaveBeenCalledWith('test-user-123', 'course-123', undefined);
                expect(mockGetPersonalizedRecommendations).toHaveBeenCalledWith('test-user-123');
        });

        it('handles analytics data flow with different learning patterns', async () => {
                window.umami = mockUmami;

                // Mock different learning patterns
                mockGetLearningAnalytics.mockResolvedValue({
                        timeSpent: 7200,
                        completionRate: 0.95,
                        engagementScore: 0.9,
                        averageScore: 92,
                        learningStyle: 'kinesthetic',
                        preferredDifficulty: 'advanced',
                        strongTopics: ['physics', 'engineering'],
                        challengingTopics: ['literature'],
                        preferredContentTypes: ['interactive', 'simulation'],
                        sessionLength: 60,
                        progressData: [
                                { date: '2024-01-01', value: 40 },
                                { date: '2024-01-02', value: 70 },
                                { date: '2024-01-03', value: 95 },
                        ]
                });

                const AdvancedLearnerComponent = () => {
                        const { trackEvent } = useUmamiTracker();

                        const simulateAdvancedPattern = () => {
                                // Simulate advanced learner behavior
                                trackEvent('learning_interaction', {
                                        event_type: 'content_interaction',
                                        content_type: 'simulation',
                                        engagement_level: 'high',
                                        difficulty: 'advanced'
                                });

                                trackEvent('learning_interaction', {
                                        event_type: 'assessment_complete',
                                        score: 95,
                                        time_spent: 180,
                                        difficulty: 'advanced'
                                });
                        };

                        return (
                                <div>
                                        <button onClick={simulateAdvancedPattern}>
                                                Simulate Advanced Pattern
                                        </button>
                                        <LearningAnalytics userId="advanced-user" showDetailedView={true} />
                                </div>
                        );
                };

                render(
                        <TestWrapper>
                                <UmamiTracker websiteId="test-website" />
                                <AdvancedLearnerComponent />
                        </TestWrapper>
                );

                // Simulate advanced learning pattern
                const simulateButton = screen.getByText('Simulate Advanced Pattern');
                fireEvent.click(simulateButton);

                // Verify advanced pattern tracking
                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        content_type: 'simulation',
                        engagement_level: 'high',
                        difficulty: 'advanced'
                }));

                // Wait for analytics to display advanced learner data
                await waitFor(() => {
                        expect(screen.getByText('Learning Analytics')).toBeInTheDocument();
                });

                // Should show detailed view for advanced learner
                await waitFor(() => {
                        expect(screen.getByText('Learning Patterns')).toBeInTheDocument();
                        expect(screen.getByText('Strong Topics')).toBeInTheDocument();
                });
        });

        it('handles real-time analytics updates during learning session', async () => {
                window.umami = mockUmami;

                const RealTimeComponent = () => {
                        const { trackTimeSpent, trackEngagementMetrics } = useUmamiTracker();

                        const simulateRealTimeUpdates = () => {
                                // Simulate real-time tracking every few seconds
                                const intervals = [5, 10, 15, 20]; // seconds

                                intervals.forEach((seconds, index) => {
                                        setTimeout(() => {
                                                trackTimeSpent('course-123', 'chapter-1', seconds, 'text');
                                                trackEngagementMetrics({
                                                        sessionDuration: seconds,
                                                        interactionCount: index + 1,
                                                        scrollDepth: 20 + (index * 15),
                                                        clickCount: index
                                                });
                                        }, index * 100); // Stagger the calls
                                });
                        };

                        return (
                                <div>
                                        <button onClick={simulateRealTimeUpdates}>
                                                Start Real-time Tracking
                                        </button>
                                        <LearningAnalytics userId="realtime-user" courseId="course-123" />
                                </div>
                        );
                };

                render(
                        <TestWrapper>
                                <UmamiTracker websiteId="test-website" />
                                <RealTimeComponent />
                        </TestWrapper>
                );

                // Start real-time tracking
                const startButton = screen.getByText('Start Real-time Tracking');

                await act(async () => {
                        fireEvent.click(startButton);

                        // Wait for all tracking calls to complete
                        await new Promise(resolve => setTimeout(resolve, 500));
                });

                // Verify multiple tracking calls were made
                expect(mockUmami.track).toHaveBeenCalledTimes(8); // 4 time_spent + 4 engagement_metrics

                // Verify progressive engagement tracking
                const engagementCalls = mockUmami.track.mock.calls.filter(
                        call => call[0] === 'engagement_metrics'
                );

                expect(engagementCalls).toHaveLength(4);
                expect(engagementCalls[0][1].scroll_depth).toBe(20);
                expect(engagementCalls[3][1].scroll_depth).toBe(65);
        });

        it('handles analytics errors gracefully', async () => {
                // Mock API errors
                mockGetLearningAnalytics.mockRejectedValue(new Error('Analytics API Error'));
                mockGetPersonalizedRecommendations.mockRejectedValue(new Error('Recommendations API Error'));

                const ErrorHandlingComponent = () => {
                        return (
                                <div>
                                        <LearningAnalytics userId="error-user" />
                                        <PersonalizedRecommendations userId="error-user" />
                                </div>
                        );
                };

                render(
                        <TestWrapper>
                                <ErrorHandlingComponent />
                        </TestWrapper>
                );

                // Should show loading initially
                expect(screen.getByText('Loading learning analytics...')).toBeInTheDocument();

                // Wait for error handling
                await waitFor(() => {
                        // Should gracefully handle errors without crashing
                        expect(screen.queryByText('Loading learning analytics...')).not.toBeInTheDocument();
                });

                // Verify API calls were attempted
                expect(mockGetLearningAnalytics).toHaveBeenCalled();
                expect(mockGetPersonalizedRecommendations).toHaveBeenCalled();
        });

        it('integrates analytics with course navigation', async () => {
                window.umami = mockUmami;

                const NavigationComponent = () => {
                        const { trackEvent } = useUmamiTracker();

                        const simulateNavigation = () => {
                                // Simulate course navigation events
                                trackEvent('learning_interaction', {
                                        event_type: 'page_view',
                                        page_url: '/courses/123',
                                        course_id: '123'
                                });

                                trackEvent('learning_interaction', {
                                        event_type: 'page_view',
                                        page_url: '/courses/123/chapters/1',
                                        course_id: '123',
                                        chapter_id: '1'
                                });

                                trackEvent('learning_interaction', {
                                        event_type: 'page_view',
                                        page_url: '/courses/123/chapters/2',
                                        course_id: '123',
                                        chapter_id: '2'
                                });
                        };

                        return (
                                <div>
                                        <button onClick={simulateNavigation}>
                                                Simulate Navigation
                                        </button>
                                        <LearningAnalytics userId="nav-user" courseId="123" />
                                </div>
                        );
                };

                render(
                        <TestWrapper>
                                <UmamiTracker websiteId="test-website" />
                                <NavigationComponent />
                        </TestWrapper>
                );

                // Simulate navigation
                const navButton = screen.getByText('Simulate Navigation');
                fireEvent.click(navButton);

                // Verify navigation tracking
                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'page_view',
                        page_url: '/courses/123',
                        course_id: '123'
                }));

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'page_view',
                        page_url: '/courses/123/chapters/1',
                        course_id: '123',
                        chapter_id: '1'
                }));

                // Wait for analytics to reflect navigation data
                await waitFor(() => {
                        expect(screen.getByText('Learning Analytics')).toBeInTheDocument();
                });

                // Verify course-specific analytics call
                expect(mockGetLearningAnalytics).toHaveBeenCalledWith('nav-user', '123', undefined);
        });

        it('handles performance with high-frequency tracking', async () => {
                window.umami = mockUmami;

                const HighFrequencyComponent = () => {
                        const { trackEvent } = useUmamiTracker();

                        const simulateHighFrequency = () => {
                                // Simulate high-frequency events (like scroll tracking)
                                for (let i = 0; i < 50; i++) {
                                        trackEvent('engagement_metrics', {
                                                scroll_depth: i * 2,
                                                timestamp: Date.now() + i
                                        });
                                }
                        };

                        return (
                                <div>
                                        <button onClick={simulateHighFrequency}>
                                                High Frequency Tracking
                                        </button>
                                </div>
                        );
                };

                render(
                        <TestWrapper>
                                <UmamiTracker websiteId="test-website" />
                                <HighFrequencyComponent />
                        </TestWrapper>
                );

                const startTime = performance.now();

                // Simulate high-frequency tracking
                const highFreqButton = screen.getByText('High Frequency Tracking');
                fireEvent.click(highFreqButton);

                const endTime = performance.now();
                const executionTime = endTime - startTime;

                // Should handle high-frequency events efficiently
                expect(executionTime).toBeLessThan(100); // Should complete in under 100ms
                expect(mockUmami.track).toHaveBeenCalledTimes(50);
        });
});