# Modern UI Component System

This directory contains the modern purple-themed UI components with glass morphism effects, animations, and comprehensive styling utilities.

## Components

### Button (`Button.jsx`)

Modern button component with multiple variants and sizes.

**Variants:**
- `primary` - Purple gradient button with shadow effects
- `secondary` - Purple border button with transparent background
- `ghost` - Minimal button with subtle hover effects
- `gradient` - Animated gradient background button

**Sizes:**
- `xs` - Extra small (6px 12px padding)
- `sm` - Small (8px 16px padding)
- `md` - Medium (12px 24px padding) - Default
- `lg` - Large (16px 32px padding)
- `xl` - Extra large (20px 40px padding)

**Props:**
- `variant` - Button style variant
- `size` - Button size
- `disabled` - Disable the button
- `loading` - Show loading state
- `leftIcon` - Icon on the left side
- `rightIcon` - Icon on the right side
- `fullWidth` - Make button full width

**Example:**
```jsx
import { Button } from './components/ui';

<Button variant="primary" size="lg" leftIcon={<IconHome />}>
  Get Started
</Button>
```

### Card (`Card.jsx`)

Modern card component with glass morphism and various styling options.

**Variants:**
- `default` - Standard card with subtle border and shadow
- `glass` - Glass morphism effect with backdrop blur
- `elevated` - Enhanced shadows for floating appearance
- `gradient` - Subtle purple gradient background
- `outline` - Transparent background with purple border

**Props:**
- `variant` - Card style variant
- `hoverable` - Enable hover effects
- `padding` - Internal padding (xs, sm, md, lg, xl)
- `radius` - Border radius (xs, sm, md, lg, xl)
- `withBorder` - Add border
- `shadow` - Shadow intensity

**Example:**
```jsx
import { Card } from './components/ui';

<Card variant="glass" hoverable className="p-6">
  <div className="card-header">
    <h3 className="card-title">Card Title</h3>
  </div>
  <div className="card-content">
    <p>Card content goes here</p>
  </div>
</Card>
```

### Navigation (`Navigation.jsx`)

Modern navigation components with purple accents and smooth transitions.

**Components:**
- `Navigation` - Main navigation component
- `Breadcrumb` - Breadcrumb navigation
- `TabNavigation` - Tab-based navigation

**Navigation Variants:**
- `horizontal` - Horizontal layout
- `vertical` - Vertical layout
- `sidebar` - Full sidebar navigation

**Example:**
```jsx
import { Navigation, Breadcrumb, TabNavigation } from './components/ui';

const navItems = [
  { key: 'home', to: '/', label: 'Home', icon: <IconHome /> },
  { key: 'profile', to: '/profile', label: 'Profile', badge: '2' }
];

<Navigation items={navItems} variant="horizontal" />
```

## CSS Classes and Utilities

### Animation Classes

- `animate-fade-in-up` - Fade in from bottom animation
- `animate-slide-in-right` - Slide in from right animation
- `animate-float` - Floating animation (infinite)
- `animate-pulse-purple` - Purple pulse animation
- `animate-gradient-shift` - Gradient shifting animation

### Transition Classes

- `transition-smooth` - Smooth all transitions (0.3s cubic-bezier)
- `transition-bounce` - Bouncy transitions (0.4s bounce easing)
- `transition-colors` - Color-only transitions
- `transition-transform` - Transform-only transitions
- `transition-opacity` - Opacity-only transitions
- `transition-shadow` - Shadow-only transitions

### Duration Modifiers

- `duration-150` - 150ms duration
- `duration-200` - 200ms duration
- `duration-300` - 300ms duration
- `duration-500` - 500ms duration
- `duration-700` - 700ms duration

### Easing Modifiers

- `ease-linear` - Linear easing
- `ease-in` - Ease in
- `ease-out` - Ease out
- `ease-in-out` - Ease in-out
- `ease-bounce` - Bounce easing

### Transform Utilities

- `hover:-translate-y-1` - Lift on hover (4px up)
- `hover:-translate-y-2` - Lift on hover (8px up)
- `hover:-translate-y-4` - Lift on hover (16px up)
- `hover:scale-105` - Scale up 5% on hover
- `hover:scale-110` - Scale up 10% on hover

### Shadow Utilities

- `shadow-purple-sm` - Small purple shadow
- `shadow-purple-md` - Medium purple shadow
- `shadow-purple-lg` - Large purple shadow
- `shadow-purple-xl` - Extra large purple shadow
- `shadow-purple-2xl` - 2X large purple shadow

### Backdrop Blur Utilities

- `backdrop-blur-sm` - Small blur (4px)
- `backdrop-blur` - Default blur (8px)
- `backdrop-blur-md` - Medium blur (12px)
- `backdrop-blur-lg` - Large blur (16px)
- `backdrop-blur-xl` - Extra large blur (24px)
- `backdrop-blur-2xl` - 2X large blur (40px)

### Gradient Background Utilities

- `bg-gradient-purple` - Main purple gradient
- `bg-gradient-purple-light` - Light purple gradient
- `bg-gradient-purple-subtle` - Subtle purple gradient (10% opacity)
- `bg-gradient-purple-radial` - Radial purple gradient

### Interactive Utilities

- `interactive` - Makes element interactive with hover lift
- `loading` - Loading state with spinner
- `hover-lift` - Lift effect on hover
- `hover-scale` - Scale effect on hover

## Color System

The components use CSS custom properties for consistent theming:

### Purple Palette
- `--purple-50` to `--purple-900` - Purple color scale
- Automatically switches between light and dark mode variants

### Background Colors
- `--bg-primary` - Primary background
- `--bg-secondary` - Secondary background
- `--bg-tertiary` - Tertiary background
- `--bg-card` - Card background (with transparency)
- `--bg-glass` - Glass morphism background

### Text Colors
- `--text-primary` - Primary text color
- `--text-secondary` - Secondary text color
- `--text-tertiary` - Tertiary text color

## Accessibility

All components include:
- Proper focus indicators with purple outlines
- Keyboard navigation support
- Screen reader compatibility
- Reduced motion support (respects `prefers-reduced-motion`)
- High contrast ratios for WCAG compliance

## Browser Support

- Modern browsers with CSS custom properties support
- Backdrop-filter support (with fallbacks)
- CSS Grid and Flexbox support
- Automatic fallbacks for unsupported features

## Usage Tips

1. **Import components from the index file:**
   ```jsx
   import { Button, Card, Navigation } from './components/ui';
   ```

2. **Use CSS classes for consistent styling:**
   ```jsx
   <div className="transition-smooth hover:-translate-y-2 shadow-purple-lg">
     Content with smooth hover effects
   </div>
   ```

3. **Combine components for complex layouts:**
   ```jsx
   <Card variant="glass" hoverable>
     <Navigation items={items} variant="vertical" />
     <Button variant="gradient" fullWidth>Action</Button>
   </Card>
   ```

4. **Leverage animation classes for enhanced UX:**
   ```jsx
   <div className="animate-fade-in-up stagger-1">
     <Card>Content that fades in with delay</Card>
   </div>
   ```

## Performance Considerations

- All animations use GPU acceleration (`transform: translateZ(0)`)
- Transitions respect user's motion preferences
- CSS is optimized for minimal repaints
- Components are tree-shakeable for optimal bundle size