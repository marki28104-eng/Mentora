import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import UmamiTracker, { useUmamiTracker } from '../UmamiTracker';

// Mock window.umami
const mockUmami = {
        track: jest.fn()
};

// Test component that uses the hook
const TestComponent = () => {
        const {
                trackEvent,
                trackCourseStart,
                trackChapterComplete,
                trackAssessmentComplete,
                trackContentInteraction,
                trackTimeSpent,
                trackEngagementMetrics,
                isLoaded
        } = useUmamiTracker();

        return (
                <div>
                        <button onClick={() => trackEvent('test_event', { test: 'data' })}>
                                Track Event
                        </button>
                        <button onClick={() => trackCourseStart('course-123', 'beginner')}>
                                Track Course Start
                        </button>
                        <button onClick={() => trackChapterComplete('course-123', 'chapter-1', 300)}>
                                Track Chapter Complete
                        </button>
                        <button onClick={() => trackAssessmentComplete('course-123', 'quiz-1', 85, 120)}>
                                Track Assessment Complete
                        </button>
                        <button onClick={() => trackContentInteraction('course-123', 'video', 180, { quality: 'HD' })}>
                                Track Content Interaction
                        </button>
                        <button onClick={() => trackTimeSpent('course-123', 'chapter-1', 240, 'text')}>
                                Track Time Spent
                        </button>
                        <button onClick={() => trackEngagementMetrics({ sessionDuration: 1800, interactionCount: 25, scrollDepth: 80, clickCount: 15 })}>
                                Track Engagement Metrics
                        </button>
                        <span>{isLoaded() ? 'Loaded' : 'Not Loaded'}</span>
                </div>
        );
};

describe('UmamiTracker', () => {
        beforeEach(() => {
                // Clear any existing umami
                delete window.umami;
                mockUmami.track.mockClear();
        });

        it('renders without crashing', () => {
                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                        </BrowserRouter>
                );
        });

        it('loads tracking script with correct attributes', () => {
                render(
                        <BrowserRouter>
                                <UmamiTracker
                                        websiteId="test-website-id"
                                        src="http://localhost:3001/script.js"
                                        domains={['localhost', 'test.com']}
                                />
                        </BrowserRouter>
                );

                // Check if script tag was added
                const script = document.querySelector('script[data-website-id="test-website-id"]');
                expect(script).toBeTruthy();
                expect(script.src).toBe('http://localhost:3001/script.js');
                expect(script.getAttribute('data-domains')).toBe('localhost,test.com');
        });

        it('tracks events when umami is loaded', () => {
                // Mock umami being loaded
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Event');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('test_event', { test: 'data' });
        });

        it('tracks course start events', () => {
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Course Start');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'course_start',
                        course_id: 'course-123',
                        difficulty: 'beginner',
                        timestamp: expect.any(String)
                }));
        });

        it('tracks chapter completion events', () => {
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Chapter Complete');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'chapter_complete',
                        course_id: 'course-123',
                        chapter_id: 'chapter-1',
                        time_spent: 300,
                        timestamp: expect.any(String)
                }));
        });

        it('tracks assessment completion events', () => {
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Assessment Complete');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'assessment_complete',
                        course_id: 'course-123',
                        assessment_id: 'quiz-1',
                        score: 85,
                        time_spent: 120,
                        timestamp: expect.any(String)
                }));
        });

        it('tracks content interaction events', () => {
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Content Interaction');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'content_interaction',
                        course_id: 'course-123',
                        content_type: 'video',
                        time_spent: 180,
                        quality: 'HD',
                        timestamp: expect.any(String)
                }));
        });

        it('tracks time spent events', () => {
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Time Spent');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('learning_interaction', expect.objectContaining({
                        event_type: 'time_spent',
                        course_id: 'course-123',
                        chapter_id: 'chapter-1',
                        content_type: 'text',
                        time_spent: 240,
                        timestamp: expect.any(String)
                }));
        });

        it('tracks engagement metrics', () => {
                window.umami = mockUmami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Engagement Metrics');
                fireEvent.click(button);

                expect(mockUmami.track).toHaveBeenCalledWith('engagement_metrics', expect.objectContaining({
                        session_duration: 1800,
                        interaction_count: 25,
                        scroll_depth: 80,
                        click_count: 15,
                        timestamp: expect.any(String)
                }));
        });

        it('handles missing umami gracefully', () => {
                // Ensure umami is not available
                delete window.umami;

                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                const button = screen.getByText('Track Event');

                // Should not throw error when umami is not available
                expect(() => fireEvent.click(button)).not.toThrow();
        });

        it('reports correct loading status', () => {
                render(
                        <BrowserRouter>
                                <UmamiTracker websiteId="test-id" />
                                <TestComponent />
                        </BrowserRouter>
                );

                // Initially not loaded
                expect(screen.getByText('Not Loaded')).toBeTruthy();

                // Mock umami being loaded
                window.umami = mockUmami;

                // Re-render to check status
                render(
                        <BrowserRouter>
                                <TestComponent />
                        </BrowserRouter>
                );

                expect(screen.getByText('Loaded')).toBeTruthy();
        });
});