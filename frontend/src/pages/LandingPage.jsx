import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import {
  Container,
  Title,
  Text,
  Button,
  Grid,
  Card,
  Group,
  Image,
  Stack,
  List,
  ThemeIcon,
  Transition,
  Box,
  useMantineTheme,
  keyframes,
  createStyles,
  Badge,
  Flex,
} from "@mantine/core";

import {
  IconCheck,
  IconBrain,
  IconChartBar,
  IconUser,
  IconArrowRight,
  IconTrophy,
  IconSparkles,
  IconRocket,
  IconTarget,
  IconBolt,
  IconGhost,
} from "@tabler/icons-react";
import { useAuth } from "../contexts/AuthContext";

import { useMediaQuery } from '@mantine/hooks';

import { HeroAnimation } from "../components/HeroAnimation";

const fadeIn = keyframes({
  from: { opacity: 0, transform: "translateY(30px)" },
  to: { opacity: 1, transform: "translateY(0)" },
});

const slideInFromRight = keyframes({
  '0%': { transform: 'translateX(100px) scale(0.98)', opacity: 0 },
  '100%': { transform: 'translateX(0) scale(1)', opacity: 1 }
});

const float = keyframes({
  '0%, 100%': { transform: 'translateY(0)' },
  '50%': { transform: 'translateY(-10px)' }
});

const pulse = keyframes({
  '0%': { boxShadow: '0 0 0 0 rgba(139, 92, 246, 0.4)' },
  '70%': { boxShadow: '0 0 0 20px rgba(139, 92, 246, 0)' },
  '100%': { boxShadow: '0 0 0 0 rgba(139, 92, 246, 0)' }
});

const gradientShift = keyframes({
  '0%': { backgroundPosition: '0% 50%' },
  '50%': { backgroundPosition: '100% 50%' },
  '100%': { backgroundPosition: '0% 50%' }
});

