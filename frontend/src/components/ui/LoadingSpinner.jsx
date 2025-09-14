import React from 'react';
import { Loader, Box, Text } from '@mantine/core';
import './LoadingSpinner.css';

const LoadingSpinner = ({
        size = 'md',
        variant = 'purple',
        text = null,
        fullScreen = false,
        className = '',
        ...props
}) => {
        const getSpinnerClasses = () => {
                const baseClasses = 'loading-spinner';
                const variantClasses = {
                        purple: 'loading-purple',
                        gradient: 'loading-gradient',
                        pulse: 'loading-pulse'
                };
                const sizeClasses = {
                        xs: 'loading-xs',
                        sm: 'loading-sm',
                        md: 'loading-md',
                        lg: 'loading-lg',
                        xl: 'loading-xl'
                };

                return `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
        };

        const content = (
                <Box className={getSpinnerClasses()} {...props}>
                        <div className="spinner-container">
                                <Loader
                                        size={size}
                                        color="violet"
                                        variant="dots"
                                        className="mantine-loader"
                                />
                                <div className="custom-spinner">
                                        <div className="spinner-ring"></div>
                                        <div className="spinner-ring"></div>
                                        <div className="spinner-ring"></div>
                                </div>
                        </div>
                        {text && (
                                <Text
                                        size="sm"
                                        color="dimmed"
                                        className="loading-text"
                                        mt="md"
                                >
                                        {text}
                                </Text>
                        )}
                </Box>
        );

        if (fullScreen) {
                return (
                        <Box className="loading-fullscreen">
                                {content}
                        </Box>
                );
        }

        return content;
};

// Skeleton Loading Component
const SkeletonLoader = ({
        lines = 3,
        height = 20,
        className = '',
        animated = true
}) => {
        return (
                <Box className={`skeleton-loader ${animated ? 'skeleton-animated' : ''} ${className}`}>
                        {Array.from({ length: lines }).map((_, index) => (
                                <div
                                        key={index}
                                        className="skeleton-line"
                                        style={{
                                                height: `${height}px`,
                                                width: index === lines - 1 ? '75%' : '100%'
                                        }}
                                />
                        ))}
                </Box>
        );
};

// Page Loading Component
const PageLoader = ({ message = 'Loading...' }) => {
        return (
                <Box className="page-loader">
                        <div className="page-loader-content">
                                <div className="page-loader-spinner">
                                        <div className="spinner-orbit">
                                                <div className="spinner-planet"></div>
                                        </div>
                                </div>
                                <Text size="lg" weight={500} className="page-loader-text">
                                        {message}
                                </Text>
                                <div className="page-loader-dots">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                </div>
                        </div>
                </Box>
        );
};

export { LoadingSpinner, SkeletonLoader, PageLoader };
export default LoadingSpinner;