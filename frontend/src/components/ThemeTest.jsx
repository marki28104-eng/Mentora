import { Paper, Text, Group, Button } from '@mantine/core';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from './ThemeToggle';

const ThemeTest = () => {
        const { colorScheme, isDark, isLight, purpleVariants, getThemeColor } = useTheme();

        return (
                <Paper p="md" className="glass-card">
                        <Group position="apart" mb="md">
                                <Text size="lg" weight={600}>Theme System Test</Text>
                                <ThemeToggle />
                        </Group>

                        <Text mb="sm">Current theme: <strong>{colorScheme}</strong></Text>
                        <Text mb="sm">Is Dark: {isDark ? 'Yes' : 'No'}</Text>
                        <Text mb="sm">Is Light: {isLight ? 'Yes' : 'No'}</Text>

                        <Group mt="md">
                                <Button
                                        style={{ backgroundColor: purpleVariants.primary }}
                                        color="purple"
                                >
                                        Primary Purple
                                </Button>
                                <Button
                                        variant="outline"
                                        style={{
                                                borderColor: purpleVariants.secondary,
                                                color: purpleVariants.secondary
                                        }}
                                >
                                        Secondary Purple
                                </Button>
                        </Group>

                        <Paper
                                mt="md"
                                p="sm"
                                style={{
                                        backgroundColor: getThemeColor('#f8f9fa', '#2d3748'),
                                        border: `1px solid ${purpleVariants.muted}`
                                }}
                        >
                                <Text size="sm">
                                        This background adapts to theme: {getThemeColor('Light background', 'Dark background')}
                                </Text>
                        </Paper>
                </Paper>
        );
};

export default ThemeTest;