import { createContext, useContext, useState, useEffect } from 'react';
import { ColorSchemeProvider } from '@mantine/core';

const ThemeContext = createContext();

export const useTheme = () => {
        const context = useContext(ThemeContext);
        if (!context) {
                throw new Error('useTheme must be used within a ThemeProvider');
        }
        return context;
};

export const ThemeProvider = ({ children }) => {
        // Initialize theme state with system preference detection
        const [colorScheme, setColorScheme] = useState(() => {
                // Check localStorage first
                const savedTheme = localStorage.getItem('mentora-color-scheme');
                if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
                        return savedTheme;
                }

                // Fall back to system preference
                return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        });

        const [isTransitioning, setIsTransitioning] = useState(false);

        // Theme persistence logic
        const persistTheme = (theme) => {
                try {
                        localStorage.setItem('mentora-color-scheme', theme);
                } catch (error) {
                        console.warn('Failed to save theme preference:', error);
                }
        };

        // Enhanced theme toggle with smooth transitions
        const toggleColorScheme = (value) => {
                setIsTransitioning(true);

                const nextColorScheme = value || (colorScheme === 'dark' ? 'light' : 'dark');

                // Add transition class to document
                document.documentElement.classList.add('theme-transitioning');

                // Update theme after a brief delay to allow transition setup
                setTimeout(() => {
                        setColorScheme(nextColorScheme);
                        persistTheme(nextColorScheme);

                        // Remove transition class after transition completes
                        setTimeout(() => {
                                document.documentElement.classList.remove('theme-transitioning');
                                setIsTransitioning(false);
                        }, 300);
                }, 50);
        };

        // System preference detection and auto-switching
        useEffect(() => {
                const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

                const handleSystemThemeChange = (e) => {
                        // Only auto-switch if user hasn't manually set a preference
                        const savedTheme = localStorage.getItem('mentora-color-scheme');
                        if (!savedTheme) {
                                const systemTheme = e.matches ? 'dark' : 'light';
                                setColorScheme(systemTheme);
                        }
                };

                // Listen for system theme changes
                mediaQuery.addEventListener('change', handleSystemThemeChange);

                return () => {
                        mediaQuery.removeEventListener('change', handleSystemThemeChange);
                };
        }, []);

        // Apply theme to document element for CSS custom properties
        useEffect(() => {
                document.documentElement.setAttribute('data-mantine-color-scheme', colorScheme);
                document.documentElement.setAttribute('data-theme', colorScheme);

                // Update meta theme-color for mobile browsers
                const metaThemeColor = document.querySelector('meta[name="theme-color"]');
                if (metaThemeColor) {
                        metaThemeColor.setAttribute('content', colorScheme === 'dark' ? '#0f0f23' : '#ffffff');
                }
        }, [colorScheme]);

        // Initialize theme on mount
        useEffect(() => {
                const savedTheme = localStorage.getItem('mentora-color-scheme');
                if (!savedTheme) {
                        // Save initial system preference
                        persistTheme(colorScheme);
                }
        }, []);

        const themeValue = {
                colorScheme,
                toggleColorScheme,
                isTransitioning,
                isDark: colorScheme === 'dark',
                isLight: colorScheme === 'light',
                // Utility functions for theme-aware styling
                getThemeColor: (lightColor, darkColor) => colorScheme === 'dark' ? darkColor : lightColor,
                // Purple theme variants
                purpleVariants: {
                        primary: colorScheme === 'dark' ? '#7c3aed' : '#a855f7',
                        secondary: colorScheme === 'dark' ? '#8b5cf6' : '#9333ea',
                        accent: colorScheme === 'dark' ? '#a78bfa' : '#c084fc',
                        muted: colorScheme === 'dark' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(139, 92, 246, 0.05)',
                }
        };

        return (
                <ThemeContext.Provider value={themeValue}>
                        <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
                                {children}
                        </ColorSchemeProvider>
                </ThemeContext.Provider>
        );
};

export default ThemeProvider;