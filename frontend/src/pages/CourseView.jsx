import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Container,
  Title,
  Text,
  Card,
  Group,
  SimpleGrid,
  Progress,
  Badge,
  Button,
  ThemeIcon,
  Loader,
  Alert,
  Box,
  Paper,
  Image,
  Grid,
  Divider,
  RingProgress,
  Overlay,
  Modal,
  ActionIcon,
  Stack,
} from '@mantine/core';
import {
  IconAlertCircle,
  IconCircleCheck,
  IconClock,
  IconArrowRight,
  IconBrain,
  IconTrophy,
  IconArrowBack,
  IconCheck,
  IconChevronRight,
  IconX,
  IconPlayerPlay,
} from '@tabler/icons-react';
import { courseService } from '../api/courseService';
import { useUmamiTracker } from '../components/UmamiTracker';

function CourseView() {
  const { t } = useTranslation('courseView');
  const { courseId } = useParams();
  const navigate = useNavigate();
  const {
    trackEvent,
    trackCourseStart,
    trackContentInteraction,
    trackTimeSpent
  } = useUmamiTracker();

  const [course, setCourse] = useState(null);
  const [chapters, setChapters] = useState([]); // ADDED: Dedicated state for chapters
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // NEW: State for first-time video popup
  const [showVideoPopup, setShowVideoPopup] = useState(false);
  const [hasSeenVideo, setHasSeenVideo] = useState(false);
  const [contentReady, setContentReady] = useState(false);

  const [creationProgressUI, setCreationProgressUI] = useState({
    statusText: t('creation.statusInitializing'),
    percentage: 0,
    chaptersCreated: 0,
    estimatedTotal: 0,
  });

  // NEW: Check localStorage on mount
  useEffect(() => {
    const hasSeenVideoFlag = localStorage.getItem('hasSeenFirstCourseVideo');
    if (hasSeenVideoFlag === 'true') {
      setHasSeenVideo(true);
    }
  }, []);

  // NEW: Monitor when course content becomes ready
  useEffect(() => {
    if (course && course.title && course.description && course.image_url &&
      course.title !== 'None' && course.description !== 'None') {
      setContentReady(true);
    }
  }, [course]);

  // NEW: Show video popup after content is ready (with 2 second delay)
  useEffect(() => {
    if (contentReady && !hasSeenVideo && course?.status === 'CourseStatus.CREATING') {
      const timer = setTimeout(() => {
        setShowVideoPopup(true);
        // Mark as seen when popup is shown
        localStorage.setItem('hasSeenFirstCourseVideo', 'true');
        setHasSeenVideo(true);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [contentReady, hasSeenVideo, course?.status]);

  // NEW: Function to close video popup
  const closeVideoPopup = () => {
    setShowVideoPopup(false);
  };

  // Initial data fetch
  useEffect(() => {
    if (!courseId) {
      setError(t('errors.invalidCourseId'));
      setLoading(false);
      return;
    }

    const fetchInitialCourseData = async () => {
      try {
        setLoading(true);
        console.log('Fetching initial course data for ID:', courseId);
        const [courseData, currentChaptersData] = await Promise.all([ // CHANGED: Renamed variable for clarity
          courseService.getCourseById(courseId),
          courseService.getCourseChapters(courseId)
        ]);
        const currentChapters = currentChaptersData || []; // Ensure chapters is an array

        setCourse(courseData);
        setChapters(currentChapters); // ADDED: Populate the new chapters state
        setError(null);

        // Track course start with difficulty level
        trackCourseStart(courseId, courseData.difficulty || 'intermediate');

        // Track course view for additional analytics
        trackEvent('course_view', {
          course_id: courseId,
          course_name: courseData.title,
          course_status: courseData.status,
          chapter_count: currentChapters.length
        });

        // Initialize creationProgressUI if course is in creating state
        if (courseData.status === 'CourseStatus.CREATING') {
          const totalChapters = courseData.chapter_count || 0;
          const currentChapters_length = currentChapters === null ? 0 : currentChapters.filter(chapter => chapter.id !== null).length;
          const progressPercent = totalChapters > 0 ? Math.round((currentChapters_length / totalChapters) * 100) : 0;

          setCreationProgressUI({
            statusText: t('creation.statusCreatingChapters', {
              chaptersCreated: currentChapters_length,
              totalChapters: totalChapters || t('creation.unknownTotal')
            }),
            percentage: progressPercent,
            chaptersCreated: currentChapters_length,
            estimatedTotal: totalChapters,
          });
        }
        console.log('Initial data fetched:', courseData, 'Chapters:', currentChapters);
      } catch (err) {
        setError(t('errors.loadFailed'));
        console.error('Error fetching initial course:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialCourseData();
  }, [courseId, t]);

  // Polling effect for course creation
  useEffect(() => {
    // Only poll if course exists and is in CREATING status
    if (!courseId || !course || course.status !== 'CourseStatus.CREATING') {
      return;
    }

    console.log('Starting polling for course ID:', courseId, 'current status:', course.status);
    const pollInterval = setInterval(async () => {
      try {
        const [polledData, polledChaptersData] = await Promise.all([ // CHANGED: Renamed variable
          courseService.getCourseById(courseId),
          courseService.getCourseChapters(courseId)
        ]);
        const currentChapters = polledChaptersData || [];

        console.log('Polled course data:', polledData, 'Polled chapters:', currentChapters);
        setCourse(polledData);         // Update the main course state
        setChapters(currentChapters);  // ADDED: Update the chapters state on each poll

        const totalChapters = polledData.chapter_count || 0;

        const currentChapters_length = currentChapters === null ? 0 : currentChapters.filter(chapter => chapter.id !== null).length;
        const progressPercent = totalChapters > 0 ? Math.round((currentChapters_length / totalChapters) * 100) : 0;

        if (polledData.status === 'CourseStatus.FINISHED') {
          setCreationProgressUI({
            statusText: t('creation.statusComplete'),
            percentage: 100,
            chaptersCreated: currentChapters_length,
            estimatedTotal: totalChapters,
          });
          console.log('Course creation completed. Stopping poll.');
          clearInterval(pollInterval);
        } else if (polledData.status === 'CourseStatus.CREATING') {
          setCreationProgressUI({
            statusText: t('creation.statusCreatingChapters', {
              chaptersCreated: currentChapters_length,
              totalChapters: totalChapters || t('creation.unknownTotal')
            }),
            percentage: progressPercent,
            chaptersCreated: currentChapters_length,
            estimatedTotal: totalChapters,
          });
        } else {
          console.log('Course status changed to:', polledData.status, '. Stopping poll.');
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error('Error polling course data:', err);
      }
    }, 2000);

    return () => {
      console.log('Cleaning up poll interval for course ID:', courseId);
      clearInterval(pollInterval);
    };
  }, [course, courseId, t]); // The 'chapters' state is not needed here as it's an outcome, not a trigger for this effect.

  // Learning progress calculation
  const { learningPercentage, actualCompletedLearningChapters, totalCourseChaptersForLearning } = useMemo(() => {
    // CHANGED: This logic now uses the separate `chapters` state
    if (!course || !chapters) {
      return { learningPercentage: 0, actualCompletedLearningChapters: 0, totalCourseChaptersForLearning: 0 };
    }
    const completedCount = chapters.filter(ch => ch.is_completed).length;
    // We still get the total count from the main course object, which is good practice.
    const totalCount = course.chapter_count || chapters.length || 0;
    const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
    return {
      learningPercentage: percentage,
      actualCompletedLearningChapters: completedCount,
      totalCourseChaptersForLearning: totalCount
    };
  }, [course, chapters]); // CHANGED: Dependency array now includes `chapters`

  if (loading && !course) {
    return (
      <Container
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '50vh',
          textAlign: 'center',
          gap: '1rem'
        }}
      >
        <Loader size="xl" variant="dots" />
        <Text size="lg" color="dimmed">
          {t('loadingCourseDetails')}
        </Text>
      </Container>
    );
  }

  if (error && !course) {
    return (
      <Container size="lg" py="xl">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title={t('errors.genericTitle')}
          color="red"
          mb="lg"
        >
          {error}
        </Alert>
      </Container>
    );
  }

  const showNonCriticalError = error && course;

  return (
    <Container size="lg" py="xl">
      {/* NEW: First-time video popup */}
      <Modal
        opened={showVideoPopup}
        onClose={closeVideoPopup}
        fullScreen
        padding={0}
        withCloseButton={false}
        overlayProps={{
          color: '#000',
          opacity: 0.95,
        }}
        styles={{
          content: {
            background: 'transparent',
          },
          body: {
            padding: 0,
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          },
        }}
      >
        <Box
          sx={{
            position: 'relative',
            width: '90%',
            maxWidth: '1000px',
            height: '80%',
            maxHeight: '600px',
          }}
        >
          {/* Close button */}
          <ActionIcon
            size="xl"
            radius="xl"
            color="white"
            variant="filled"
            onClick={closeVideoPopup}
            sx={{
              position: 'absolute',
              top: -60,
              right: 0,
              zIndex: 1000,
              background: 'rgba(255, 255, 255, 0.9)',
              color: '#000',
              '&:hover': {
                background: 'rgba(255, 255, 255, 1)',
              },
            }}
          >
            <IconX size={24} />
          </ActionIcon>

          {/* Video container */}
          <Box
            sx={{
              width: '100%',
              height: '100%',
              position: 'relative',
              borderRadius: '12px',
              overflow: 'hidden',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
            }}
          >
            <iframe
              width="100%"
              height="100%"
              src="https://www.youtube.com/embed/I0Nb0O1pSxM"
              title="Welcome Video"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              style={{
                borderRadius: '12px',
              }}
            />
          </Box>

          {/* Welcome text above video */}
          <Box
            sx={{
              position: 'absolute',
              top: -120,
              left: 0,
              right: 0,
              textAlign: 'center',
            }}
          >
            <Stack spacing="xs">
              <Group position="center" spacing="xs">
                <ThemeIcon size="lg" radius="xl" color="teal" variant="filled">
                  <IconPlayerPlay size={20} />
                </ThemeIcon>
                <Title order={2} color="white" weight={600}>
                  Welcome to your AI Learning Journey!
                </Title>
              </Group>
              <Text color="rgba(255, 255, 255, 0.8)" size="lg">
                Watch this quick intro to get the most out of your personalized course
              </Text>
            </Stack>
          </Box>
        </Box>
      </Modal>

      {showNonCriticalError && (
        <Alert
          icon={<IconAlertCircle size={16} />}
          title={t('errors.genericTitle')}
          color="orange"
          mb="lg"
          withCloseButton
          onClose={() => setError(null)}
        >
          {error}
        </Alert>
      )}

      {course?.status === "CourseStatus.CREATING" && (
        <Paper
          radius="md"
          p="xl"
          withBorder
          mb="xl"
          sx={(theme) => ({
            position: 'relative',
            overflow: 'hidden',
            backgroundColor: theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)',
            border: theme.colorScheme === 'dark' 
              ? '1px solid rgba(139, 92, 246, 0.2)' 
              : '1px solid rgba(0, 0, 0, 0.06)',
            '&:hover': {
              borderColor: theme.colorScheme === 'dark' 
                ? 'rgba(139, 92, 246, 0.3)' 
                : 'rgba(0, 0, 0, 0.1)',
            },
          })}
        >
          <Box
            sx={(theme) => ({
              position: 'absolute',
              top: 0,
              right: 0,
              width: '50%',
              height: '100%',
              opacity: 0.05,
              backgroundImage: (course && course.image_url) ? `url("${course.image_url}")` : 'url("https://cdn-icons-png.flaticon.com/512/8136/8136031.png")',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              [theme.fn.smallerThan('md')]: {
                width: '100%',
              },
            })}
          />

          <Group position="apart" mb="xl">
            <Box>
              <Badge color="blue" variant="filled" size="lg" radius="sm" mb="sm">
                <Group spacing="xs">
                  <IconBrain size={16} />
                  <span>{t('creation.aiInActionBadge')}</span>
                </Group>
              </Badge>
              <Title
                order={2}
                sx={{
                  fontWeight: 800,
                  fontSize: '1.8rem',
                }}
              >
                {t('creation.title')}
              </Title>
            </Box>

            <ThemeIcon
              size={60}
              radius="xl"
              color={creationProgressUI.percentage === 100 ? "green" : "cyan"}
              variant="light"
              sx={{ border: '4px solid #f0f0f0' }}
            >
              {creationProgressUI.percentage === 100 ?
                <IconCheck size={30} /> :
                <IconClock size={30} />
              }
            </ThemeIcon>
          </Group>

          <Box mb="xl">
            <Group position="apart" mb="xs">
              <Text size="sm" weight={600} color="dimmed">{t('creation.progressLabel')}</Text>
              <Text size="sm" weight={700}>{creationProgressUI.percentage}%</Text>
            </Group>

            <Progress
              value={creationProgressUI.percentage}
              size="lg"
              radius="xl"
              color={creationProgressUI.percentage === 100 ? 'green' : 'teal'}
              animate={creationProgressUI.percentage > 0 && creationProgressUI.percentage < 100}
              sx={{
                height: 12,
                '& .mantine-Progress-bar': creationProgressUI.percentage !== 100 ? {
                  background: 'linear-gradient(90deg, #36D1DC 0%, #5B86E5 100%)'
                } : {}
              }}
            />
          </Box>

          <Box
            py="md"
            px="lg"
            mt="md"
            sx={(theme) => ({
              backgroundColor: theme.colorScheme === 'dark' ?
                theme.colors.dark[7] :
                theme.fn.rgba(theme.colors.gray[0], 0.7),
              borderRadius: theme.radius.md,
              position: 'relative',
              zIndex: 2,
            })}
          >
            <Text align="center" size="lg" weight={600} mb="xs" color={creationProgressUI.percentage === 100 ? 'teal' : undefined}>
              {t('creation.currentStatusLabel')} {creationProgressUI.statusText}
            </Text>

            {creationProgressUI.percentage > 0 && creationProgressUI.percentage < 100 && (
              <Text color="dimmed" size="sm" align="center">
                {t('creation.description')}
              </Text>
            )}

            {creationProgressUI.percentage === 100 && (
              <Group position="center" mt="md">
                <Button
                  variant="gradient"
                  gradient={{ from: 'teal', to: 'green' }}
                  leftIcon={<IconArrowRight size={16} />}
                  onClick={() => window.location.reload()}
                >
                  {t('buttons.viewCompletedCourse')}
                </Button>
              </Group>
            )}
          </Box>

          {creationProgressUI.chaptersCreated > 0 && (
            <Group position="center" mt="md" spacing="xl">
              <Box sx={{ textAlign: 'center' }}>
                <Text size="xl" weight={700}>{creationProgressUI.chaptersCreated}</Text>
                <Text size="xs" color="dimmed">{t('creation.chaptersCreatedLabel_one')}</Text>
              </Box>

              <Divider orientation="vertical" />

              <Box sx={{ textAlign: 'center' }}>
                <Text size="xl" weight={700}>{creationProgressUI.estimatedTotal || t('creation.calculating')}</Text>
                <Text size="xs" color="dimmed">{t('creation.estimatedTotalLabel')}</Text>
              </Box>

              <Divider orientation="vertical" />

              <Box sx={{ textAlign: 'center' }}>
                <Text size="xl" weight={700}>{course?.total_time_hours || t('creation.calculating')} hrs</Text>
                <Text size="xs" color="dimmed">{t('creation.learningTimeLabel')}</Text>
              </Box>
            </Group>
          )}
        </Paper>
      )}

      {course && (
        <>
          <Paper
            radius="xl"
            p={0}
            withBorder
            mb="xl"
            className="card-modern card-glass transition-all duration-300"
            sx={(theme) => ({
              position: 'relative',
              overflow: 'hidden',
              background: theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: theme.colorScheme === 'dark' 
                ? '1px solid rgba(139, 92, 246, 0.2)' 
                : '1px solid rgba(0, 0, 0, 0.06)',
              boxShadow: theme.colorScheme === 'dark'
                ? '0 8px 32px rgba(0, 0, 0, 0.2)'
                : '0 8px 32px rgba(0, 0, 0, 0.05)',
            })}
          >
            <Grid gutter={0}>
              <Grid.Col md={7}>
                <Box p="xl">
                  <Group position="apart">
                    <Button
                      variant="subtle"
                      leftIcon={<IconArrowBack size={16} />}
                      onClick={() => navigate('/dashboard')}
                      mb="md"
                    >
                      {t('buttons.backToDashboard')}
                    </Button>

                    {course.status === "CourseStatus.CREATING" ? (
                      <Badge size="lg" color="blue" variant="filled" px="md" py="sm">
                        <Group spacing="xs" noWrap>
                          <IconClock size={16} />
                          {t('creation.statusCreatingCourse')}
                        </Group>
                      </Badge>
                    ) : (
                      <Badge size="lg" color="teal" variant="filled" px="md" py="sm">
                        {t('progress.percentageComplete', { percentage: learningPercentage })}
                      </Badge>
                    )}
                  </Group>

                  <Title
                    order={1}
                    mb="xs"
                    sx={(theme) => ({
                      fontSize: '2.5rem',
                      fontWeight: 900,
                      backgroundImage: theme.colorScheme === 'dark'
                        ? `linear-gradient(45deg, ${theme.colors.teal[4]}, ${theme.colors.cyan[6]})`
                        : `linear-gradient(45deg, ${theme.colors.teal[7]}, ${theme.colors.cyan[5]})`,
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    })}
                  >
                    {course.title && course.title != 'None' ? course.title : t('courseLoadingTitle')}
                  </Title>

                  <Text size="md" mb="lg" color="dimmed" sx={{ maxWidth: '600px' }}>
                    {course.description && course.description != 'None' ? course.description : t('courseLoadingDescription')}
                  </Text>

                  <Group position="apart" mb="lg">
                    <Box>
                      <Text size="sm" weight={500} color="dimmed">{t('progress.courseProgressLabel')}</Text>
                      <Group spacing="xs" mt="xs">
                        <RingProgress
                          size={60}
                          thickness={4}
                          roundCaps
                          sections={[{ value: learningPercentage, color: 'teal' }]}
                          label={
                            <Text size="xs" align="center" weight={700}>
                              {learningPercentage}%
                            </Text>
                          }
                        />
                        <div>
                          <Text size="md" weight={700}>{actualCompletedLearningChapters} of {totalCourseChaptersForLearning}</Text>
                          <Text size="xs" color="dimmed">{t('progress.chaptersCompletedStats', { completedChapters: actualCompletedLearningChapters, totalChapters: totalCourseChaptersForLearning })}</Text>
                        </div>
                      </Group>
                    </Box>

                    <Box>
                      <Text size="sm" weight={500} color="dimmed">{t('progress.estimatedTimeLabel')}</Text>
                      <Group spacing="xs" mt="xs">
                        <ThemeIcon size="lg" radius="md" color="teal" variant="light">
                          <IconClock size={20} />
                        </ThemeIcon>
                        <div>
                          <Text size="md" weight={700}>{course.total_time_hours || "..."} hours</Text>
                        </div>
                      </Group>
                    </Box>
                  </Group>

                  {course.status !== "CourseStatus.CREATING" && chapters.length > 0 && chapters[0]?.id !== null && (
                    <Button
                      size="md"
                      variant="gradient"
                      gradient={{ from: 'teal', to: 'cyan' }}
                      rightIcon={<IconChevronRight size={16} />}
                      onClick={() => {
                        // Track content interaction for course navigation
                        trackContentInteraction(
                          courseId,
                          'interactive',
                          0,
                          {
                            chapter_id: chapters[0]?.id,
                            chapter_name: chapters[0]?.title,
                            navigation_method: 'start_button'
                          }
                        );

                        trackEvent('chapter_start', {
                          course_id: courseId,
                          chapter_id: chapters[0]?.id,
                          chapter_name: chapters[0]?.title,
                          navigation_method: 'start_button'
                        });
                        navigate(`/dashboard/courses/${courseId}/chapters/${chapters[0]?.id}`);
                      }}
                      mt="md"
                    >
                      {learningPercentage > 0 ? t('buttons.continueLearning') : t('buttons.startLearning')}
                    </Button>
                  )}
                </Box>
              </Grid.Col>

              <Grid.Col md={5} sx={{ position: 'relative' }}>
                <Image
                  src={course.image_url || "https://storage.googleapis.com/proudcity/mebanenc/uploads/2021/03/placeholder-image.png"}
                  height={400}
                  sx={{
                    objectFit: 'cover',
                    height: '100%',
                  }}
                  alt={course.title || t('courseImageAlt')}
                />
                <Box
                  sx={(theme) => ({
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '50%',
                    background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
                    display: 'flex',
                    alignItems: 'flex-end',
                    padding: theme.spacing.md,
                  })}
                >
                  <Group spacing="xs">
                    <ThemeIcon size={32} radius="xl" color="teal" variant="filled">
                      <IconBrain size={18} />
                    </ThemeIcon>
                    <div>
                      <Text color="white" weight={600}>{t('aiGeneratedCourseLabel')}</Text>
                      <Text color="white" opacity={0.7} size="xs">
                        {t('personalizedLearningPathLabel')}
                      </Text>
                    </div>
                  </Group>
                </Box>
              </Grid.Col>
            </Grid>
          </Paper>

          <Group position="apart" align="center" mb="xl">
            <Box>
              <Title
                order={2}
                sx={(theme) => ({
                  fontWeight: 700,
                  color: theme.colorScheme === 'dark' ? theme.white : theme.black,
                })}
              >
                {t('learningJourneyLabel')}
              </Title>
              <Text color="dimmed">
                {t('followChaptersLabel')}
              </Text>
            </Box>

            {course.status !== "CourseStatus.CREATING" && chapters.length > 0 && (
              <Group spacing="xs">
                <ThemeIcon
                  size={34}
                  radius="xl"
                  color={actualCompletedLearningChapters === totalCourseChaptersForLearning && totalCourseChaptersForLearning > 0 ? "green" : "teal"}
                  variant={actualCompletedLearningChapters === totalCourseChaptersForLearning && totalCourseChaptersForLearning > 0 ? "filled" : "light"}
                >
                  {actualCompletedLearningChapters === totalCourseChaptersForLearning && totalCourseChaptersForLearning > 0 ?
                    <IconTrophy size={18} /> :
                    <IconBrain size={18} />
                  }
                </ThemeIcon>
                <div>
                  <Text weight={600} size="sm">
                    {actualCompletedLearningChapters === totalCourseChaptersForLearning && totalCourseChaptersForLearning > 0 ?
                      t('courseMasteredLabel') :
                      `${actualCompletedLearningChapters === 0 ? t('beginLearningLabel') : t('continueLearningLabel')}`}
                  </Text>
                  <Text size="xs" color="dimmed">
                    {actualCompletedLearningChapters === totalCourseChaptersForLearning && totalCourseChaptersForLearning > 0 ?
                      t('congratulationsLabel') :
                      t('progress.chaptersCompletedText', { completedChapters: actualCompletedLearningChapters, totalChapters: totalCourseChaptersForLearning })}
                  </Text>
                </div>
              </Group>
            )}
          </Group>

          {course.status === "CourseStatus.CREATING" && chapters.length === 0 && creationProgressUI.estimatedTotal === 0 && (
            <Paper withBorder p="xl" radius="md" mb="lg" sx={(theme) => ({
              backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[0],
              textAlign: 'center',
            })}>
              <Loader size="md" mb="md" mx="auto" />
              <Title order={3} mb="sm">{t('creation.buildingCourseLabel')}</Title>
              <Text color="dimmed" size="sm" maw={400} mx="auto">
                {t('creation.creatingHighQualityContentLabel')}
              </Text>
            </Paper>
          )}

          <SimpleGrid
            cols={3}
            spacing="xl"
            breakpoints={[
              { maxWidth: 'md', cols: 2 },
              { maxWidth: 'sm', cols: 1 },
            ]}
          >
            {chapters.map((chapter, index) => {
              const isCompleted = chapter.is_completed;
              const chapterProgress = isCompleted ? 100 : 0;

              return (
                <Card
                  key={chapter.id || index}
                  shadow="sm"
                  padding="xl"
                  radius="xl"
                  withBorder
                  className="card-modern card-glass card-hoverable transition-all duration-300"
                  sx={(theme) => ({
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                    background: theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(20px)',
                    border: theme.colorScheme === 'dark' 
                      ? '1px solid rgba(139, 92, 246, 0.2)' 
                      : '1px solid rgba(0, 0, 0, 0.06)',
                    '&:hover': {
                      borderColor: theme.colorScheme === 'dark' 
                        ? 'rgba(139, 92, 246, 0.3)' 
                        : 'rgba(0, 0, 0, 0.1)',
                    },
                    cursor: 'pointer',
                    overflow: 'hidden',
                    minHeight: '280px',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 25px 50px -12px rgba(139, 92, 246, 0.25)',
                      borderColor: 'rgba(139, 92, 246, 0.4)',
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)',
                      opacity: 0,
                      transition: 'opacity 0.4s ease',
                      zIndex: 0,
                    },
                    '&:hover::before': {
                      opacity: 1,
                    },
                  })}
                  onClick={() => {
                    if (chapter.id) {
                      trackContentInteraction(
                        courseId,
                        'interactive',
                        0,
                        {
                          chapter_id: chapter.id,
                          chapter_name: chapter.title || chapter.caption,
                          navigation_method: 'chapter_card'
                        }
                      );

                      trackEvent('chapter_start', {
                        course_id: courseId,
                        chapter_id: chapter.id,
                        chapter_name: chapter.title || chapter.caption,
                        navigation_method: 'chapter_card'
                      });
                      navigate(`/dashboard/courses/${courseId}/chapters/${chapter.id}`);
                    }
                  }}
                >
                  {/* Purple accent line for completed chapters */}
                  {isCompleted && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        background: 'linear-gradient(90deg, var(--purple-500) 0%, var(--purple-400) 100%)',
                        zIndex: 2,
                      }}
                    />
                  )}

                  {/* Chapter Number Badge */}
                  <Group position="apart" mb="md" sx={{ position: 'relative', zIndex: 1 }}>
                    <Badge
                      size="lg"
                      radius="xl"
                      variant="gradient"
                      gradient={{ from: 'purple.6', to: 'purple.4' }}
                      sx={{
                        background: isCompleted
                          ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                          : 'linear-gradient(135deg, var(--purple-600) 0%, var(--purple-400) 100%)',
                        color: 'white',
                        fontWeight: 700,
                      }}
                    >
                      {isCompleted ? (
                        <Group spacing={4} noWrap>
                          <IconCircleCheck size={14} />
                          <span>Chapter {index + 1}</span>
                        </Group>
                      ) : (
                        `Chapter ${index + 1}`
                      )}
                    </Badge>

                    {chapter.estimated_minutes && (
                      <Group spacing={4} noWrap>
                        <ThemeIcon size="sm" radius="xl" color="purple" variant="light">
                          <IconClock size={12} />
                        </ThemeIcon>
                        <Text size="xs" color="dimmed" weight={500}>
                          {chapter.estimated_minutes}min
                        </Text>
                      </Group>
                    )}
                  </Group>

                  {/* Chapter Title */}
                  <Title
                    order={4}
                    mb="sm"
                    sx={(theme) => ({
                      position: 'relative',
                      zIndex: 1,
                      color: theme.colorScheme === 'dark' ? theme.white : theme.black,
                      fontWeight: 700,
                      lineHeight: 1.3,
                      minHeight: '2.6em',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    })}
                  >
                    {chapter.title || chapter.caption || `Chapter ${index + 1}`}
                  </Title>

                  {/* Chapter Description */}
                  <Text
                    size="sm"
                    color="dimmed"
                    mb="md"
                    sx={{
                      position: 'relative',
                      zIndex: 1,
                      flexGrow: 1,
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      lineHeight: 1.5,
                    }}
                  >
                    {chapter.description || 'Explore this chapter to continue your learning journey.'}
                  </Text>

                  {/* Progress Indicator */}
                  <Box sx={{ position: 'relative', zIndex: 1 }}>
                    <Group position="apart" mb={6}>
                      <Text size="xs" weight={600} color="dimmed">
                        Progress
                      </Text>
                      <Text size="xs" weight={700} color={isCompleted ? 'green' : 'purple'}>
                        {chapterProgress}%
                      </Text>
                    </Group>
                    <Progress
                      value={chapterProgress}
                      size="sm"
                      radius="xl"
                      color={isCompleted ? 'green' : 'purple'}
                      sx={{
                        '& .mantine-Progress-bar': {
                          background: isCompleted
                            ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                            : 'linear-gradient(90deg, var(--purple-500) 0%, var(--purple-400) 100%)',
                        },
                      }}
                    />
                  </Box>

                  {/* Action Button */}
                  <Button
                    fullWidth
                    mt="md"
                    variant={isCompleted ? "light" : "gradient"}
                    gradient={isCompleted ? undefined : { from: 'purple.6', to: 'purple.4' }}
                    color={isCompleted ? "green" : undefined}
                    rightIcon={<IconArrowRight size={16} />}
                    sx={{
                      position: 'relative',
                      zIndex: 1,
                      fontWeight: 600,
                      '&:hover': {
                        transform: 'translateY(-2px)',
                      },
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (chapter.id) {
                        trackContentInteraction(
                          courseId,
                          'interactive',
                          0,
                          {
                            chapter_id: chapter.id,
                            chapter_name: chapter.title || chapter.caption,
                            navigation_method: 'chapter_button'
                          }
                        );

                        trackEvent('chapter_start', {
                          course_id: courseId,
                          chapter_id: chapter.id,
                          chapter_name: chapter.title || chapter.caption,
                          navigation_method: 'chapter_button'
                        });
                        navigate(`/dashboard/courses/${courseId}/chapters/${chapter.id}`);
                      }
                    }}
                  >
                    {isCompleted ? 'Review Chapter' : 'Start Chapter'}
                  </Button>
                </Card>
              );
            })}

            {course.status === "CourseStatus.CREATING" &&
              creationProgressUI.estimatedTotal > chapters.length &&
              Array.from({ length: creationProgressUI.estimatedTotal - chapters.length }).map((_, idx) => {
                const placeholderIndex = chapters.length + idx;
                return (
                  <Card
                    key={`placeholder-${placeholderIndex}`}
                    shadow="sm"
                    padding="lg"
                    radius="md"
                    withBorder
                    sx={(theme) => ({
                      display: 'flex',
                      flexDirection: 'column',
                      background: theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)',
                      backdropFilter: 'blur(20px)',
                      border: theme.colorScheme === 'dark' 
                        ? '1px solid rgba(139, 92, 246, 0.2)' 
                        : '1px solid rgba(0, 0, 0, 0.06)',
                      '&:hover': {
                        borderColor: theme.colorScheme === 'dark' 
                          ? 'rgba(139, 92, 246, 0.3)' 
                          : 'rgba(0, 0, 0, 0.1)',
                        transform: 'translateY(-4px)',
                        boxShadow: theme.colorScheme === 'dark'
                          ? '0 12px 40px rgba(139, 92, 246, 0.15)'
                          : '0 8px 30px rgba(0, 0, 0, 0.05)',
                      },
                      transition: 'all 0.3s ease',
                    })}
                  >
                    <Card.Section>
                      <Box sx={{ position: 'relative' }}>
                        <Image
                          src="https://storage.googleapis.com/proudcity/mebanenc/uploads/2021/03/placeholder-image.png"
                          height={180}
                          alt={t('creation.upcomingChapterAlt', { chapterNumber: placeholderIndex + 1 })}
                          sx={{ filter: 'blur(3px) grayscale(50%)' }}
                        />
                        <Overlay opacity={0.6} color="#000" />
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: 20,
                          }}
                        >
                          <Loader color="white" size="md" mb="md" />
                          <Text align="center" color="white" weight={600}>{t('creation.creatingChapterOverlay', { chapterNumber: placeholderIndex + 1 })}</Text>
                          <Text align="center" color="white" size="xs" opacity={0.8}>{t('creation.aiCraftingOverlay')}</Text>
                        </Box>
                      </Box>
                    </Card.Section>
                    <Box mt="md" sx={{ flex: 1 }}>
                      <Text weight={500} color="dimmed">{t('creation.placeholderChapterTitle', { chapterNumber: placeholderIndex + 1 })}</Text>
                      <Box mt="sm" mb="lg">
                        <Box sx={{ height: '1rem', width: '80%', backgroundColor: 'rgba(128,128,128,0.2)', borderRadius: '4px', marginBottom: '0.5rem' }} />
                        <Box sx={{ height: '1rem', width: '60%', backgroundColor: 'rgba(128,128,128,0.2)', borderRadius: '4px', marginBottom: '0.5rem' }} />
                        <Box sx={{ height: '1rem', width: '70%', backgroundColor: 'rgba(128,128,128,0.2)', borderRadius: '4px' }} />
                      </Box>
                    </Box>
                    <Button variant="light" color="gray" fullWidth mt="md" disabled>
                      {t('creation.placeholderButtonCreating')}
                    </Button>
                  </Card>
                );
              })}
          </SimpleGrid>
        </>
      )
      }
    </Container >
  );
}

export default CourseView;