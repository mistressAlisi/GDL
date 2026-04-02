# 🎭 Modal Components Documentation

## Overview

Two new modal components have been added to handle ticket generation states:

1. **ProcessingModal** - Loading state during ticket generation
2. **NoEventsModal** - Error state when insufficient events are available

Both modals are **theme-responsive** and automatically adapt to the selected theme.

---

## 📦 Components

### 1. ProcessingModal

**File:** `/sportslotto/components/ProcessingModal.tsx`

**Purpose:** Displays a loading spinner while tickets are being generated via WebSocket/API.

**Features:**
- ✅ Animated spinning loader
- ✅ Three-dot bouncing animation
- ✅ Theme-responsive colors
- ✅ Non-dismissible (no close button)
- ✅ Full-screen overlay with backdrop blur

**Props:**
```typescript
interface ProcessingModalProps {
  isOpen: boolean;           // Controls modal visibility
  message?: string;          // Main message (default: "Processing...")
  subMessage?: string;       // Sub-text (default: "Ticket Generation in progress")
}
```

**Usage:**
```tsx
import { ProcessingModal } from './components/ProcessingModal';
import { useTicketGeneration } from '../services/api-hooks';

function MyComponent() {
  const { generateTicket, loading } = useTicketGeneration();

  return (
    <>
      <button onClick={() => generateTicket({...})}>
        Generate Ticket
      </button>
      
      {/* Shows automatically when loading */}
      <ProcessingModal isOpen={loading} />
    </>
  );
}
```

**Custom Messages:**
```tsx
<ProcessingModal 
  isOpen={true}
  message="Generating Your Tickets..."
  subMessage="Finding the best matches for you"
/>
```

---

### 2. NoEventsModal

**File:** `/sportslotto/components/NoEventsModal.tsx`

**Purpose:** Displays an error message when there aren't enough events to generate a ticket.

**Features:**
- ✅ Yellow warning icon
- ✅ Close button (X in top-right)
- ✅ Click outside to dismiss
- ✅ Theme-responsive "Got It!" button
- ✅ Full-screen overlay with backdrop blur

**Props:**
```typescript
interface NoEventsModalProps {
  isOpen: boolean;           // Controls modal visibility
  onClose: () => void;       // Callback when modal is closed
  title?: string;            // Title (default: "Oops! Not Enough Events")
  message?: string;          // Error message
  suggestion?: string;       // Suggestion text
}
```

**Usage:**
```tsx
import { NoEventsModal } from './components/NoEventsModal';

function MyComponent() {
  const [showNoEvents, setShowNoEvents] = useState(false);
  const { error } = useTicketGeneration();

  useEffect(() => {
    // Show modal when API returns "not enough events" error
    if (error?.includes('not enough') || error?.includes('events')) {
      setShowNoEvents(true);
    }
  }, [error]);

  return (
    <NoEventsModal 
      isOpen={showNoEvents}
      onClose={() => setShowNoEvents(false)}
    />
  );
}
```

**Custom Messages:**
```tsx
<NoEventsModal 
  isOpen={true}
  onClose={() => {}}
  title="Custom Error Title"
  message="Your custom error message here"
  suggestion="Try this suggestion instead"
/>
```

---

## 🎨 Theme Integration

Both modals use the `useTheme()` hook to adapt to the current theme:

```tsx
import { useTheme } from '../contexts/ThemeContext';

export function ProcessingModal({ isOpen }) {
  const { theme } = useTheme();
  
  return (
    <div style={{
      border: `2px solid ${theme.cardBorder}`,
      boxShadow: `0 8px 32px ${theme.cardGlow}`
    }}>
      {/* Spinner color matches theme */}
      <svg style={{ color: theme.accentColor }}>...</svg>
      
      {/* Dots color matches theme */}
      <div style={{ backgroundColor: theme.accentColor }} />
    </div>
  );
}
```

