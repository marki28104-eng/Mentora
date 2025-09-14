import { Box, Text } from '@mantine/core';
import { LoadingSpinner } from './LoadingSpinner';
import { Navigation } from './Navigation';
import { IconHome2, IconSettings, IconUser } from '@tabler/icons-react';

const ComponentTest = () => {
        const navItems = [
                {
                        key: 'home',
                        to: '/dashboard',
                        label: 'Dashboard',
                        icon: <IconHome2 size={16} />
                },
                {
                        key: 'settings',
                        to: '/settings',
                        label: 'Settings',
                        icon: <IconSettings size={16} />
                },
                {
                        key: 'profile',
                        to: '/profile',
                        label: 'Profile',
                        icon: <IconUser size={16} />
                }
        ];

        return (
                <Box p="md">
                        <Text size="lg" weight={600} mb="md">Component Test</Text>

                        <Box mb="xl">
                                <Text size="md" weight={500} mb="sm">Loading Spinner</Text>
                                <LoadingSpinner size="md" variant="purple" text="Loading..." />
                        </Box>

                        <Box mb="xl">
                                <Text size="md" weight={500} mb="sm">Navigation - Horizontal</Text>
                                <Navigation items={navItems} variant="horizontal" />
                        </Box>

                        <Box mb="xl">
                                <Text size="md" weight={500} mb="sm">Navigation - Vertical</Text>
                                <Navigation items={navItems} variant="vertical" />
                        </Box>
                </Box>
        );
};

export default ComponentTest;