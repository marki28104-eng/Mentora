import React, { forwardRef } from 'react';
import { Textarea } from '@mantine/core';
import './FormTextarea.css';

const FormTextarea = forwardRef(({
        variant = 'default',
        error,
        className = '',
        autosize = false,
        minRows = 3,
        maxRows = 8,
        ...props
}, ref) => {
        const textareaClasses = `
    form-textarea-modern 
    ${variant === 'filled' ? 'form-textarea-filled' : ''}
    ${error ? 'form-textarea-error' : ''}
    ${className}
  `.trim();

        const commonProps = {
                ref,
                className: textareaClasses,
                error,
                radius: 'md',
                size: 'md',
                autosize,
                minRows,
                maxRows,
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
                                minHeight: autosize ? 'auto' : `${minRows * 24 + 24}px`,
                                resize: autosize ? 'none' : 'vertical',
                                fontFamily: 'inherit',
                                lineHeight: '1.5',
                                '&:focus': {
                                        borderColor: 'var(--purple-500)',
                                        boxShadow: '0 0 0 3px rgba(139, 92, 246, 0.1)',
                                        backgroundColor: 'var(--bg-primary)',
                                        transform: 'translateY(-1px)',
                                        outline: 'none',
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

        return <Textarea {...commonProps} />;
});

FormTextarea.displayName = 'FormTextarea';

export default FormTextarea;