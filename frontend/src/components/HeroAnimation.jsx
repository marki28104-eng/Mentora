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
  '0%, 100%': {
    boxShadow: '0 0 25px 8px rgba(139, 92, 246, 0.4), 0 0 50px 15px rgba(139, 92, 246, 0.1)',
    transform: 'scale(1)'
  },
  '50%': {
    boxShadow: '0 0 40px 15px rgba(139, 92, 246, 0.6), 0 0 80px 25px rgba(139, 92, 246, 0.2)',
    transform: 'scale(1.05)'
  },
});

const float = keyframes({
  '0%, 100%': { transform: 'translateY(0px)' },
  '50%': { transform: 'translateY(-8px)' },
});

const sparkle = keyframes({
  '0%, 100%': { opacity: 0, transform: 'scale(0)' },
  '50%': { opacity: 1, transform: 'scale(1)' },
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
    animation: `${pulseGlow} 4s ease-in-out infinite`,
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'scale(1.1)',
      boxShadow: '0 0 50px 20px rgba(139, 92, 246, 0.6)',
    },
    '&::before': {
      content: '""',
      position: 'absolute',
      width: '120%',
      height: '120%',
      borderRadius: '50%',
      background: 'linear-gradient(135deg, rgba(196, 181, 253, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%)',
      opacity: 0.6,
      animation: `${float} 3s ease-in-out infinite`,
      zIndex: -1,
    },
    '&::after': {
      content: '""',
      position: 'absolute',
      width: '60%',
      height: '60%',
      borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, transparent 70%)',
      top: '20%',
      left: '20%',
      animation: `${sparkle} 2s ease-in-out infinite`,
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
    animation: `${orbit} 10s linear infinite`,
  },
  path2: {
    animation: `${orbit2} 8s linear infinite`,
  },
  path3: {
    animation: `${orbit3} 15s linear infinite`,
  },

  sparkleEffect: {
    position: 'absolute',
    width: 4,
    height: 4,
    borderRadius: '50%',
    background: '#ffffff',
    animation: `${sparkle} 1.5s ease-in-out infinite`,
    pointerEvents: 'none',
  },
}));

export function HeroAnimation() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const { classes } = useStyles({ isMobile });
  const theme = useMantineTheme();

  // Generate random sparkle positions
  const sparkles = Array.from({ length: 8 }, (_, i) => ({
    id: i,
    top: Math.random() * 100 + '%',
    left: Math.random() * 100 + '%',
    delay: Math.random() * 2 + 's',
  }));

  return (
    <Box className={classes.container}>
      {/* Sparkle effects */}
      {sparkles.map((sparkle) => (
        <Box
          key={sparkle.id}
          className={classes.sparkleEffect}
          style={{
            top: sparkle.top,
            left: sparkle.left,
            animationDelay: sparkle.delay,
          }}
        />
      ))}

      <Box className={classes.centralCore} />

      <Box className={`${classes.orbitPath} ${classes.path1}`}>
        <Box className={classes.satellite} style={{
          background: 'linear-gradient(135deg, #c084fc 0%, #a855f7 100%)',
          boxShadow: '0 0 15px rgba(139, 92, 246, 0.8)',
          animation: `${float} 2s ease-in-out infinite`,
        }} />
      </Box>

      <Box className={`${classes.orbitPath} ${classes.path2}`}>
        <Box className={classes.satellite} style={{
          width: 12,
          height: 12,
          top: -6,
          left: -6,
          background: theme.colorScheme === 'dark'
            ? 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)'
            : 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
          boxShadow: theme.colorScheme === 'dark'
            ? '0 0 12px rgba(255, 255, 255, 0.8)'
            : '0 0 12px rgba(31, 41, 55, 0.6)',
          animation: `${float} 2.5s ease-in-out infinite 0.5s`,
        }} />
      </Box>

      <Box className={`${classes.orbitPath} ${classes.path3}`}>
        <Box className={classes.satellite} style={{
          width: 20,
          height: 20,
          top: -10,
          left: -10,
          background: 'linear-gradient(135deg, #ddd6fe 0%, #c084fc 100%)',
          boxShadow: '0 0 18px rgba(196, 181, 253, 0.8)',
          animation: `${float} 1.8s ease-in-out infinite 1s`,
        }} />
      </Box>
    </Box>
  );
}

export default HeroAnimation;