const useStyles = createStyles((theme) => ({
  hero: {
    position: 'relative',
    paddingTop: theme.spacing.xl * 6,
    paddingBottom: theme.spacing.xl * 6,
    minHeight: 'calc(100vh - 80px)',
    display: 'flex',
    alignItems: 'center',
    overflow: 'hidden',
    background: theme.colorScheme === 'dark'
      ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f0f23 100%)'
      : 'linear-gradient(135deg, #fafafa 0%, #f8fafc 25%, #f1f5f9 50%, #ffffff 100%)',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: theme.colorScheme === 'dark'
        ? 'radial-gradient(ellipse 800px 600px at 50% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 50%)'
        : 'radial-gradient(ellipse 800px 600px at 50% 0%, rgba(139, 92, 246, 0.08) 0%, transparent 50%)',
      zIndex: 1,
    },
    '&::after': {
      content: '""',
      position: 'absolute',
      top: '20%',
      right: '-10%',
      width: '40%',
      height: '60%',
      background: theme.colorScheme === 'dark'
        ? 'radial-gradient(ellipse, rgba(168, 85, 247, 0.1) 0%, transparent 70%)'
        : 'radial-gradient(ellipse, rgba(168, 85, 247, 0.05) 0%, transparent 70%)',
      borderRadius: '50%',
      zIndex: 1,
    },
  },

  heroContent: {
    position: 'relative',
    zIndex: 3,
    animation: `${fadeIn} 1s ease-out`,
    [theme.fn.smallerThan('md')]: {
      textAlign: 'center',
    },
  },

  heroImage: {
    position: 'relative',
    zIndex: 2,
    '&::before': {
      content: '""',
      position: 'absolute',
      width: '120%',
      height: '120%',
      top: '-10%',
      left: '-10%',
      background: 'radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0) 70%)',
      borderRadius: '50%',
      zIndex: -1,
      animation: `${pulse} 4s infinite`,
    },
    [theme.fn.smallerThan('md')]: {
      marginTop: theme.spacing.xl * 2,
    },
  },

  badge: {
    background: theme.colorScheme === 'dark'
      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)'
      : 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
    border: `1px solid ${theme.colorScheme === 'dark' ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.2)'}`,
    color: theme.colorScheme === 'dark' ? '#c4b5fd' : '#7c3aed',
    fontWeight: 600,
    fontSize: '0.75rem',
    letterSpacing: '0.5px',
    textTransform: 'uppercase',
  },

  featureCard: {
    height: '100%',
    background: theme.colorScheme === 'dark'
      ? 'rgba(15, 15, 35, 0.6)'
      : 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(20px)',
    border: '1px solid',
    borderColor: theme.colorScheme === 'dark'
      ? 'rgba(139, 92, 246, 0.2)'
      : 'rgba(139, 92, 246, 0.1)',
    borderRadius: theme.radius.xl,
    padding: theme.spacing.xl * 1.5,
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    position: 'relative',
    overflow: 'hidden',
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
    '&:hover': {
      transform: 'translateY(-12px)',
      boxShadow: theme.colorScheme === 'dark'
        ? '0 25px 50px -12px rgba(139, 92, 246, 0.25)'
        : '0 25px 50px -12px rgba(139, 92, 246, 0.15)',
      borderColor: theme.colorScheme === 'dark'
        ? 'rgba(139, 92, 246, 0.4)'
        : 'rgba(139, 92, 246, 0.3)',
      '&::before': {
        opacity: 1,
      },
      '& .featureIcon': {
        transform: 'scale(1.1) rotate(5deg)',
        background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
        boxShadow: '0 8px 25px rgba(139, 92, 246, 0.4)',
      },
    },
  },

  featureIcon: {
    width: 64,
    height: 64,
    borderRadius: theme.radius.xl,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.lg,
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    background: theme.colorScheme === 'dark'
      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)'
      : 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)',
    border: `1px solid ${theme.colorScheme === 'dark' ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.2)'}`,
    position: 'relative',
    zIndex: 1,
  },

  section: {
    padding: '80px 0',
    position: 'relative',
    overflow: 'hidden',
    [theme.fn.smallerThan('sm')]: {
      padding: '60px 0',
    },
    '&:nth-of-type(even)': {
      background: theme.colorScheme === 'dark'
        ? 'linear-gradient(180deg, rgba(15, 15, 35, 0.4) 0%, rgba(26, 26, 46, 0.4) 100%)'
        : 'linear-gradient(180deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%)',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: theme.colorScheme === 'dark'
          ? 'radial-gradient(ellipse 1200px 800px at 50% 50%, rgba(139, 92, 246, 0.03) 0%, transparent 50%)'
          : 'radial-gradient(ellipse 1200px 800px at 50% 50%, rgba(139, 92, 246, 0.02) 0%, transparent 50%)',
        zIndex: 0,
      },
    },
  },

  gradient: {
    position: 'relative',
    background: theme.colorScheme === 'dark'
      ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)'
      : 'linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(168, 85, 247, 0.05) 100%)',
    borderRadius: theme.radius.xl,
    padding: theme.spacing.xl * 3,
    overflow: 'hidden',
    border: `1px solid ${theme.colorScheme === 'dark' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.1)'}`,
    backdropFilter: 'blur(20px)',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: theme.colorScheme === 'dark'
        ? 'linear-gradient(45deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)'
        : 'linear-gradient(45deg, rgba(139, 92, 246, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)',
      opacity: 0.5,
      zIndex: 0,
    },
  },

  ctaButton: {
    position: 'relative',
    overflow: 'hidden',
    padding: '14px 32px',
    borderRadius: theme.radius.xl,
    fontWeight: 600,
    letterSpacing: '0.3px',
    textTransform: 'none',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    fontSize: '1rem',
    '&:hover': {
      transform: 'translateY(-3px)',
    },
  },

  primaryButton: {
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #9333ea 100%)',
    backgroundSize: '200% 200%',
    color: 'white',
    border: 'none',
    boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
    animation: `${gradientShift} 3s ease infinite`,
    '&:hover': {
      background: 'linear-gradient(135deg, #7c3aed 0%, #9333ea 50%, #8b5cf6 100%)',
      boxShadow: '0 8px 25px rgba(139, 92, 246, 0.6)',
      transform: 'translateY(-3px) scale(1.02)',
    },
  },

  secondaryButton: {
    border: '2px solid',
    borderColor: theme.colorScheme === 'dark' ? '#8b5cf6' : '#7c3aed',
    color: theme.colorScheme === 'dark' ? '#c4b5fd' : '#7c3aed',
    background: 'transparent',
    '&:hover': {
      background: theme.colorScheme === 'dark'
        ? 'rgba(139, 92, 246, 0.1)'
        : 'rgba(139, 92, 246, 0.05)',
      borderColor: theme.colorScheme === 'dark' ? '#a855f7' : '#8b5cf6',
      transform: 'translateY(-3px)',
    },
  },

  floatingShape: {
    position: 'absolute',
    borderRadius: '50%',
    filter: 'blur(60px)',
    opacity: theme.colorScheme === 'dark' ? 0.15 : 0.08,
    zIndex: 0,
  },

  shape1: {
    width: '500px',
    height: '500px',
    background: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
    top: '-150px',
    right: '-150px',
    animation: `${float} 12s ease-in-out infinite`,
  },

  shape2: {
    width: '350px',
    height: '350px',
    background: 'linear-gradient(135deg, #a855f7, #9333ea)',
    bottom: '100px',
    left: '-100px',
    animation: `${float} 15s ease-in-out 2s infinite`,
  },

  shape3: {
    width: '250px',
    height: '250px',
    background: 'linear-gradient(135deg, #c084fc, #8b5cf6)',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    animation: `${float} 10s ease-in-out 1s infinite`,
  },

  // NEW: Styles for the product demo video
  videoContainer: {
    position: 'relative',
    overflow: 'hidden',
    width: '100%',
    paddingTop: '56.25%', // 16:9 Aspect Ratio
    borderRadius: theme.radius.lg,
    boxShadow: theme.shadows.xl,
    border: `1px solid ${theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[3]}`,
    marginTop: theme.spacing.xl * 2,
  },

  videoIframe: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
    width: '100%',
    height: '100%',
    border: 'none',
  },
}));

