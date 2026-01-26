# Component Showcase - Modern Dark UI

## Visual Design Language

### Color System

#### Dark Theme Colors (Active)
```
Background:    #0A0A0A (Deep Black)
Card:          #121212 (Elevated Black)
Foreground:    #FAFAFA (Off-white)
Primary:       #FAFAFA (White - for dark mode)
Border:        #262626 (Subtle Gray)
Muted:         #262626 (Secondary Elements)
Accent:        #262626 (Hover States)
Destructive:   #DC2626 (Red for Delete)
```

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  Header (Sticky)                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  [Icon] My Tasks                        [Sign Out] ▶  │  │
│  │  2 active · 1 completed                                │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Main Content                                                │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Add Task Form                                         │  │
│  │  ┌─────────────────────────────────────────────┐      │  │
│  │  │  What needs to be done?                [+]  │      │  │
│  │  └─────────────────────────────────────────────┘      │  │
│  │  (Expands on focus to show description field)         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ○ ACTIVE TASKS ─────────────────────────────────────────  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ☐  Task Title                          [Edit] [Del]  │  │
│  │      Task description text                             │  │
│  │      Created Jan 15, 2026                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ✓ COMPLETED ────────────────────────────────────────────  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ☑  Completed Task (Strikethrough)     [Edit] [Del]  │  │
│  │      (Reduced opacity: 60%)                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Task Card

#### States:
- **Default (Active)**
  - White border on dark card background
  - Checkbox: Empty with border
  - Full opacity
  - Hover: Gradient overlay + border color change

- **Completed**
  - 60% opacity
  - Checkbox: Filled with animated checkmark
  - Title: Strikethrough + slight shift right
  - Subtle muted colors

- **Hover**
  - Scale: 1.0 → (subtle border glow)
  - Shadow: Enhanced with primary color
  - Gradient: Fades in from top-left
  - Action buttons: Become more visible

#### Animations:
- **Entrance**: Fade in + slide up (20px)
- **Checkbox Toggle**:
  - Checkmark: Rotate -180° → 0° with spring
  - Background: Color transition
- **Delete Confirmation**:
  - Expand from 0 height with border separator
- **Action Buttons**:
  - Edit: Rotate 5° on hover
  - Delete: Rotate -5° on hover

#### Layout:
```
┌─────────────────────────────────────────────────────────┐
│  [☐] Task Title                           [✎] [🗑]      │
│      Optional description text                          │
│      Jan 15, 2026                                       │
└─────────────────────────────────────────────────────────┘
```

### 2. Add Task Form

#### States:
- **Collapsed** (Initial)
  - Single input + button
  - Placeholder: "What needs to be done?"

- **Expanded** (On focus)
  - Input + Description textarea + Collapse button
  - Smooth height animation

- **Focused**
  - Border: Changes to primary color with ring
  - Scale: Subtle 1.01x on input
  - Shadow: Elevated with primary glow

#### Animations:
- **Form entrance**: Fade in from top (-20px)
- **Expand/Collapse**: Height animation with overflow handling
- **Submit button**:
  - Plus icon: Rotates -90° on mount, 90° on exit
  - Loading: Transforms to spinning loader
  - Hover: Scale 1.05x + shadow enhancement

#### Special Features:
- **Character counter**: Appears at 200/255 characters
  - Green: 200-240
  - Yellow: 240-255
  - Red: Over 255 (with validation)

#### Layout:
```
┌─────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────┐  [+] │
│  │  What needs to be done?                    │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  (When expanded:)                                   │
│  ┌─────────────────────────────────────────────┐   │
│  │  Add details... (optional)                   │   │
│  │                                              │   │
│  └─────────────────────────────────────────────┘   │
│                                      [Collapse]     │
└─────────────────────────────────────────────────────┘
```

### 3. Edit Task Modal

