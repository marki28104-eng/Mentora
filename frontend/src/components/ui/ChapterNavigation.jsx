import React from 'react';
import { Group, Button, Text, Box, ThemeIcon } from '@mantine/core';
import { IconArrowLeft, IconArrowRight, IconCheck } from '@tabler/icons-react';

const ChapterNavigation = ({
        currentChapter,
        totalChapters,
        onPrevious,
        onNext,
        onComplete,
        isCompleted = false,
        isLoading = false,
        className = "",
        ...props
}) => {
        const hasPrevious = currentChapter > 1;
        const hasNext = currentChapter < totalChapters;

        return (
                <Box
                        className={`card-modern card-glass transition-all duration-300 ${className}`}
                        sx={{
                                background: 'var(--bg-card)',
                                backdropFilter: 'blur(20px)',
                                border: '1px solid rgba(139, 92, 246, 0.2)',
                                borderRadius: '16px',
                                padding: '20px',
                        }}
                        {...props}
                >
                        <Group position="apart" align="center">
                                {/* Previous Chapter Button */}
                                <Button
                                        variant="light"
                                        color="purple"
                                        leftIcon={<IconArrowLeft size={16} />}
                                        onClick={onPrevious}
                                        disabled={!hasPrevious}
                                        className="btn-modern transition-all duration-300"
                                        sx={{
                                                opacity: hasPrevious ? 1 : 0.5,
                                                '&:hover:not(:disabled)': {
                                                        transform: 'translateY(-2px)',
                                                        boxShadow: '0 8px 25px rgba(139, 92, 246, 0.3)',
                                                },
                                        }}
                                >
                                        Previous Chapter
                                </Button>

                                {/* Chapter Progress Indicator */}
                                <Box sx={{ textAlign: 'center' }}>
                                        <Group spacing={8} position="center" mb={4}>
                                                <ThemeIcon
                                                        size="sm"
                                                        radius="xl"
                                                        color={isCompleted ? "green" : "purple"}
                                                        variant="light"
                                                >
                                                        {isCompleted ? <IconCheck size={14} /> : <Text size="xs" weight={700}>{currentChapter}</Text>}
                                                </ThemeIcon>
                                                <Text size="sm" weight={600} color="dimmed">
                                                        Chapter {currentChapter} of {totalChapters}
                                                </Text>
                                        </Group>

                                        {/* Progress Bar */}
                                        <Box
                                                sx={{
                                                        width: '120px',
                                                        height: '4px',
                                                        background: 'var(--bg-tertiary)',
                                                        borderRadius: '2px',
                                                        overflow: 'hidden',
                                                        position: 'relative',
                                                }}
                                        >
                                                <Box
                                                        sx={{
                                                                width: `${(currentChapter / totalChapters) * 100}%`,
                                                                height: '100%',
                                                                background: isCompleted
                                                                        ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                                                                        : 'linear-gradient(90deg, var(--purple-500) 0%, var(--purple-400) 100%)',
                                                                transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
                                                        }}
                                                />
                                        </Box>
                                </Box>

                                {/* Next Chapter / Complete Button */}
                                {hasNext ? (
                                        <Button
                                                variant="gradient"
                                                gradient={{ from: 'purple.6', to: 'purple.4' }}
                                                rightIcon={<IconArrowRight size={16} />}
                                                onClick={onNext}
                                                className="btn-modern transition-all duration-300"
                                                sx={{
                                                        '&:hover': {
                                                                transform: 'translateY(-2px)',
                                                                boxShadow: '0 8px 25px rgba(139, 92, 246, 0.4)',
                                                        },
                                                }}
                                        >
                                                Next Chapter
                                        </Button>
                                ) : (
                                        <Button
                                                variant="gradient"
                                                gradient={{ from: 'green.6', to: 'green.4' }}
                                                rightIcon={<IconCheck size={16} />}
                                                onClick={onComplete}
                                                loading={isLoading}
                                                disabled={isCompleted}
                                                className="btn-modern transition-all duration-300"
                                                sx={{
                                                        '&:hover:not(:disabled)': {
                                                                transform: 'translateY(-2px)',
                                                                boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                                                        },
                                                }}
                                        >
                                                {isCompleted ? 'Completed' : 'Complete Course'}
                                        </Button>
                                )}
                        </Group>
                </Box>
        );
};

export default ChapterNavigation;