import React from 'react';
import { Card as MantineCard } from '@mantine/core';
import './Card.css';

const Card = ({
        variant = 'default',
        children,
        className = '',
        padding = 'md',
        radius = 'md',
        withBorder = false,
        shadow = 'sm',
        hoverable = false,
        ...props
}) => {
        const getCardClasses = () => {
                const baseClasses = 'card-modern transition-smooth';
                const variantClasses = {
                        default: 'card-default',
                        glass: 'card-glass',
                        elevated: 'card-elevated',
                        gradient: 'card-gradient',
                        outline: 'card-outline'
                };

                const hoverClass = hoverable ? 'card-hoverable' : '';

                return `${baseClasses} ${variantClasses[variant]} ${hoverClass} ${className}`;
        };

        return (
                <MantineCard
                        className={getCardClasses()}
                        padding={padding}
                        radius={radius}
                        withBorder={withBorder}
                        shadow={shadow}
                        {...props}
                >
                        {children}
                </MantineCard>
        );
};

export default Card;