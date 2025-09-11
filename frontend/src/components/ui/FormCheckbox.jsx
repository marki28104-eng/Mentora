import React, { forwardRef } from 'react';
import { Checkbox, Radio } from '@mantine/core';
import './FormCheckbox.css';

const FormCheckbox = forwardRef(({
        type = 'checkbox',
        variant = 'default',
        error,
        className = '',
        ...props
}, ref) => {
        const checkboxClasses = `
    form-checkbox-modern 
    ${variant === 'filled' ? 'form-checkbox-filled' : ''}
    ${error ? 'form-checkbox-error' : ''}
    ${className}
  `.trim();

        const commonStyles = (theme) => ({
                input: {
                        backgroundColor: 'var(--bg-card)',
                        border: '2px solid rgba(139, 92, 246, 0.3)',
                        borderRadius: type === 'radio' ? '50%' : '6px',
                        width: '20px',
                        height: '20px',
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        cursor: 'pointer',
                        '&:checked': {
                                backgroundColor: 'var(--purple-500)',
                                borderColor: 'var(--purple-500)',
                                '&::before': {
                                        backgroundColor: 'white',
                                },
                        },
                        '&:hover': {
                                borderColor: 'var(--purple-400)',
                                backgroundColor: 'rgba(139, 92, 246, 0.05)',
                                transform: 'scale(1.05)',
                        },
                        '&:focus': {
                                outline: 'none',
                                boxShadow: '0 0 0 3px rgba(139, 92, 246, 0.2)',
                        },
                        ...(error && {
                                borderColor: '#ef4444',
                                '&:checked': {
                                        backgroundColor: '#ef4444',
                                        borderColor: '#ef4444',
                                },
                        }),
                },
                label: {
                        color: 'var(--text-primary)',
                        fontSize: '15px',
                        fontWeight: 500,
                        cursor: 'pointer',
                        paddingLeft: '12px',
                        lineHeight: '1.4',
                        transition: 'color 0.2s ease',
                        '&:hover': {
                                color: 'var(--purple-600)',
                        },
                },
                error: {
                        color: '#ef4444',
                        fontSize: '13px',
                        fontWeight: 500,
                        marginTop: '6px',
                },
        });

        const commonProps = {
                ref,
                className: checkboxClasses,
                error,
                size: 'md',
                styles: commonStyles,
                ...props,
        };

        if (type === 'radio') {
                return <Radio {...commonProps} />;
        }

        return <Checkbox {...commonProps} />;
});

FormCheckbox.displayName = 'FormCheckbox';

export default FormCheckbox;