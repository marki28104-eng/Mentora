import { Box, createStyles, keyframes, useMantineTheme } from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';



// Define the keyframes for our animations
const orbit = keyframes({
  '0%': { transform: 'rotate(0deg) translateX(120px) rotate(0deg)' },
  '100%': { transform: 'rotate(360deg) translateX(120px) rotate(-360deg)' },
});

const orbit2 = keyframes({
  '0%': { transform: 'rotate(0deg) translateX(80px) rotate(0deg)' },
  '100%': { transform: 'rotate(-360deg) translateX(80px) rotate(360deg)' },
});

const orbit3 = keyframes({
  '0%': { transform: 'rotate(0deg) translateX(160px) rotate(0deg)' },
  '100%': { transform: 'rotate(360deg) translateX(160px) rotate(-360deg)' },
});

const pulseGlow = keyframes({
  '0%, 100%': { boxShadow: '0 0 25px 8px rgba(139, 92, 246, 0.4)' },
  '50%': { boxShadow: '0 0 40px 15px rgba(139, 92, 246, 0.2)' },
});


// Define the styles for the animation elements
const useStyles = createStyles((theme) => ({

  container: {
    position: 'relative',
    width: 350,
    height: 350,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    [theme.fn.smallerThan('lg')]: {
      width: 300,
      height: 300,
    },
    [theme.fn.smallerThan('sm')]: {
      width: 250,
      height: 250,
    },
  },

  centralCore: {
    width: 80,
    height: 80,
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #9333ea 100%)',
    animation: `${pulseGlow} ${useMediaQuery('(max-width: 768px)') ? '12s' : '4s'} ease-in-out infinite`,
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    '&::before': {
      content: '""',
      position: 'absolute',
      width: '100%',
      height: '100%',
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #c084fc 0%, #8b5cf6 100%)',
      opacity: 0.3,
      animation: 'pulse 2s ease-in-out infinite alternate',
    },
  },

  // Base style for the invisible path the satellites will follow
  orbitPath: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: 1,
    height: 1,
    borderRadius: '50%',
  },

  // The visible satellite dot
  satellite: {
    position: 'absolute',
    top: -8,
    left: -8,
    width: 16,
    height: 16,
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #c084fc 0%, #a855f7 100%)',
    boxShadow: '0 0 10px rgba(139, 92, 246, 0.6)',
  },

  // Specific animation assignments for each path
  path1: {
    animation: `${orbit} ${useMediaQuery('(max-width: 768px)') ? '30s' : '10s'} linear infinite`,
  },
  path2: {
    animation: `${orbit2} ${useMediaQuery('(max-width: 768px)') ? '20s' : '8s'} linear infinite`,
  },
  path3: {
    animation: `${orbit3} ${useMediaQuery('(max-width: 768px)') ? '40s' : '15s'} linear infinite`,
  },
}));

export function HeroAnimation() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const { classes } = useStyles({ isMobile });
  const theme = useMantineTheme();


  return (
    <Box className={classes.container}>
      <Box className={classes.centralCore} />

      <Box className={`${classes.orbitPath} ${classes.path1}`}>
        <Box className={classes.satellite} />
      </Box>

      <Box className={`${classes.orbitPath} ${classes.path2}`}>
        <Box className={classes.satellite} style={{
          width: 12,
          height: 12,
          top: -6,
          left: -6,
          background: theme.colorScheme === 'dark' ? '#ffffff' : '#1f2937',
          boxShadow: theme.colorScheme === 'dark' ? '0 0 8px rgba(255, 255, 255, 0.8)' : '0 0 8px rgba(31, 41, 55, 0.6)'
        }} />
      </Box>

      <Box className={`${classes.orbitPath} ${classes.path3}`}>
        <Box className={classes.satellite} style={{
          width: 20,
          height: 20,
          top: -10,
          left: -10,
          background: 'linear-gradient(135deg, #ddd6fe 0%, #c084fc 100%)',
          boxShadow: '0 0 12px rgba(196, 181, 253, 0.8)'
        }} />
      </Box>
    </Box>
  );
}

export default HeroAnimation;