### Available Themes:
- Default (Purple) - `#A855F7`
- Royal Purple - `#7C3AED`
- Hot Magenta - `#EC4899`
- Electric Cyan - `#06B6D4`
- Emerald Green - `#10B981`
- Golden Orange - `#FB923C`

The modals will automatically update when the user changes themes via the Theme Settings page.

---

## 🔄 Integration with API Hooks

### Quick Picks Flow

```tsx
import { useTicketGeneration } from '../../services/api-hooks';
import { ProcessingModal } from './components/ProcessingModal';
import { NoEventsModal } from './components/NoEventsModal';

function QuickPicksForm() {
  const { generateTicket, loading, error, response } = useTicketGeneration();
  const [showNoEvents, setShowNoEvents] = useState(false);

  const handleSubmit = (formData) => {
    // Trigger ticket generation
    generateTicket({
      wager: formData.riskAmount,
      entries: formData.entries,
      sports: ['tennis', 'soccer'],
      timeframe: '24h',
      luckyPick: true,
      gameType: 'quick-play',
    });
  };

  useEffect(() => {
    // Handle errors
    if (error?.includes('not enough events')) {
      setShowNoEvents(true);
    }

    // Handle success
    if (response?.success && response.ticket) {
      // Add ticket to cart, close modals, etc.
      console.log('Ticket generated:', response.ticket);
    }
  }, [error, response]);

  return (
    <>
      {/* Form UI */}
      <button onClick={handleSubmit}>Generate Tickets</button>

      {/* Modals */}
      <ProcessingModal isOpen={loading} />
      <NoEventsModal 
        isOpen={showNoEvents}
        onClose={() => setShowNoEvents(false)}
      />
    </>
  );
}
```

### Custom Tickets Flow

```tsx
function CustomTicketsForm() {
  const { generateTicket, loading, error, response } = useTicketGeneration();
  const [showNoEvents, setShowNoEvents] = useState(false);

  const handleSubmit = (formData) => {
    generateTicket({
      wager: formData.stake,
      entries: formData.events,
      sports: formData.selectedSports,
      timeframe: formData.timeframe,
      luckyPick: false,
      gameType: 'custom',
    });
  };

  useEffect(() => {
    if (error?.includes('not enough events')) {
      setShowNoEvents(true);
    }

    if (response?.success) {
      // Navigate to tickets page, etc.
    }
  }, [error, response]);

  return (
    <>
      {/* Form UI */}
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Generating...' : 'Submit'}
      </button>

      {/* Modals */}
      <ProcessingModal isOpen={loading} />
      <NoEventsModal 
        isOpen={showNoEvents}
        onClose={() => setShowNoEvents(false)}
      />
    </>
  );
}
```

---

## 🎯 State Management

### Recommended Pattern

```tsx
export default function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showNoEvents, setShowNoEvents] = useState(false);

  const handleQuickPicksSubmit = async (data) => {
    setIsProcessing(true);
    
    try {
      const result = await generateTicket(data);
      if (result.success) {
        // Success handling
      }
    } catch (error) {
      if (error.message.includes('not enough events')) {
        setShowNoEvents(true);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      {/* App content */}
      
      <ProcessingModal isOpen={isProcessing} />
      <NoEventsModal 
        isOpen={showNoEvents}
        onClose={() => setShowNoEvents(false)}
      />
    </>
  );
}
```

---

## 📱 Responsive Design

Both modals are fully responsive:

### Mobile (< 768px)
- Modal width: 90% of screen
- Padding: 6 (24px)
- Font sizes adjusted
- Touch-friendly close button

### Desktop (≥ 768px)
- Modal width: max-width 28rem (448px)
- Padding: 8 (32px)
- Larger fonts
- Hover effects enabled

### Backdrop
- Full-screen overlay
- Black with 70% opacity
- Backdrop blur effect
- Click outside to dismiss (NoEventsModal only)

---

## 🎬 Animations

### ProcessingModal Animations

