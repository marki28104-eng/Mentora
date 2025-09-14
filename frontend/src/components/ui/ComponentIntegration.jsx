import React from 'react';
import { Button, Card, Navigation } from './index.js';
import { IconHome } from '@tabler/icons-react';

// Simple integration test component to verify all components work together
const ComponentIntegration = () => {
        const navItems = [
                { key: 'home', to: '/', label: 'Home', icon: <IconHome size={16} /> }
        ];

        return (
                <div className="p-4 space-y-4">
                        <h2 className="text-xl font-bold">Component Integration Test</h2>

                        <Card variant="glass" className="p-4">
                                <h3 className="text-lg font-semibold mb-2">Button Test</h3>
                                <div className="space-x-2">
                                        <Button variant="primary">Primary</Button>
                                        <Button variant="secondary">Secondary</Button>
                                        <Button variant="ghost">Ghost</Button>
                                        <Button variant="gradient">Gradient</Button>
                                </div>
                        </Card>

                        <Card variant="default" className="p-4">
                                <h3 className="text-lg font-semibold mb-2">Navigation Test</h3>
                                <Navigation items={navItems} variant="horizontal" />
                        </Card>

                        <Card variant="elevated" hoverable className="p-4">
                                <h3 className="text-lg font-semibold mb-2">Animation Test</h3>
                                <div className="animate-fade-in-up">
                                        <p>This text should fade in from below</p>
                                </div>
                        </Card>
                </div>
        );
};

export default ComponentIntegration;