import React, { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

// Extend Window interface to include umami
declare global {
        interface Window {
                umami?: {
                        track: (eventName?: string | null, eventData?: Record<string, any>) => void;
                };
        }
}

// TypeScript interfaces for Umami tracking
export interface UmamiTrackerProps {
        websiteId: string;
        src?: string;
        domains?: string[];
        autoTrack?: boolean;
}

export interface TrackingEvent {
        name: string;
        data?: Record<string, any>;
}

export interface LearningInteractionEvent {
        eventType: 'course_start' | 'chapter_complete' | 'assessment_complete' | 'content_interaction' | 'time_spent';
        courseId?: string;
        chapterId?: string;
        assessmentId?: string;
        contentType?: 'video' | 'text' | 'interactive' | 'quiz';
        difficulty?: 'beginner' | 'intermediate' | 'advanced';
        timeSpent?: number;
        score?: number;
        completionRate?: number;
        metadata?: Record<string, any>;
}

export interface EngagementMetrics {
        sessionDuration: number;
        interactionCount: number;
        scrollDepth: number;
        clickCount: number;
}

/**
 * UmamiTracker Component
 * 
 * Integrates Umami analytics for privacy-compliant user behavior tracking.
 * Tracks page views and custom events without using cookies or personal identifiers.
 */
const UmamiTracker: React.FC<UmamiTrackerProps> = ({
        websiteId,
        src = 'https://analytics.umami.is/script.js',
        domains = [],
        autoTrack = true
}) => {
        const location = useLocation();
        const scriptLoaded = useRef(false);
        const umamiRef = useRef<Window['umami'] | null>(null);

        // Load Umami script
        useEffect(() => {
                if (scriptLoaded.current || !websiteId) return;

                const script = document.createElement('script');
                script.async = true;
                script.defer = true;
                script.src = src;
                script.setAttribute('data-website-id', websiteId);

                if (domains.length > 0) {
                        script.setAttribute('data-domains', domains.join(','));
                }

                // Add script to head
                document.head.appendChild(script);

                script.onload = () => {
                        scriptLoaded.current = true;
                        // Store reference to umami object when available
                        if (window.umami) {
                                umamiRef.current = window.umami;
                        }
                };

                return () => {
                        // Cleanup script on unmount
                        if (script.parentNode) {
                                script.parentNode.removeChild(script);
                        }
                        scriptLoaded.current = false;
                };
        }, [websiteId, src, domains]);

        // Track page views on route changes
        useEffect(() => {
                if (!autoTrack || !scriptLoaded.current) return;

                // Wait for umami to be available
                const trackPageView = () => {
                        if (window.umami && window.umami.track) {
                                window.umami.track();
                        }
                };

                // Small delay to ensure umami is ready
                const timer = setTimeout(trackPageView, 100);

                return () => clearTimeout(timer);
        }, [location.pathname, autoTrack]);

        return null; // This component doesn't render anything
};

/**
 * Hook for tracking custom events with learning-specific methods
 */
export const useUmamiTracker = () => {
        const trackEvent = (eventName: string, eventData: Record<string, any> = {}) => {
                if (window.umami && window.umami.track) {
                        window.umami.track(eventName, eventData);
                } else {
                        console.warn('Umami not loaded, event not tracked:', eventName);
                }
        };

        const trackPageView = (url: string | null = null) => {
                if (window.umami && window.umami.track) {
                        window.umami.track(url);
                }
        };

        // Learning-specific tracking methods
        const trackLearningInteraction = (interaction: LearningInteractionEvent) => {
                const eventData = {
                        event_type: interaction.eventType,
                        course_id: interaction.courseId,
                        chapter_id: interaction.chapterId,
                        assessment_id: interaction.assessmentId,
                        content_type: interaction.contentType,
                        difficulty: interaction.difficulty,
                        time_spent: interaction.timeSpent,
                        score: interaction.score,
                        completion_rate: interaction.completionRate,
                        timestamp: new Date().toISOString(),
                        ...interaction.metadata
                };

                trackEvent('learning_interaction', eventData);
        };

        const trackCourseStart = (courseId: string, difficulty: string) => {
                trackLearningInteraction({
                        eventType: 'course_start',
                        courseId,
                        difficulty: difficulty as 'beginner' | 'intermediate' | 'advanced'
                });
        };

        const trackChapterComplete = (courseId: string, chapterId: string, timeSpent: number) => {
                trackLearningInteraction({
                        eventType: 'chapter_complete',
                        courseId,
                        chapterId,
                        timeSpent
                });
        };

        const trackAssessmentComplete = (
                courseId: string, 
                assessmentId: string, 
                score: number, 
                timeSpent: number
        ) => {
                trackLearningInteraction({
                        eventType: 'assessment_complete',
                        courseId,
                        assessmentId,
                        score,
                        timeSpent
                });
        };

        const trackContentInteraction = (
                courseId: string,
                contentType: 'video' | 'text' | 'interactive' | 'quiz',
                timeSpent: number,
                metadata: Record<string, any> = {}
        ) => {
                trackLearningInteraction({
                        eventType: 'content_interaction',
                        courseId,
                        contentType,
                        timeSpent,
                        metadata
                });
        };

        const trackTimeSpent = (
                courseId: string,
                chapterId: string,
                timeSpent: number,
                contentType?: 'video' | 'text' | 'interactive' | 'quiz'
        ) => {
                trackLearningInteraction({
                        eventType: 'time_spent',
                        courseId,
                        chapterId,
                        contentType,
                        timeSpent
                });
        };

        const trackEngagementMetrics = (metrics: EngagementMetrics) => {
                trackEvent('engagement_metrics', {
                        session_duration: metrics.sessionDuration,
                        interaction_count: metrics.interactionCount,
                        scroll_depth: metrics.scrollDepth,
                        click_count: metrics.clickCount,
                        timestamp: new Date().toISOString()
                });
        };

        return {
                trackEvent,
                trackPageView,
                trackLearningInteraction,
                trackCourseStart,
                trackChapterComplete,
                trackAssessmentComplete,
                trackContentInteraction,
                trackTimeSpent,
                trackEngagementMetrics,
                isLoaded: () => !!(window.umami && window.umami.track)
        };
};

export default UmamiTracker;