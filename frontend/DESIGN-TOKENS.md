# Design Tokens Reference

## Quick Copy-Paste Design System

### Color Classes (Tailwind)

#### Backgrounds
```tsx
className="bg-background"        // Main page background (deep black)
className="bg-card"              // Card/panel background (elevated black)
className="bg-primary"           // Primary action background (white in dark)
className="bg-secondary"         // Secondary elements
className="bg-muted"             // Muted/disabled states
className="bg-accent"            // Hover/active states
className="bg-destructive"       // Delete/error actions
```

#### Text Colors
```tsx
className="text-foreground"      // Primary text (off-white)
className="text-primary"         // Primary colored text
className="text-muted-foreground" // Secondary/meta text
className="text-destructive"     // Error/warning text
className="text-card-foreground" // Text on cards
```

#### Borders
```tsx
className="border-border"        // Standard borders
className="border-primary"       // Accent borders
className="border-destructive"   // Error borders
```

### Spacing Scale

```tsx
// Gaps & Padding
gap-1   // 4px    - Tight icon spacing
gap-2   // 8px    - Small element gaps
gap-3   // 12px   - Default gaps
gap-4   // 16px   - Section spacing

p-2     // 8px    - Icon button padding
p-4     // 16px   - Small padding
p-5     // 20px   - Card padding
p-6     // 24px   - Page padding

px-4 py-2  // 16px×8px - Button padding
px-6 py-3  // 24px×12px - Large button
```

### Border Radius

```tsx
rounded-sm    // calc(0.5rem - 4px)
rounded-md    // calc(0.5rem - 2px)
rounded-lg    // 0.5rem (8px) - Cards
rounded-xl    // 0.75rem (12px) - Large cards
rounded-2xl   // 1rem (16px) - Modals
```

### Shadows

```tsx
shadow-sm     // Subtle elevation
shadow-lg     // Card elevation
shadow-xl     // Modal elevation
shadow-2xl    // Maximum elevation

// Custom shadows
shadow-primary/25   // Primary colored shadow (25% opacity)
shadow-primary/30   // Hover state shadow
```

### Common Component Patterns

#### Card Pattern
```tsx
<div className="rounded-xl border bg-card p-5 shadow-sm hover:shadow-lg transition-all">
  {/* Card content */}
</div>
```

#### Button Pattern (Primary)
```tsx
<button className={cn(
  "rounded-lg px-5 py-2.5 text-sm font-medium",
  "bg-primary text-primary-foreground",
  "hover:bg-primary/90 shadow-lg shadow-primary/25",
  "disabled:opacity-50 disabled:cursor-not-allowed"
)}>
  Button Text
</button>
```

#### Button Pattern (Secondary)
```tsx
<button className={cn(
  "rounded-lg px-4 py-2 text-sm font-medium",
  "bg-secondary text-secondary-foreground",
  "hover:bg-secondary/80 transition-colors"
)}>
  Secondary
</button>
```

#### Input Pattern
```tsx
<input className={cn(
  "w-full rounded-lg border bg-background px-4 py-3 text-base",
  "placeholder:text-muted-foreground/50",
  "focus:outline-none focus:ring-2 focus:ring-primary/20",
  "disabled:opacity-50 disabled:cursor-not-allowed"
)} />
```

#### Icon Button Pattern
```tsx
<button className={cn(
  "rounded-lg p-2",
  "text-muted-foreground hover:text-foreground",
  "hover:bg-accent transition-colors"
)}>
  <Icon className="h-4 w-4" />
</button>
```

## Framer Motion Patterns

### Basic Entrance
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
```

### Exit Animation
```tsx
<AnimatePresence>
  {show && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
  )}
</AnimatePresence>
```

### Hover/Tap
```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
```

### Layout Animation
```tsx
<motion.div layout>
  {/* Content that might change position */}
</motion.div>
```

### Staggered List
```tsx
{items.map((item, index) => (
  <motion.div
    key={item.id}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.05 }}
  >
    {item.content}
  </motion.div>
))}
```

## Typography Scale

```tsx
// Headings
text-xl font-bold         // Page title (20px)
text-lg font-semibold     // Card title (18px)
text-sm font-medium       // Labels (14px)

