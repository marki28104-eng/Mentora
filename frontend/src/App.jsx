import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { MantineProvider } from '@mantine/core';
import { AuthProvider } from './contexts/AuthContext';
import { ToolbarProvider } from './contexts/ToolbarContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { PomodoroProvider } from './contexts/PomodoroContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import UmamiTracker from './components/UmamiTracker';
import LearningTracker from './components/LearningTracker';

import './i18n/i18n';

// Pages
import Dashboard from './pages/Dashboard.jsx';
import CreateCourse from './pages/CreateCourse';
import CourseView from './pages/CourseView';
import ChapterView from './pages/ChapterView';
import Login from './pages/Login';
import Register from './pages/Register';
import LandingPage from './pages/LandingPage';
import PricingPage from './pages/PricingPage';
import AppLayout from './layouts/AppLayout';
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';
import AdminProtectedRoute from './components/AdminProtectedRoute';
import SettingsPage from './pages/SettingsPage';
import StatisticsPage from './pages/StatisticsPage';
import OAuthCallbackPage from './pages/OAuthCallbackPage';
import Impressum from './pages/Impressum';
import Privacy from './pages/Privacy';
import About from './pages/About';
import PublicCourses from './pages/PublicCourses';
import MyCourses from './pages/MyCourses';
import NotFoundPage from './pages/NotFoundPage';
import AdminView from './pages/AdminView';
import AnkiGeneratorDashboard from "./pages/AnkiGenerator/AnkiGeneratorDashboard.jsx";
import AnkiProcessingStatus from "./pages/AnkiGenerator/AnkiProcessingStatus.jsx";

// Enhanced Mantine theme configuration component
const MantineThemeProvider = ({ children }) => {
  const { colorScheme } = useTheme();

  const mantineTheme = {
    colorScheme: colorScheme,
    primaryColor: 'purple',
    colors: {
      purple: colorScheme === 'dark' ? [
        '#1e1b4b', // 50 - Dark mode
        '#312e81', // 100
        '#3730a3', // 200
        '#4338ca', // 300
        '#5b21b6', // 400
        '#7c3aed', // 500 - Primary
        '#8b5cf6', // 600
        '#a78bfa', // 700
        '#c4b5fd', // 800
        '#ddd6fe'  // 900
      ] : [
        '#faf5ff', // 50 - Light mode
        '#f3e8ff', // 100
        '#e9d5ff', // 200
        '#d8b4fe', // 300
        '#c084fc', // 400
        '#a855f7', // 500 - Primary
        '#9333ea', // 600
        '#7c3aed', // 700
        '#6b21b6', // 800
        '#581c87'  // 900
      ],
      // Keep violet for backward compatibility during transition
      violet: [
        '#f3f0ff',
        '#e9e5ff',
        '#d9d4ff',
        '#c4b5fd',
        '#a78bfa',
        '#8b5cf6',
        '#7c3aed',
        '#6d28d9',
        '#5b21b6',
        '#4c1d95'
      ],
    },
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    headings: {
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
      fontWeight: 600,
    },
    components: {
      Button: {
        styles: (theme) => ({
          root: {
            fontWeight: 600,
            borderRadius: '12px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              transform: 'translateY(-2px)',
            },
          },
        }),
      },
      Card: {
        styles: (theme) => ({
          root: {
            borderRadius: '16px',
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            border: `1px solid ${theme.colorScheme === 'dark'
              ? 'rgba(139, 92, 246, 0.2)'
              : 'rgba(139, 92, 246, 0.1)'}`,
            backdropFilter: 'blur(20px)',
            '&:hover': {
              transform: 'translateY(-4px)',
              borderColor: theme.colorScheme === 'dark'
                ? 'rgba(139, 92, 246, 0.4)'
                : 'rgba(139, 92, 246, 0.3)',
            },
          },
        }),
      },
      Paper: {
        styles: (theme) => ({
          root: {
            borderRadius: '12px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          },
        }),
      },
      TextInput: {
        styles: (theme) => ({
          input: {
            borderRadius: '8px',
            transition: 'all 0.2s ease',
            '&:focus': {
              borderColor: theme.colors.purple[5],
              boxShadow: `0 0 0 2px ${theme.colors.purple[1]}`,
            },
          },
        }),
      },
      Select: {
        styles: (theme) => ({
          input: {
            borderRadius: '8px',
            transition: 'all 0.2s ease',
            '&:focus': {
              borderColor: theme.colors.purple[5],
              boxShadow: `0 0 0 2px ${theme.colors.purple[1]}`,
            },
          },
        }),
      },
      Textarea: {
        styles: (theme) => ({
          input: {
            borderRadius: '8px',
            transition: 'all 0.2s ease',
            '&:focus': {
              borderColor: theme.colors.purple[5],
              boxShadow: `0 0 0 2px ${theme.colors.purple[1]}`,
            },
          },
        }),
      },
    },
  };

  return (
    <MantineProvider withGlobalStyles withNormalizeCSS theme={mantineTheme}>
      {children}
    </MantineProvider>
  );
};

function App() {
  return (
    <ThemeProvider>
      <MantineThemeProvider>
        <LanguageProvider>
          <AuthProvider>
            <ToolbarProvider>
              <PomodoroProvider>
                <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                  {/* Umami Analytics Integration */}
                  <UmamiTracker
                    websiteId={import.meta.env.VITE_UMAMI_WEBSITE_ID}
                    src={import.meta.env.VITE_UMAMI_SRC}
                    domains={import.meta.env.VITE_UMAMI_DOMAINS?.split(',')}
                  />
                  <LearningTracker>
                    <AppContent />
                  </LearningTracker>
                </BrowserRouter>
              </PomodoroProvider>
            </ToolbarProvider>
          </AuthProvider>
        </LanguageProvider>
      </MantineThemeProvider>
    </ThemeProvider>
  );
}

// Separate component for app content to access theme context
const AppContent = () => {
  const { colorScheme } = useTheme();

  return (
    <>
      <Routes>
        {/* Public routes with MainLayout */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/signup" element={<Register />} />
          <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/impressum" element={<Impressum />} />
          <Route path="/privacy" element={<Privacy />} />
        </Route>

        {/* Protected routes now based at /dashboard */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<AppLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="public-courses" element={<PublicCourses />} />
            <Route path="my-courses" element={<MyCourses />} />
            <Route path="create-course" element={<CreateCourse />} />
            <Route path="courses/:courseId" element={<CourseView />} />
            <Route path="courses/:courseId/chapters/:chapterId" element={<ChapterView />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="statistics" element={<StatisticsPage />} />
            <Route path="anki-generator" element={<AnkiGeneratorDashboard />} />
            <Route path="anki-generator/processing/:taskId" element={<AnkiProcessingStatus />} />
          </Route>
        </Route>

        {/* Admin-only routes */}
        <Route element={<AdminProtectedRoute />}>
          <Route path="/admin" element={<AppLayout />}>
            <Route index element={<AdminView />} />
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>

      <ToastContainer
        position="top-right"
        autoClose={3000}
        theme={colorScheme}
        toastClassName="transition-smooth"
      />
    </>
  );
};

export default App;