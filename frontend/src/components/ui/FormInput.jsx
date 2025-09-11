import React, { forwardRef } from 'react';
import { TextInput, PasswordInput } from '@mantine/core';
import './FormInput.css';

const FormInput = forwardRef(({
        type = 'text',
        variant = 'default',
        error,
        className = '',
        ...props
}, ref) => {
        const inputClasses = `
    form-input-modern 
    ${variant === 'filled' ? 'form-input-filled' : ''}
    ${error ? 'form-input-error' : ''}
    ${className}
  `.trim();

        const commonProps = {
                ref,
                className: inputClasses,
                error,
                radius: 'md',
                size: 'md',
                styles: (theme) => ({
                        input: {
                                backgroundColor: 'var(--bg-card)',
                                border: '2px solid rgba(139, 92, 246, 0.2)',
                                borderRadius: '12px',
                                padding: '12px 16px',
                                fontSize: '16px',
                                fontWeight: 500,
                                color: 'var(--text-primary)',
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                backdropFilter: 'blur(10px)',
                                '&:focus': {
                                        borderColor: 'var(--purple-500)',
                                        boxShadow: '0 0 0 3px rgba(139, 92, 246, 0.1)',
                                        backgroundColor: 'var(--bg-primary)',
                                        transform: 'translateY(-1px)',
                                },
                                '&:hover': {
                                        borderColor: 'rgba(139, 92, 246, 0.4)',
                                        backgroundColor: 'var(--bg-primary)',
                                },
                                '&::placeholder': {
                                        color: 'var(--text-tertiary)',
                                        fontWeight: 400,
                                },
                                ...(error && {
                                        borderColor: '#ef4444',
                                        '&:focus': {
                                                borderColor: '#ef4444',
                                                boxShadow: '0 0 0 3px rgba(239, 68, 68, 0.1)',
                                        },
                                }),
                        },
                        label: {
                                color: 'var(--text-primary)',
                                fontWeight: 600,
                                fontSize: '14px',
                                marginBottom: '8px',
                        },
                        error: {
                                color: '#ef4444',
                                fontSize: '13px',
                                fontWeight: 500,
                                marginTop: '6px',
                        },
                }),
                ...props,
        };

        if (type === 'password') {
                return (
                        <PasswordInput
                                {...commonProps}
                                styles={(theme) => ({
                                        ...commonProps.styles(theme),
                                        innerInput: commonProps.styles(theme).input,
                                        visibilityToggle: {
                                                color: 'var(--purple-500)',
                                                '&:hover': {
                                                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                                                },
                                        },
                                })}
                        />
                );
        }

        return <TextInput {...commonProps} />;
});

FormInput.displayName = 'FormInput';

export default FormInput;