**Spinning Loader:**
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```
- Duration: 1s
- Timing: linear
- Infinite loop
- Reverse direction for inner spinner

**Bouncing Dots:**
```css
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
```
- Duration: 1.4s
- Timing: ease-in-out
- Infinite loop
- Staggered delays: -0.32s, -0.16s, 0s

### NoEventsModal Animations

**Button Hover:**
- Scale: 1.05
- Smooth transition
- Theme-based shadow glow

---

## 🔧 Customization Examples

### Different Processing Messages

```tsx
// Quick Picks
<ProcessingModal 
  isOpen={loading}
  message="Generating Quick Picks..."
  subMessage="Selecting random events for you"
/>

// Custom Tickets
<ProcessingModal 
  isOpen={loading}
  message="Building Custom Ticket..."
  subMessage="Matching your sport preferences"
/>

// Lucky Pick
<ProcessingModal 
  isOpen={loading}
  message="Feeling Lucky..."
  subMessage="Finding your winning combination"
/>
```

### Different Error Scenarios

```tsx
// Not enough events
<NoEventsModal 
  isOpen={true}
  onClose={() => {}}
  title="Oops! Not Enough Events"
  message="Not enough events available for this combo right now!"
  suggestion="Try adding more events or reducing the payout!"
/>

// Service unavailable
<NoEventsModal 
  isOpen={true}
  onClose={() => {}}
  title="Service Temporarily Unavailable"
  message="We're having trouble connecting to our servers."
  suggestion="Please try again in a few moments."
/>

// Invalid combination
<NoEventsModal 
  isOpen={true}
  onClose={() => {}}
  title="Invalid Combination"
  message="This sport combination is not available."
  suggestion="Try selecting different sports or timeframes."
/>
```

---

## ✅ Integration Checklist

- [ ] Import both modal components in your form
- [ ] Add state variables: `isProcessing`, `showNoEvents`
- [ ] Connect ProcessingModal to `loading` state from API hook
- [ ] Watch for "not enough events" errors
- [ ] Show NoEventsModal when error occurs
- [ ] Handle success case (hide modals, show tickets)
- [ ] Test with different themes
- [ ] Test on mobile and desktop
- [ ] Verify backdrop dismiss works (NoEventsModal only)
- [ ] Verify close button works (NoEventsModal only)

---

## 🐛 Troubleshooting

### Modal Not Showing

**Issue:** ProcessingModal doesn't appear
```tsx
// ❌ Wrong
<ProcessingModal isOpen={false} />

// ✅ Correct
const { loading } = useTicketGeneration();
<ProcessingModal isOpen={loading} />
```

### Theme Not Updating

**Issue:** Modal colors don't match current theme
```tsx
// ❌ Missing ThemeProvider
<App />

// ✅ Correct
<ThemeProvider>
  <App />
</ThemeProvider>
```

### NoEventsModal Won't Close

**Issue:** Modal stays open after clicking "Got It!"
```tsx
// ❌ Wrong - no state update
<NoEventsModal isOpen={true} onClose={() => {}} />

// ✅ Correct
const [show, setShow] = useState(false);
<NoEventsModal isOpen={show} onClose={() => setShow(false)} />
```

---

## 📚 Related Files

- `/sportslotto/components/ProcessingModal.tsx` - ProcessingModal component
- `/sportslotto/components/NoEventsModal.tsx` - NoEventsModal component
- `/sportslotto/contexts/ThemeContext.tsx` - Theme system
- `/services/api-hooks.ts` - API integration hooks
- `/components/examples/ModalUsageExample.tsx` - Usage examples
- `/sportslotto/App.tsx` - Main app with modal integration

---

## 🚀 Summary

Both modals are now integrated and ready to use:

1. **ProcessingModal** shows automatically when `loading = true`
2. **NoEventsModal** shows when API returns insufficient events error
3. Both adapt to the current theme automatically
4. Fully responsive for mobile and desktop
5. Smooth animations and transitions
6. Ready for Django backend integration

To use them, simply import and connect to your API hook's loading/error states! 🎉
