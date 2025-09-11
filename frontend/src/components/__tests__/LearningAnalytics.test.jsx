import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import LearningAnalytics from '../LearningAnalytics';

// Mock translation hook
jest.mock('react-i18next', () => ({
        useTranslation: () => ({
                t: (key) => key,
        }),
}));

const TestWrapper = ({ children }) => (
        <BrowserRouter>
                <MantineProvider>
                        {children}
                </MantineProvider>
        </BrowserRouter>
);

describe('LearningAnalytics', () => {
        it('renders loading state initially', () => {
                render(
                        <TestWrapper>
                                <LearningAnalytics userId="test-user-123" />
                        </TestWrapper>
                );

                expect(screen.getByText('Loading learning analytics...')).toBeInTheDocument();
        });

        it('renders analytics data after loading', async () => {
                render(
                        <TestWrapper>
                                <LearningAnalytics userId="test-user-123" />
                        </TestWrapper>
                );

                // Wait for loading to complete
                await waitFor(() => {
                        expect(screen.getByText('Learning Analytics')).toBeInTheDocument();
                });

                // Check for key metrics
                expect(screen.getByText('TIME SPENT')).toBeInTheDocument();
                expect(screen.getByText('COMPLETION RATE')).toBeInTheDocument();
                expect(screen.getByText('ENGAGEMENT SCORE')).toBeInTheDocument();
                expect(screen.getByText('AVERAGE SCORE')).toBeInTheDocument();
        });

        it('renders learning patterns section', async () => {
                render(
                        <TestWrapper>
                                <LearningAnalytics userId="test-user-123" showDetailedView={true} />
                        </TestWrapper>
                );

                await waitFor(() => {
                        expect(screen.getByText('Learning Patterns')).toBeInTheDocument();
                });

                expect(screen.getByText('PREFERRED CONTENT')).toBeInTheDocument();
                expect(screen.getByText('LEARNING STYLE')).toBeInTheDocument();
                expect(screen.getByText('DIFFICULTY LEVEL')).toBeInTheDocument();
                expect(screen.getByText('SESSION LENGTH')).toBeInTheDocument();
        });

        it('renders strengths and challenges sections', async () => {
                render(
                        <TestWrapper>
                                <LearningAnalytics userId="test-user-123" showDetailedView={true} />
                        </TestWrapper>
                );

                await waitFor(() => {
                        expect(screen.getByText('Strong Topics')).toBeInTheDocument();
                        expect(screen.getByText('Areas for Improvement')).toBeInTheDocument();
                });
        });

        it('hides detailed view when showDetailedView is false', async () => {
                render(
                        <TestWrapper>
                                <LearningAnalytics userId="test-user-123" showDetailedView={false} />
                        </TestWrapper>
                );

                await waitFor(() => {
                        expect(screen.getByText('Learning Analytics')).toBeInTheDocument();
                });

                // Should not show detailed sections
                expect(screen.queryByText('Learning Patterns')).not.toBeInTheDocument();
                expect(screen.queryByText('Strong Topics')).not.toBeInTheDocument();
        });

        it('handles course-specific analytics', async () => {
                render(
                        <TestWrapper>
                                <LearningAnalytics
                                        userId="test-user-123"
                                        courseId="course-456"
                                        chapterId="chapter-789"
                                />
                        </TestWrapper>
                );

                await waitFor(() => {
                        expect(screen.getByText('Learning Analytics')).toBeInTheDocument();
                });

                // Component should render normally with course/chapter context
                expect(screen.getByText('TIME SPENT')).toBeInTheDocument();
        });
});