import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMediaQuery } from '@mantine/hooks';
import {
  Container,
  Title,
  Text,
  Grid,
  Card,
  Image,
  Button,
  Group,
  Loader,
  Alert,
  useMantineTheme,
  Box,
  TextInput,
  Paper,
  Stack,
  ActionIcon,
  Modal,
  Textarea,
  Switch,
  rem,
  Progress,
  Badge,
  ThemeIcon,
} from '@mantine/core';
import SearchBar from '../components/SearchBar';
import {
  IconBook,
  IconAlertCircle,
  IconWorld,
  IconSearch,
  IconPencil,
  IconTrash,
  IconCheck,
  IconLoader,
  IconFlame,
  IconClock
} from '@tabler/icons-react';
import courseService from '../api/courseService';
import { useTranslation } from 'react-i18next';
import PlaceGolderImage from '../assets/place_holder_image.png';

function MyCourses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [courseToDeleteId, setCourseToDeleteId] = useState(null);
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [courseToRename, setCourseToRename] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  const navigate = useNavigate();
  const theme = useMantineTheme();
  const { t } = useTranslation('dashboard');

  // Helper function to get status badge color and icon
  const getStatusInfo = (status) => {
    const label = t(`status.${status?.replace(/^.*\./, '').toLowerCase()}`, { defaultValue: status });

    switch (status) {
      case 'CourseStatus.CREATING':
        return { label, color: 'yellow', Icon: IconLoader };
      case 'CourseStatus.FINISHED':
      case 'CourseStatus.COMPLETED':
        return { label, color: 'green', Icon: IconCheck };
      case 'CourseStatus.FAILED':
        return { label, color: 'red', Icon: IconAlertCircle };
      default:
        return { label, color: 'gray', Icon: IconBook };
    }
  };

  // Calculate progress for a course
  const calculateProgress = (course) => {
    if (course.status === 'CourseStatus.COMPLETED') return 100;
    if (course.status === 'CourseStatus.CREATING') return 0;
    return (course?.chapter_count > 0)
      ? Math.round((100 * (course.completed_chapter_count || 0)) / course.chapter_count)
      : 0;
  };

  // Fetch user's courses
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const coursesData = await courseService.getUserCourses();
        setCourses(coursesData);
        setError(null);
      } catch (err) {
        setError(t('loadCoursesError'));
        console.error('Error fetching courses:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [t]);

  // Update filtered courses when search query or courses change
  useEffect(() => {
    if (!searchQuery) {
      setFilteredCourses(courses);
    } else {
      const query = searchQuery.toLowerCase().trim();
      const filtered = courses.filter(course => {
        const title = (course.title || '').toLowerCase();
        const description = (course.description || '').toLowerCase();
        return title.includes(query) || description.includes(query);
      });
      setFilteredCourses(filtered);
    }
  }, [searchQuery, courses]);

  // Handle course deletion
  const handleDelete = (courseId) => {
    setCourseToDeleteId(courseId);
    setDeleteModalOpen(true);
  };

  const confirmDeleteHandler = async () => {
    if (!courseToDeleteId) return;
    try {
      await courseService.deleteCourse(courseToDeleteId);
      setCourses(prevCourses => prevCourses.filter(course => course.course_id !== courseToDeleteId));
      setDeleteModalOpen(false);
    } catch (err) {
      setError(t('errors.deleteCourse', { message: err.message || '' }));
      console.error('Error deleting course:', err);
    }
  };

  // Handle course renaming
  const handleRename = (course) => {
    setCourseToRename(course);
    setNewTitle(course.title || '');
    setNewDescription(course.description || '');
    setIsPublic(course.is_public || false);
    setRenameModalOpen(true);
  };

  const confirmRenameHandler = async () => {
    if (!courseToRename) return;
    try {
      // First, update the public status
      await courseService.updateCoursePublicStatus(courseToRename.course_id, isPublic);

      // Then, update the title and description
      const updatedCourse = await courseService.updateCourse(
        courseToRename.course_id,
        newTitle,
        newDescription
      );

      // Combine updates for the UI
      const finalUpdatedCourse = { ...updatedCourse, is_public: isPublic };

      setCourses(prevCourses =>
        prevCourses.map(course =>
          course.course_id === courseToRename.course_id ? finalUpdatedCourse : course
        )
      );
      setRenameModalOpen(false);
    } catch (err) {
      setError(t('errors.renameCourse', { message: err.message || '' }));
      console.error('Error updating course:', err);
    }
  };

  if (loading) {
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
          {t('loadingMyCourses', { ns: 'dashboard', defaultValue: 'Loading your courses...' })}
        </Text>
      </Container>
    );
  }

  if (error) {
    return (
      <Container style={{ paddingTop: '20px' }}>
        <Alert icon={<IconAlertCircle size={16} />} title={t('errorTitle')} color="red">
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container size="lg" py="xl">
      <Box
        pb="xl"
        mb="xl"
        style={{
          borderBottom: `1px solid ${
            theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[2]
          }`,
        }}
      >
        <Group position="apart" align="flex-start">
          <div>
            <Title order={2} style={{ color: theme.colorScheme === 'dark' ? theme.white : theme.black }}>
              {t('myCoursesTitle', { defaultValue: 'Meine Kurse' })}
            </Title>
            <Text color="dimmed" mt={4}>
              {t('myCoursesSubtitle', { defaultValue: 'Verwalte und durchsuche deine persönlichen Kurse.' })}
            </Text>
          </div>
          <IconBook size={40} color={theme.colors.blue[5]} stroke={1.5} style={{ marginTop: 4 }} />
        </Group>
      </Box>

      <TextInput
        placeholder={t('searchMyCoursesPlaceholder', { ns: 'dashboard', defaultValue: 'Kurse durchsuchen...' })}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.currentTarget.value)}
        icon={<IconSearch size={16} />}
        mb="xl"
      />

      {filteredCourses.length === 0 && !loading ? (
        <Paper withBorder radius="md" p="xl" mt="xl" bg={theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)'}>
          <Stack align="center" spacing="md" py="xl">
            <IconBook size={60} color={theme.colors.gray[6]} stroke={1.5} />
            <Title order={3} align="center">
              {searchQuery
                ? t('noSearchResults', { defaultValue: 'Keine Kurse gefunden' })
                : t('noCoursesYet', { defaultValue: 'Noch keine Kurse vorhanden' })}
            </Title>
            <Text color="dimmed" size="sm" align="center">
              {searchQuery
                ? t('tryDifferentKeywords', { defaultValue: 'Versuche es mit anderen Suchbegriffen.' })
                : t('createFirstCourse', { defaultValue: 'Erstelle deinen ersten Kurs, um loszulegen.' })}
            </Text>
            {!searchQuery && (
              <Button
                leftIcon={<IconFlame size={16} />}
                onClick={() => navigate('/dashboard/create-course')}
                mt="md"
              >
                {t('createCourseButton', { defaultValue: 'Kurs erstellen' })}
              </Button>
            )}
          </Stack>
        </Paper>
      ) : (
        <Grid gutter="xl">
          {filteredCourses.map((course) => {
            const { label: statusLabel, color: statusColor, Icon: StatusIcon } = getStatusInfo(course.status);
            const progress = calculateProgress(course);

            return (
              <Grid.Col key={course.course_id} sm={6} md={4} lg={4}>
                <Card
                  shadow="sm"
                  p="xl"
                  radius="xl"
                  withBorder
                  className="card-modern card-glass card-hoverable transition-all duration-300"
                  style={{ display: 'flex', flexDirection: 'column', height: '100%' }}
                  sx={(theme) => ({
                    background: theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(20px)',
                    border: theme.colorScheme === 'dark' 
                      ? '1px solid rgba(139, 92, 246, 0.2)' 
                      : '1px solid rgba(0, 0, 0, 0.06)',
                    position: 'relative',
                    overflow: 'hidden',
                    minHeight: '480px',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      borderColor: theme.colorScheme === 'dark' 
                        ? 'rgba(139, 92, 246, 0.3)' 
                        : 'rgba(0, 0, 0, 0.1)',
                      boxShadow: theme.colorScheme === 'dark'
                        ? '0 12px 40px rgba(139, 92, 246, 0.15)'
                        : '0 8px 30px rgba(0, 0, 0, 0.08)',
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: theme.colorScheme === 'dark' 
                        ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)' 
                        : 'linear-gradient(135deg, rgba(139, 92, 246, 0.02) 0%, rgba(168, 85, 247, 0.02) 100%)',
                      opacity: 0,
                      transition: 'opacity 0.4s ease',
                      zIndex: 0,
                    },
                    '&:hover::before': {
                      opacity: 1,
                    },
                  })}
                >
                  <Card.Section sx={{ position: 'relative', zIndex: 1 }}>
                    <Image
                      src={course.image_url || PlaceGolderImage}
                      height={180}
                      alt={course.title}
                      withPlaceholder
                      style={{
                        objectFit: 'cover',
                        width: '100%',
                        height: '180px'
                      }}
                    />
                    {/* Gradient overlay on image */}
                    <Box
                      sx={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '50%',
                        background: 'linear-gradient(transparent, rgba(0,0,0,0.6))',
                        display: 'flex',
                        alignItems: 'flex-end',
                        padding: '16px',
                      }}
                    >
                      <Badge
                        size="lg"
                        radius="xl"
                        variant="gradient"
                        gradient={
                          statusColor === 'green'
                            ? { from: 'green.6', to: 'green.4' }
                            : statusColor === 'yellow'
                              ? { from: 'yellow.6', to: 'orange.4' }
                              : { from: 'purple.6', to: 'purple.4' }
                        }
                        leftSection={<StatusIcon size={16} />}
                        sx={{ color: 'white', fontWeight: 700 }}
                      >
                        {statusLabel}
                      </Badge>
                    </Box>
                  </Card.Section>

                  <Box sx={{ position: 'relative', zIndex: 1, flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <Group position="apart" mt="md" mb="xs" align="flex-start" style={{ width: '100%' }}>
                    <Text
                      weight={700}
                      size="lg"
                      sx={(theme) => ({
                        color: theme.colorScheme === 'dark' ? theme.white : theme.black,
                        lineHeight: 1.3,
                        fontSize: '1.125rem',
                        flex: 1,
                        minWidth: 0,
                        wordBreak: 'break-word',
                        paddingRight: '8px',
                        '&:hover': {
                          textDecoration: 'underline',
                          textUnderlineOffset: '2px'
                        }
                      })}
                    >
                      {course.title || t('untitledCourse', { defaultValue: 'Unbenannter Kurs' })}
                    </Text>
                    <Group spacing="xs" style={{ flexShrink: 0, marginTop: '2px' }}>
                        <ActionIcon
                          variant="light"
                          color="purple"
                          size="md"
                          radius="xl"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRename(course);
                          }}
                          sx={{
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              boxShadow: '0 4px 15px rgba(139, 92, 246, 0.3)',
                            },
                          }}
                        >
                          <IconPencil size={16} />
                        </ActionIcon>

                        <ActionIcon
                          variant="light"
                          color="red"
                          size="md"
                          radius="xl"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(course.course_id);
                          }}
                          sx={{
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              boxShadow: '0 4px 15px rgba(239, 68, 68, 0.3)',
                            },
                          }}
                        >
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Group>
                    </Group>

                    <Box 
                      sx={{
                        flexGrow: 1,
                        marginBottom: '1rem',
                        overflow: 'hidden',
                        display: 'flex',
                        flexDirection: 'column',
                        minHeight: '80px', // Ensure minimum height for the description area
                      }}
                    >
                      <Text
                        size="sm"
                        color="dimmed"
                        sx={{
                          lineHeight: 1.5,
                          overflowY: 'auto',
                          maxHeight: '120px', // Adjust based on your needs
                          paddingRight: '8px',
                          '&::-webkit-scrollbar': {
                            width: '6px',
                          },
                          '&::-webkit-scrollbar-track': {
                            background: theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[1],
                            borderRadius: '3px',
                          },
                          '&::-webkit-scrollbar-thumb': {
                            background: theme.colorScheme === 'dark' ? theme.colors.dark[4] : theme.colors.gray[4],
                            borderRadius: '3px',
                            '&:hover': {
                              background: theme.colorScheme === 'dark' ? theme.colors.dark[3] : theme.colors.gray[5],
                            },
                          },
                        }}
                      >
                        {course.description || t('noDescription', { defaultValue: 'Keine Beschreibung' })}
                      </Text>
                    </Box>

                    {/* Modern Progress Indicator */}
                    <Box mb="lg">
                      <Group position="apart" mb={8}>
                        <Group spacing={6} noWrap>
                          <ThemeIcon size="sm" radius="xl" color="purple" variant="light">
                            <IconClock size={12} />
                          </ThemeIcon>
                          <Text size="sm" color="dimmed" weight={600}>
                            {t('progress', { defaultValue: 'Fortschritt' })}
                          </Text>
                        </Group>
                        <Text size="sm" weight={700} color={progress === 100 ? 'green' : 'purple'}>
                          {progress}%
                        </Text>
                      </Group>
                      <Progress
                        value={progress}
                        size="md"
                        radius="xl"
                        color={progress === 100 ? 'green' : 'purple'}
                        sx={{
                          '& .mantine-Progress-bar': {
                            background: progress === 100
                              ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                              : 'linear-gradient(90deg, var(--purple-500) 0%, var(--purple-400) 100%)',
                          },
                        }}
                      />
                    </Box>

                    <Button
                      fullWidth
                      variant="gradient"
                      gradient={{ from: 'purple.6', to: 'purple.4' }}
                      onClick={() => navigate(`/dashboard/courses/${course.course_id}`)}
                      leftIcon={<IconBook size={16} />}
                      className="btn-modern transition-all duration-300"
                      sx={{
                        fontWeight: 600,
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 25px rgba(139, 92, 246, 0.4)',
                        },
                      }}
                    >
                      {t('openCourse', { defaultValue: 'Open' })}
                    </Button>
                  </Box>
                </Card>
              </Grid.Col>
            );
          })}
        </Grid>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        opened={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title={t('deleteModal.title', { defaultValue: 'Kurs löschen' })}
        centered
      >
        <Text>{t('deleteModal.confirmation', { defaultValue: 'Möchtest du diesen Kurs wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.' })}</Text>
        <Group position="right" mt="md">
          <Button variant="default" onClick={() => setDeleteModalOpen(false)}>
            {t('cancel', { defaultValue: 'Abbrechen' })}
          </Button>
          <Button color="red" onClick={confirmDeleteHandler}>
            {t('delete', { defaultValue: 'Löschen' })}
          </Button>
        </Group>
      </Modal>

      {/* Rename Course Modal */}
      <Modal
        opened={renameModalOpen}
        onClose={() => setRenameModalOpen(false)}
        title={t('renameModal.title', { defaultValue: 'Kurs bearbeiten' })}
        size="lg"
      >
        <Stack spacing="md">
          <TextInput
            label={t('title', { defaultValue: 'Titel' })}
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />

          <Textarea
            label={t('description', { defaultValue: 'Beschreibung' })}
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            minRows={3}
          />

          <Switch
            label={t('publicCourse', { defaultValue: 'Öffentlich sichtbar' })}
            checked={isPublic}
            onChange={(e) => setIsPublic(e.currentTarget.checked)}
            description={t('publicCourseDescription', {
              defaultValue: 'Andere Nutzer können diesen Kurs finden und darauf zugreifen.'
            })}
          />

          <Group position="right" mt="md">
            <Button variant="default" onClick={() => setRenameModalOpen(false)}>
              {t('cancel', { defaultValue: 'Abbrechen' })}
            </Button>
            <Button onClick={confirmRenameHandler}>
              {t('saveChanges', { defaultValue: 'Änderungen speichern' })}
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
}

export default MyCourses;
