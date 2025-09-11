import React, { useState, useEffect } from 'react';
import {
        Paper,
        Title,
        Text,
        Group,
        Stack,
        Progress,
        Badge,
        Grid,
        Card,
        RingProgress,
        Center,
        ThemeIcon,
        Box,
        Loader,
        Alert
} from '@mantine/core';
import {
        IconClock,
        IconTrendingUp,
        IconTarget,
        IconBrain,
        IconChartBar,
        IconAlertCircle,
        IconBook,
        IconQuestionMark
} from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';

/**
 * @typedef {Object} UserLearningMetrics
 * @property {number} timeSpent
 * @property {number} completionRate
 * @property {number} engagementScore
 * @property {'beginner'|'intermediate'|'advanced'} difficultyPreference
 * @property {number} averageScore
 * @property {number} totalCourses
 * @property {number} totalChapters
 * @property {number} totalAssessments
 */

/**
 * @typedef {Object} LearningPattern
 * @property {'video'|'text'|'interactive'|'quiz'} preferredContentType
 * @property {number} optimalSessionDuration
 * @property {string[]} peakLearningHours
 * @property {string[]} strongTopics
 * @property {string[]} challengingTopics
 * @property {'visual'|'auditory'|'kinesthetic'|'reading'} learningStyle
 */

/**
 * @typedef {Object} LearningAnalyticsProps
 * @property {string} userId
 * @property {string} [courseId]
 * @property {string} [chapterId]
 * @property {boolean} [showDetailedView]
 */

/**
 * LearningAnalytics Component
 * @param {LearningAnalyticsProps} props
 */
