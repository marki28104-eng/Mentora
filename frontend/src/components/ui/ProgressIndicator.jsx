import React from 'react';
import { Progress, Group, Text, ThemeIcon, Box } from '@mantine/core';
import { IconClock, IconCheck } from '@tabler/icons-react';

const ProgressIndicator = ({
        value = 0,
        label = "Progress",
        showIcon = true,
        size = "md",
        color = "purple",
        animated = true,
        className = "",
        ...props
}) => {
        const isCompleted = value >= 100;
        const progressColor = isCompleted ? 'green' : color;

        return (
                <Box className={`transition-all duration-300 ${className}`} {...props}>
                        <Group position="apart" mb={8}>
                                <Group spacing={6} noWrap>
                                        {showIcon && (
                                                <ThemeIcon
                                                        size="sm"
                                                        radius="xl"
                                                        color={progressColor}
                                                        variant="light"
                                                        className="transition-all duration-300"
                                                >
                                                        {isCompleted ? <IconCheck size={12} /> : <IconClock size={12} />}
                                                </ThemeIcon>
                                        )}
                                        <Text size="sm" color="dimmed" weight={600}>
                                                {label}
                                        </Text>
                                </Group>
                                <Text
                                        size="sm"
                                        weight={700}
                                        color={isCompleted ? 'green' : color}
                                        className="transition-colors duration-300"
                                >
                                        {value}%
                                </Text>
                        </Group>

                        <Progress
                                value={value}
                                size={size}
                                radius="xl"
                                color={progressColor}
                                animate={animated && value > 0 && value < 100}
                                className="transition-all duration-300"
                                sx={{
                                        '& .mantine-Progress-bar': {
                                                background: isCompleted
                                                        ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                                                        : `linear-gradient(90deg, var(--${color}-500) 0%, var(--${color}-400) 100%)`,
                                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                        },
                                }}
                        />
                </Box>
        );
};

export default ProgressIndicator;