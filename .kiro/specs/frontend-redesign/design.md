# Design Document

## Overview

This design document outlines the comprehensive frontend redesign of Mentora to implement a modern, purple-themed design system with dark/light mode support, inspired by the Kiro website aesthetic. The redesign will transform the visual appearance while maintaining all existing functionality, creating a cohesive and professional user experience.

## Architecture

### Design System Architecture

The new design system will be built on top of the existing Mantine UI framework, leveraging its theming capabilities while introducing custom purple color palettes and modern visual elements.

```
Design System Structure:
├── Color System (Purple-based palette)
├── Typography (Modern font stack)
├── Spacing & Layout (Consistent grid system)
├── Components (Styled Mantine components)
├── Animations (Smooth transitions & micro-interactions)
└── Theme Provider (Dark/Light mode management)
```

### Technology Stack Integration

- **Mantine UI**: Enhanced with custom purple theme configuration
- **Tailwind CSS**: Extended with purple color variants
- **CSS Variables**: Centralized color token management
- **React Context**: Theme state management
- **i18n**: Maintained language support (German/English)

## Components and Interfaces

### 1. Color System

#### Purple Color Palette
```css
/* Light Mode Purple Palette */
--purple-50: #faf5ff
--purple-100: #f3e8ff
--purple-200: #e9d5ff
--purple-300: #d8b4fe
--purple-400: #c084fc
--purple-500: #a855f7  /* Primary */
--purple-600: #9333ea
--purple-700: #7c3aed
--purple-800: #6b21b6
--purple-900: #581c87

/* Dark Mode Purple Palette */
--purple-dark-50: #1e1b4b
--purple-dark-100: #312e81
--purple-dark-200: #3730a3
--purple-dark-300: #4338ca
--purple-dark-400: #5b21b6
--purple-dark-500: #7c3aed  /* Primary */
--purple-dark-600: #8b5cf6
--purple-dark-700: #a78bfa
--purple-dark-800: #c4b5fd
--purple-dark-900: #ddd6fe
```

#### Background Colors
```css
/* Light Mode Backgrounds */
--bg-primary: #ffffff
--bg-secondary: #fafafa
--bg-tertiary: #f8fafc
--bg-card: rgba(255, 255, 255, 0.8)
--bg-glass: rgba(255, 255, 255, 0.1)

/* Dark Mode Backgrounds */
--bg-primary-dark: #0f0f23
--bg-secondary-dark: #1a1a2e
--bg-tertiary-dark: #16213e
--bg-card-dark: rgba(15, 15, 35, 0.6)
--bg-glass-dark: rgba(139, 92, 246, 0.1)
```

### 2. Typography System

#### Font Stack
```css
--font-primary: 'Inter', system-ui, -apple-system, sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', monospace
```

#### Typography Scale
```css
--text-xs: 0.75rem     /* 12px */
--text-sm: 0.875rem    /* 14px */
--text-base: 1rem      /* 16px */
--text-lg: 1.125rem    /* 18px */
--text-xl: 1.25rem     /* 20px */
--text-2xl: 1.5rem     /* 24px */
--text-3xl: 1.875rem   /* 30px */
--text-4xl: 2.25rem    /* 36px */
--text-5xl: 3rem       /* 48px */
--text-6xl: 3.75rem    /* 60px */
```

### 3. Component Design Specifications

#### Buttons
```css
/* Primary Button */
.btn-primary {
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #9333ea 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6);
}

/* Secondary Button */
.btn-secondary {
  border: 2px solid var(--purple-500);
  background: transparent;
  border-radius: 12px;
  padding: 10px 22px;
  font-weight: 600;
  color: var(--purple-500);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-secondary:hover {
  background: rgba(139, 92, 246, 0.1);
  transform: translateY(-2px);
}
```

#### Cards
```css
.card-modern {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.card-modern:hover {
  transform: translateY(-8px);
  box-shadow: 0 25px 50px -12px rgba(139, 92, 246, 0.25);
  border-color: rgba(139, 92, 246, 0.4);
}

.card-modern::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.card-modern:hover::before {
  opacity: 1;
}
```

#### Navigation
```css
.nav-modern {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(139, 92, 246, 0.1);
  padding: 16px 0;
}

.nav-item {
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: var(--text-secondary);
}

.nav-item:hover {
  background: rgba(139, 92, 246, 0.1);
  color: var(--purple-500);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
  color: var(--purple-600);
  font-weight: 600;
}
```

### 4. Animation System