#### Structure:
```
      ╔═══════════════════════════════════════════════╗
      ║  [💾] Edit Task                          [✕]  ║
      ╟───────────────────────────────────────────────╢
      ║  Title                                        ║
      ║  ┌─────────────────────────────────────────┐ ║
      ║  │ Current task title                      │ ║
      ║  └─────────────────────────────────────────┘ ║
      ║                                               ║
      ║  Description (optional)                       ║
      ║  ┌─────────────────────────────────────────┐ ║
      ║  │ Current description                     │ ║
      ║  │                                         │ ║
      ║  └─────────────────────────────────────────┘ ║
      ╟───────────────────────────────────────────────╢
      ║                       [Cancel] [💾 Save]     ║
      ╚═══════════════════════════════════════════════╝
```

#### Animations:
- **Backdrop**: Fade in with blur effect
- **Modal**: Scale 0.95 → 1.0 + fade in + slide up
- **Close button**: Rotates 90° on hover
- **Exit**: Reverse of entrance

#### Features:
- **Click outside**: Closes modal
- **Escape key**: Closes modal (native)
- **Auto-focus**: Title input on mount
- **Error handling**: Animated error banner
- **Version conflict**: Special error message

### 4. Task Sections

#### Active Tasks Section:
```
○ ACTIVE TASKS ─────────────────────────────────
(Icon) (Label)        (Divider line)

[Task cards with stagger animation]
```

#### Completed Tasks Section:
```
✓ COMPLETED ────────────────────────────────────
(Icon) (Label)        (Divider line)

[Completed task cards - reduced opacity]
```

#### Empty States:
```
    ┌─────┐
    │ 📋  │  (Large icon in circle)
    └─────┘

    No tasks yet
    Start organizing your work by creating
    your first task above.
```

### 5. Loading State

```
        ⟳ (Spinning loader)

    Loading your tasks...
```

### 6. Header (Sticky)

```
┌───────────────────────────────────────────────────┐
│  [📋] My Tasks                     [→ Sign out]   │
│       2 active · 1 completed                      │
└───────────────────────────────────────────────────┘
```

Features:
- **Backdrop blur**: Glass morphism effect
- **Sticky positioning**: Stays at top on scroll
- **Task count**: Real-time statistics
- **Sign out**: Icon + text button

## Interaction Patterns

### Hover Effects
1. **Task Cards**: Border glow + gradient overlay
2. **Buttons**: Scale 1.05x + shadow enhancement
3. **Icons**: Subtle rotation (5° or -5°)
4. **Close buttons**: Rotate 90°

### Tap/Click Effects
1. **All buttons**: Scale down to 0.95x
2. **Checkboxes**: Scale 0.95x with spring back
3. **Submit actions**: Button remains scaled during loading

### Focus Effects
1. **Inputs**: Ring glow in primary color
2. **Textareas**: Same ring effect
3. **Buttons**: Visible outline for accessibility

## Animation Timing

### Quick Actions (Micro-interactions)
- Duration: 0.2s
- Easing: Spring or ease-out

### UI Transitions
- Duration: 0.3s
- Easing: Spring with bounce

### List Stagger
- Base delay: 0.05s per item
- Max items before instant: ~20

### Layout Animations
- Automatic via Framer Motion
- Smart DOM reconciliation

## Accessibility

### Keyboard Navigation
- ✓ Tab through all interactive elements
- ✓ Enter to submit forms
- ✓ Escape to close modals
- ✓ Space to toggle checkboxes

### Screen Readers
- ✓ ARIA labels on icon buttons
- ✓ Semantic HTML (headers, sections)
- ✓ Form labels properly associated
- ✓ Error messages announced

### Visual
- ✓ High contrast in dark mode
- ✓ Visible focus indicators
- ✓ Color not sole indicator
- ✓ Touch targets 44px minimum

## Performance

### Optimizations
- Transform and opacity for GPU acceleration
- Layout animations batched by Framer Motion
- Icons tree-shaken from lucide-react
- CSS variables for instant theme updates

### Bundle Impact
- Framer Motion: ~35KB gzipped
- Lucide React: ~5KB (tree-shaken)
- Total added: ~40KB for modern UI

## Responsive Behavior

### Breakpoints (Tailwind default)
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Adaptations
- Padding: Reduced on mobile (px-4 → px-6)
- Font sizes: Responsive text-base → text-lg
- Max width: 4xl container (896px)
- Touch targets: Larger on mobile
