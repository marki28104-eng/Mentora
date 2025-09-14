import { ActionIcon, Tooltip } from '@mantine/core';
import { IconSun, IconMoon } from '@tabler/icons-react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle = ({ size = 'md', variant = 'subtle', ...props }) => {
        const { colorScheme, toggleColorScheme, isTransitioning } = useTheme();

        return (
                <Tooltip
                        label={colorScheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
                        position="bottom"
                >
                        <ActionIcon
                                onClick={() => toggleColorScheme()}
                                size={size}
                                variant={variant}
                                disabled={isTransitioning}
                                className="transition-smooth hover-scale"
                                style={{
                                        opacity: isTransitioning ? 0.6 : 1,
                                        transform: isTransitioning ? 'scale(0.95)' : 'scale(1)',
                                }}
                                {...props}
                        >
                                {colorScheme === 'dark' ? (
                                        <IconSun size={18} className="animate-pulse" />
                                ) : (
                                        <IconMoon size={18} />
                                )}
                        </ActionIcon>
                </Tooltip>
        );
};

export default ThemeToggle;