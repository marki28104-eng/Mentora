import React from 'react';
import { Alert, Text, Group } from '@mantine/core';
import { IconAlertCircle, IconCheck, IconExclamationMark } from '@tabler/icons-react';
import './FormValidation.css';

// Form Error Alert Component
export const FormError = ({
        error,
        title = 'Validation Error',
        onClose,
        className = '',
        ...props
}) => {
        if (!error) return null;

        return (
                <Alert
                        icon={<IconAlertCircle size={18} />}
                        title={title}
                        color="red"
                        radius="md"
                        className={`form-error-alert ${className}`}
                        withCloseButton={!!onClose}
                        onClose={onClose}
                        styles={{
                                root: {
                                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                        border: '1px solid rgba(239, 68, 68, 0.3)',
                                        backdropFilter: 'blur(10px)',
                                },
                                title: {
                                        color: '#dc2626',
                                        fontWeight: 600,
                                },
                                body: {
                                        color: '#dc2626',
                                },
                                icon: {
                                        color: '#dc2626',
                                },
                        }}
                        {...props}
                >
                        {typeof error === 'string' ? error : error?.message || 'An error occurred'}
                </Alert>
        );
};

// Form Success Alert Component
export const FormSuccess = ({
        message,
        title = 'Success',
        onClose,
        className = '',
        ...props
}) => {
        if (!message) return null;

        return (
                <Alert
                        icon={<IconCheck size={18} />}
                        title={title}
                        color="green"
                        radius="md"
                        className={`form-success-alert ${className}`}
                        withCloseButton={!!onClose}
                        onClose={onClose}
                        styles={{
                                root: {
                                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                        border: '1px solid rgba(16, 185, 129, 0.3)',
                                        backdropFilter: 'blur(10px)',
                                },
                                title: {
                                        color: '#059669',
                                        fontWeight: 600,
                                },
                                body: {
                                        color: '#059669',
                                },
                                icon: {
                                        color: '#059669',
                                },
                        }}
                        {...props}
                >
                        {message}
                </Alert>
        );
};

// Form Warning Alert Component
export const FormWarning = ({
        message,
        title = 'Warning',
        onClose,
        className = '',
        ...props
}) => {
        if (!message) return null;

        return (
                <Alert
                        icon={<IconExclamationMark size={18} />}
                        title={title}
                        color="yellow"
                        radius="md"
                        className={`form-warning-alert ${className}`}
                        withCloseButton={!!onClose}
                        onClose={onClose}
                        styles={{
                                root: {
                                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                                        border: '1px solid rgba(245, 158, 11, 0.3)',
                                        backdropFilter: 'blur(10px)',
                                },
                                title: {
                                        color: '#d97706',
                                        fontWeight: 600,
                                },
                                body: {
                                        color: '#d97706',
                                },
                                icon: {
                                        color: '#d97706',
                                },
                        }}
                        {...props}
                >
                        {message}
                </Alert>
        );
};

// Field Error Component
export const FieldError = ({ error, className = '' }) => {
        if (!error) return null;

        return (
                <Text
                        size="sm"
                        color="red"
                        className={`field-error ${className}`}
                        style={{
                                marginTop: '6px',
                                fontSize: '13px',
                                fontWeight: 500,
                                color: '#ef4444',
                        }}
                >
                        {error}
                </Text>
        );
};

// Field Success Component
export const FieldSuccess = ({ message, className = '' }) => {
        if (!message) return null;

        return (
                <Text
                        size="sm"
                        color="green"
                        className={`field-success ${className}`}
                        style={{
                                marginTop: '6px',
                                fontSize: '13px',
                                fontWeight: 500,
                                color: '#10b981',
                        }}
                >
                        {message}
                </Text>
        );
};

