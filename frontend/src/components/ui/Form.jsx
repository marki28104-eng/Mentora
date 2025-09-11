import React, { forwardRef } from 'react';
import { Stack, Paper, Group, Title, Text } from '@mantine/core';
import { FormError, FormSuccess, FormWarning, FormValidationSummary } from './FormValidation';
import './Form.css';

// Main Form Container Component
const Form = forwardRef(({
        children,
        title,
        description,
        error,
        success,
        warning,
        validationErrors = [],
        validationWarnings = [],
        onSubmit,
        className = '',
        variant = 'default',
        spacing = 'md',
        withBorder = true,
        withShadow = true,
        ...props
}, ref) => {
        const formClasses = `
    form-modern 
    ${variant === 'card' ? 'form-card' : ''}
    ${variant === 'minimal' ? 'form-minimal' : ''}
    ${className}
  `.trim();

        const handleSubmit = (e) => {
                e.preventDefault();
                if (onSubmit) {
                        onSubmit(e);
                }
        };

        const FormContent = () => (
                <>
                        {(title || description) && (
                                <div className="form-header">
                                        {title && (
                                                <Title
                                                        order={3}
                                                        className="form-title"
                                                        style={{
                                                                color: 'var(--text-primary)',
                                                                marginBottom: description ? '8px' : '24px',
                                                                fontWeight: 600,
                                                        }}
                                                >
                                                        {title}
                                                </Title>
                                        )}
                                        {description && (
                                                <Text
                                                        size="sm"
                                                        className="form-description"
                                                        style={{
                                                                color: 'var(--text-secondary)',
                                                                marginBottom: '24px',
                                                                lineHeight: 1.5,
                                                        }}
                                                >
                                                        {description}
                                                </Text>
                                        )}
                                </div>
                        )}

                        <FormValidationSummary
                                errors={validationErrors}
                                warnings={validationWarnings}
                        />

                        <FormError error={error} />
                        <FormSuccess message={success} />
                        <FormWarning message={warning} />

                        <Stack spacing={spacing}>
                                {children}
                        </Stack>
                </>
        );

        if (variant === 'minimal') {
                return (
                        <form
                                ref={ref}
                                className={formClasses}
                                onSubmit={handleSubmit}
                                {...props}
                        >
                                <FormContent />
                        </form>
                );
        }

        return (
                <Paper
                        className={formClasses}
                        withBorder={withBorder}
                        shadow={withShadow ? 'md' : undefined}
                        radius="lg"
                        p="xl"
                        style={{
                                backgroundColor: 'var(--bg-card)',
                                backdropFilter: 'blur(20px)',
                                border: withBorder ? '1px solid rgba(139, 92, 246, 0.2)' : 'none',
                        }}
                >
                        <form
                                ref={ref}
                                onSubmit={handleSubmit}
                                {...props}
                        >
                                <FormContent />
                        </form>
                </Paper>
        );
});

// Form Section Component for organizing form fields
export const FormSection = ({
        title,
        description,
        children,
        className = '',
        spacing = 'md',
        ...props
}) => {
        return (
                <div className={`form-section ${className}`} {...props}>
                        {(title || description) && (
                                <div className="form-section-header">
                                        {title && (
                                                <Title
                                                        order={4}
                                                        className="form-section-title"
                                                        style={{
                                                                color: 'var(--text-primary)',
                                                                marginBottom: description ? '4px' : '16px',
                                                                fontWeight: 600,
                                                                fontSize: '16px',
                                                        }}
                                                >
                                                        {title}
                                                </Title>
                                        )}
                                        {description && (
                                                <Text
                                                        size="sm"
                                                        className="form-section-description"
                                                        style={{
                                                                color: 'var(--text-secondary)',
                                                                marginBottom: '16px',
                                                                lineHeight: 1.4,
                                                        }}
                                                >
                                                        {description}
                                                </Text>
                                        )}
                                </div>
                        )}
                        <Stack spacing={spacing}>
                                {children}
                        </Stack>
                </div>
        );
};

// Form Field Group Component
export const FormFieldGroup = ({
        children,
        direction = 'vertical',
        spacing = 'md',
        className = '',
        ...props
}) => {
        const isHorizontal = direction === 'horizontal';

        return (
                <div
                        className={`form-field-group ${isHorizontal ? 'horizontal' : 'vertical'} ${className}`}
                        {...props}
                >
                        {isHorizontal ? (
                                <Group spacing={spacing} grow>
                                        {children}
                                </Group>
                        ) : (
                                <Stack spacing={spacing}>
                                        {children}
                                </Stack>
                        )}
                </div>
        );
};

// Form Actions Component for buttons
export const FormActions = ({
        children,
        align = 'right',
        spacing = 'md',
        className = '',
        ...props
}) => {
        const getPosition = () => {
                switch (align) {
                        case 'left':
                                return 'flex-start';
                        case 'center':
                                return 'center';
                        case 'right':
                        default:
                                return 'flex-end';
                        case 'apart':
                                return 'space-between';
                }
        };

        return (
                <Group
                        position={align === 'apart' ? 'apart' : align}
                        spacing={spacing}
                        className={`form-actions ${className}`}
                        style={{
                                marginTop: '24px',
                                paddingTop: '16px',
                                borderTop: '1px solid rgba(139, 92, 246, 0.1)',
                                justifyContent: getPosition(),
                        }}
                        {...props}
                >
                        {children}
                </Group>
        );
};

Form.displayName = 'Form';
FormSection.displayName = 'FormSection';
FormFieldGroup.displayName = 'FormFieldGroup';
FormActions.displayName = 'FormActions';

export default Form;
export { FormSection, FormFieldGroup, FormActions };