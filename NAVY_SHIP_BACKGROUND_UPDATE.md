# Navy Ship Background Implementation

## Overview
Added the navy ship image as a fixed background in the hero section of the landing page with 70% opacity and proper positioning to ensure it doesn't scroll with the content.

## Implementation Details

### Background Image Configuration
- **Image**: `/navy_ship.png` - Navy ships on blue ocean
- **Opacity**: 30% for subtle background effect (reduced for better readability)
- **Position**: Fixed positioning (`background-attachment: fixed`)
- **Size**: Cover to fill entire viewport
- **Position**: Center aligned for optimal visual impact

### CSS Properties Applied
```css
{
  backgroundImage: 'url(/navy_ship.png)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat',
  backgroundAttachment: 'fixed',
  opacity: 0.3
}
```

### Hero Section Structure
1. **Container**: Full viewport height with flex centering
2. **Background Layer**: Fixed positioned div with navy ship image (z-index: 0)
3. **Content Layer**: Hero content with standard styling (z-index: 10)

### Visual Enhancements
- **Reduced opacity**: Navy ship background at 30% opacity for optimal text readability
- **Clean design**: Removed overlays and glassmorphism effects for cleaner appearance
- **Seamless sections**: Removed wave separator and white section backgrounds for continuous navy ship background visibility
- **Transparent backgrounds**: Features and testimonials sections use transparent backgrounds to maintain visual continuity

### Key Features
1. **Fixed Background**: Image remains stationary during page scroll
2. **Responsive Design**: Adapts to all screen sizes
3. **Dark Mode Support**: Overlay adjusts for light/dark themes
4. **Text Readability**: Multiple layers ensure content visibility
5. **Performance Optimized**: Uses CSS transforms and fixed positioning

### Files Modified
- `parseqri_v01/frontend/src/pages/LandingPage.tsx`: Hero section structure and styling

### Technical Implementation
The background uses a combination of:
- Fixed positioning for the background image
- Layered z-index system for proper stacking
- CSS backdrop filters for modern glassmorphism effect
- Responsive utilities for mobile compatibility

This creates a professional, naval-themed landing page that maintains readability while showcasing the Indian Navy branding. 