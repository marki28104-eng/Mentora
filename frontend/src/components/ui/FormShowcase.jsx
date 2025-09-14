import React, { useState } from 'react';
import { Container, Title, Stack, Group, Button as MantineButton, Text, Divider } from '@mantine/core';
import { useForm } from '@mantine/form';
import {
        Form,
        FormSection,
        FormFieldGroup,
        FormActions,
        FormInput,
        FormSelect,
        FormCheckbox,
        FormTextarea,
        FormError,
        FormSuccess,
        ValidationStatus,
        Button
} from './index';

const FormShowcase = () => {
        const [submitResult, setSubmitResult] = useState(null);
        const [isLoading, setIsLoading] = useState(false);

        const form = useForm({
                initialValues: {
                        firstName: '',
                        lastName: '',
                        email: '',
                        password: '',
                        country: '',
                        interests: [],
                        newsletter: false,
                        terms: false,
                        bio: '',
                },
                validate: {
                        firstName: (value) => (!value ? 'First name is required' : null),
                        lastName: (value) => (!value ? 'Last name is required' : null),
                        email: (value) => (!/^\S+@\S+$/.test(value) ? 'Invalid email' : null),
                        password: (value) => (value.length < 6 ? 'Password must be at least 6 characters' : null),
                        country: (value) => (!value ? 'Please select a country' : null),
                        terms: (value) => (!value ? 'You must accept the terms' : null),
                },
        });

        const handleSubmit = async (values) => {
                setIsLoading(true);
                setSubmitResult(null);

                // Simulate API call
                setTimeout(() => {
                        setIsLoading(false);
                        setSubmitResult({ type: 'success', message: 'Form submitted successfully!' });
                        console.log('Form values:', values);
                }, 2000);
        };

        const countryOptions = [
                { value: 'us', label: 'United States' },
                { value: 'ca', label: 'Canada' },
                { value: 'uk', label: 'United Kingdom' },
                { value: 'de', label: 'Germany' },
                { value: 'fr', label: 'France' },
        ];

        const interestOptions = [
                { value: 'tech', label: 'Technology' },
                { value: 'design', label: 'Design' },
                { value: 'business', label: 'Business' },
                { value: 'science', label: 'Science' },
                { value: 'arts', label: 'Arts' },
        ];

        return (
                <Container size="md" py="xl">
                        <Stack spacing="xl">
                                <div>
                                        <Title order={1} align="center" mb="md">
                                                Modern Form Components Showcase
                                        </Title>
                                        <Text align="center" color="dimmed" size="lg">
                                                Demonstrating the new purple-themed form components with validation
                                        </Text>
                                </div>

                                <Divider />

                                {/* Main Form Example */}
                                <Form
                                        title="User Registration Form"
                                        description="Fill out this form to create your account with our modern form components."
                                        onSubmit={form.onSubmit(handleSubmit)}
                                        error={submitResult?.type === 'error' ? submitResult.message : null}
                                        success={submitResult?.type === 'success' ? submitResult.message : null}
                                >
                                        <FormSection
                                                title="Personal Information"
                                                description="Tell us about yourself"
                                        >
                                                <FormFieldGroup direction="horizontal">
                                                        <FormInput
                                                                label="First Name"
                                                                placeholder="Enter your first name"
                                                                required
                                                                {...form.getInputProps('firstName')}
                                                        />
                                                        <FormInput
                                                                label="Last Name"
                                                                placeholder="Enter your last name"
                                                                required
                                                                {...form.getInputProps('lastName')}
                                                        />
                                                </FormFieldGroup>

                                                <FormInput
                                                        label="Email Address"
                                                        placeholder="your.email@example.com"
                                                        type="email"
                                                        required
                                                        {...form.getInputProps('email')}
                                                />

                                                <FormInput
                                                        label="Password"
                                                        placeholder="Choose a secure password"
                                                        type="password"
                                                        required
                                                        {...form.getInputProps('password')}
                                                />
                                        </FormSection>

                                        <FormSection
                                                title="Location & Preferences"
                                                description="Help us customize your experience"
                                        >
                                                <FormSelect
                                                        label="Country"
                                                        placeholder="Select your country"
                                                        data={countryOptions}
                                                        required
                                                        {...form.getInputProps('country')}
                                                />

                                                <FormSelect
                                                        label="Interests"
                                                        placeholder="Select your interests"
                                                        data={interestOptions}
                                                        multiple
                                                        {...form.getInputProps('interests')}
                                                />

                                                <FormTextarea
                                                        label="Bio"
                                                        placeholder="Tell us a bit about yourself..."
                                                        autosize
                                                        minRows={3}
                                                        maxRows={6}
                                                        {...form.getInputProps('bio')}
                                                />
                                        </FormSection>

                                        <FormSection title="Preferences">
                                                <Stack spacing="sm">
                                                        <FormCheckbox
                                                                label="Subscribe to newsletter for updates and tips"
                                                                {...form.getInputProps('newsletter', { type: 'checkbox' })}
                                                        />

                                                        <FormCheckbox
                                                                label="I agree to the terms and conditions"
                                                                required
                                                                {...form.getInputProps('terms', { type: 'checkbox' })}
                                                        />
                                                </Stack>
                                        </FormSection>

                                        <FormActions align="apart">
                                                <MantineButton variant="subtle" color="gray">
                                                        Cancel
                                                </MantineButton>
                                                <Button
                                                        type="submit"
                                                        loading={isLoading}
                                                        variant="primary"
                                                >
                                                        Create Account
                                                </Button>
                                        </FormActions>
                                </Form>

                                <Divider />

                                {/* Component Variants Showcase */}
                                <div>
                                        <Title order={2} mb="lg">Component Variants</Title>

                                        <Stack spacing="xl">
                                                {/* Input Variants */}
                                                <FormSection title="Input Variants">
                                                        <FormFieldGroup>
                                                                <FormInput
                                                                        label="Default Input"
                                                                        placeholder="Default styling"
                                                                />
                                                                <FormInput
                                                                        label="Filled Input"
                                                                        placeholder="Filled variant"
                                                                        variant="filled"
                                                                />
                                                                <FormInput
                                                                        label="Error State"
                                                                        placeholder="Input with error"
                                                                        error="This field has an error"
                                                                />
                                                                <FormInput
                                                                        label="Disabled Input"
                                                                        placeholder="Disabled input"
                                                                        disabled
                                                                />
                                                        </FormFieldGroup>
                                                </FormSection>

                                                {/* Select Variants */}
                                                <FormSection title="Select Variants">
                                                        <FormFieldGroup>
                                                                <FormSelect
                                                                        label="Single Select"
                                                                        placeholder="Choose one option"
                                                                        data={countryOptions}
                                                                />
                                                                <FormSelect
                                                                        label="Multi Select"
                                                                        placeholder="Choose multiple options"
                                                                        data={interestOptions}
                                                                        multiple
                                                                />
                                                                <FormSelect
                                                                        label="Select with Error"
                                                                        placeholder="Select with error state"
                                                                        data={countryOptions}
                                                                        error="Please select an option"
                                                                />
                                                        </FormFieldGroup>
                                                </FormSection>

                                                {/* Checkbox and Radio Variants */}
                                                <FormSection title="Checkbox & Radio Variants">
                                                        <FormFieldGroup>
                                                                <div>
                                                                        <Text size="sm" weight={600} mb="sm">Checkboxes</Text>
                                                                        <Stack spacing="xs">
                                                                                <FormCheckbox label="Default checkbox" />
                                                                                <FormCheckbox label="Checked checkbox" defaultChecked />
                                                                                <FormCheckbox label="Checkbox with error" error="This is required" />
                                                                                <FormCheckbox label="Disabled checkbox" disabled />
                                                                        </Stack>
                                                                </div>

                                                                <div>
                                                                        <Text size="sm" weight={600} mb="sm">Radio Buttons</Text>
                                                                        <Stack spacing="xs">
                                                                                <FormCheckbox type="radio" name="radio-demo" label="Option 1" />
                                                                                <FormCheckbox type="radio" name="radio-demo" label="Option 2" defaultChecked />
                                                                                <FormCheckbox type="radio" name="radio-demo" label="Option 3" />
                                                                        </Stack>
                                                                </div>
                                                        </FormFieldGroup>
                                                </FormSection>

                                                {/* Textarea Variants */}
                                                <FormSection title="Textarea Variants">
                                                        <FormFieldGroup>
                                                                <FormTextarea
                                                                        label="Default Textarea"
                                                                        placeholder="Enter your message..."
                                                                />
                                                                <FormTextarea
                                                                        label="Autosize Textarea"
                                                                        placeholder="This textarea grows with content..."
                                                                        autosize
                                                                        minRows={2}
                                                                        maxRows={5}
                                                                />
                                                                <FormTextarea
                                                                        label="Textarea with Error"
                                                                        placeholder="Textarea with error state"
                                                                        error="This field is required"
                                                                />
                                                        </FormFieldGroup>
                                                </FormSection>

                                                {/* Validation Status Examples */}
                                                <FormSection title="Validation Status Examples">
                                                        <Stack spacing="sm">
                                                                <ValidationStatus status="success" message="Field validation passed" />
                                                                <ValidationStatus status="error" message="Field validation failed" />
                                                                <ValidationStatus status="warning" message="Field needs attention" />
                                                        </Stack>
                                                </FormSection>
                                        </Stack>
                                </div>
                        </Stack>
                </Container>
        );
};

export default FormShowcase;