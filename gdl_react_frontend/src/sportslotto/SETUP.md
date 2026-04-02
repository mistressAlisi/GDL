# SPORTSLOTTO Setup Guide

## Overview

The SPORTSLOTTO application is a standalone SPA (Single Page Application) that lives in the `/sportslotto` directory, similar to the `/cashier` structure. It can be run independently or alongside other applications.

## Initial Setup

### Step 1: Navigate to the Directory
```bash
cd sportslotto
```

### Step 2: Install Dependencies

**Option A - Using Setup Script (Recommended):**

Windows:
```bash
setup.bat
```

Mac/Linux:
```bash
chmod +x setup.sh
./setup.sh
```

**Option B - Manual Installation:**
```bash
npm install
```

## Running the Application

### Development Mode
```bash
npm run dev
```

The application will start on **port 5174**: http://localhost:5174

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Running Multiple Applications

You can run the SPORTSLOTTO app alongside other apps:

### Terminal 1 - Main BETANY LOTTO App
```bash
# From project root
npm run dev
# Runs on http://localhost:5173
```

### Terminal 2 - Cashier App
```bash
# From project root
cd cashier
npm run dev
# Runs on http://localhost:5173
```

### Terminal 3 - SPORTSLOTTO App
```bash
# From project root
cd sportslotto
npm run dev
# Runs on http://localhost:5174
```

## Port Configuration

The SPORTSLOTTO app is configured to run on port **5174** to avoid conflicts:

```typescript
// vite.config.ts
server: {
  port: 5174,
  open: true
}
```

## Project Integration

### Integrating Cashier Forms

To use existing cashier forms from the main project:

```typescript
// Example: Import cashier component
import { Cashier } from '../components/Cashier';

// Use in your component
<Cashier
  balance={balance}
  onDeposit={handleDeposit}
  onWithdraw={handleWithdraw}
  // ... other props
/>
```

### Shared Styles

The SPORTSLOTTO app uses its own styles in `/sportslotto/src/styles/globals.css` which includes:
- Glass-morphism utilities
- Golden gradient classes
- 3D transform utilities
- Custom border glow effects

## File Structure

```
/sportslotto
├── index.html                        # HTML entry point
├── main.tsx                          # React entry (root level)
├── App.tsx                          # Main app component
├── components/                      # React components
│   ├── MainMenu.tsx
│   ├── CustomTicketsForm.tsx
│   ├── QuickPicksForm.tsx
│   ├── TicketsGrid.tsx
│   └── TicketDetailsPanel.tsx
├── src/
│   ├── main.tsx                     # Alternative entry point
│   └── styles/
│       └── globals.css              # Global styles
├── package.json                     # Dependencies
├── vite.config.ts                   # Vite configuration
├── tsconfig.json                    # TypeScript config
├── setup.sh / setup.bat             # Setup scripts
├── README.md                        # Documentation
├── QUICKSTART.md                    # Quick start guide
├── SETUP.md                         # This file
└── VERSION.md                       # Version history
```

## Troubleshooting

### Port Already in Use
If port 5174 is already in use, modify `vite.config.ts`:
```typescript
server: {
  port: 5175, // or any available port
  open: true
}
```

### Dependencies Not Installing
Try clearing npm cache:
```bash
npm cache clean --force
npm install
```

### Build Errors
Ensure you have the correct Node.js version:
```bash
node --version  # Should be v18 or higher
```

### TypeScript Errors
Regenerate TypeScript types:
```bash
npm run build
```

## Development Workflow

1. **Make Changes** - Edit components in `/sportslotto/components`
2. **Hot Reload** - Changes automatically reflected in browser
3. **Test** - Use browser dev tools to debug
4. **Build** - Run `npm run build` before deployment

## Next Steps

After setup:
1. Read `QUICKSTART.md` for usage instructions
2. Check `README.md` for feature overview
3. Review `VERSION.md` for current version details
4. Start building on the core functionality!

## Support

For issues:
- Check the browser console for errors
- Review Vite logs in the terminal
- Ensure all dependencies are installed
- Verify port availability

Happy coding! 🎰⚽🏀