#### Keyframe Animations
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
  }
  70% {
    box-shadow: 0 0 0 20px rgba(139, 92, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
  }
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
```

#### Transition Classes
```css
.transition-smooth {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.transition-bounce {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.hover-lift:hover {
  transform: translateY(-4px);
}

.hover-scale:hover {
  transform: scale(1.05);
}
```

## Data Models

### Theme Configuration Model
```typescript
interface ThemeConfig {
  colorScheme: 'light' | 'dark';
  primaryColor: string;
  colors: {
    purple: string[];
    gray: string[];
    background: {
      primary: string;
      secondary: string;
      tertiary: string;
      card: string;
      glass: string;
    };
    text: {
      primary: string;
      secondary: string;
      tertiary: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}
```

### Component Style Model
```typescript
interface ComponentStyles {
  button: {
    primary: CSSProperties;
    secondary: CSSProperties;
    ghost: CSSProperties;
  };
  card: {
    default: CSSProperties;
    elevated: CSSProperties;
    glass: CSSProperties;
  };
  navigation: {
    container: CSSProperties;
    item: CSSProperties;
    activeItem: CSSProperties;
  };
}
```

## Error Handling

### Theme Loading Error Handling
```typescript
const ThemeProvider = ({ children }) => {
  const [themeError, setThemeError] = useState(null);
  
  const handleThemeError = (error) => {
    console.error('Theme loading error:', error);
    setThemeError(error);
    // Fallback to default theme
    return defaultTheme;
  };
  
  if (themeError) {
    return <FallbackTheme>{children}</FallbackTheme>;
  }
  
  return <MantineProvider theme={theme}>{children}</MantineProvider>;
};
```

### CSS Loading Fallbacks
```css
/* Fallback styles for when custom CSS fails to load */
.fallback-theme {
  --primary-color: #8b5cf6;
  --background-color: #ffffff;
  --text-color: #1f2937;
}

@media (prefers-color-scheme: dark) {
  .fallback-theme {
    --background-color: #1f2937;
    --text-color: #ffffff;
  }
}
```

### Animation Performance Optimization
```css
/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* GPU acceleration for smooth animations */
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
}
```

## Testing Strategy

### Visual Regression Testing
```typescript
// Component visual testing with Storybook
export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    themes: {
      default: 'light',
      list: [
        { name: 'light', class: 'theme-light', color: '#ffffff' },
        { name: 'dark', class: 'theme-dark', color: '#0f0f23' }
      ]
    }
  }
};

export const Primary = {
  args: {
    variant: 'primary',
    children: 'Primary Button'
  }
};

export const Secondary = {
  args: {
    variant: 'secondary',
    children: 'Secondary Button'
  }
};
```

### Theme Testing
```typescript
describe('Theme System', () => {
  test('should apply light theme correctly', () => {
    render(<App theme="light" />);
    expect(document.documentElement).toHaveClass('theme-light');
  });
  
  test('should apply dark theme correctly', () => {
    render(<App theme="dark" />);
    expect(document.documentElement).toHaveClass('theme-dark');
  });
  
  test('should persist theme preference', () => {
    const { rerender } = render(<App theme="dark" />);
    expect(localStorage.getItem('theme')).toBe('dark');
    
    rerender(<App />);
    expect(document.documentElement).toHaveClass('theme-dark');
  });
});
```

### Accessibility Testing
```typescript
describe('Accessibility', () => {
  test('should maintain proper contrast ratios', () => {
    render(<Button variant="primary">Test Button</Button>);
    const button = screen.getByRole('button');
    
    // Test contrast ratio meets WCAG AA standards
    expect(getContrastRatio(button)).toBeGreaterThan(4.5);
  });
  
  test('should support keyboard navigation', () => {
    render(<Navigation />);
    const firstItem = screen.getByRole('link', { name: /dashboard/i });
    
    firstItem.focus();
    fireEvent.keyDown(firstItem, { key: 'Tab' });
    
    expect(document.activeElement).toBe(
      screen.getByRole('link', { name: /courses/i })
    );
  });
});
```

### Performance Testing
```typescript
describe('Performance', () => {
  test('should load theme styles within performance budget', async () => {
    const startTime = performance.now();
    render(<App />);
    
    await waitFor(() => {
      expect(document.querySelector('.theme-loaded')).toBeInTheDocument();
    });
    
    const loadTime = performance.now() - startTime;
    expect(loadTime).toBeLessThan(100); // 100ms budget
  });
  
  test('should not cause layout shifts during theme changes', () => {
    const { rerender } = render(<App theme="light" />);
    const initialLayout = getLayoutMetrics();
    
    rerender(<App theme="dark" />);
    const newLayout = getLayoutMetrics();
    
    expect(newLayout.cumulativeLayoutShift).toBe(0);
  });
});
```

## Implementation Phases

### Phase 1: Foundation Setup
1. Update CSS variables and Tailwind configuration
2. Enhance Mantine theme configuration
3. Implement theme provider with dark/light mode support
4. Create base component styles

### Phase 2: Core Components
1. Redesign navigation and layout components
2. Update button and form components
3. Implement modern card designs
4. Add animation system

### Phase 3: Page Updates
1. Redesign landing page with new theme
2. Update dashboard and course pages
3. Modernize settings and admin pages
4. Implement responsive design improvements

### Phase 4: Polish & Optimization
1. Add micro-interactions and animations
2. Optimize performance and accessibility
3. Conduct visual regression testing
4. Fine-tune responsive behavior

This design provides a comprehensive foundation for transforming Mentora into a modern, purple-themed application that rivals the visual appeal of Kiro while maintaining all existing functionality and improving the overall user experience.