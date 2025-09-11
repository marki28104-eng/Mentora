import { useEffect, useState } from 'react';
import { Button, Card, Text, Group, Stack } from '@mantine/core';
import { useUmamiTracker } from '../UmamiTracker';
import LearningTracker from '../LearningTracker';

/**
 * Example component demonstrating Umami tracking integration
 * This shows how to track various learning interactions
 */
const UmamiTrackingExample = () => {
        const { trackEvent, isLoaded } = useUmamiTracker();
        const [eventCount, setEventCount] = useState(0);

        useEffect(() => {
                // Track component mount
                if (isLoaded()) {
                        trackEvent('example_component_mounted');
                }
        }, [isLoaded, trackEvent]);

        const handleBasicEvent = () => {
                trackEvent('button_clicked', {
                        button_type: 'basic_example',
                        timestamp: Date.now()
                });
                setEventCount(prev => prev + 1);
        };

        const handleLearningEvent = () => {
                trackEvent('learning_interaction', {
                        interaction_type: 'example_learning',
                        content_type: 'demo',
                        engagement_level: 'high'
                });
                setEventCount(prev => prev + 1);
        };

        return (
                <LearningTracker>
                        {(trackingMethods) => (
                                <Card shadow="sm" padding="lg" radius="md" withBorder>
                                        <Stack spacing="md">
                                                <Text size="lg" weight={500}>
                                                        Umami Tracking Example
                                                </Text>

                                                <Text size="sm" color="dimmed">
                                                        This component demonstrates how to integrate Umami analytics tracking.
                                                        Events tracked: {eventCount}
                                                </Text>

                                                <Group>
                                                        <Button
                                                                onClick={handleBasicEvent}
                                                                variant="outline"
                                                        >
                                                                Track Basic Event
                                                        </Button>

                                                        <Button
                                                                onClick={handleLearningEvent}
                                                                variant="filled"
                                                        >
                                                                Track Learning Event
                                                        </Button>

                                                        <Button
                                                                onClick={() => {
                                                                        trackingMethods.trackCourseView('demo-course', 'Demo Course');
                                                                        setEventCount(prev => prev + 1);
                                                                }}
                                                                variant="light"
                                                        >
                                                                Track Course View
                                                        </Button>
                                                </Group>

                                                <Text size="xs" color="dimmed">
                                                        Umami Status: {isLoaded() ? '✅ Loaded' : '⏳ Loading...'}
                                                </Text>
                                        </Stack>
                                </Card>
                        )}
                </LearningTracker>
        );
};

export default UmamiTrackingExample;