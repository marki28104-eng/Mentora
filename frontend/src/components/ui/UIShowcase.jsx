import React, { useState } from 'react';
import { Button, Card, Navigation, Breadcrumb, TabNavigation } from './index.js';
import { IconHome, IconUser, IconSettings, IconBell, IconSearch } from '@tabler/icons-react';

const UIShowcase = () => {
        const [activeTab, setActiveTab] = useState('buttons');

        const navigationItems = [
                { key: 'home', to: '/', label: 'Home', icon: <IconHome size={16} /> },
                { key: 'profile', to: '/profile', label: 'Profile', icon: <IconUser size={16} />, badge: '2' },
                { key: 'settings', to: '/settings', label: 'Settings', icon: <IconSettings size={16} /> },
                { key: 'notifications', href: '#', label: 'Notifications', icon: <IconBell size={16} />, badge: '5' },
                { key: 'search', onClick: () => alert('Search clicked'), label: 'Search', icon: <IconSearch size={16} /> },
                { key: 'disabled', label: 'Disabled Item', disabled: true }
        ];

        const breadcrumbItems = [
                { key: 'home', to: '/', label: 'Home' },
                { key: 'components', to: '/components', label: 'Components' },
                { key: 'ui', label: 'UI Showcase' }
        ];

        const tabs = [
                { key: 'buttons', label: 'Buttons', icon: <IconHome size={14} /> },
                { key: 'cards', label: 'Cards', badge: '4' },
                { key: 'navigation', label: 'Navigation' },
                { key: 'animations', label: 'Animations' }
        ];

        return (
                <div className="p-8 space-y-8 bg-background-primary min-h-screen">
                        <div className="max-w-6xl mx-auto">
                                <h1 className="text-4xl font-bold text-purple-gradient mb-2">UI Component Showcase</h1>
                                <p className="text-text-secondary mb-8">Modern purple-themed components with glass morphism and animations</p>

                                <Breadcrumb items={breadcrumbItems} className="mb-6" />

                                <TabNavigation
                                        tabs={tabs}
                                        activeTab={activeTab}
                                        onTabChange={setActiveTab}
                                        className="mb-8"
                                />

                                {activeTab === 'buttons' && (
                                        <div className="space-y-8">
                                                <Card variant="glass" className="p-6">
                                                        <h2 className="text-2xl font-semibold mb-4 text-text-primary">Button Variants</h2>
                                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Primary Buttons</h3>
                                                                        <Button variant="primary" size="xs">Extra Small</Button>
                                                                        <Button variant="primary" size="sm">Small</Button>
                                                                        <Button variant="primary" size="md">Medium</Button>
                                                                        <Button variant="primary" size="lg">Large</Button>
                                                                        <Button variant="primary" size="xl">Extra Large</Button>
                                                                </div>

                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Secondary Buttons</h3>
                                                                        <Button variant="secondary" size="xs">Extra Small</Button>
                                                                        <Button variant="secondary" size="sm">Small</Button>
                                                                        <Button variant="secondary" size="md">Medium</Button>
                                                                        <Button variant="secondary" size="lg">Large</Button>
                                                                        <Button variant="secondary" size="xl">Extra Large</Button>
                                                                </div>

                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Ghost Buttons</h3>
                                                                        <Button variant="ghost" size="xs">Extra Small</Button>
                                                                        <Button variant="ghost" size="sm">Small</Button>
                                                                        <Button variant="ghost" size="md">Medium</Button>
                                                                        <Button variant="ghost" size="lg">Large</Button>
                                                                        <Button variant="ghost" size="xl">Extra Large</Button>
                                                                </div>

                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Gradient Buttons</h3>
                                                                        <Button variant="gradient" size="xs">Extra Small</Button>
                                                                        <Button variant="gradient" size="sm">Small</Button>
                                                                        <Button variant="gradient" size="md">Medium</Button>
                                                                        <Button variant="gradient" size="lg">Large</Button>
                                                                        <Button variant="gradient" size="xl">Extra Large</Button>
                                                                </div>
                                                        </div>

                                                        <div className="mt-8 space-y-4">
                                                                <h3 className="font-medium text-text-secondary">Button States</h3>
                                                                <div className="flex flex-wrap gap-4">
                                                                        <Button variant="primary" leftIcon={<IconHome size={16} />}>With Left Icon</Button>
                                                                        <Button variant="secondary" rightIcon={<IconSettings size={16} />}>With Right Icon</Button>
                                                                        <Button variant="primary" disabled>Disabled</Button>
                                                                        <Button variant="primary" loading>Loading</Button>
                                                                        <Button variant="primary" fullWidth>Full Width</Button>
                                                                </div>
                                                        </div>
                                                </Card>
                                        </div>
                                )}

                                {activeTab === 'cards' && (
                                        <div className="space-y-8">
                                                <div className="cards-grid">
                                                        <Card variant="default" hoverable className="p-6">
                                                                <div className="card-header">
                                                                        <h3 className="card-title">Default Card</h3>
                                                                        <span className="text-purple-500">✨</span>
                                                                </div>
                                                                <div className="card-content">
                                                                        <p>This is a default card with standard styling and hover effects.</p>
                                                                </div>
                                                                <div className="card-footer">
                                                                        <Button variant="ghost" size="sm">Action</Button>
                                                                        <span className="text-text-tertiary text-sm">2 min ago</span>
                                                                </div>
                                                        </Card>

                                                        <Card variant="glass" hoverable className="p-6">
                                                                <div className="card-header">
                                                                        <h3 className="card-title">Glass Morphism Card</h3>
                                                                        <span className="text-purple-500">🔮</span>
                                                                </div>
                                                                <div className="card-content">
                                                                        <p>This card features glass morphism with backdrop blur effects.</p>
                                                                </div>
                                                                <div className="card-footer">
                                                                        <Button variant="secondary" size="sm">Explore</Button>
                                                                        <span className="text-text-tertiary text-sm">5 min ago</span>
                                                                </div>
                                                        </Card>

                                                        <Card variant="elevated" hoverable className="p-6">
                                                                <div className="card-header">
                                                                        <h3 className="card-title">Elevated Card</h3>
                                                                        <span className="text-purple-500">⬆️</span>
                                                                </div>
                                                                <div className="card-content">
                                                                        <p>This card has enhanced shadows for a floating appearance.</p>
                                                                </div>
                                                                <div className="card-footer">
                                                                        <Button variant="primary" size="sm">Get Started</Button>
                                                                        <span className="text-text-tertiary text-sm">10 min ago</span>
                                                                </div>
                                                        </Card>

                                                        <Card variant="gradient" hoverable className="p-6">
                                                                <div className="card-header">
                                                                        <h3 className="card-title">Gradient Card</h3>
                                                                        <span className="text-purple-500">🌈</span>
                                                                </div>
                                                                <div className="card-content">
                                                                        <p>This card features subtle purple gradient backgrounds.</p>
                                                                </div>
                                                                <div className="card-footer">
                                                                        <Button variant="gradient" size="sm">Try Now</Button>
                                                                        <span className="text-text-tertiary text-sm">15 min ago</span>
                                                                </div>
                                                        </Card>
                                                </div>
                                        </div>
                                )}

                                {activeTab === 'navigation' && (
                                        <div className="space-y-8">
                                                <Card variant="glass" className="p-6">
                                                        <h2 className="text-2xl font-semibold mb-4 text-text-primary">Navigation Components</h2>

                                                        <div className="space-y-6">
                                                                <div>
                                                                        <h3 className="font-medium text-text-secondary mb-3">Horizontal Navigation</h3>
                                                                        <Navigation items={navigationItems} variant="horizontal" />
                                                                </div>

                                                                <div>
                                                                        <h3 className="font-medium text-text-secondary mb-3">Vertical Navigation</h3>
                                                                        <div className="max-w-xs">
                                                                                <Navigation items={navigationItems} variant="vertical" />
                                                                        </div>
                                                                </div>
                                                        </div>
                                                </Card>
                                        </div>
                                )}

                                {activeTab === 'animations' && (
                                        <div className="space-y-8">
                                                <Card variant="glass" className="p-6">
                                                        <h2 className="text-2xl font-semibold mb-4 text-text-primary">Animation Examples</h2>

                                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Fade In Up</h3>
                                                                        <div className="animate-fade-in-up">
                                                                                <Card variant="default" className="p-4 text-center">
                                                                                        <p>Fade In Up Animation</p>
                                                                                </Card>
                                                                        </div>
                                                                </div>

                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Slide In Right</h3>
                                                                        <div className="animate-slide-in-right">
                                                                                <Card variant="default" className="p-4 text-center">
                                                                                        <p>Slide In Right Animation</p>
                                                                                </Card>
                                                                        </div>
                                                                </div>

                                                                <div className="space-y-4">
                                                                        <h3 className="font-medium text-text-secondary">Float Animation</h3>
                                                                        <div className="animate-float">
                                                                                <Card variant="gradient" className="p-4 text-center">
                                                                                        <p>Floating Animation</p>
                                                                                </Card>
                                                                        </div>
                                                                </div>
                                                        </div>

                                                        <div className="mt-8 space-y-4">
                                                                <h3 className="font-medium text-text-secondary">Interactive Hover Effects</h3>
                                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                                        <Card variant="default" className="p-4 text-center hover-lift transition-smooth cursor-pointer">
                                                                                <p>Hover Lift Effect</p>
                                                                        </Card>
                                                                        <Card variant="default" className="p-4 text-center hover-scale transition-smooth cursor-pointer">
                                                                                <p>Hover Scale Effect</p>
                                                                        </Card>
                                                                        <Card variant="default" className="p-4 text-center hover:shadow-purple-xl transition-shadow cursor-pointer">
                                                                                <p>Hover Shadow Effect</p>
                                                                        </Card>
                                                                </div>
                                                        </div>
                                                </Card>
                                        </div>
                                )}
                        </div>
                </div>
        );
};

export default UIShowcase;