// Validation Status Indicator
export const ValidationStatus = ({
        status,
        message,
        className = '',
        showIcon = true
}) => {
        if (!status || !message) return null;

        const getStatusConfig = () => {
                switch (status) {
                        case 'success':
                                return {
                                        color: '#10b981',
                                        icon: <IconCheck size={14} />,
                                        bgColor: 'rgba(16, 185, 129, 0.1)',
                                };
                        case 'error':
                                return {
                                        color: '#ef4444',
                                        icon: <IconAlertCircle size={14} />,
                                        bgColor: 'rgba(239, 68, 68, 0.1)',
                                };
                        case 'warning':
                                return {
                                        color: '#f59e0b',
                                        icon: <IconExclamationMark size={14} />,
                                        bgColor: 'rgba(245, 158, 11, 0.1)',
                                };
                        default:
                                return {
                                        color: 'var(--text-secondary)',
                                        icon: null,
                                        bgColor: 'transparent',
                                };
                }
        };

        const config = getStatusConfig();

        return (
                <Group
                        spacing={6}
                        className={`validation-status validation-status-${status} ${className}`}
                        style={{
                                marginTop: '6px',
                                padding: '4px 8px',
                                borderRadius: '6px',
                                backgroundColor: config.bgColor,
                        }}
                >
                        {showIcon && config.icon && (
                                <span style={{ color: config.color, display: 'flex', alignItems: 'center' }}>
                                        {config.icon}
                                </span>
                        )}
                        <Text
                                size="sm"
                                style={{
                                        fontSize: '13px',
                                        fontWeight: 500,
                                        color: config.color,
                                }}
                        >
                                {message}
                        </Text>
                </Group>
        );
};

// Form Validation Summary Component
export const FormValidationSummary = ({
        errors = [],
        warnings = [],
        className = '',
        title = 'Please fix the following issues:',
        ...props
}) => {
        const hasErrors = errors.length > 0;
        const hasWarnings = warnings.length > 0;

        if (!hasErrors && !hasWarnings) return null;

        return (
                <div className={`form-validation-summary ${className}`} {...props}>
                        {hasErrors && (
                                <Alert
                                        icon={<IconAlertCircle size={18} />}
                                        title={title}
                                        color="red"
                                        radius="md"
                                        mb={hasWarnings ? 'md' : 0}
                                        styles={{
                                                root: {
                                                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                                        border: '1px solid rgba(239, 68, 68, 0.3)',
                                                        backdropFilter: 'blur(10px)',
                                                },
                                                title: {
                                                        color: '#dc2626',
                                                        fontWeight: 600,
                                                        marginBottom: '8px',
                                                },
                                                body: {
                                                        color: '#dc2626',
                                                },
                                                icon: {
                                                        color: '#dc2626',
                                                },
                                        }}
                                >
                                        <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                                {errors.map((error, index) => (
                                                        <li key={index} style={{ marginBottom: '4px' }}>
                                                                {typeof error === 'string' ? error : error?.message || 'Unknown error'}
                                                        </li>
                                                ))}
                                        </ul>
                                </Alert>
                        )}

                        {hasWarnings && (
                                <Alert
                                        icon={<IconExclamationMark size={18} />}
                                        title="Warnings:"
                                        color="yellow"
                                        radius="md"
                                        styles={{
                                                root: {
                                                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                                                        border: '1px solid rgba(245, 158, 11, 0.3)',
                                                        backdropFilter: 'blur(10px)',
                                                },
                                                title: {
                                                        color: '#d97706',
                                                        fontWeight: 600,
                                                        marginBottom: '8px',
                                                },
                                                body: {
                                                        color: '#d97706',
                                                },
                                                icon: {
                                                        color: '#d97706',
                                                },
                                        }}
                                >
                                        <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                                {warnings.map((warning, index) => (
                                                        <li key={index} style={{ marginBottom: '4px' }}>
                                                                {typeof warning === 'string' ? warning : warning?.message || 'Unknown warning'}
                                                        </li>
                                                ))}
                                        </ul>
                                </Alert>
                        )}
                </div>
        );
};

export default {
        FormError,
        FormSuccess,
        FormWarning,
        FieldError,
        FieldSuccess,
        ValidationStatus,
        FormValidationSummary,
};