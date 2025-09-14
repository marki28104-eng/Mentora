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
        p="xl"
        radius="xl"
        withBorder
        shadow="lg"
        mb="xl"
        className="glass-card card-hoverable transition-all duration-300"
        sx={{
          background: 'var(--bg-card)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)',
            opacity: 0,
            transition: 'opacity 0.4s ease',
            borderRadius: 'inherit',
          },
          '&:hover::before': {
            opacity: 1,
          },
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 25px 50px -12px rgba(139, 92, 246, 0.25)',
            borderColor: 'rgba(139, 92, 246, 0.4)',
          }
        }}
      >
        <Group position="apart" spacing="xl" noWrap>
          {statItems.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Group spacing="md" noWrap>
                <Box
                  sx={{
                    position: 'relative',
                    zIndex: 1,
                  }}
                >
                  <ThemeIcon
                    size={isMobile ? 44 : 52}
                    radius="xl"
                    variant="light"
                    sx={{
                      minWidth: isMobile ? 44 : 52,
                      background: `linear-gradient(135deg, ${stat.purpleColor}15, ${stat.purpleColor}25)`,
                      border: `1px solid ${stat.purpleColor}30`,
                      color: stat.purpleColor,
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        background: `linear-gradient(135deg, ${stat.purpleColor}25, ${stat.purpleColor}35)`,
                        transform: 'scale(1.1)',
                        boxShadow: `0 8px 25px ${stat.purpleColor}40`,
                      }
                    }}
                  >
                    {stat.icon}
                  </ThemeIcon>
                </Box>
                <Box sx={{ position: 'relative', zIndex: 1 }}>
                  <Text
                    size={isMobile ? 'xs' : 'sm'}
                    color="dimmed"
                    weight={500}
                    sx={{
                      marginBottom: 4,
                      transition: 'color 0.3s ease',
                    }}
                  >
                    {stat.label}
                  </Text>
                  <Text
                    size={isMobile ? 'lg' : 'xl'}
                    weight={700}
                    sx={{
                      background: `linear-gradient(135deg, ${stat.purpleColor}, var(--purple-300))`,
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      transition: 'all 0.3s ease',
                    }}
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
