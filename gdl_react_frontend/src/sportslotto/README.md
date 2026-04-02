# SPORTSLOTTO - Sports Betting Platform

A premium sports lottery betting platform built with React, TypeScript, and Tailwind CSS featuring glass-morphism design and golden gradient styling.

## Quick Start

### Setup

Run the setup script for your platform:

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Development

Start the development server:

```bash
npm run dev
```

The application will open at http://localhost:5174

## Features

- **Main Menu** - Landing page with sport categories and game modes
- **Custom Tickets** - Build custom sports lottery tickets with:
  - Configurable stake, events, and win amounts
  - Multiple sport selections (Tennis, US Sports, Soccer, NCAA Basketball, MLB, NFL)
  - Time frame filters (24hrs, 48hrs, 1 week, All)
  
- **Quick Picks** - Automated ticket generation with:
  - Configurable ticket count
  - Risk amount distribution
  - Sport selection

- **Tickets Grid** - Display tickets with:
  - 3D flip animations
  - Green/Red selection buttons
  - Win amount reveals
  - Pending/Win/Loss states

- **Ticket Details** - Expanded view showing:
  - All events and matchups
  - League information
  - Event dates and times
  - Accept/Reject actions

## Project Structure

```
/sportslotto
├── App.tsx                           # Main application with routing
├── components/
│   ├── MainMenu.tsx                  # Landing page
│   ├── CustomTicketsForm.tsx         # Custom ticket creation
│   ├── QuickPicksForm.tsx           # Quick picks generation
│   ├── TicketsGrid.tsx              # Tickets display with flip
│   └── TicketDetailsPanel.tsx       # Details modal
├── src/
│   └── styles/
│       └── globals.css              # Global styles and utilities
├── index.html
├── main.tsx
├── package.json
└── vite.config.ts
```

## Design System

- **Colors**: Golden gradients (#ffd700, #ffed4e), purple/pink accents
- **Glass Morphism**: Frosted glass effects with backdrop blur
- **Typography**: Bold headings, uppercase labels
- **Animations**: 3D card flips, hover effects, smooth transitions

## Integration

The cashier can be integrated by importing the existing cashier forms from the main project:

```typescript
import { Cashier } from '../components/Cashier';
```

## Tech Stack

- React 18.3
- TypeScript 5.6
- Vite 6.0
- Tailwind CSS 4.0
