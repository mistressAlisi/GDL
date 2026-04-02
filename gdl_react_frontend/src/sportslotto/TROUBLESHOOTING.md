# SPORTSLOTTO Troubleshooting Guide

## Common Issues & Solutions

### Installation Issues

#### ❌ Problem: npm install fails
```bash
Error: ENOENT: no such file or directory
```

**Solution:**
```bash
# Make sure you're in the right directory
cd sportslotto

# Clear npm cache
npm cache clean --force

# Try again
npm install
```

#### ❌ Problem: Permission denied when running setup.sh
```bash
-bash: ./setup.sh: Permission denied
```

**Solution:**
```bash
# Make the file executable
chmod +x setup.sh

# Run again
./setup.sh
```

---

### Development Server Issues

#### ❌ Problem: Port 5174 already in use
```bash
Port 5174 is in use, trying another one...
```

**Solution 1:** Kill the process using port 5174
```bash
# Windows
netstat -ano | findstr :5174
taskkill /PID <process_id> /F

# Mac/Linux
lsof -ti:5174 | xargs kill -9
```

**Solution 2:** Change the port in vite.config.ts
```typescript
server: {
  port: 5175, // Use a different port
  open: true
}
```

#### ❌ Problem: "Cannot find module" errors
```bash
Error: Cannot find module './components/MainMenu'
```

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

---

### Build Issues

#### ❌ Problem: TypeScript errors during build
```bash
error TS2307: Cannot find module 'react'
```

**Solution:**
```bash
# Install type definitions
npm install --save-dev @types/react @types/react-dom

# Rebuild
npm run build
```

#### ❌ Problem: Tailwind classes not working
```bash
Classes not applying in production build
```

**Solution:**
Check `src/styles/globals.css` has the Tailwind import:
```css
@import "tailwindcss";
```

---

### Runtime Issues

#### ❌ Problem: 3D flip animation not working
The card doesn't flip when clicked.

**Solution:**
1. Check browser compatibility (needs modern browser)
2. Verify CSS utilities are loaded:
```css
/* In globals.css */
.transform-style-3d {
  transform-style: preserve-3d;
}
.backface-hidden {
  backface-visibility: hidden;
}
.rotate-y-180 {
  transform: rotateY(180deg);
}
```

#### ❌ Problem: Tickets not generating
Clicking Submit/Generate doesn't create tickets.

**Solution:**
Check browser console for errors:
```javascript
// In App.tsx, add console logs
const handleCustomSubmit = (ticketData: any) => {
  console.log('Submitting:', ticketData);
  const newTickets = generateCustomTickets(ticketData);
  console.log('Generated tickets:', newTickets);
  setTickets(prev => [...prev, ...newTickets]);
  setCurrentPage('tickets');
};
```

#### ❌ Problem: Details modal not opening
Clicking Details button doesn't show modal.

**Solution:**
1. Check that `showDetails` state is updating
2. Verify `TicketDetailsPanel` is being rendered
3. Check z-index in browser dev tools

---

### Styling Issues

#### ❌ Problem: Glass morphism not visible
Cards appear solid instead of translucent.

**Solution:**
1. Check if backdrop-filter is supported:
```javascript
// In browser console
console.log(CSS.supports('backdrop-filter', 'blur(10px)'));
```

2. Add fallback styles:
```css
.glass-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px); /* Safari */
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

#### ❌ Problem: Golden gradient text not showing
Text appears solid instead of gradient.

**Solution:**
Check browser compatibility:
```css
.text-golden {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent; /* Fallback */
}
```

#### ❌ Problem: Buttons not clickable
Buttons don't respond to clicks.

**Solution:**
1. Check for overlapping elements with higher z-index
2. Verify pointer-events are not disabled
3. Inspect in browser dev tools for obstructing elements

---

### State Management Issues

#### ❌ Problem: Balance not updating
Balance stays the same after ticket creation.

**Solution:**
The current implementation uses mock data. To update balance:
```typescript
const handleCustomSubmit = (ticketData: any) => {
  const newTickets = generateCustomTickets(ticketData);
  setTickets(prev => [...prev, ...newTickets]);
  
  // Update balance
  const totalCost = newTickets.reduce((sum, t) => sum + t.amount, 0);
  setBalance(prev => prev - totalCost);
  setAvailable(prev => prev - totalCost);
  
  setCurrentPage('tickets');
};
```

#### ❌ Problem: Tickets persist between sessions
Old tickets still appear after refreshing.

**Solution:**
This is expected with local state. To clear:
```typescript
// Add a reset function
const handleReset = () => {
  setTickets([]);
  localStorage.removeItem('sportslotto-tickets');
};
```

Or implement localStorage:
```typescript
// Save tickets
useEffect(() => {
  localStorage.setItem('sportslotto-tickets', JSON.stringify(tickets));
}, [tickets]);

