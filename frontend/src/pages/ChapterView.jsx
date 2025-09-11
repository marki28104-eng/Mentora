//ChapterView.jsx - Fixed tab switching logic

import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Title,
  Text,
  Group,
  Button,
  Tabs,
  Alert,
  Box,
  Loader,
  Paper,
  Badge,
} from '@mantine/core';
import { IconDownload } from '@tabler/icons-react';
import { useMediaQuery } from '@mantine/hooks';
import { IconAlertCircle, IconBookmark, IconQuestionMark, IconPhoto, IconFileText, IconCards, IconCheck, IconArrowBack, IconCircleCheck, IconClock } from '@tabler/icons-react';
import { MediaGallery } from '../components/media/MediaGallery';
import { FileList } from '../components/media/FileList';
import { toast } from 'react-toastify';
import { courseService } from '../api/courseService';
import ToolbarContainer from '../components/tools/ToolbarContainer';
import { useToolbar } from '../contexts/ToolbarContext';
import { useUmamiTracker } from '../components/UmamiTracker';
import AiCodeWrapper from "../components/AiCodeWrapper.jsx";
import { downloadChapterContentAsPDF, prepareElementForPDF } from '../utils/pdfDownload';
import FullscreenContentWrapper from '../components/FullscreenContentWrapper';
import Quiz from './Quiz';
import FlashcardDeck from '../components/flashcards/FlashcardDeck';

