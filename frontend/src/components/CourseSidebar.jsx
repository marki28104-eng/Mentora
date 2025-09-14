import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom';
import { Box, NavLink, Text, Button, ThemeIcon, Loader, useMantineTheme, ActionIcon } from '@mantine/core';
import {
  IconHome2,
  IconChevronRight,
  IconChevronDown,
  IconFileText,
  IconPhoto,
  IconQuestionMark,
  IconCircleCheck,
  IconCircleDashed,
  IconSchool,
} from '@tabler/icons-react';
import { courseService } from '../api/courseService';
import { useTranslation } from 'react-i18next';
import { MainLink } from "../layouts/AppLayout.jsx";
import { useMediaQuery } from "@mantine/hooks";
import { LoadingSpinner } from './ui/LoadingSpinner';

const ChapterLink = ({ chapter, activeChapter, index, handleChapterClick, handleNavigation, chapterId, courseId, opened, currentTab, isExpanded, ...props }) => {
  const [hasQuestions, setHasQuestions] = useState(false);
  const intervalRef = useRef(null);
  const theme = useMantineTheme();

  useEffect(() => {
    // If this chapter already has a quiz, don't poll.
    if (hasQuestions) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    // Poll for quiz questions for this specific chapter
    intervalRef.current = setInterval(async () => {
      try {
        // Use chapter.id from the mapped chapter, not the active chapterId from params
        const questions = await courseService.getChapterQuestions(courseId, chapter.id);
        if (questions && questions.length > 0) {
          setHasQuestions(true);
          clearInterval(intervalRef.current);
        }
      } catch (error) {
        console.error(`Error polling for quiz in chapter ${chapter.id}:`, error);
        clearInterval(intervalRef.current);
      }
    }, 500); // Poll every 500ms

    // Cleanup function for when the component unmounts or dependencies change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [courseId, chapter.id, hasQuestions]); // Dependencies for the effect

  // When collapsed, render as a simple numbered button
  if (!opened) {
    return (
      <ActionIcon
        key={chapter.id}
        variant="light"
        size="xl"
        color={chapter.is_completed ? 'violet' : 'gray'}
        onClick={() => handleNavigation(chapter.id, 'content')}
        className="transition-all hover:-translate-y-1 hover:shadow-purple-md"
        style={{
          display: 'flex',
          justifyContent: 'center',
          width: '100%',
          marginBottom: theme.spacing.xs,
          minHeight: 48,
          background: chapterId === chapter.id.toString()
            ? 'rgba(139, 92, 246, 0.15)'
            : chapter.is_completed
              ? 'rgba(139, 92, 246, 0.08)'
              : 'rgba(156, 163, 175, 0.08)',
          border: chapterId === chapter.id.toString()
            ? `2px solid var(--purple-500)`
            : `1px solid rgba(139, 92, 246, 0.1)`,
          borderRadius: theme.radius.lg,
        }}
        title={`${index + 1}. ${chapter.caption}`}
      >
        <Text
          size="sm"
          weight={600}
          sx={{
            color: chapterId === chapter.id.toString()
              ? 'var(--purple-600)'
              : chapter.is_completed
                ? 'var(--purple-500)'
                : 'var(--text-secondary)'
          }}
        >
          {index + 1}
        </Text>
      </ActionIcon>
    );
  }

  // When expanded, render full navigation structure
  return (
    <div
      className="transition-all"
      style={{
        backgroundColor: chapterId === chapter.id.toString()
          ? 'rgba(139, 92, 246, 0.1)'
          : undefined,
        borderRadius: theme.radius.md,
        margin: '4px 0',
      }}
    >
      <NavLink
        key={chapter.id}
        label={`${index + 1}. ${chapter.caption}`}
        opened={isExpanded}
        onClick={() => handleChapterClick(chapter.id.toString())}
        className="transition-all hover:bg-purple-gradient-subtle"
        style={{
          backgroundColor: chapterId === chapter.id.toString()
            ? 'rgba(139, 92, 246, 0.1)'
            : undefined,
          borderRadius: theme.radius.md,
          border: chapterId === chapter.id.toString()
            ? `1px solid rgba(139, 92, 246, 0.2)`
            : '1px solid transparent',
          color: chapterId === chapter.id.toString()
            ? 'var(--purple-600)'
            : 'var(--text-primary)',
        }}
        icon={
          <ThemeIcon
            variant="light"
            size="sm"
            color={chapter.is_completed ? 'violet' : 'gray'}
            sx={{
              background: chapter.is_completed
                ? 'rgba(139, 92, 246, 0.1)'
                : 'rgba(156, 163, 175, 0.1)',
              color: chapter.is_completed
                ? 'var(--purple-500)'
                : 'var(--text-secondary)',
            }}
          >
            {chapter.is_completed ? <IconCircleCheck size={14} /> : <IconCircleDashed size={14} />}
          </ThemeIcon>
        }
        rightSection={
          <div className="transition-transform">
            {isExpanded ? <IconChevronDown size={14} /> : <IconChevronRight size={14} />}
          </div>
        }
      >
        <NavLink
          label="Content"
          icon={<IconFileText size={16} />}
          onClick={(e) => {
            e.stopPropagation();
            handleNavigation(chapter.id, 'content');
          }}
          active={chapterId === chapter.id.toString() && currentTab === 'content'}
          className="transition-colors"
          styles={{
            root: {
              borderRadius: theme.radius.sm,
              margin: '2px 8px',
              '&:hover': {
                backgroundColor: 'rgba(139, 92, 246, 0.08)',
                color: 'var(--purple-600)',
              },
              '&[data-active]': {
                backgroundColor: 'rgba(139, 92, 246, 0.15)',
                color: 'var(--purple-600)',
                borderLeft: '3px solid var(--purple-500)',
              },
            },
          }}
        />
        {chapter.file_count > 0 && (
          <NavLink
            label="Files"
            icon={<IconPhoto size={16} />}
            onClick={(e) => {
              e.stopPropagation();
              handleNavigation(chapter.id, 'files');
            }}
            active={chapterId === chapter.id.toString() && currentTab === 'files'}
            className="transition-colors"
            styles={{
              root: {
                borderRadius: theme.radius.sm,
                margin: '2px 8px',
                '&:hover': {
                  backgroundColor: 'rgba(139, 92, 246, 0.08)',
                  color: 'var(--purple-600)',
                },
                '&[data-active]': {
                  backgroundColor: 'rgba(139, 92, 246, 0.15)',
                  color: 'var(--purple-600)',
                  borderLeft: '3px solid var(--purple-500)',
                },
              },
            }}
          />
        )}
        {hasQuestions && (
          <NavLink
            label="Quiz"
            icon={<IconQuestionMark size={16} />}
            onClick={(e) => {
              e.stopPropagation();
              handleNavigation(chapter.id, 'quiz');
            }}
            active={chapterId === chapter.id.toString() && currentTab === 'quiz'}
            className="transition-colors"
            styles={{
              root: {
                borderRadius: theme.radius.sm,
                margin: '2px 8px',
                '&:hover': {
                  backgroundColor: 'rgba(139, 92, 246, 0.08)',
                  color: 'var(--purple-600)',
                },
                '&[data-active]': {
                  backgroundColor: 'rgba(139, 92, 246, 0.15)',
                  color: 'var(--purple-600)',
                  borderLeft: '3px solid var(--purple-500)',
                },
              },
            }}
          />
        )}
      </NavLink>
    </div>
  );
};

const CourseSidebar = ({ opened, setopen }) => {
  const { t } = useTranslation(['navigation', 'app', 'settings']);
  const navigate = useNavigate();
  const location = useLocation();
  const { courseId, chapterId } = useParams();

  const [course, setCourse] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedChapters, setExpandedChapters] = useState(new Set());
  const isMobile = useMediaQuery('(max-width: 768px)');

  // Get current tab from URL search params
  const searchParams = new URLSearchParams(location.search);
  const currentTab = searchParams.get('tab') || 'content';

  // Refs to hold interval IDs for cleanup
  const coursePollInterval = useRef(null);

  // Update activeChapter when chapterId changes
  useEffect(() => {
    // Ensure the active chapter is always expanded
    if (chapterId && !expandedChapters.has(chapterId)) {
      setExpandedChapters(prev => new Set([...prev, chapterId]));
    }
  }, [chapterId]);

  // Toggle chapter expansion
  const toggleChapter = (chapterId) => {
    setExpandedChapters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(chapterId)) {
        newSet.delete(chapterId);
      } else {
        newSet.add(chapterId);
      }
      return newSet;
    });
  };

  // --- Polling and Data Fetching Logic ---

  // Fetches initial course and chapter data
  const fetchInitialData = async () => {
    if (!courseId) return;
    try {
      setLoading(true);
      const [courseData, chaptersData] = await Promise.all([
        courseService.getCourseById(courseId),
        courseService.getCourseChapters(courseId),
      ]);

      setCourse(courseData);
      // Initialize chapters with has_questions as false. It will be updated by polling.
      const initialChapters = (chaptersData || []).map(ch => ({ ...ch, has_questions: false }));
      setChapters(initialChapters);

      // If the course is being created, start polling for updates
      if (courseData?.status === 'CourseStatus.CREATING') {
        startCoursePolling();
      }
    } catch (error) {
      console.error('Failed to fetch initial course data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Polls for course status and new chapters
  const startCoursePolling = () => {
    if (coursePollInterval.current) clearInterval(coursePollInterval.current);

    coursePollInterval.current = setInterval(async () => {
      try {
        const [updatedCourse, updatedChaptersData] = await Promise.all([
          courseService.getCourseById(courseId),
          courseService.getCourseChapters(courseId),
        ]);

        setCourse(updatedCourse);

        // Check for newly added chapters
        setChapters(prevChapters => {
          const newChapters = (updatedChaptersData || []).map(newChap => {
            const existing = prevChapters.find(p => p.id === newChap.id);
            return existing ? existing : { ...newChap, has_questions: false };
          });

          return newChapters;
        });

        // If course creation is finished, stop polling
        if (updatedCourse?.status === 'CourseStatus.FINISHED') {
          clearInterval(coursePollInterval.current);
        }
      } catch (error) {
        console.error('Error during course polling:', error);
        clearInterval(coursePollInterval.current); // Stop on error
      }
    }, 2000); // Poll every 2 seconds
  };

  // --- Effects ---

  // Initial data load
  useEffect(() => {
    fetchInitialData();

    // Cleanup function to clear all intervals when the component unmounts
    return () => {
      if (coursePollInterval.current) {
        clearInterval(coursePollInterval.current);
      }
    };
  }, [courseId]);

  // --- Handlers ---

  const handleChapterClick = (id) => {
    toggleChapter(id);
  };

  const handleNavigation = (chapId, tab) => {
    // Force navigation even if we're already on the same chapter
    const newUrl = `/dashboard/courses/${courseId}/chapters/${chapId}?tab=${tab}`;
    navigate(newUrl);

    // Close mobile sidebar after navigation
    if (isMobile) {
      setopen(false);
    }
  };

  const handleCourseTitleClick = () => {
    navigate(`/dashboard/courses/${courseId}`);

    // Close mobile sidebar after navigation
    if (isMobile) {
      setopen(false);
    }
  };

  const handleNavigate = () => {
    if (isMobile) {
      setopen(false);
    }
  };

  // --- Render Logic ---

  if (loading) {
    return (
      <Box p="md" className="glass-card" style={{ textAlign: 'center', margin: '16px' }}>
        <LoadingSpinner size="md" variant="purple" text="Loading Course..." />
      </Box>
    );
  }

  const link = { icon: <IconHome2 size={20} />, color: 'violet', label: t('home', { ns: 'navigation' }), to: '/dashboard' }

  return (
    <Box className="nav-sidebar glass-nav">
      <MainLink
        {...link}
        key={link.label}
        isActive={false} // Home is not active when we're in course view
        collapsed={!opened}
        onNavigate={handleNavigate}
      />

      {opened ? (
        <Button
          variant="light"
          color="violet"
          fullWidth
          onClick={handleCourseTitleClick}
          className="transition-all hover:-translate-y-1 hover:shadow-purple-md"
          styles={(theme) => ({
            root: {
              padding: `${theme.spacing.md}px`,
              height: 'auto',
              marginBottom: theme.spacing.md,
              marginTop: 30,
              background: 'rgba(139, 92, 246, 0.08)',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: theme.radius.lg,
              '&:hover': {
                background: 'rgba(139, 92, 246, 0.12)',
                borderColor: 'rgba(139, 92, 246, 0.3)',
              }
            },
            label: {
              whiteSpace: 'normal',
              fontSize: theme.fontSizes.lg,
              fontWeight: 700,
              color: 'var(--purple-600)'
            },
          })}
        >
          {course?.title && course?.title != "None" ? course?.title : 'Course Overview'}
        </Button>
      ) : (
        <ActionIcon
          variant="light"
          color="violet"
          size="xl"
          onClick={handleCourseTitleClick}
          className="transition-all hover:-translate-y-1 hover:shadow-purple-md"
          style={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%',
            margin: '30px 0',
            background: 'rgba(139, 92, 246, 0.08)',
            border: '1px solid rgba(139, 92, 246, 0.2)',
          }}
          title={course?.title || 'Course Overview'}
        >
          <IconSchool size={24} />
        </ActionIcon>
      )}

      {chapters.map((chapter, index) =>
        (chapter.id !== null) ? (
          <ChapterLink
            key={chapter.id}
            chapter={chapter}
            index={index}
            activeChapter={chapterId}
            handleChapterClick={handleChapterClick}
            handleNavigation={handleNavigation}
            chapterId={chapterId}
            courseId={courseId}
            opened={opened}
            currentTab={currentTab}
            isExpanded={expandedChapters.has(chapter.id.toString())}
          />
        ) : <></>
      )}
    </Box>
  );
};

export default CourseSidebar;