const LearningAnalytics = ({
        userId,
        courseId,
        chapterId,
        showDetailedView = true
}) => {
        const { t } = useTranslation('dashboard');

        const [metrics, setMetrics] = useState(null);
        const [patterns, setPatterns] = useState(null);
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState(null);

        // Mock data for demonstration - in real implementation, this would fetch from API
        useEffect(() => {
                const fetchAnalytics = async () => {
                        try {
                                setLoading(true);

                                // Simulate API call delay
                                await new Promise(resolve => setTimeout(resolve, 1000));

                                // Mock analytics data
                                const mockMetrics = {
                                        timeSpent: 12450, // seconds
                                        completionRate: 78.5,
                                        engagementScore: 85.2,
                                        difficultyPreference: 'intermediate',
                                        averageScore: 82.3,
                                        totalCourses: 5,
                                        totalChapters: 23,
                                        totalAssessments: 47
                                };

                                const mockPatterns = {
                                        preferredContentType: 'interactive',
                                        optimalSessionDuration: 45, // minutes
                                        peakLearningHours: ['09:00-11:00', '14:00-16:00'],
                                        strongTopics: ['Mathematics', 'Programming', 'Data Analysis'],
                                        challengingTopics: ['Advanced Statistics', 'Machine Learning Theory'],
                                        learningStyle: 'visual'
                                };

                                setMetrics(mockMetrics);
                                setPatterns(mockPatterns);
                                setError(null);
                        } catch (err) {
                                setError('Failed to load learning analytics');
                                console.error('Error fetching analytics:', err);
                        } finally {
                                setLoading(false);
                        }
                };

                fetchAnalytics();
        }, [userId, courseId, chapterId]);

        const formatTime = (seconds) => {
                const hours = Math.floor(seconds / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);

                if (hours > 0) {
                        return `${hours}h ${minutes}m`;
                }
                return `${minutes}m`;
        };

        const getDifficultyColor = (difficulty) => {
                switch (difficulty) {
                        case 'beginner': return 'green';
                        case 'intermediate': return 'yellow';
                        case 'advanced': return 'red';
                        default: return 'blue';
                }
        };

        const getEngagementColor = (score) => {
                if (score >= 80) return 'green';
                if (score >= 60) return 'yellow';
                return 'red';
        };

        if (loading) {
                return (
                        <Paper p="md" withBorder>
                                <Center>
                                        <Stack align="center" spacing="sm">
                                                <Loader size="lg" />
                                                <Text color="dimmed">Loading learning analytics...</Text>
                                        </Stack>
                                </Center>
                        </Paper>
                );
        }

        if (error) {
                return (
                        <Alert icon={<IconAlertCircle size={16} />} color="red" variant="light">
                                {error}
                        </Alert>
                );
        }

        if (!metrics || !patterns) {
                return (
                        <Alert icon={<IconAlertCircle size={16} />} color="yellow" variant="light">
                                No analytics data available yet. Start learning to see your progress!
                        </Alert>
                );
        }

        return (
                <Stack spacing="md">
                        {/* Header */}
                        <Group position="apart" align="flex-start">
                                <Stack spacing={4}>
                                        <Title order={3}>Learning Analytics</Title>
                                        <Text color="dimmed" size="sm">
                                                Your personalized learning insights and progress
                                        </Text>
                                </Stack>
                        </Group>

                        {/* Key Metrics Grid */}
                        <Grid>
                                <Grid.Col span={12} md={6} lg={3}>
                                        <Card withBorder p="md">
                                                <Group position="apart" align="flex-start">
                                                        <Stack spacing={4}>
                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                        TIME SPENT
                                                                </Text>
                                                                <Text size="xl" weight={700}>
                                                                        {formatTime(metrics.timeSpent)}
                                                                </Text>
                                                        </Stack>
                                                        <ThemeIcon color="blue" variant="light" size="lg">
                                                                <IconClock size={20} />
                                                        </ThemeIcon>
                                                </Group>
                                        </Card>
                                </Grid.Col>

                                <Grid.Col span={12} md={6} lg={3}>
                                        <Card withBorder p="md">
                                                <Group position="apart" align="flex-start">
                                                        <Stack spacing={4}>
                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                        COMPLETION RATE
                                                                </Text>
                                                                <Text size="xl" weight={700}>
                                                                        {metrics.completionRate.toFixed(1)}%
                                                                </Text>
                                                        </Stack>
                                                        <ThemeIcon color="green" variant="light" size="lg">
                                                                <IconTarget size={20} />
                                                        </ThemeIcon>
                                                </Group>
                                                <Progress
                                                        value={metrics.completionRate}
                                                        color="green"
                                                        size="xs"
                                                        mt="sm"
                                                />
                                        </Card>
                                </Grid.Col>

                                <Grid.Col span={12} md={6} lg={3}>
                                        <Card withBorder p="md">
                                                <Group position="apart" align="flex-start">
                                                        <Stack spacing={4}>
                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                        ENGAGEMENT SCORE
                                                                </Text>
                                                                <Text size="xl" weight={700}>
                                                                        {metrics.engagementScore.toFixed(1)}
                                                                </Text>
                                                        </Stack>
                                                        <ThemeIcon color={getEngagementColor(metrics.engagementScore)} variant="light" size="lg">
                                                                <IconTrendingUp size={20} />
                                                        </ThemeIcon>
                                                </Group>
                                                <Progress
                                                        value={metrics.engagementScore}
                                                        color={getEngagementColor(metrics.engagementScore)}
                                                        size="xs"
                                                        mt="sm"
                                                />
                                        </Card>
                                </Grid.Col>

                                <Grid.Col span={12} md={6} lg={3}>
                                        <Card withBorder p="md">
                                                <Group position="apart" align="flex-start">
                                                        <Stack spacing={4}>
                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                        AVERAGE SCORE
                                                                </Text>
                                                                <Text size="xl" weight={700}>
                                                                        {metrics.averageScore.toFixed(1)}%
                                                                </Text>
                                                        </Stack>
                                                        <ThemeIcon color="violet" variant="light" size="lg">
                                                                <IconChartBar size={20} />
                                                        </ThemeIcon>
                                                </Group>
                                        </Card>
                                </Grid.Col>
                        </Grid>

                        {showDetailedView && (
                                <>
                                        {/* Learning Progress Overview */}
                                        <Grid>
                                                <Grid.Col span={12} md={4}>
                                                        <Card withBorder p="md" h="100%">
                                                                <Stack spacing="md">
                                                                        <Text weight={600} size="sm">Learning Progress</Text>

                                                                        <Center>
                                                                                <RingProgress
                                                                                        size={120}
                                                                                        thickness={8}
                                                                                        sections={[
                                                                                                { value: metrics.completionRate, color: 'blue' },
                                                                                        ]}
                                                                                        label={
                                                                                                <Center>
                                                                                                        <Stack spacing={0} align="center">
                                                                                                                <Text size="xs" color="dimmed">Completed</Text>
                                                                                                                <Text weight={700} size="sm">
                                                                                                                        {metrics.completionRate.toFixed(0)}%
                                                                                                                </Text>
                                                                                                        </Stack>
                                                                                                </Center>
                                                                                        }
                                                                                />
                                                                        </Center>

                                                                        <Stack spacing="xs">
                                                                                <Group position="apart">
                                                                                        <Text size="xs" color="dimmed">Courses</Text>
                                                                                        <Badge size="sm" variant="light">
                                                                                                {metrics.totalCourses}
                                                                                        </Badge>
                                                                                </Group>
                                                                                <Group position="apart">
                                                                                        <Text size="xs" color="dimmed">Chapters</Text>
                                                                                        <Badge size="sm" variant="light">
                                                                                                {metrics.totalChapters}
                                                                                        </Badge>
                                                                                </Group>
                                                                                <Group position="apart">
                                                                                        <Text size="xs" color="dimmed">Assessments</Text>
                                                                                        <Badge size="sm" variant="light">
                                                                                                {metrics.totalAssessments}
                                                                                        </Badge>
                                                                                </Group>
                                                                        </Stack>
                                                                </Stack>
                                                        </Card>
                                                </Grid.Col>

                                                <Grid.Col span={12} md={8}>
                                                        <Card withBorder p="md" h="100%">
                                                                <Stack spacing="md">
                                                                        <Text weight={600} size="sm">Learning Patterns</Text>

                                                                        <Grid>
                                                                                <Grid.Col span={6}>
                                                                                        <Stack spacing="xs">
                                                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                                                        PREFERRED CONTENT
                                                                                                </Text>
                                                                                                <Badge
                                                                                                        color="blue"
                                                                                                        variant="light"
                                                                                                        leftSection={<IconBook size={12} />}
                                                                                                >
                                                                                                        {patterns.preferredContentType}
                                                                                                </Badge>
                                                                                        </Stack>
                                                                                </Grid.Col>

                                                                                <Grid.Col span={6}>
                                                                                        <Stack spacing="xs">
                                                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                                                        LEARNING STYLE
                                                                                                </Text>
                                                                                                <Badge
                                                                                                        color="violet"
                                                                                                        variant="light"
                                                                                                        leftSection={<IconBrain size={12} />}
                                                                                                >
                                                                                                        {patterns.learningStyle}
                                                                                                </Badge>
                                                                                        </Stack>
                                                                                </Grid.Col>

                                                                                <Grid.Col span={6}>
                                                                                        <Stack spacing="xs">
                                                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                                                        DIFFICULTY LEVEL
                                                                                                </Text>
                                                                                                <Badge
                                                                                                        color={getDifficultyColor(metrics.difficultyPreference)}
                                                                                                        variant="light"
                                                                                                >
                                                                                                        {metrics.difficultyPreference}
                                                                                                </Badge>
                                                                                        </Stack>
                                                                                </Grid.Col>

                                                                                <Grid.Col span={6}>
                                                                                        <Stack spacing="xs">
                                                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                                                        SESSION LENGTH
                                                                                                </Text>
                                                                                                <Badge
                                                                                                        color="teal"
                                                                                                        variant="light"
                                                                                                        leftSection={<IconClock size={12} />}
                                                                                                >
                                                                                                        {patterns.optimalSessionDuration}m
                                                                                                </Badge>
                                                                                        </Stack>
                                                                                </Grid.Col>
                                                                        </Grid>

                                                                        <Stack spacing="xs">
                                                                                <Text size="xs" color="dimmed" weight={500}>
                                                                                        PEAK LEARNING HOURS
                                                                                </Text>
                                                                                <Group spacing="xs">
                                                                                        {patterns.peakLearningHours.map((hour, index) => (
                                                                                                <Badge key={index} color="orange" variant="light" size="sm">
                                                                                                        {hour}
                                                                                                </Badge>
                                                                                        ))}
                                                                                </Group>
                                                                        </Stack>
                                                                </Stack>
                                                        </Card>
                                                </Grid.Col>
                                        </Grid>

                                        {/* Strengths and Challenges */}
                                        <Grid>
                                                <Grid.Col span={12} md={6}>
                                                        <Card withBorder p="md" h="100%">
                                                                <Stack spacing="md">
                                                                        <Group>
                                                                                <ThemeIcon color="green" variant="light" size="sm">
                                                                                        <IconTarget size={14} />
                                                                                </ThemeIcon>
                                                                                <Text weight={600} size="sm">Strong Topics</Text>
                                                                        </Group>

                                                                        <Stack spacing="xs">
                                                                                {patterns.strongTopics.map((topic, index) => (
                                                                                        <Group key={index} position="apart">
                                                                                                <Text size="sm">{topic}</Text>
                                                                                                <Badge color="green" variant="light" size="xs">
                                                                                                        Strong
                                                                                                </Badge>
                                                                                        </Group>
                                                                                ))}
                                                                        </Stack>
                                                                </Stack>
                                                        </Card>
                                                </Grid.Col>

                                                <Grid.Col span={12} md={6}>
                                                        <Card withBorder p="md" h="100%">
                                                                <Stack spacing="md">
                                                                        <Group>
                                                                                <ThemeIcon color="yellow" variant="light" size="sm">
                                                                                        <IconQuestionMark size={14} />
                                                                                </ThemeIcon>
                                                                                <Text weight={600} size="sm">Areas for Improvement</Text>
                                                                        </Group>

                                                                        <Stack spacing="xs">
                                                                                {patterns.challengingTopics.map((topic, index) => (
                                                                                        <Group key={index} position="apart">
                                                                                                <Text size="sm">{topic}</Text>
                                                                                                <Badge color="yellow" variant="light" size="xs">
                                                                                                        Focus
                                                                                                </Badge>
                                                                                        </Group>
                                                                                ))}
                                                                        </Stack>
                                                                </Stack>
                                                        </Card>
                                                </Grid.Col>
                                        </Grid>
                                </>
                        )}
                </Stack>
        );
};

export default LearningAnalytics;