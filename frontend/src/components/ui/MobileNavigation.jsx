import React, { useState } from 'react';
import {
        Drawer,
        Button,
        ActionIcon,
        Box,
        Group,
        Text,
        Divider,
        Stack
} from '@mantine/core';
import {
        IconMenu2,
        IconX,
        IconHome2,
        IconSettings,
        IconUser,
        IconLogout
} from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import './MobileNavigation.css';

const MobileNavigation = ({
        opened,
        onClose,
        onToggle,
        children
}) => {
        const navigate = useNavigate();
        const { user, logout, isAuthenticated } = useAuth();
        const { t } = useTranslation(['navigation', 'app']);

        const handleLogout = () => {
                logout();
                navigate('/auth/login');
                onClose();
        };

        const handleNavigation = (path) => {
                navigate(path);
                onClose();
        };

        const navigationItems = [
                {
                        icon: <IconHome2 size={20} />,
                        label: t('dashboard', { ns: 'navigation' }),
                        path: '/dashboard',
                        color: 'violet'
                },
                {
                        icon: <IconSettings size={20} />,
                        label: t('settings', { ns: 'navigation' }),
                        path: '/dashboard/settings',
                        color: 'violet'
                },
        ];

        return (
                <>
                        {/* Mobile Menu Toggle Button */}
                        <ActionIcon
                                variant="light"
                                color="violet"
                                size="lg"
                                radius="xl"
                                onClick={onToggle}
                                className="mobile-nav-toggle transition-all hover:-translate-y-1 hover:shadow-purple-md"
                                sx={{
                                        background: 'rgba(139, 92, 246, 0.08)',
                                        border: '1px solid rgba(139, 92, 246, 0.2)',
                                        color: 'var(--purple-500)',
                                        '&:hover': {
                                                background: 'rgba(139, 92, 246, 0.12)',
                                                borderColor: 'rgba(139, 92, 246, 0.3)',
                                        },
                                        display: { base: 'flex', md: 'none' },
                                }}
                        >
                                {opened ? <IconX size={20} /> : <IconMenu2 size={20} />}
                        </ActionIcon>

                        {/* Mobile Navigation Drawer */}
                        <Drawer
                                opened={opened}
                                onClose={onClose}
                                position="left"
                                size="280px"
                                padding="md"
                                className="mobile-nav-drawer"
                                overlayProps={{
                                        opacity: 0.5,
                                        blur: 4,
                                }}
                                styles={(theme) => ({
                                        drawer: {
                                                background: 'var(--bg-card)',
                                                backdropFilter: 'blur(20px)',
                                                border: '1px solid rgba(139, 92, 246, 0.1)',
                                        },
                                        header: {
                                                background: 'transparent',
                                                borderBottom: '1px solid rgba(139, 92, 246, 0.1)',
                                                paddingBottom: theme.spacing.md,
                                        },
                                        body: {
                                                padding: 0,
                                        },
                                })}
                        >
                                <Box className="mobile-nav-content">
                                        {/* User Profile Section */}
                                        {isAuthenticated && user && (
                                                <Box className="mobile-nav-profile glass-card" p="md" mb="md">
                                                        <Group spacing="sm">
                                                                <Box
                                                                        sx={{
                                                                                width: 40,
                                                                                height: 40,
                                                                                borderRadius: '50%',
                                                                                background: 'linear-gradient(135deg, var(--purple-500), var(--purple-600))',
                                                                                display: 'flex',
                                                                                alignItems: 'center',
                                                                                justifyContent: 'center',
                                                                                color: 'white',
                                                                                fontWeight: 600,
                                                                                fontSize: '14px',
                                                                        }}
                                                                >
                                                                        {user.username ? user.username.substring(0, 2).toUpperCase() : <IconUser size={18} />}
                                                                </Box>
                                                                <Box>
                                                                        <Text size="sm" weight={600} color="var(--text-primary)">
                                                                                {user.username}
                                                                        </Text>
                                                                        <Text size="xs" color="var(--text-secondary)">
                                                                                {t('onlineStatusBadge', { ns: 'app', defaultValue: 'Online' })}
                                                                        </Text>
                                                                </Box>
                                                        </Group>
                                                </Box>
                                        )}

                                        {/* Navigation Items */}
                                        <Stack spacing="xs" px="md">
                                                {navigationItems.map((item, index) => (
                                                        <Button
                                                                key={index}
                                                                variant="light"
                                                                color={item.color}
                                                                leftIcon={item.icon}
                                                                onClick={() => handleNavigation(item.path)}
                                                                className="mobile-nav-item transition-all hover:-translate-y-1"
                                                                sx={{
                                                                        justifyContent: 'flex-start',
                                                                        height: 48,
                                                                        background: 'rgba(139, 92, 246, 0.05)',
                                                                        border: '1px solid rgba(139, 92, 246, 0.1)',
                                                                        borderRadius: 12,
                                                                        '&:hover': {
                                                                                background: 'rgba(139, 92, 246, 0.1)',
                                                                                borderColor: 'rgba(139, 92, 246, 0.2)',
                                                                                transform: 'translateY(-2px)',
                                                                        },
                                                                }}
                                                        >
                                                                {item.label}
                                                        </Button>
                                                ))}
                                        </Stack>

                                        {/* Custom Content (e.g., Course Sidebar) */}
                                        {children && (
                                                <>
                                                        <Divider my="md" color="rgba(139, 92, 246, 0.1)" />
                                                        <Box px="md">
                                                                {children}
                                                        </Box>
                                                </>
                                        )}

                                        {/* Logout Button */}
                                        {isAuthenticated && (
                                                <>
                                                        <Divider my="md" color="rgba(139, 92, 246, 0.1)" />
                                                        <Box px="md" pb="md">
                                                                <Button
                                                                        variant="light"
                                                                        color="red"
                                                                        leftIcon={<IconLogout size={20} />}
                                                                        onClick={handleLogout}
                                                                        fullWidth
                                                                        className="transition-all hover:-translate-y-1"
                                                                        sx={{
                                                                                height: 48,
                                                                                borderRadius: 12,
                                                                        }}
                                                                >
                                                                        {t('logout', { ns: 'navigation' })}
                                                                </Button>
                                                        </Box>
                                                </>
                                        )}
                                </Box>
                        </Drawer>
                </>
        );
};

// Mobile Navigation Hook
export const useMobileNavigation = () => {
        const [opened, setOpened] = useState(false);

        const open = () => setOpened(true);
        const close = () => setOpened(false);
        const toggle = () => setOpened((prev) => !prev);

        return {
                opened,
                open,
                close,
                toggle,
        };
};

export default MobileNavigation;