import React, { useState, useEffect } from 'react';
import {
        Card,
        Title,
        Text,
        Stack,
        Group,
        Badge,
        Button,
        Loader,
        Alert,
        Progress,
        Box,
        Grid,
        ThemeIcon,
        ActionIcon,
        Tooltip,
        useMantineTheme
} from '@mantine/core';
import {
        IconBrain,
        IconTarget,
        IconTrendingUp,
        IconBook,
        IconClock,
        IconStar,
        IconArrowRight,
        IconRefresh,
        IconInfoCircle,
        IconChevronRight
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import dashboardService from '../api/dashboardService';

const PersonalizedRecommendations = ({ userId, onRecommendationClick }) => {
        const [dashboardData, setDashboardData] = useState(null);
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState(null);
        const [refreshing, setRefreshing] = useState(false);

        const theme = useMantineTheme();
        const navigate = useNavigate();

        useEffect(() => {
                if (userId) {
                        fetchDashboardData();
                }
        }, [userId]);

        const fetchDashboardData = async () => {
                try {
                        setLoading(true);
                        setError(null);
                        const data = await dashboardService.getPersonalizedDashboard();
                        setDashboardData(data.dashboard_data);
                } catch (err) {
                        setError('Failed to load personalized recommendations');
                        console.error('Error fetching dashboard data:', err);
                } finally {
                        setLoading(false);
                }
        };

        const handleRefresh = async () => {
                setRefreshing(true);
                await fetchDashboardData();
                setRefreshing(false);
        };

        const handleRecommendationClick = (recommendation) => {
                if (onRecommendationClick) {
                        onRecommendationClick(recommendation);
                } else {
                        navigate(`/dashboard/courses/${recommendation.course_id}`);
                }
        };

        const getDifficultyColor = (difficulty) => {
                switch (difficulty) {
                        case 'beginner': return 'green';
                        case 'intermediate': return 'yellow';
                        case 'advanced': return 'red';
                        default: return 'gray';
                }
        };

        const getScoreColor = (score) => {
                if (score >= 0.8) return 'green';
                if (score >= 0.6) return 'yellow';
                return 'orange';
        };

        if (loading) {
                return (
                        <Card withBorder radius="md" p="lg">
                                <Group position="center" spacing="md">
                                        <Loader size="sm" />
                                        <Text color="dimmed">Loading personalized recommendations...</Text>
                                </Group>
                        </Card>
                );
        }

        if (error) {
                return (
                        <Alert
                                icon={<IconInfoCircle size={16} />}
                                title="Recommendations Unavailable"
                                color="yellow"
                                variant="outline"
                        >
                                <Text size="sm" mb="md">{error}</Text>
                                <Button size="xs" variant="light" onClick={handleRefresh}>
                                        Try Again
                                </Button>
                        </Alert>
                );
        }

        if (!dashboardData?.personalization_available) {
                return (
                        <Card withBorder radius="md" p="lg">
                                <Group position="apart" mb="md">
                                        <Group spacing="sm">
                                                <ThemeIcon color="blue" variant="light">
                                                        <IconBrain size={20} />
                                                </ThemeIcon>
                                                <Title order={4}>Personalized Recommendations</Title>
                                        </Group>
                                </Group>

                                <Alert
                                        icon={<IconInfoCircle size={16} />}
                                        title="Building Your Learning Profile"
                                        color="blue"
                                        variant="light"
                                >
                                        <Text size="sm">
                                                Complete more learning activities to unlock personalized recommendations
                                                tailored to your learning style and preferences.
                                        </Text>
                                </Alert>
                        </Card>
                );
        }

        const { recommendations, user_profile, personalized_metrics, next_actions } = dashboardData;

        return (
                <Stack spacing="lg">
                        {/* Learning Profile Summary */}
                        {user_profile && (
                                <Card withBorder radius="md" p="lg">
                                        <Group position="apart" mb="md">
                                                <Group spacing="sm">
                                                        <ThemeIcon color="teal" variant="light">
                                                                <IconTarget size={20} />
                                                        </ThemeIcon>
                                                        <Title order={4}>Your Learning Profile</Title>
                                                </Group>
                                                <ActionIcon
                                                        variant="subtle"
                                                        onClick={handleRefresh}
                                                        loading={refreshing}
                                                >
                                                        <IconRefresh size={16} />
                                                </ActionIcon>
                                        </Group>

                                        <Grid gutter="md">
                                                <Grid.Col span={6}>
                                                        <Stack spacing="xs">
                                                                <Text size="sm" weight={500}>Learning Style</Text>
                                                                <Badge
                                                                        color="blue"
                                                                        variant="light"
                                                                        size="lg"
                                                                        leftSection={<IconBrain size={14} />}
                                                                >
                                                                        {user_profile.learning_style || 'Analyzing...'}
                                                                </Badge>
                                                        </Stack>
                                                </Grid.Col>

                                                <Grid.Col span={6}>
                                                        <Stack spacing="xs">
                                                                <Text size="sm" weight={500}>Completion Rate</Text>
                                                                <Group spacing="xs">
                                                                        <Progress
                                                                                value={user_profile.completion_rate * 100}
                                                                                size="lg"
                                                                                color={getScoreColor(user_profile.completion_rate)}
                                                                                style={{ flex: 1 }}
                                                                        />
                                                                        <Text size="sm" weight={500}>
                                                                                {Math.round(user_profile.completion_rate * 100)}%
                                                                        </Text>
                                                                </Group>
                                                        </Stack>
                                                </Grid.Col>

                                                {user_profile.strong_topics?.length > 0 && (
                                                        <Grid.Col span={12}>
                                                                <Stack spacing="xs">
                                                                        <Text size="sm" weight={500}>Strong Areas</Text>
                                                                        <Group spacing="xs">
                                                                                {user_profile.strong_topics.slice(0, 3).map((topic, index) => (
                                                                                        <Badge key={index} color="green" variant="light" size="sm">
                                                                                                {topic}
                                                                                        </Badge>
                                                                                ))}
                                                                        </Group>
                                                                </Stack>
                                                        </Grid.Col>
                                                )}
                                        </Grid>
                                </Card>
                        )}

                        {/* Course Recommendations */}
                        {recommendations?.length > 0 && (
                                <Card withBorder radius="md" p="lg">
                                        <Group position="apart" mb="md">
                                                <Group spacing="sm">
                                                        <ThemeIcon color="blue" variant="light">
                                                                <IconStar size={20} />
                                                        </ThemeIcon>
                                                        <Title order={4}>Recommended for You</Title>
                                                </Group>
                                                <Badge color="blue" variant="light">
                                                        {recommendations.length} courses
                                                </Badge>
                                        </Group>

                                        <Stack spacing="md">
                                                {recommendations.slice(0, 3).map((rec, index) => (
                                                        <motion.div
                                                                key={rec.course_id}
                                                                initial={{ opacity: 0, y: 20 }}
                                                                animate={{ opacity: 1, y: 0 }}
                                                                transition={{ delay: index * 0.1 }}
                                                        >
                                                                <Card
                                                                        withBorder
                                                                        radius="sm"
                                                                        p="md"
                                                                        style={{
                                                                                cursor: 'pointer',
                                                                                transition: 'transform 0.2s ease, box-shadow 0.2s ease'
                                                                        }}
                                                                        onClick={() => handleRecommendationClick(rec)}
                                                                        sx={{
                                                                                '&:hover': {
                                                                                        transform: 'translateY(-2px)',
                                                                                        boxShadow: theme.shadows.md
                                                                                }
                                                                        }}
                                                                >
                                                                        <Group position="apart" align="flex-start">
                                                                                <Box style={{ flex: 1 }}>
                                                                                        <Group position="apart" mb="xs">
                                                                                                <Text weight={600} size="md" lineClamp={1}>
                                                                                                        {rec.title}
                                                                                                </Text>
                                                                                                <Badge
                                                                                                        color={getDifficultyColor(rec.recommended_difficulty)}
                                                                                                        variant="light"
                                                                                                        size="sm"
                                                                                                >
                                                                                                        {rec.recommended_difficulty}
                                                                                                </Badge>
                                                                                        </Group>

                                                                                        <Text size="sm" color="dimmed" mb="xs" lineClamp={2}>
                                                                                                {rec.reason}
                                                                                        </Text>

                                                                                        <Group spacing="md">
                                                                                                <Group spacing="xs">
                                                                                                        <IconClock size={14} color={theme.colors.gray[6]} />
                                                                                                        <Text size="xs" color="dimmed">
                                                                                                                ~{rec.estimated_completion_time} min
                                                                                                        </Text>
                                                                                                </Group>

                                                                                                <Group spacing="xs">
                                                                                                        <IconTrendingUp size={14} color={theme.colors.blue[6]} />
                                                                                                        <Text size="xs" color="dimmed">
                                                                                                                {Math.round(rec.recommendation_score * 100)}% match
                                                                                                        </Text>
                                                                                                </Group>
                                                                                        </Group>
                                                                                </Box>

                                                                                <ActionIcon variant="subtle" color="blue">
                                                                                        <IconChevronRight size={16} />
                                                                                </ActionIcon>
                                                                        </Group>
                                                                </Card>
                                                        </motion.div>
                                                ))}
                                        </Stack>

                                        {recommendations.length > 3 && (
                                                <Group position="center" mt="md">
                                                        <Button
                                                                variant="subtle"
                                                                rightIcon={<IconArrowRight size={16} />}
                                                                onClick={() => navigate('/dashboard/recommendations')}
                                                        >
                                                                View All Recommendations
                                                        </Button>
                                                </Group>
                                        )}
                                </Card>
                        )}

                        {/* Next Actions */}
                        {next_actions?.length > 0 && (
                                <Card withBorder radius="md" p="lg">
                                        <Group position="apart" mb="md">
                                                <Group spacing="sm">
                                                        <ThemeIcon color="orange" variant="light">
                                                                <IconTarget size={20} />
                                                        </ThemeIcon>
                                                        <Title order={4}>Continue Learning</Title>
                                                </Group>
                                        </Group>

                                        <Stack spacing="sm">
                                                {next_actions.slice(0, 2).map((action, index) => (
                                                        <Card
                                                                key={index}
                                                                withBorder
                                                                radius="sm"
                                                                p="sm"
                                                                style={{ cursor: 'pointer' }}
                                                                onClick={() => {
                                                                        if (action.course_id) {
                                                                                navigate(`/dashboard/courses/${action.course_id}`);
                                                                        } else if (action.type === 'create_course') {
                                                                                navigate('/dashboard/create-course');
                                                                        }
                                                                }}
                                                        >
                                                                <Group position="apart">
                                                                        <Box>
                                                                                <Text weight={500} size="sm">{action.title}</Text>
                                                                                <Text size="xs" color="dimmed">{action.description}</Text>
                                                                                {action.progress !== undefined && (
                                                                                        <Progress
                                                                                                value={action.progress * 100}
                                                                                                size="xs"
                                                                                                mt="xs"
                                                                                                color="orange"
                                                                                                style={{ width: 100 }}
                                                                                        />
                                                                                )}
                                                                        </Box>
                                                                        <Badge
                                                                                color={action.priority === 'high' ? 'red' : action.priority === 'medium' ? 'yellow' : 'gray'}
                                                                                variant="light"
                                                                                size="sm"
                                                                        >
                                                                                {action.priority}
                                                                        </Badge>
                                                                </Group>
                                                        </Card>
                                                ))}
                                        </Stack>
                                </Card>
                        )}

                        {/* Personalized Goals */}
                        {personalized_metrics?.personalized_goals?.length > 0 && (
                                <Card withBorder radius="md" p="lg">
                                        <Group position="apart" mb="md">
                                                <Group spacing="sm">
                                                        <ThemeIcon color="green" variant="light">
                                                                <IconTrendingUp size={20} />
                                                        </ThemeIcon>
                                                        <Title order={4}>Your Goals</Title>
                                                </Group>
                                        </Group>

                                        <Stack spacing="md">
                                                {personalized_metrics.personalized_goals.map((goal, index) => (
                                                        <Box key={index}>
                                                                <Group position="apart" mb="xs">
                                                                        <Text weight={500} size="sm">{goal.title}</Text>
                                                                        <Text size="xs" color="dimmed">
                                                                                {Math.round(goal.current * 100)}% / {Math.round(goal.target * 100)}%
                                                                        </Text>
                                                                </Group>
                                                                <Progress
                                                                        value={(goal.current / goal.target) * 100}
                                                                        size="sm"
                                                                        color="green"
                                                                        mb="xs"
                                                                />
                                                                <Text size="xs" color="dimmed">{goal.suggestion}</Text>
                                                        </Box>
                                                ))}
                                        </Stack>
                                </Card>
                        )}
                </Stack>
        );
};

export default PersonalizedRecommendations;