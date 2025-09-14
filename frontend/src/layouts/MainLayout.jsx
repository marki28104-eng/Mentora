import { Outlet, useLocation } from 'react-router-dom';
import { useMediaQuery } from '@mantine/hooks';
import {
  AppShell,
  Header,
  Group,
  useMantineTheme,
  ActionIcon,
  Box,
  Button,
  Avatar,
  Menu,
  useMantineColorScheme,
  Badge,
  Divider,
  UnstyledButton,
  Text,

} from '@mantine/core';
import {
  IconSettings,
  IconSun,
  IconMoonStars,
  IconUser,
  IconLogout,
  IconInfoCircle,
  IconHome2,

} from '@tabler/icons-react';
import AppFooter from '../components/AppFooter';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import MobileNavigation, { useMobileNavigation } from '../components/ui/MobileNavigation';


function MainLayout() {
  const theme = useMantineTheme();
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth(); // Ensure isAuthenticated is destructured
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const { t } = useTranslation(['app', 'navigation', 'common']); // Initialize translation hook for app, navigation, and common namespaces
  // Search functionality moved to SearchBar component
  const { pathname } = useLocation();
  const dark = colorScheme === 'dark';
  const isMobile = useMediaQuery('(max-width: 768px)'); // Add mobile detection
  const mobileNav = useMobileNavigation();

  // Logic to determine avatar source
  let avatarSrc = null;
  if (user && user.profile_image_base64) {
    if (user.profile_image_base64.startsWith('data:image')) {
      avatarSrc = user.profile_image_base64;
    } else {
      avatarSrc = `data:image/jpeg;base64,${user.profile_image_base64}`;
    }
  }

  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <AppShell
      styles={{
        main: {
          background: dark ? theme.colors.dark[8] : theme.colors.gray[0],
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          width: '100%',
          padding: 0,
          overflowX: 'hidden',
          touchAction: 'manipulation',
          textSizeAdjust: '100%',
        },
      }}
      header={
        <Header
          height={{ base: 60, md: 70 }}
          p="md"
          className="glass-nav transition-all"
          sx={(theme) => ({
            background: dark
              ? 'var(--bg-card)'
              : 'var(--bg-card)',
            backdropFilter: 'blur(20px)',
            borderBottom: `1px solid rgba(139, 92, 246, 0.1)`,
            boxShadow: dark
              ? '0 4px 20px rgba(139, 92, 246, 0.1)'
              : '0 4px 20px rgba(139, 92, 246, 0.05)',
            zIndex: 200,
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: dark
                ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)'
                : 'linear-gradient(135deg, rgba(139, 92, 246, 0.02) 0%, rgba(168, 85, 247, 0.02) 100%)',
              pointerEvents: 'none',
            },
          })}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            height: '100%',
            position: 'relative',
            zIndex: 1
          }}>
            {(!isMobile || isAuthenticated) && (
              <RouterLink
                to={isAuthenticated ? "/dashboard" : "/"}
                style={{ textDecoration: "none" }}
                className="transition-transform hover:scale-105"
              >
                <img
                  src="/mentora_schrift_türk_2.svg"
                  alt="Mentora"
                  style={{
                    height: 40,
                    width: 'auto',
                    filter: 'drop-shadow(0 2px 8px rgba(139, 92, 246, 0.4))',
                    cursor: 'pointer',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  }}
                />
              </RouterLink>
            )}

            <Box sx={{ flexGrow: 1 }} />

            <Box sx={{ flexGrow: 1, '@media (min-width: 769px)': { display: 'none' } }} />

            <Group spacing="md">
              {/* Mobile Navigation Toggle */}
              {isMobile && isAuthenticated && (
                <MobileNavigation
                  opened={mobileNav.opened}
                  onClose={mobileNav.close}
                  onToggle={mobileNav.toggle}
                />
              )}

              {(!isMobile || isAuthenticated) && (
                <ActionIcon
                  variant="light"
                  color="violet"
                  onClick={() => toggleColorScheme()}
                  title={t('colorSchemeToggleTitle', { ns: 'app', defaultValue: 'Toggle color scheme' })}
                  size="lg"
                  radius="xl"
                  className="transition-all hover:-translate-y-1 hover:shadow-purple-md"
                  sx={{
                    background: dark
                      ? 'rgba(139, 92, 246, 0.1)'
                      : 'rgba(139, 92, 246, 0.08)',
                    border: `1px solid rgba(139, 92, 246, 0.2)`,
                    color: 'var(--purple-500)',
                    '&:hover': {
                      background: dark
                        ? 'rgba(139, 92, 246, 0.15)'
                        : 'rgba(139, 92, 246, 0.12)',
                      borderColor: 'rgba(139, 92, 246, 0.3)',
                      color: dark ? 'var(--purple-400)' : 'var(--purple-600)',
                    },
                    display: isMobile && !isAuthenticated ? 'none' : 'flex',
                  }}
                >
                  {dark ? <IconSun size={20} /> : <IconMoonStars size={20} />}
                </ActionIcon>
              )}

              {isAuthenticated && user ? (
                <Menu shadow="xl" width={240} withinPortal={true} zIndex={300}>
                  <Menu.Target>
                    <UnstyledButton
                      className="transition-all hover:-translate-y-1 hover:shadow-purple-md"
                      sx={{
                        padding: theme.spacing.xs,
                        borderRadius: theme.radius.xl,
                        background: dark
                          ? 'rgba(139, 92, 246, 0.05)'
                          : 'rgba(139, 92, 246, 0.03)',
                        border: `1px solid rgba(139, 92, 246, 0.1)`,
                        '&:hover': {
                          background: dark
                            ? 'rgba(139, 92, 246, 0.1)'
                            : 'rgba(139, 92, 246, 0.08)',
                          borderColor: 'rgba(139, 92, 246, 0.2)',
                        },
                      }}
                    >
                      <Group spacing="xs">
                        <Avatar
                          key={avatarSrc || user.id}
                          src={avatarSrc}
                          radius="xl"
                          alt={user.username || t('userAvatarAlt', { ns: 'app', defaultValue: 'User avatar' })}
                          color="violet"
                          sx={{
                            cursor: 'pointer',
                            border: `2px solid rgba(139, 92, 246, 0.3)`,
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            '&:hover': {
                              border: `2px solid var(--purple-500)`,
                              boxShadow: '0 0 20px rgba(139, 92, 246, 0.4)',
                            },
                          }}
                        >
                          {!avatarSrc && user.username ? user.username.substring(0, 2).toUpperCase() : (!avatarSrc ? <IconUser size={18} /> : null)}
                        </Avatar>
                        <Box>
                          <Text size="sm" weight={500}>{user.username}</Text>
                          <Badge
                            size="xs"
                            variant="light"
                            color="violet"
                            sx={{
                              textTransform: 'none',
                              background: 'rgba(139, 92, 246, 0.1)',
                              color: 'var(--purple-600)',
                              border: '1px solid rgba(139, 92, 246, 0.2)'
                            }}
                          >
                            {t('onlineStatusBadge', { ns: 'app', defaultValue: 'Online' })}
                          </Badge>
                        </Box>
                      </Group>
                    </UnstyledButton>
                  </Menu.Target>
                  <Menu.Dropdown
                    className="glass-card"
                    sx={{
                      background: 'var(--bg-card)',
                      backdropFilter: 'blur(20px)',
                      border: `1px solid rgba(139, 92, 246, 0.2)`,
                      boxShadow: dark
                        ? '0 20px 40px rgba(139, 92, 246, 0.15)'
                        : '0 20px 40px rgba(139, 92, 246, 0.1)',
                      zIndex: 300,
                      borderRadius: theme.radius.lg,
                    }}
                  >
                    <Menu.Item
                      icon={<IconHome2 size={16} />}
                      onClick={() => navigate('/dashboard')}
                      className="transition-colors"
                      sx={{
                        borderRadius: theme.radius.md,
                        margin: '4px',
                        '&:hover': {
                          background: 'rgba(139, 92, 246, 0.1)',
                          color: 'var(--purple-600)',
                        },
                      }}
                    >
                      {t('dashboard', { ns: 'navigation' })}
                    </Menu.Item>
                    {/*<Menu.Item 
                      icon={<IconChartLine size={14} />} 
                      onClick={() => navigate('/dashboard/statistics')}
                      sx={{
                        '&:hover': {
                          backgroundColor: dark ? theme.colors.dark[6] : theme.colors.gray[1],
                        },
                      }}
                    >
                      {t('statistics', { ns: 'navigation' })}
                    </Menu.Item>
                    */}
                    <Menu.Item
                      icon={<IconSettings size={16} />}
                      onClick={() => navigate('/dashboard/settings')}
                      className="transition-colors"
                      sx={{
                        borderRadius: theme.radius.md,
                        margin: '4px',
                        '&:hover': {
                          background: 'rgba(139, 92, 246, 0.1)',
                          color: 'var(--purple-600)',
                        },
                      }}
                    >
                      {t('settings', { ns: 'navigation' })}
                    </Menu.Item>
                    <Divider />
                    <Menu.Item
                      icon={<IconInfoCircle size={16} />}
                      onClick={() => navigate('/about')}
                      className="transition-colors"
                      sx={{
                        borderRadius: theme.radius.md,
                        margin: '4px',
                        '&:hover': {
                          background: 'rgba(139, 92, 246, 0.1)',
                          color: 'var(--purple-600)',
                        },
                      }}
                    >
                      {t('about', { ns: 'navigation' })}
                    </Menu.Item>
                    <Menu.Item
                      icon={<IconLogout size={16} />}
                      onClick={handleLogout}
                      color="red"
                      className="transition-colors"
                      sx={{
                        borderRadius: theme.radius.md,
                        margin: '4px',
                        '&:hover': {
                          backgroundColor: `${theme.colors.red[6]}15`,
                          color: theme.colors.red[6],
                        },
                      }}
                    >
                      {t('logout', { ns: 'navigation' })}
                    </Menu.Item>
                  </Menu.Dropdown>
                </Menu>
              ) : (
                !['/auth/login', '/auth/signup'].includes(pathname) && (
                  <Group spacing="xs">
                    <Button
                      component={RouterLink}
                      to="/auth/login"
                      variant="light"
                      color="violet"
                      radius="xl"
                      className="transition-all hover:-translate-y-1 hover:shadow-purple-md"
                      sx={{
                        background: 'rgba(139, 92, 246, 0.08)',
                        border: '1px solid rgba(139, 92, 246, 0.2)',
                        color: 'var(--purple-600)',
                        '&:hover': {
                          background: 'rgba(139, 92, 246, 0.12)',
                          borderColor: 'rgba(139, 92, 246, 0.3)',
                        },
                      }}
                    >
                      {t('login', { ns: 'navigation' })}
                    </Button>
                    <Button
                      component={RouterLink}
                      to="/auth/signup"
                      variant="gradient"
                      gradient={{ from: 'violet', to: 'grape', deg: 135 }}
                      radius="xl"
                      className="btn-purple-primary transition-all hover:-translate-y-1 hover:shadow-purple-lg"
                      sx={{
                        background: 'linear-gradient(135deg, var(--purple-600) 0%, var(--purple-500) 50%, var(--purple-700) 100%)',
                        border: 'none',
                        boxShadow: '0 4px 15px rgba(139, 92, 246, 0.4)',
                        '&:hover': {
                          boxShadow: '0 8px 25px rgba(139, 92, 246, 0.6)',
                        },
                      }}
                    >
                      {t('register', { ns: 'navigation' })}
                    </Button>
                  </Group>
                )
              )}
            </Group>
          </div>
        </Header>
      }
    >
      <Box sx={{ flex: 1 }}>
        <Outlet />
      </Box>
      <AppFooter />
    </AppShell>
  );
}

export default MainLayout;