// Load tickets on mount
useEffect(() => {
  const saved = localStorage.getItem('sportslotto-tickets');
  if (saved) {
    setTickets(JSON.parse(saved));
  }
}, []);
```

---

### Browser Compatibility

#### Supported Browsers
✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+

#### Not Fully Supported
❌ Internet Explorer (any version)
⚠️ Chrome < 90 (3D transforms may not work)
⚠️ Safari < 14 (backdrop-filter issues)

#### Browser-Specific Issues

**Safari:**
```css
/* Add webkit prefixes */
.glass-card {
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
}
```

**Firefox:**
```css
/* Ensure 3D transforms work */
.transform-style-3d {
  transform-style: preserve-3d;
  -moz-transform-style: preserve-3d;
}
```

---

### Performance Issues

#### ❌ Problem: Slow animations
Flip animations are laggy or janky.

**Solution:**
1. Enable hardware acceleration:
```css
.ticket-card {
  transform: translateZ(0);
  will-change: transform;
}
```

2. Reduce the number of tickets displayed:
```typescript
// Paginate tickets
const ticketsPerPage = 20;
const displayedTickets = tickets.slice(0, ticketsPerPage);
```

#### ❌ Problem: High memory usage
Browser tab uses too much memory.

**Solution:**
1. Limit the number of tickets stored
2. Implement virtual scrolling for large lists
3. Clean up unused state

---

### Integration Issues

#### ❌ Problem: Can't import from main project
```bash
Error: Cannot find module '../components/Cashier'
```

**Solution:**
Check the relative path:
```typescript
// From /sportslotto/App.tsx to /components/Cashier.tsx
import { Cashier } from '../components/Cashier';

// If that doesn't work, use absolute import with vite config:
// vite.config.ts
resolve: {
  alias: {
    '@': path.resolve(__dirname, '../')
  }
}

// Then:
import { Cashier } from '@/components/Cashier';
```

---

### Debugging Tips

#### Enable Detailed Logging
```typescript
// Add to App.tsx
useEffect(() => {
  console.log('Current page:', currentPage);
  console.log('Tickets:', tickets);
  console.log('Selected sport:', selectedSport);
}, [currentPage, tickets, selectedSport]);
```

#### Check State in React DevTools
1. Install React Developer Tools browser extension
2. Open DevTools → Components tab
3. Select App component
4. View hooks and props

#### Network Issues
```typescript
// If integrating with API, log fetch calls
const response = await fetch('/api/tickets');
console.log('Response:', response.status, await response.json());
```

---

### Getting Help

If you're still stuck:

1. **Check the Console**
   - Open browser DevTools (F12)
   - Look at Console tab for errors
   - Check Network tab for failed requests

2. **Review Documentation**
   - README.md - Feature overview
   - SETUP.md - Installation details
   - INTEGRATION.md - API integration
   - FLOW-MAP.md - Application structure

3. **Common Error Messages**

   | Error | Likely Cause | Fix |
   |-------|--------------|-----|
   | "Module not found" | Missing import/typo | Check file path |
   | "Cannot read property of undefined" | State not initialized | Add null checks |
   | "Unexpected token" | Syntax error | Check brackets/quotes |
   | "Failed to compile" | TypeScript error | Check types |

4. **Verify Your Setup**
   ```bash
   # Check Node version (should be 18+)
   node --version
   
   # Check npm version
   npm --version
   
   # List installed packages
   npm list --depth=0
   
   # Check for outdated packages
   npm outdated
   ```

---

## Quick Fixes Checklist

When something goes wrong, try these in order:

- [ ] Refresh the browser (Ctrl/Cmd + R)
- [ ] Hard refresh (Ctrl/Cmd + Shift + R)
- [ ] Clear browser cache
- [ ] Restart dev server (Ctrl + C, then npm run dev)
- [ ] Delete node_modules and reinstall (npm install)
- [ ] Check browser console for errors
- [ ] Check terminal for build errors
- [ ] Verify you're in the right directory (pwd or cd)
- [ ] Check file permissions (especially setup.sh)
- [ ] Update dependencies (npm update)
- [ ] Check git status (git status)

---

## Still Having Issues?

If none of these solutions work:

1. **Create a minimal reproduction**
   - Start with a fresh install
   - Add features one at a time
   - Identify what breaks

2. **Check system requirements**
   - Node.js 18+
   - npm 9+
   - Modern browser
   - Sufficient disk space

3. **Review recent changes**
   - What was the last thing that worked?
   - What did you change since then?
   - Can you revert and try again?

Happy troubleshooting! 🔧