function LandingPage() {
  const { t } = useTranslation("landingPage");
  const { classes, cx } = useStyles();
  const theme = useMantineTheme();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);
  const isMobile = useMediaQuery('(max-width: 768px)');

  // Animation trigger on mount
  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 100); // Small delay to ensure mount
    return () => clearTimeout(timer);
  }, []);

  // Scroll to section helper
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <Box style={{ position: 'relative', overflowX: 'hidden' }}>
      {/* Floating shapes for visual interest */}
      <Box className={cx(classes.floatingShape, classes.shape1)} />
      <Box className={cx(classes.floatingShape, classes.shape2)} />
      <Box className={cx(classes.floatingShape, classes.shape3)} />

      {/* Hero Section */}
      <Box
        className={classes.hero}
        id="home"
        sx={{
          paddingTop: isMobile ? '6rem !important' : undefined,
        }}
      >
        <Container size="xl" px="md">
          <Grid gutter={50} align="center">
            <Grid.Col md={6} className={classes.heroContent}>
              <Transition mounted={visible} transition="slide-up" duration={800} delay={200}>
                {(styles) => (
                  <div style={styles}>
                    <Badge
                      className={classes.badge}
                      leftSection={<IconSparkles size={14} />}
                      size="lg"
                      radius="xl"
                      mb="xl"
                    >
                      {t('hero.pretitle', 'AI-Powered Learning Platform')}
                    </Badge>

                    <Title
                      order={1}
                      size={isMobile ? 42 : 64}
                      weight={800}
                      mb="lg"
                      sx={{
                        lineHeight: 1.1,
                        background: theme.colorScheme === 'dark'
                          ? 'linear-gradient(135deg, #ffffff 0%, #c4b5fd 50%, #a855f7 100%)'
                          : 'linear-gradient(135deg, #1f2937 0%, #7c3aed 50%, #8b5cf6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        backgroundSize: '200% 200%',
                        animation: `${gradientShift} 4s ease infinite`,
                        display: 'inline-block',
                        fontFamily: 'system-ui, -apple-system, sans-serif',
                      }}
                    >
                      {t('hero.title', 'Transform Learning with Intelligent AI')}
                    </Title>

                    <Text
                      size="xl"
                      color={theme.colorScheme === 'dark' ? 'gray.4' : 'gray.6'}
                      mb="xl"
                      style={{
                        maxWidth: '85%',
                        lineHeight: 1.7,
                        fontSize: '1.125rem',
                        fontWeight: 400,
                      }}
                    >
                      {t('hero.subtitle', 'Create personalized courses, generate interactive content, and track progress with our advanced AI-powered educational platform designed for the future of learning.')}
                    </Text>

                    <Flex gap="md" wrap="wrap">
                      <Button
                        size="lg"
                        rightSection={<IconRocket size={18} />}
                        onClick={() => navigate(isAuthenticated ? '/dashboard' : '/auth/signup')}
                        className={cx(classes.ctaButton, classes.primaryButton)}
                        radius="xl"
                      >
                        {isAuthenticated ? t('goToDashboard', 'Go to Dashboard') : t('getStarted', 'Start Building')}
                      </Button>
                      <Button
                        variant="outline"
                        size="lg"
                        leftSection={<IconTarget size={18} />}
                        onClick={() => scrollToSection('demo')}
                        className={cx(classes.ctaButton, classes.secondaryButton)}
                        radius="xl"
                      >
                        {t('watchDemo', 'Watch Demo')}
                      </Button>
                    </Flex>
                  </div>
                )}
              </Transition>
            </Grid.Col>




            <Grid.Col md={6}>
              <Transition mounted={visible} transition="pop" duration={800} delay={400}>
                {(styles) => (
                  <div
                    className={classes.heroImage}
                    style={{
                      ...styles,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minHeight: 350 // Ensures container has height for centering
                    }}
                  >
                    <HeroAnimation />
                  </div>
                )}
              </Transition>
            </Grid.Col>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Box id="features" className={classes.section}>
        <Container>
          <Stack align="center" spacing="md" mb="xl">
            <Badge
              size="lg"
              radius="xl"
              variant="light"
              color="violet"
              leftSection={<IconBolt size={16} />}
            >
              {t("features.badge", "Powerful Features")}
            </Badge>
            <Title order={2} align="center" fz="2.5rem" fw={800}>
              {t("features.title", "Everything You Need to Succeed")}
            </Title>
            <Text size="xl" color="dimmed" align="center" maw={600}>
              {t("features.subtitle", "Comprehensive tools designed to transform how you create, deliver, and track educational content.")}
            </Text>
          </Stack>

          <Grid gutter="xl">
            <Grid.Col sm={6} md={3}>
              <Transition mounted={visible} transition="pop" duration={600} delay={200}>
                {(styles) => (
                  <Card className={classes.featureCard} style={styles}>
                    <Stack spacing="lg">
                      <Box className={cx(classes.featureIcon, 'featureIcon')}>
                        <IconBrain size={28} color="#8b5cf6" />
                      </Box>
                      <Stack spacing={8}>
                        <Title order={3} fz="lg" fw={700}>{t("features.feature1Title", "AI Content Generation")}</Title>
                        <Text size="sm" c="dimmed" lh={1.6}>{t("features.feature1Text", "Generate comprehensive lesson plans, interactive quizzes, and engaging course materials instantly with advanced AI.")}</Text>
                      </Stack>
                    </Stack>
                  </Card>
                )}
              </Transition>
            </Grid.Col>

            <Grid.Col sm={6} md={3}>
              <Transition mounted={visible} transition="pop" duration={600} delay={400}>
                {(styles) => (
                  <Card className={classes.featureCard} style={styles}>
                    <Stack spacing="lg">
                      <Box className={cx(classes.featureIcon, 'featureIcon')}>
                        <IconChartBar size={28} color="#8b5cf6" />
                      </Box>
                      <Stack spacing={8}>
                        <Title order={3} fz="lg" fw={700}>{t("features.feature2Title", "Smart Analytics")}</Title>
                        <Text size="sm" c="dimmed" lh={1.6}>{t("features.feature2Text", "Track learning progress with intelligent insights and beautiful dashboards that reveal student engagement patterns.")}</Text>
                      </Stack>
                    </Stack>
                  </Card>
                )}
              </Transition>
            </Grid.Col>

            <Grid.Col sm={6} md={3}>
              <Transition mounted={visible} transition="pop" duration={600} delay={600}>
                {(styles) => (
                  <Card className={classes.featureCard} style={styles}>
                    <Stack spacing="lg">
                      <Box className={cx(classes.featureIcon, 'featureIcon')}>
                        <IconBolt size={28} color="#8b5cf6" />
                      </Box>
                      <Stack spacing={8}>
                        <Title order={3} fz="lg" fw={700}>{t("features.feature3Title", "Adaptive Learning")}</Title>
                        <Text size="sm" c="dimmed" lh={1.6}>{t("features.feature3Text", "Personalize every learning journey with AI that adapts to individual pace, style, and knowledge level.")}</Text>
                      </Stack>
                    </Stack>
                  </Card>
                )}
              </Transition>
            </Grid.Col>

            <Grid.Col sm={6} md={3}>
              <Transition mounted={visible} transition="pop" duration={600} delay={800}>
                {(styles) => (
                  <Card className={classes.featureCard} style={styles}>
                    <Stack spacing="lg">
                      <Box className={cx(classes.featureIcon, 'featureIcon')}>
                        <IconRocket size={28} color="#8b5cf6" />
                      </Box>
                      <Stack spacing={8}>
                        <Title order={3} fz="lg" fw={700}>{t("features.feature4Title", "Rapid Deployment")}</Title>
                        <Text size="sm" c="dimmed" lh={1.6}>{t("features.feature4Text", "Launch courses in minutes with our streamlined interface and automated content optimization.")}</Text>
                      </Stack>
                    </Stack>
                  </Card>
                )}
              </Transition>
            </Grid.Col>
          </Grid>
        </Container>
      </Box>

      {/* Award Section */}
      <Box id="award" className={classes.section}>
        <Container>
          <Transition mounted={visible} transition="fade" duration={800} delay={400}>
            {(styles) => (
              <Box className={classes.gradient} style={styles}>
                <Stack align="center" spacing="xl" sx={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
                  <Box
                    sx={{
                      width: 100,
                      height: 100,
                      borderRadius: theme.radius.xl,
                      background: theme.colorScheme === 'dark'
                        ? 'linear-gradient(135deg, #1f2937 0%, #374151 50%, #4b5563 100%)'
                        : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%)',
                      border: `2px solid ${theme.colorScheme === 'dark' ? '#8b5cf6' : '#7c3aed'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: theme.colorScheme === 'dark'
                        ? '0 10px 30px rgba(139, 92, 246, 0.3)'
                        : '0 10px 30px rgba(124, 58, 237, 0.2)',
                      animation: `${float} 6s ease-in-out infinite`,
                    }}
                  >
                    <IconGhost size={48} color={theme.colorScheme === 'dark' ? '#8b5cf6' : '#7c3aed'} />
                  </Box>
                  <Title order={2} size="2.75rem" fw={800}>
                    {t('award.title', 'Powered by Kiro AI')}
                  </Title>
                  <Title order={3} size="1.25rem" weight={500} color="dimmed" mt={-10}>
                    {t('award.subtitle', 'Built with the Future of Development')}
                  </Title>
                  <Text size="lg" maw={800} lh={1.7}>
                    {t('award.body', 'Mentora showcases what\'s possible when you build with Kiro - the AI-powered IDE that revolutionizes development. From intelligent code generation to automated testing, Kiro accelerated our development process and helped us create a more robust, scalable platform.')}
                  </Text>
                  <Group spacing="md" mt="xl">
                    <Button
                      component="a"
                      href="https://kiro.dev"
                      target="_blank"
                      rel="noopener noreferrer"
                      variant="outline"
                      size="md"
                      radius="xl"
                      leftSection={<IconRocket size={18} />}
                      className={cx(classes.ctaButton, classes.secondaryButton)}
                    >
                      {t('award.tryKiro', 'Experience Kiro')}
                    </Button>
                    <Button
                      component="a"
                      href="https://kiro.dev/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      variant="subtle"
                      size="md"
                      radius="xl"
                      leftSection={<IconArrowRight size={18} />}
                      color="violet"
                    >
                      {t('award.learnMore', 'See How We Built This')}
                    </Button>
                  </Group>
                </Stack>
              </Box>
            )}
          </Transition>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box id="how-it-works" className={classes.section}>
        <Container>
          <Grid gutter={50} align="center">
            <Grid.Col md={6}>
              <Transition mounted={visible} transition="slide-right" duration={800}>
                {(styles) => (
                  <div style={styles}>
                    <Image
                      radius="md"
                      src="https://images.unsplash.com/photo-1516321497487-e288fb19713f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80"
                      alt={t("howItWorks.imageAlt", "People collaborating on a project")}
                    />
                  </div>
                )}
              </Transition>
            </Grid.Col>
            <Grid.Col md={6}>
              <Transition mounted={visible} transition="slide-left" duration={800}>
                {(styles) => (
                  <Stack spacing="xl" style={styles}>
                    <Title order={2}>{t("howItWorks.title", "Get Started in Minutes")}</Title>
                    <List spacing="lg" size="lg" center icon={<ThemeIcon color="teal" size={28} radius="xl"><IconCheck size={18} /></ThemeIcon>}>
                      <List.Item>
                        <Text size="lg" weight={500}>{t("howItWorks.step1Title", "Sign Up")}</Text>
                        <Text color="dimmed">{t("howItWorks.step1Text", "Create your free account to get started.")}</Text>
                      </List.Item>
                      <List.Item>
                        <Text size="lg" weight={500}>{t("howItWorks.step2Title", "Create Your Course")}</Text>
                        <Text color="dimmed">{t("howItWorks.step2Text", "Use our AI assistant to build your curriculum.")}</Text>
                      </List.Item>
                      <List.Item>
                        <Text size="lg" weight={500}>{t("howItWorks.step3Title", "Enroll Students")}</Text>
                        <Text color="dimmed">{t("howItWorks.step3Text", "Invite learners to join your course.")}</Text>
                      </List.Item>
                      <List.Item>
                        <Text size="lg" weight={500}>{t("howItWorks.step4Title", "Analyze & Grow")}</Text>
                        <Text color="dimmed">{t("howItWorks.step4Text", "Use analytics to improve and expand.")}</Text>
                      </List.Item>
                    </List>
                  </Stack>
                )}
              </Transition>
            </Grid.Col>
          </Grid>
        </Container>
      </Box>

      {/* NEW: Product Demo Section */}
      <Box id="demo" className={classes.section}>
        <Container>
          <Stack align="center" spacing="md" sx={{ textAlign: 'center' }}>
            <Badge
              size="lg"
              radius="xl"
              variant="light"
              color="violet"
              leftSection={<IconTarget size={16} />}
            >
              {t("demo.badge", "Live Demo")}
            </Badge>
            <Title order={2} fz="2.5rem" fw={800}>
              {t("demo.title", "See Mentora in Action")}
            </Title>
            <Text size="xl" color="dimmed" maw={800} lh={1.6}>
              {t("demo.subtitle", "Experience the power of AI-driven course creation. Watch how our platform transforms learning materials into engaging, interactive educational experiences in minutes.")}
            </Text>
          </Stack>

          <Transition mounted={visible} transition="pop" duration={800} delay={400}>
            {(styles) => (
              <Box className={classes.videoContainer} style={styles}>
                <iframe
                  className={classes.videoIframe}
                  src="https://youtu.be/I0Nb0O1pSxM"
                  title="YouTube video player"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                ></iframe>
              </Box>
            )}
          </Transition>
        </Container>
      </Box>

      {/* Testimonial Section */}
      <Box id="testimonials" className={classes.section}>
        <Container>
          <Stack align="center" spacing="md" mb="xl">
            <Badge
              size="lg"
              radius="xl"
              variant="light"
              color="violet"
              leftSection={<IconUser size={16} />}
            >
              {t("testimonials.badge", "Success Stories")}
            </Badge>
            <Title order={2} align="center" fz="2.5rem" fw={800}>
              {t("testimonials.title", "Trusted by Thousands")}
            </Title>
          </Stack>
          <Grid>
            <Grid.Col sm={12} md={4}>
              <Transition mounted={visible} transition="fade" duration={1000} delay={200}>
                {(styles) => (
                  <Card shadow="sm" p="lg" radius="md" withBorder style={styles}>
                    <Text italic size="lg" mb="md">{t("testimonials.quote1", "This platform transformed how I create content. The AI saves me hours of work every week!")}</Text>
                    <Group>
                      <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: "50%",
                        background: "linear-gradient(135deg, #8b5cf6, #a855f7)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontWeight: 600,
                        fontSize: "1rem"
                      }}>JD</div>
                      <div>
                        <Text weight={500}>{t("testimonials.name1", "Jane Doe")}</Text>
                        <Text size="xs" color="dimmed">{t("testimonials.role1", "University Professor")}</Text>
                      </div>
                    </Group>
                  </Card>
                )}
              </Transition>
            </Grid.Col>
            <Grid.Col sm={12} md={4}>
              <Transition mounted={visible} transition="fade" duration={1000} delay={400}>
                {(styles) => (
                  <Card shadow="sm" p="lg" radius="md" withBorder style={styles}>
                    <Text italic size="lg" mb="md">{t("testimonials.quote2", "As a student, the personalized feedback is incredible. I feel like I have a personal tutor.")}</Text>
                    <Group>
                      <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: "50%",
                        background: "linear-gradient(135deg, #a855f7, #9333ea)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontWeight: 600,
                        fontSize: "1rem"
                      }}>JS</div>
                      <div>
                        <Text weight={500}>{t("testimonials.name2", "John Smith")}</Text>
                        <Text size="xs" color="dimmed">{t("testimonials.role2", "Online Learner")}</Text>
                      </div>
                    </Group>
                  </Card>
                )}
              </Transition>
            </Grid.Col>
            <Grid.Col sm={12} md={4}>
              <Transition mounted={visible} transition="fade" duration={1000} delay={600}>
                {(styles) => (
                  <Card shadow="sm" p="lg" radius="md" withBorder style={styles}>
                    <Text italic size="lg" mb="md">{t("testimonials.quote3", "The analytics dashboard is a game-changer for understanding student engagement.")}</Text>
                    <Group>
                      <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: "50%",
                        background: "linear-gradient(135deg, #9333ea, #7c3aed)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontWeight: 600,
                        fontSize: "1rem"
                      }}>RJ</div>
                      <div>
                        <Text weight={500}>{t("testimonials.name3", "Robert Johnson")}</Text>
                        <Text size="xs" color="dimmed">{t("testimonials.role3", "Corporate Trainer")}</Text>
                      </div>
                    </Group>
                  </Card>
                )}
              </Transition>
            </Grid.Col>
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box id="cta" py={100} className={classes.section}>
        <Container>
          <Transition mounted={visible} transition="fade" duration={800}>
            {(styles) => (
              <Stack align="center" spacing="xl" style={styles}>
                <Title order={2} align="center">
                  {t("cta.title", "Ready to Revolutionize Your Teaching?")}
                </Title>
                <Text size="xl" align="center" color="dimmed" maw={600} mx="auto">
                  {t("cta.subtitle", "Join thousands of educators and learners who are shaping the future of education. Get started today for free.")}
                </Text>
                <Button
                  onClick={() => navigate(isAuthenticated ? '/dashboard' : '/auth/signup')}
                  size="xl"
                  radius="xl"
                  className={cx(classes.ctaButton, classes.primaryButton)}
                  px="3rem"
                  py="1rem"
                  fw={700}
                  fz="1.125rem"
                  rightSection={<IconRocket size={20} />}
                >
                  {isAuthenticated ? t('cta.createNextCourse', 'Create Your Next Course') : t("cta.getStarted", "Start Building Today")}
                </Button>
              </Stack>
            )}
          </Transition>
        </Container>
      </Box>
    </Box>
  );
}

export default LandingPage;