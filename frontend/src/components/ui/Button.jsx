import React from 'react';
import { Button as MantineButton } from '@mantine/core';
import './Button.css';

const Button = ({
        variant = 'primary',
        size = 'md',
        children,
        className = '',
        disabled = false,
        loading = false,
        leftIcon,
        rightIcon,
        fullWidth = false,
        ...props
}) => {
        const getButtonClasses = () => {
                const baseClasses = 'btn-modern transition-smooth focus-purple';
                const variantClasses = {
                        primary: 'btn-purple-primary',
                        secondary: 'btn-purple-secondary',
                        ghost: 'btn-purple-ghost',
                        gradient: 'btn-purple-gradient'
                };

                const sizeClasses = {
                        xs: 'btn-xs',
                        sm: 'btn-sm',
                        md: 'btn-md',
                        lg: 'btn-lg',
                        xl: 'btn-xl'
                };

                return `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
        };

        return (
                <MantineButton
                        className={getButtonClasses()}
                        disabled={disabled}
                        loading={loading}
                        leftSection={leftIcon}
                        rightSection={rightIcon}
                        fullWidth={fullWidth}
                        {...props}
                >
                        {children}
                </MantineButton>
        );
};

export default Button;