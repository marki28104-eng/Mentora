/**
 * Analytics monitoring dashboard component for admin users
 */

import React, { useState, useEffect } from 'react';
import {
        Card,
        Grid,
        Text,
        Badge,
        Group,
        Stack,
        Button,
        Alert,
        Loader,
        Progress,
        ActionIcon,
        Tooltip,
        Modal,
        JsonInput
} from '@mantine/core';
import {
        IconRefresh,
        IconAlertTriangle,
        IconCheck,
        IconX,
        IconClock,
        IconDatabase,
        IconChartBar,
        IconBrain,
        IconCloud
} from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import { notifications } from '@mantine/notifications';

const AnalyticsMonitoring = () => {
        const { t } = useTranslation();
        const [healthStatus, setHealthStatus] = useState(null);
        const [metrics, setMetrics] = useState(null);
        const [alerts, setAlerts] = useState([]);
        const [loading, setLoading] = useState(true);
        const [refreshing, setRefreshing] = useState(false);
        const [detailsModal, setDetailsModal] = useState({ open: false, service: null, data: null });

        useEffect(() => {
                fetchMonitoringData();

                // Set up auto-refresh every 30 seconds
                const interval = setInterval(fetchMonitoringData, 30000);
                return () => clearInterval(interval);
        }, []);

        const fetchMonitoringData = async () => {
                try {
                        setRefreshing(true);

                        // Fetch health status
                        const healthResponse = await fetch('/api/monitoring/health', {
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });

                        if (healthResponse.ok) {
                                const healthData = await healthResponse.json();
                                setHealthStatus(healthData.data);
                        }

                        // Fetch metrics
                        const metricsResponse = await fetch('/api/monitoring/metrics', {
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });

                        if (metricsResponse.ok) {
                                const metricsData = await metricsResponse.json();
                                setMetrics(metricsData.data);
                        }

                        // Fetch alerts
                        const alertsResponse = await fetch('/api/monitoring/alerts', {
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });

                        if (alertsResponse.ok) {
                                const alertsData = await alertsResponse.json();
                                setAlerts(alertsData.data.active_alerts || []);
                        }

                } catch (error) {
                        console.error('Failed to fetch monitoring data:', error);
                        notifications.show({
                                title: 'Error',
                                message: 'Failed to fetch monitoring data',
                                color: 'red',
                                icon: <IconX />
                        });
                } finally {
                        setLoading(false);
                        setRefreshing(false);
                }
        };

        const getStatusColor = (status) => {
                switch (status) {
                        case 'healthy': return 'green';
                        case 'warning': return 'yellow';
                        case 'critical': return 'red';
                        default: return 'gray';
                }
        };

        const getStatusIcon = (status) => {
                switch (status) {
                        case 'healthy': return <IconCheck size={16} />;
                        case 'warning': return <IconAlertTriangle size={16} />;
                        case 'critical': return <IconX size={16} />;
                        default: return <IconClock size={16} />;
                }
        };

        const getServiceIcon = (serviceName) => {
                switch (serviceName) {
                        case 'umami_integration': return <IconCloud size={20} />;
                        case 'analytics_processing': return <IconChartBar size={20} />;
                        case 'personalization_engine': return <IconBrain size={20} />;
                        case 'database': return <IconDatabase size={20} />;
                        default: return <IconClock size={20} />;
                }
        };

        const sendTestAlert = async () => {
                try {
                        const response = await fetch('/api/monitoring/alerts/test', {
                                method: 'POST',
                                headers: {
                                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                        });

                        if (response.ok) {
                                notifications.show({
                                        title: 'Success',
                                        message: 'Test alert sent successfully',
                                        color: 'green',
                                        icon: <IconCheck />
                                });
                        }
                } catch (error) {
                        notifications.show({
                                title: 'Error',
                                message: 'Failed to send test alert',
                                color: 'red',
                                icon: <IconX />
                        });
                }
        };

        const showServiceDetails = (serviceName, serviceData) => {
                setDetailsModal({
                        open: true,
                        service: serviceName,
                        data: serviceData
                });
        };

        if (loading) {
                return (
                        <Card>
                                <Group justify="center" p="xl">
                                        <Loader size="lg" />
                                        <Text>Loading monitoring data...</Text>
                                </Group>
                        </Card>
                );
        }

        return (
                <Stack spacing="md">
                        {/* Header */}
                        <Group justify="space-between">
                                <Text size="xl" fw={700}>Analytics System Monitoring</Text>
                                <Group>
                                        <Button
                                                variant="outline"
                                                leftSection={<IconRefresh size={16} />}
                                                onClick={fetchMonitoringData}
                                                loading={refreshing}
                                        >
                                                Refresh
                                        </Button>
                                        <Button
                                                variant="light"
                                                onClick={sendTestAlert}
                                        >
                                                Test Alert
                                        </Button>
                                </Group>
                        </Group>

                        {/* Overall Status */}
                        <Card>
                                <Group justify="space-between">
                                        <Text size="lg" fw={600}>Overall System Status</Text>
                                        <Badge
                                                color={getStatusColor(healthStatus?.overall_status)}
                                                leftSection={getStatusIcon(healthStatus?.overall_status)}
                                                size="lg"
                                        >
                                                {healthStatus?.overall_status?.toUpperCase() || 'UNKNOWN'}
                                        </Badge>
                                </Group>
                        </Card>

                        {/* Active Alerts */}
                        {alerts.length > 0 && (
                                <Alert
                                        icon={<IconAlertTriangle size={16} />}
                                        title="Active Alerts"
                                        color="red"
                                >
                                        <Stack spacing="xs">
                                                {alerts.map((alert, index) => (
                                                        <Text key={index} size="sm">
                                                                <strong>{alert.name}:</strong> {alert.message}
                                                                {alert.current_value && (
                                                                        <Text span c="dimmed" ml="xs">
                                                                                (Current: {alert.current_value}, Threshold: {alert.threshold})
                                                                        </Text>
                                                                )}
                                                        </Text>
                                                ))}
                                        </Stack>
                                </Alert>
                        )}

                        {/* Service Health Cards */}
                        <Grid>
                                {healthStatus?.services && Object.entries(healthStatus.services).map(([serviceName, serviceData]) => (
                                        <Grid.Col key={serviceName} span={{ base: 12, md: 6, lg: 3 }}>
                                                <Card
                                                        style={{ cursor: 'pointer' }}
                                                        onClick={() => showServiceDetails(serviceName, serviceData)}
                                                >
                                                        <Stack spacing="sm">
                                                                <Group justify="space-between">
                                                                        <Group>
                                                                                {getServiceIcon(serviceName)}
                                                                                <Text fw={600} size="sm">
                                                                                        {serviceName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                                                </Text>
                                                                        </Group>
                                                                        <Badge
                                                                                color={getStatusColor(serviceData.status)}
                                                                                leftSection={getStatusIcon(serviceData.status)}
                                                                                size="sm"
                                                                        >
                                                                                {serviceData.status}
                                                                        </Badge>
                                                                </Group>

                                                                <Text size="xs" c="dimmed">
                                                                        {serviceData.message}
                                                                </Text>

                                                                <Group justify="space-between">
                                                                        <Text size="xs" c="dimmed">
                                                                                Response Time
                                                                        </Text>
                                                                        <Text size="xs" fw={500}>
                                                                                {serviceData.response_time_ms?.toFixed(0)}ms
                                                                        </Text>
                                                                </Group>

                                                                <Progress
                                                                        value={Math.min((serviceData.response_time_ms || 0) / 10, 100)}
                                                                        color={serviceData.response_time_ms > 1000 ? 'red' : serviceData.response_time_ms > 500 ? 'yellow' : 'green'}
                                                                        size="xs"
                                                                />
                                                        </Stack>
                                                </Card>
                                        </Grid.Col>
                                ))}
                        </Grid>

                        {/* Metrics Cards */}
                        {metrics && (
                                <Grid>
                                        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
                                                <Card>
                                                        <Stack spacing="xs">
                                                                <Text size="sm" c="dimmed">Total Events (24h)</Text>
                                                                <Text size="xl" fw={700}>{metrics.total_events_24h?.toLocaleString() || 0}</Text>
                                                        </Stack>
                                                </Card>
                                        </Grid.Col>

                                        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
                                                <Card>
                                                        <Stack spacing="xs">
                                                                <Text size="sm" c="dimmed">Active Users (24h)</Text>
                                                                <Text size="xl" fw={700}>{metrics.unique_users_24h?.toLocaleString() || 0}</Text>
                                                        </Stack>
                                                </Card>
                                        </Grid.Col>

                                        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
                                                <Card>
                                                        <Stack spacing="xs">
                                                                <Text size="sm" c="dimmed">Avg Engagement</Text>
                                                                <Text size="xl" fw={700}>
                                                                        {((metrics.average_engagement_score || 0) * 100).toFixed(1)}%
                                                                </Text>
                                                        </Stack>
                                                </Card>
                                        </Grid.Col>

                                        <Grid.Col span={{ base: 12, md: 6, lg: 3 }}>
                                                <Card>
                                                        <Stack spacing="xs">
                                                                <Text size="sm" c="dimmed">Error Rate</Text>
                                                                <Text size="xl" fw={700} c={metrics.error_rate > 0.05 ? 'red' : 'green'}>
                                                                        {((metrics.error_rate || 0) * 100).toFixed(2)}%
                                                                </Text>
                                                        </Stack>
                                                </Card>
                                        </Grid.Col>
                                </Grid>
                        )}

                        {/* Service Details Modal */}
                        <Modal
                                opened={detailsModal.open}
                                onClose={() => setDetailsModal({ open: false, service: null, data: null })}
                                title={`${detailsModal.service?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Details`}
                                size="lg"
                        >
                                {detailsModal.data && (
                                        <Stack spacing="md">
                                                <Group>
                                                        <Text fw={600}>Status:</Text>
                                                        <Badge color={getStatusColor(detailsModal.data.status)}>
                                                                {detailsModal.data.status}
                                                        </Badge>
                                                </Group>

                                                <Text>
                                                        <strong>Message:</strong> {detailsModal.data.message}
                                                </Text>

                                                <Text>
                                                        <strong>Response Time:</strong> {detailsModal.data.response_time_ms?.toFixed(2)}ms
                                                </Text>

                                                <Text>
                                                        <strong>Last Check:</strong> {new Date(detailsModal.data.timestamp).toLocaleString()}
                                                </Text>

                                                {detailsModal.data.details && (
                                                        <>
                                                                <Text fw={600}>Details:</Text>
                                                                <JsonInput
                                                                        value={JSON.stringify(detailsModal.data.details, null, 2)}
                                                                        readOnly
                                                                        autosize
                                                                        minRows={3}
                                                                        maxRows={10}
                                                                />
                                                        </>
                                                )}
                                        </Stack>
                                )}
                        </Modal>
                </Stack>
        );
};

export default AnalyticsMonitoring;