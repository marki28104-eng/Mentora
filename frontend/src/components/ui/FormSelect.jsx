import React, { forwardRef } from 'react';
import { Select, MultiSelect } from '@mantine/core';
import { IconChevronDown } from '@tabler/icons-react';
import './FormSelect.css';

const FormSelect = forwardRef(({
        variant = 'default',
        multiple = false,
        error,
        className = '',
        ...props
}, ref) => {
        const selectClasses = `
    form-select-modern 
    ${variant === 'filled' ? 'form-select-filled' : ''}
    ${error ? 'form-select-error' : ''}
    ${className}
  `.trim();

        const commonProps = {
                ref,
                className: selectClasses,
                error,
                radius: 'md',
                size: 'md',
                rightSection: <IconChevronDown size={16} className="form-select-chevron" />,
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
                                minHeight: '48px',
                                cursor: 'pointer',
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
                        rightSection: {
                                color: 'var(--purple-500)',
                                transition: 'transform 0.2s ease',
                        },
                        dropdown: {
                                backgroundColor: 'var(--bg-card)',
                                border: '2px solid rgba(139, 92, 246, 0.2)',
                                borderRadius: '12px',
                                backdropFilter: 'blur(20px)',
                                boxShadow: '0 10px 25px rgba(139, 92, 246, 0.15)',
                                padding: '8px',
                        },
                        item: {
                                borderRadius: '8px',
                                padding: '12px 16px',
                                margin: '2px 0',
                                fontSize: '15px',
                                fontWeight: 500,
                                color: 'var(--text-primary)',
                                transition: 'all 0.2s ease',
                                '&[data-selected]': {
                                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                                        color: 'var(--purple-600)',
                                        fontWeight: 600,
                                },
                                '&[data-hovered]': {
                                        backgroundColor: 'rgba(139, 92, 246, 0.05)',
                                        color: 'var(--purple-500)',
                                },
                        },
                        searchInput: {
                                backgroundColor: 'var(--bg-primary)',
                                border: '1px solid rgba(139, 92, 246, 0.2)',
                                borderRadius: '8px',
                                padding: '8px 12px',
                                margin: '4px 0 8px 0',
                                fontSize: '14px',
                                color: 'var(--text-primary)',
                                '&:focus': {
                                        borderColor: 'var(--purple-500)',
                                        outline: 'none',
                                },
                        },
                }),
                ...props,
        };

        if (multiple) {
                return (
                        <MultiSelect
                                {...commonProps}
                                styles={(theme) => ({
                                        ...commonProps.styles(theme),
                                        values: {
                                                minHeight: '48px',
                                                padding: '8px 12px',
                                        },
                                        value: {
                                                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                                                color: 'var(--purple-600)',
                                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                                borderRadius: '6px',
                                                padding: '4px 8px',
                                                fontSize: '13px',
                                                fontWeight: 500,
                                        },
                                        defaultValue: {
                                                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                                                color: 'var(--purple-600)',
                                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                        },
                                })}
                        />
                );
        }

        return <Select {...commonProps} />;
});

FormSelect.displayName = 'FormSelect';

export default FormSelect;