function ChapterView() {
  const { t } = useTranslation('chapterView');
  const { courseId, chapterId } = useParams();
  const navigate = useNavigate();
  const location = useLocation(); // Get location to read query params
  const { toolbarOpen, toolbarWidth } = useToolbar();
  const isMobile = useMediaQuery('(max-width: 768px)');
  const {
    trackEvent,
    trackContentInteraction,
    trackTimeSpent,
    trackChapterComplete
  } = useUmamiTracker();

  // Read tab from URL, default to 'content'
  const queryParams = new URLSearchParams(location.search);
  const initialTab = queryParams.get('tab') || 'content';

  const [chapter, setChapter] = useState(null);
  const [images, setImages] = useState([]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mediaLoading, setMediaLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(initialTab);
  const [markingComplete, setMarkingComplete] = useState(false);
  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [deletingItem, setDeletingItem] = useState(null);
  const [hasQuestions, setHasQuestions] = useState(false);
  const [questionsCreated, setQuestionsCreated] = useState(false); // Start as false
  const [questionCount, setQuestionCount] = useState(0);
  const [isBlinking, setIsBlinking] = useState(false); // New state for blinking
  const [quizKey, setQuizKey] = useState(0); // Force Quiz component re-mount

  // Refs for cleanup
  const contentRef = useRef(null);
  const pollIntervalRef = useRef(null);
  const blinkTimeoutRef = useRef(null);

  // Time tracking
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [tabStartTime, setTabStartTime] = useState(null);
  const [totalTimeSpent, setTotalTimeSpent] = useState(0);
  const timeTrackingRef = useRef(null);

  // Listen for URL parameter changes and update active tab
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const urlTab = queryParams.get('tab') || 'content';
    setActiveTab(urlTab);
  }, [location.search]);

  // Handle tab change and update URL
  const handleTabChange = (newTab) => {
    // Track time spent on previous tab
    if (tabStartTime && activeTab) {
      const timeSpent = Date.now() - tabStartTime;
      const contentType = activeTab === 'content' ? 'text' :
        activeTab === 'quiz' ? 'quiz' :
          activeTab === 'media' ? 'interactive' : 'text';

      trackTimeSpent(courseId, chapterId, Math.round(timeSpent / 1000), contentType);
      trackContentInteraction(courseId, contentType, Math.round(timeSpent / 1000), {
        tab: activeTab,
        interaction_type: 'tab_exit'
      });
    }

    // Track tab change as content interaction
    trackEvent('content_interaction', {
      course_id: courseId,
      chapter_id: chapterId,
      interaction_type: 'tab_change',
      content_type: newTab,
      from_tab: activeTab,
      to_tab: newTab
    });

    // Track new tab interaction
    const newContentType = newTab === 'content' ? 'text' :
      newTab === 'quiz' ? 'quiz' :
        newTab === 'media' ? 'interactive' : 'text';

    trackContentInteraction(courseId, newContentType, 0, {
      tab: newTab,
      interaction_type: 'tab_enter'
    });

    // Update tab start time
    setTabStartTime(Date.now());

    const currentParams = new URLSearchParams(location.search);
    currentParams.set('tab', newTab);
    navigate(`${location.pathname}?${currentParams.toString()}`, { replace: true });
  };

  useEffect(() => {
    console.log("Toolbar state changed:", { open: toolbarOpen, width: toolbarWidth });
  }, [toolbarOpen, toolbarWidth]);


  // Fetch chapter data and media info
  useEffect(() => {
    const fetchChapterAndMediaInfo = async () => {
      try {
        setLoading(true);

        // Fetch chapter data and media info (including questions check)
        const [chapterData, imagesData, filesData, questionsData] = await Promise.all([
          courseService.getChapter(courseId, chapterId),
          courseService.getImages(courseId),
          courseService.getFiles(courseId),
          courseService.getChapterQuestions(courseId, chapterId),
        ]);

        setChapter(chapterData);

        // Initialize time tracking
        const startTime = Date.now();
        setSessionStartTime(startTime);
        setTabStartTime(startTime);

        // Track chapter view
        trackEvent('chapter_view', {
          course_id: courseId,
          chapter_id: chapterId,
          chapter_name: chapterData.title,
          tab: initialTab
        });

        // Check if chapter has questions
        if (questionsData && questionsData.length > 0) {
          setHasQuestions(true);
          setQuestionCount(questionsData.length);
          setQuestionsCreated(true); // Questions already exist
        } else {
          setHasQuestions(false);
          setQuestionCount(0);
          setQuestionsCreated(false); // No questions yet, start polling
        }

        // Set initial media state with empty URLs (will be populated in next effect)
        setImages(imagesData.map(img => ({
          ...img,
          objectUrl: null,
          loading: true,
          error: null
        })));

        setFiles(filesData.map(file => ({
          ...file,
          objectUrl: null,
          loading: true,
          error: null
        })));

        setError(null);
      } catch (error) {
        setError(t('errors.loadFailed'));
        console.error('Error fetching chapter or media info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchChapterAndMediaInfo();
  }, [courseId, chapterId, t]);

  // Track if this is the initial load
  const initialLoad = useRef(true);

  // Fetch actual media files
  useEffect(() => {
    if (loading) return;

    if (!initialLoad.current && images.every(img => img.objectUrl || img.error) &&
      files.every(file => file.objectUrl || file.error)) {
      return;
    }

    const fetchMedia = async () => {
      console.log('Starting media fetch...');
      try {
        setMediaLoading(true);

        // Process images
        console.log('Processing images...', images);
        const updatedImages = await Promise.all(
          images.map(async (image) => {
            if (image.objectUrl || image.error) {
              console.log(`Skipping image ${image.id} - already processed`);
              return image;
            }

            try {
              console.log(`Fetching image ${image.id}...`);
              const blob = await courseService.downloadImage(image.id);
              const objectUrl = URL.createObjectURL(blob);
              console.log(`Successfully fetched image ${image.id}`);
              return { ...image, objectUrl, loading: false, error: null };
            } catch (error) {
              console.error(`Error fetching image ${image.id}:`, error);
              return { ...image, loading: false, error: 'Failed to load image', objectUrl: null };
            }
          })
        );

        // Process files
        console.log('Processing files...', files);
        const updatedFiles = await Promise.all(
          files.map(async (file) => {
            if (file.objectUrl || file.error) {
              console.log(`Skipping file ${file.id} - already processed`);
              return file;
            }

            try {
              console.log(`Fetching file ${file.id}...`);
              const blob = await courseService.downloadFile(file.id);
              const objectUrl = URL.createObjectURL(blob);
              console.log(`Successfully fetched file ${file.id}`);
              return { ...file, objectUrl, loading: false, error: null };
            } catch (error) {
              console.error(`Error fetching file ${file.id}:`, error);
              return { ...file, loading: false, error: 'Failed to load file', objectUrl: null };
            }
          })
        );

        setImages(updatedImages);
        setFiles(updatedFiles);

      } catch (error) {
        console.error('Error in media fetch:', error);
        toast.error(t('errors.mediaLoadFailed'));
      } finally {
        setMediaLoading(false);
        initialLoad.current = false;
      }
    };

    fetchMedia();
  }, [images, files, loading, t]);

  // Polling logic for quiz questions - FIXED
  useEffect(() => {
    // Only start polling if questions haven't been created yet
    if (questionsCreated || loading) {
      return;
    }

    console.log('Starting polling for quiz questions...');

    const pollForQuestions = async () => {
      try {
        const questionsData = await courseService.getChapterQuestions(courseId, chapterId);

        if (questionsData && questionsData.length > 0) {
          console.log('Questions found! Stopping polling.');

          // Clear the polling interval
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }

          // Update state
          setHasQuestions(true);
          setQuestionCount(questionsData.length);
          setQuestionsCreated(true);
          toast.success(t("quizReady"))


          // Force Quiz component to re-mount and fetch new data
          setQuizKey(prev => prev + 1);

          // Start blinking animation
          setIsBlinking(true);

          // Stop blinking after 4 seconds
          blinkTimeoutRef.current = setTimeout(() => {
            setIsBlinking(false);
          }, 4000);
        }
      } catch (error) {
        console.error('Error polling for questions:', error);
        // Don't show error toast for polling failures, as this is expected during creation
      }
    };

    // Start polling every 500ms
    pollIntervalRef.current = setInterval(pollForQuestions, 500);

    // Cleanup function
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [courseId, chapterId, questionsCreated, loading, t]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cleanup object URLs
      images.forEach(image => {
        if (image.objectUrl) {
          URL.revokeObjectURL(image.objectUrl);
        }
      });
      files.forEach(file => {
        if (file.objectUrl) {
          URL.revokeObjectURL(file.objectUrl);
        }
      });

      // Cleanup intervals and timeouts
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
      if (blinkTimeoutRef.current) {
        clearTimeout(blinkTimeoutRef.current);
      }
      if (timeTrackingRef.current) {
        clearInterval(timeTrackingRef.current);
      }

      // Track final time spent before leaving
      if (sessionStartTime) {
        const totalSessionTime = Date.now() - sessionStartTime;
        trackTimeSpent(courseId, chapterId, Math.round(totalSessionTime / 1000));

        // Track final tab time if available
        if (tabStartTime && activeTab) {
          const finalTabTime = Date.now() - tabStartTime;
          const contentType = activeTab === 'content' ? 'text' :
            activeTab === 'quiz' ? 'quiz' :
              activeTab === 'media' ? 'interactive' : 'text';

          trackContentInteraction(courseId, contentType, Math.round(finalTabTime / 1000), {
            tab: activeTab,
            interaction_type: 'session_end'
          });
        }
      }

    };
  }, [courseId, chapterId, images, files]);

  const handleDeleteImage = async (imageId) => {
    try {
      setDeletingItem(imageId);
      await courseService.deleteImage(imageId);

      // Find and revoke the object URL
      const imageToDelete = images.find(img => img.id === imageId);
      if (imageToDelete?.objectUrl) {
        URL.revokeObjectURL(imageToDelete.objectUrl);
      }

      // Remove from state
      setImages(prev => prev.filter(img => img.id !== imageId));
      toast.success(t('imageDeleted'));
    } catch (error) {
      console.error('Error deleting image:', error);
      toast.error(t('errors.deleteFailed'));
    } finally {
      setDeletingItem(null);
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      setDeletingItem(fileId);
      await courseService.deleteDocument(fileId);

      // Find and revoke the object URL
      const fileToDelete = files.find(file => file.id === fileId);
      if (fileToDelete?.objectUrl) {
        URL.revokeObjectURL(fileToDelete.objectUrl);
      }

      // Remove from state
      setFiles(prev => prev.filter(file => file.id !== fileId));
      toast.success(t('fileDeleted'));
    } catch (error) {
      console.error('Error deleting file:', error);
      toast.error(t('errors.deleteFailed'));
    } finally {
      setDeletingItem(null);
    }
  };

  const markChapterComplete = async () => {
    try {
      setMarkingComplete(true);
      await courseService.markChapterComplete(courseId, chapterId);
      toast.success(t('toast.markedCompleteSuccess'));
      navigate(`/dashboard/courses/${courseId}`);
    } catch (error) {
      toast.error(t('toast.markedCompleteError'));
      console.error('Error marking chapter complete:', error);
    } finally {
      setMarkingComplete(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!contentRef.current || !chapter) {
      toast.error('Content not available for download');
      return;
    }

    try {
      setDownloadingPDF(true);

      const cleanup = prepareElementForPDF(contentRef.current);
      await new Promise(resolve => setTimeout(resolve, 100));
      await downloadChapterContentAsPDF(contentRef.current, chapter.caption || 'Chapter');
      cleanup();

      toast.success('Chapter content downloaded as PDF');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error('Failed to download PDF. Please try again.');
    } finally {
      setDownloadingPDF(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <Group position="center" mt="xl">
          <Loader size="lg" />
          <Text>{t('loading')}</Text>
        </Group>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert
          icon={<IconAlertCircle size={16} />}
          title={t('errors.genericTitle')}
          color="red"
          mt="xl"
        >
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <div
      style={{
        marginRight: toolbarOpen ? `${toolbarWidth}px` : 0,
        transition: 'margin-right 0.3s ease',
        minHeight: '100vh',
        width: toolbarOpen ? `calc(100% - ${toolbarWidth}px)` : '100%',
        maxWidth: '100%',
        marginLeft: 0,
        padding: 0,
      }}
    >
      {/* Add CSS for blinking animation */}
      <style>
        {`
          @keyframes tabBlink {
            0%, 50% { 
              background-color: #339af0; 
              color: white;
              transform: scale(1.05);
            }
            25%, 75% { 
              background-color: #74c0fc; 
              color: white;
              transform: scale(1.02);
            }
          }
          
          .quiz-tab-blinking {
            animation: tabBlink 1s ease-in-out 4;
            border-radius: 4px;
          }
        `}
      </style>

      <Container
        size="xl"
        py="xl"
        style={{
          maxWidth: '100%',
          width: '100%',
          padding: '0 16px',
        }}
      >
        {chapter && (
          <>
            {/* Modern Chapter Header */}
            <Paper
              radius="xl"
              p="xl"
              mb="xl"
              className="card-modern card-glass transition-all duration-300"
              sx={(theme) => ({
                background: 'var(--bg-card)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                position: 'relative',
                overflow: 'hidden',
              })}
            >
              {/* Purple gradient background accent */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.03) 0%, rgba(168, 85, 247, 0.03) 100%)',
                  zIndex: 0,
                }}
              />

              <Group position="apart" align="flex-start" sx={{ position: 'relative', zIndex: 1 }}>
                <Box sx={{ flex: 1 }}>
                  <Group mb="md" spacing="md">
                    <Badge
                      size="lg"
                      radius="xl"
                      variant="gradient"
                      gradient={{ from: 'purple.6', to: 'purple.4' }}
                      sx={{
                        background: chapter?.is_completed
                          ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                          : 'linear-gradient(135deg, var(--purple-600) 0%, var(--purple-400) 100%)',
                        color: 'white',
                        fontWeight: 700,
                      }}
                    >
                      {chapter?.is_completed ? (
                        <Group spacing={6} noWrap>
                          <IconCircleCheck size={16} />
                          <span>Completed</span>
                        </Group>
                      ) : (
                        'In Progress'
                      )}
                    </Badge>

                    {chapter?.estimated_minutes && (
                      <Group spacing={6} noWrap>
                        <ThemeIcon size="md" radius="xl" color="purple" variant="light">
                          <IconClock size={16} />
                        </ThemeIcon>
                        <Text size="sm" color="dimmed" weight={600}>
                          {t('estimatedTime', { minutes: chapter.estimated_minutes })}
                        </Text>
                      </Group>
                    )}
                  </Group>

                  <Title
                    order={1}
                    mb="sm"
                    sx={(theme) => ({
                      fontSize: '2.25rem',
                      fontWeight: 800,
                      background: theme.colorScheme === 'dark'
                        ? 'linear-gradient(135deg, var(--purple-400) 0%, var(--purple-300) 100%)'
                        : 'linear-gradient(135deg, var(--purple-700) 0%, var(--purple-500) 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      lineHeight: 1.2,
                    })}
                  >
                    {chapter?.caption || 'Chapter'}
                  </Title>

                  <Text size="md" color="dimmed" sx={{ maxWidth: '600px', lineHeight: 1.6 }}>
                    Continue your learning journey with this comprehensive chapter.
                  </Text>
                </Box>

                <Group spacing="sm" sx={{ flexShrink: 0 }}>
                  <Button
                    variant="light"
                    color="purple"
                    leftIcon={<IconDownload size={16} />}
                    onClick={handleDownloadPDF}
                    loading={downloadingPDF}
                    disabled={downloadingPDF || activeTab !== 'content'}
                    className="btn-modern transition-all duration-300"
                    sx={{
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(139, 92, 246, 0.3)',
                      },
                    }}
                  >
                    Download PDF
                  </Button>
                  <Button
                    variant="gradient"
                    gradient={{ from: 'green.6', to: 'green.4' }}
                    onClick={markChapterComplete}
                    loading={markingComplete}
                    disabled={markingComplete || chapter?.is_completed}
                    className="btn-modern transition-all duration-300"
                    sx={{
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                      },
                    }}
                  >
                    {chapter?.is_completed ? t('badge.completed') : t('buttons.markComplete')}
                  </Button>
                </Group>
              </Group>
            </Paper>

            {/* Modern Tabs with Purple Theming */}
            <Tabs
              value={activeTab}
              onTabChange={handleTabChange}
              mb="xl"
              sx={(theme) => ({
                '& .mantine-Tabs-tabsList': {
                  background: 'var(--bg-card)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: '16px',
                  padding: '8px',
                  gap: '4px',
                },
                '& .mantine-Tabs-tab': {
                  border: 'none',
                  borderRadius: '12px',
                  padding: '12px 20px',
                  fontWeight: 600,
                  color: theme.colorScheme === 'dark' ? theme.colors.gray[4] : theme.colors.gray[6],
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    background: 'rgba(139, 92, 246, 0.1)',
                    color: 'var(--purple-500)',
                    transform: 'translateY(-2px)',
                  },
                  '&[data-active]': {
                    background: 'linear-gradient(135deg, var(--purple-500) 0%, var(--purple-400) 100%)',
                    color: 'white',
                    boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                },
              })}
            >
              <Tabs.List>
                <Tabs.Tab value="content" icon={<IconBookmark size={16} />}>
                  {t('tabs.content')}
                </Tabs.Tab>
                {/* <Tabs.Tab value="flashcards" icon={<IconCards size={16} />}>Flashcards</Tabs.Tab>*/}
                {images.length > 0 && (
                  <Tabs.Tab value="images" icon={<IconPhoto size={16} />}>
                    {t('tabs.images')} ({images.length})
                  </Tabs.Tab>
                )}
                {files.length > 0 && (
                  <Tabs.Tab value="files" icon={<IconFileText size={16} />}>
                    {t('tabs.files')} ({files.length})
                  </Tabs.Tab>
                )}
                {hasQuestions && (
                  <Tabs.Tab
                    value="quiz"
                    icon={<IconQuestionMark size={16} />}
                    className={isBlinking ? 'quiz-tab-blinking' : ''}
                  >
                    {questionCount > 0 ? t('tabs.quiz', { count: questionCount }) : 'Quiz'}
                  </Tabs.Tab>
                )}
              </Tabs.List>

              <Tabs.Panel value="content" pt="md" style={{ width: '100%' }}>
                <FullscreenContentWrapper>
                  <Paper
                    ref={contentRef}
                    className="card-modern card-glass transition-all duration-300"
                    sx={{
                      background: 'var(--bg-card)',
                      backdropFilter: 'blur(20px)',
                      border: '1px solid rgba(139, 92, 246, 0.2)',
                      borderRadius: '16px',
                      padding: '32px',
                      width: '100%',
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                  >
                    {/* Subtle gradient overlay */}
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.02) 0%, rgba(168, 85, 247, 0.02) 100%)',
                        zIndex: 0,
                      }}
                    />
                    <div className="markdown-content" style={{ width: '100%', position: 'relative', zIndex: 1 }}>
                      <AiCodeWrapper>{chapter.content}</AiCodeWrapper>
                    </div>
                  </Paper>
                </FullscreenContentWrapper>
              </Tabs.Panel>

              {/* 
              <Tabs.Panel value="flashcards" pt="md" style={{ width: '100%' }}>
                <Paper 
                  className="card-modern card-glass transition-all duration-300"
                  sx={{
                    background: 'var(--bg-card)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    borderRadius: '16px',
                    padding: '32px',
                    width: '100%',
                  }}
                >
                  <FlashcardDeck courseId={courseId} chapterId={chapterId} />
                </Paper>
              </Tabs.Panel>
              */}

              <Tabs.Panel value="images" pt="md" style={{ width: '100%' }}>
                <Paper
                  className="card-modern card-glass transition-all duration-300"
                  sx={{
                    background: 'var(--bg-card)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    borderRadius: '16px',
                    padding: '32px',
                    width: '100%',
                  }}
                >
                  <Title order={3} mb="lg" sx={{ color: 'var(--purple-600)', fontWeight: 700 }}>
                    Chapter Images ({images.length})
                  </Title>
                  <MediaGallery
                    images={images}
                    onDelete={handleDeleteImage}
                    deletingItem={deletingItem}
                    isMobile={isMobile}
                  />
                </Paper>
              </Tabs.Panel>

              <Tabs.Panel value="files" pt="md" style={{ width: '100%' }}>
                <Paper
                  className="card-modern card-glass transition-all duration-300"
                  sx={{
                    background: 'var(--bg-card)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    borderRadius: '16px',
                    padding: '32px',
                    width: '100%',
                  }}
                >
                  <Title order={3} mb="lg" sx={{ color: 'var(--purple-600)', fontWeight: 700 }}>
                    Chapter Files ({files.length})
                  </Title>
                  <FileList
                    files={files}
                    onDelete={handleDeleteFile}
                    deletingItem={deletingItem}
                    mediaLoading={mediaLoading}
                  />
                </Paper>
              </Tabs.Panel>

              <Tabs.Panel value="quiz" pt="md" style={{ width: '100%' }}>
                <Paper
                  className="card-modern card-glass transition-all duration-300"
                  sx={{
                    background: 'var(--bg-card)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    borderRadius: '16px',
                    padding: '32px',
                    width: '100%',
                  }}
                >
                  <Quiz
                    key={quizKey}
                    courseId={courseId}
                    chapterId={chapterId}
                    onQuestionCountChange={(count) => {
                      setQuestionCount(count);
                      setHasQuestions(count > 0);
                    }}
                    style={{ width: '100%' }}
                  />
                </Paper>
              </Tabs.Panel>
            </Tabs>

            {/* Modern Footer Navigation */}
            <Paper
              radius="xl"
              p="lg"
              mt="xl"
              className="card-modern card-glass transition-all duration-300"
              sx={{
                background: 'var(--bg-card)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
              }}
            >
              <Group position="apart">
                <Button
                  variant="light"
                  color="purple"
                  leftIcon={<IconArrowBack size={16} />}
                  onClick={() => navigate(`/dashboard/courses/${courseId}`)}
                  className="btn-modern transition-all duration-300"
                  sx={{
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(139, 92, 246, 0.3)',
                    },
                  }}
                >
                  {t('buttons.backToCourse')}
                </Button>

                <Group spacing="sm">
                  <Button
                    variant="gradient"
                    gradient={{ from: 'green.6', to: 'green.4' }}
                    onClick={markChapterComplete}
                    loading={markingComplete}
                    disabled={markingComplete || chapter?.is_completed}
                    rightIcon={<IconCheck size={16} />}
                    className="btn-modern transition-all duration-300"
                    sx={{
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                      },
                    }}
                  >
                    {chapter?.is_completed ? t('badge.completed') : t('buttons.markComplete')}
                  </Button>
                </Group>
              </Group>
            </Paper>
          </>
        )}
      </Container>

      <ToolbarContainer courseId={courseId} chapterId={chapterId} />
    </div>
  );
}

export default ChapterView;