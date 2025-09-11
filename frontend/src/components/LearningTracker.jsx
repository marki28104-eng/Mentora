import { useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { useUmamiTracker } from './UmamiTracker';
import { useAuth } from '../contexts/AuthContext';

/**
 * LearningTracker Component
 * 
 * Tracks learning-specific interactions and behaviors for analytics.
 * Provides methods for tracking course interactions, assessments, and learning patterns.
 */
const LearningTracker = ({ children }) => {
        const location = useLocation();
        const { trackEvent, isLoaded } = useUmamiTracker();
        const { user } = useAuth();

        // Extract learning context from URL
        const extractLearningContext = useCallback((pathname) => {
                const courseMatch = pathname.match(/\/dashboard\/courses\/(\d+)/);
                const chapterMatch = pathname.match(/\/dashboard\/courses\/\d+\/chapters\/(\d+)/);

                return {
                        courseId: courseMatch ? courseMatch[1] : null,
                        chapterId: chapterMatch ? chapterMatch[1] : null,
                        isLearningPage: !!(courseMatch || chapterMatch)
                };
        }, []);

        // Track learning session start
        useEffect(() => {
                if (!isLoaded() || !user) return;

                const context = extractLearningContext(location.pathname);

                if (context.isLearningPage) {
                        trackEvent('learning_session_start', {
                                course_id: context.courseId,
                                chapter_id: context.chapterId,
                                user_type: user.is_premium ? 'premium' : 'free'
                        });
                }
        }, [location.pathname, user, trackEvent, isLoaded, extractLearningContext]);

        // Provide tracking methods to child components
        const trackingMethods = {
                // Course interaction tracking
                trackCourseView: (courseId, courseName) => {
                        trackEvent('course_view', {
                                course_id: courseId,
                                course_name: courseName
                        });
                },

                trackChapterStart: (courseId, chapterId, chapterName) => {
                        trackEvent('chapter_start', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                chapter_name: chapterName
                        });
                },

                trackChapterComplete: (courseId, chapterId, timeSpent) => {
                        trackEvent('chapter_complete', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                time_spent: timeSpent
                        });
                },

                // Assessment tracking
                trackQuizStart: (courseId, chapterId, quizType) => {
                        trackEvent('quiz_start', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                quiz_type: quizType
                        });
                },

                trackQuizComplete: (courseId, chapterId, score, timeSpent) => {
                        trackEvent('quiz_complete', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                score: score,
                                time_spent: timeSpent
                        });
                },

                trackQuizAnswer: (courseId, chapterId, questionId, isCorrect, timeSpent) => {
                        trackEvent('quiz_answer', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                question_id: questionId,
                                is_correct: isCorrect,
                                time_spent: timeSpent
                        });
                },

                // Content interaction tracking
                trackContentInteraction: (courseId, chapterId, interactionType, contentType) => {
                        trackEvent('content_interaction', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                interaction_type: interactionType, // scroll, click, expand, etc.
                                content_type: contentType // text, video, diagram, code, etc.
                        });
                },

                trackTimeSpent: (courseId, chapterId, contentType, timeSpent) => {
                        trackEvent('time_spent', {
                                course_id: courseId,
                                chapter_id: chapterId,
                                content_type: contentType,
                                time_spent: timeSpent
                        });
                },

                // Learning behavior tracking
                trackDifficultyChange: (courseId, oldDifficulty, newDifficulty) => {
                        trackEvent('difficulty_change', {
                                course_id: courseId,
                                old_difficulty: oldDifficulty,
                                new_difficulty: newDifficulty
                        });
                },

                trackSearchQuery: (query, resultsCount) => {
                        trackEvent('search_query', {
                                query_length: query.length,
                                results_count: resultsCount
                        });
                },

                trackCourseCreation: (courseType, sourceType, difficulty) => {
                        trackEvent('course_creation', {
                                course_type: courseType,
                                source_type: sourceType, // upload, text_input, etc.
                                difficulty: difficulty
                        });
                },

                // Navigation tracking
                trackNavigation: (fromPage, toPage, navigationMethod) => {
                        trackEvent('navigation', {
                                from_page: fromPage,
                                to_page: toPage,
                                method: navigationMethod // click, breadcrumb, sidebar, etc.
                        });
                }
        };

        return typeof children === 'function' ? children(trackingMethods) : children;
};

export default LearningTracker;