// Body
text-base                 // Body text (16px)
text-sm                   // Secondary text (14px)
text-xs                   // Metadata (12px)

// Tracking
tracking-tight            // Headlines
tracking-wider            // Section labels (uppercase)
```

## Opacity Scale

```tsx
opacity-0      // Hidden (animations)
opacity-50     // Disabled
opacity-60     // Completed tasks
opacity-70     // Hover states
opacity-100    // Full visibility
```

## Transition Classes

```tsx
transition-all         // All properties
transition-colors      // Just colors
transition-transform   // Just transforms
transition-opacity     // Just opacity

duration-200          // 200ms (fast)
duration-300          // 300ms (default)
ease-out             // Ease out curve
```

## Common Icon Sizes

```tsx
h-4 w-4     // Small icons in buttons (16px)
h-5 w-5     // Standard icons (20px)
h-6 w-6     // Checkboxes (24px)
h-8 w-8     // Large icons in empty states (32px)
h-10 w-10   // Icon containers (40px)
h-12 w-12   // Button icons (48px)
```

## Z-Index Scale

```tsx
z-10        // Dropdown menus
z-50        // Modals and overlays
```

## Responsive Utilities

```tsx
// Mobile-first approach
px-4 md:px-6           // Padding increases on md+
text-sm md:text-base   // Font size increases
hidden md:block        // Show on md+
md:hidden              // Hide on md+
```

## Utility Function

```tsx
import { cn } from '@/lib/utils'

// Merge classes intelligently
className={cn(
  "base-classes",
  condition && "conditional-classes",
  "more-classes"
)}
```

## CSS Variables Access

```tsx
// In Tailwind classes
bg-[hsl(var(--background))]

// In inline styles
style={{ backgroundColor: 'hsl(var(--background))' }}

// Direct CSS
.custom-class {
  background: hsl(var(--background));
}
```

## Animation Presets

### Spring (Natural bounce)
```tsx
transition={{ type: "spring", stiffness: 200, damping: 15 }}
```

### Ease (Smooth)
```tsx
transition={{ duration: 0.3, ease: "easeOut" }}
```

### Stagger Container
```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}
```

## Accessibility Patterns

### Focus Ring
```tsx
focus:outline-none focus:ring-2 focus:ring-primary/20
```

### Screen Reader Only
```tsx
<span className="sr-only">Descriptive text</span>
```

### ARIA Label
```tsx
<button aria-label="Close dialog">
  <X className="h-4 w-4" />
</button>
```

## Component Composition Example

```tsx
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

export function CustomButton({ children, variant = "primary", ...props }) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={cn(
        "rounded-lg px-5 py-2.5 text-sm font-medium transition-colors",
        variant === "primary" && "bg-primary text-primary-foreground shadow-lg shadow-primary/25",
        variant === "secondary" && "bg-secondary text-secondary-foreground",
        "disabled:opacity-50 disabled:cursor-not-allowed"
      )}
      {...props}
    >
      {children}
    </motion.button>
  )
}
```

## Quick Reference Card

### Most Used Combinations

**Interactive Card:**
```tsx
"rounded-xl border bg-card p-5 shadow-sm hover:shadow-lg transition-all"
```

**Primary Button:**
```tsx
"rounded-lg bg-primary text-primary-foreground px-5 py-2.5 shadow-lg shadow-primary/25"
```

**Input Field:**
```tsx
"rounded-lg border bg-background px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/20"
```

**Modal Backdrop:**
```tsx
"fixed inset-0 bg-black/60 backdrop-blur-sm"
```

**Section Header:**
```tsx
"text-sm font-semibold uppercase tracking-wider text-muted-foreground"
```

**Muted Text:**
```tsx
"text-sm text-muted-foreground"
```

**Error State:**
```tsx
"rounded-lg bg-destructive/10 border border-destructive/20 text-destructive"
```
