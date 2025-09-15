import React from 'react';
import { Group, Paper, Text, ThemeIcon, useMantineTheme, Box } from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';
import { IconFlame, IconBook, IconClock } from '@tabler/icons-react';
import { useTranslation } from 'react-i18next';
import { motion } from 'motion/react';

function DashboardStats({ stats, theme }) {
  const { t } = useTranslation('dashboard');
  const isMobile = useMediaQuery('(max-width: 768px)');

  const statItems = [
    {
      label: t('stats.currentStreak'),
      value: stats?.loginStreak || 0,
      icon: <IconFlame size={24} />,
      color: 'orange',
      purpleColor: 'var(--purple-500)',
      suffix: ` ${t('stats.days')}`,
      showOnMobile: true,
    },
    {
      label: t('stats.coursesCompleted'),
      value: stats?.totalCourses || 0,
      icon: <IconBook size={24} />,
      color: 'blue',
      purpleColor: 'var(--purple-600)',
      showOnMobile: false,
    },
    {
      label: t('totalLearnTime'),
      value: stats?.totalLearnTime || 0,
      icon: <IconClock size={24} />,
      color: 'teal',
      purpleColor: 'var(--purple-400)',
      suffix: ` ${t('stats.hoursUnit')}`,
      showOnMobile: true,
    },
  ].filter(stat => !isMobile || stat.showOnMobile);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 10
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Paper
        p="md"
        radius="md"
        withBorder
        shadow="none"
        mb="xl"
        className="transition-all duration-300"
        style={{ width: '100%' }}
        sx={(theme) => ({
          background: theme.colorScheme === 'dark' ? 'rgba(30, 32, 54, 0.8)' : 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          border: theme.colorScheme === 'dark' 
            ? '1px solid rgba(139, 92, 246, 0.2)' 
            : '1px solid rgba(0, 0, 0, 0.06)',
          borderRadius: '16px',
          position: 'relative',
          overflow: 'hidden',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: 'none',
          '&:hover': {
            transform: 'translateY(-4px)',
            borderColor: theme.colorScheme === 'dark' 
              ? 'rgba(139, 92, 246, 0.3)' 
              : 'rgba(0, 0, 0, 0.1)'
          }
        })}
      >
        <Group position="apart" spacing="md" noWrap style={{ width: '100%', justifyContent: 'space-between' }}>
          {statItems.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              style={{ width: '100%' }}
            >
              <Group spacing="md" noWrap style={{ flex: 1 }}>
                <Box
                  sx={{
                    position: 'relative',
                    zIndex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginRight: theme.spacing.sm,
                  }}
                >
                  <ThemeIcon
                    size={isMobile ? 40 : 48}
                    radius="md"
                    variant="light"
                    sx={(theme) => ({
                      minWidth: isMobile ? 44 : 52,
                      background: theme.colorScheme === 'dark'
                        ? 'rgba(139, 92, 246, 0.2)'
                        : 'rgba(139, 92, 246, 0.1)',
                      border: theme.colorScheme === 'dark'
                        ? '1px solid rgba(139, 92, 246, 0.3)'
                        : '1px solid rgba(139, 92, 246, 0.1)',
                      color: theme.colorScheme === 'dark' 
                        ? theme.colors.violet[4]
                        : theme.colors.violet[6],
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.05)'
                      }
                    })}
                  >
                    {stat.icon}
                  </ThemeIcon>
                </Box>
                <Box sx={{ 
                  position: 'relative', 
                  zIndex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  minWidth: '100px'
                }}>
                  <Text
                    size={isMobile ? 'xs' : 'sm'}
                    weight={500}
                    sx={(theme) => ({
                      marginBottom: 4,
                      color: theme.colorScheme === 'dark' 
                        ? theme.colors.gray[5]
                        : theme.colors.gray[7],
                      transition: 'color 0.3s ease',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    })}
                  >
                    {stat.label}
                  </Text>
                  <Text
                    size={isMobile ? 'lg' : 'xl'}
                    weight={700}
                    sx={(theme) => ({
                      color: theme.colorScheme === 'dark' 
                        ? theme.colors[stat.color][4]
                        : theme.colors[stat.color][7],
                      transition: 'all 0.3s ease',
                      whiteSpace: 'nowrap',
                      lineHeight: 1.2
                    })}
                  >
                    {stat.value}
                    {stat.suffix || ''}
                  </Text>
                </Box>
              </Group>
            </motion.div>
          ))}
        </Group>
      </Paper>
    </motion.div>
  );
}

export default DashboardStats;
