# SPORTSLOTTO Integration Guide

## Overview

This guide explains how to integrate SPORTSLOTTO with the main BETANY LOTTO platform and how to extend functionality.

## Architecture

SPORTSLOTTO follows a standalone SPA pattern similar to the `/cashier` module:

```
Main Project (BETANY LOTTO)
├── /cashier          → Standalone Cashier SPA (port 5173)
├── /sportslotto      → Standalone Sports Betting SPA (port 5174)
└── Main App          → Core lottery platform (port 5173)
```

## Integration Points

### 1. Cashier Integration

The SPORTSLOTTO app is designed to work with existing cashier forms.

**Step 1: Import Cashier Components**

```typescript
// In /sportslotto/App.tsx or any component
import { Cashier } from '../components/Cashier';
import { Balance } from '../components/Balance';
```

**Step 2: Add Cashier to Navigation**

```typescript
// Add to App.tsx page types
export type Page = 'menu' | 'custom' | 'quickpicks' | 'tickets' | 'cashier' | 'balance';

// Add handlers
const handleCashierOpen = () => {
  setCurrentPage('cashier');
};

// Add in render
{currentPage === 'cashier' && (
  <Cashier
    balance={balance}
    onDeposit={handleDeposit}
    onWithdraw={handleWithdraw}
    onClose={() => setCurrentPage('menu')}
    // ... other props
  />
)}
```

### 2. Balance Management

**Current Implementation:**
```typescript
const [balance, setBalance] = useState(1250.00);
const [pending, setPending] = useState(450.00);
const [freePlay, setFreePlay] = useState(50.00);
const [available, setAvailable] = useState(850.00);
```

**Production Integration:**
```typescript
// Use ProfileContext from main project
import { useProfile } from '../contexts/ProfileContext';

function App() {
  const { balance, updateBalance } = useProfile();
  
  // Use profile balance instead of local state
}
```

### 3. Ticket Management

**Current Mock Implementation:**
```typescript
function generateCustomTickets(data: any): Ticket[] {
  // Mock data
}
```

**API Integration:**
```typescript
async function generateCustomTickets(data: any): Promise<Ticket[]> {
  const response = await fetch('/api/tickets/custom', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  const tickets = await response.json();
  return tickets;
}
```

### 4. Live Sports Data

**Current Mock Events:**
```typescript
const mockEvents: Event[] = [
  {
    id: '1',
    homeTeam: 'FC Midtjylland',
    awayTeam: 'Dinamo Zagreb',
    league: 'UEFA Europa League',
    date: '01/30/2025 01:00 PM'
  }
];
```

**API Integration:**
```typescript
async function fetchLiveEvents(sport: Sport, timeFrame: string): Promise<Event[]> {
  const response = await fetch(`/api/sports/events?sport=${sport}&timeFrame=${timeFrame}`);
  const events = await response.json();
  return events;
}

// Use in component
useEffect(() => {
  fetchLiveEvents(selectedSport, timeFrame).then(setEvents);
}, [selectedSport, timeFrame]);
```

## Extending Functionality

### Adding New Sports

**Step 1: Update Sport Type**
```typescript
// In App.tsx
export type Sport = 'tennis' | 'us-sports' | 'soccer' | 'ncaa-basketball' | 'cricket' | 'rugby';
```

**Step 2: Add to Sport Lists**
```typescript
// In MainMenu.tsx and forms
const sports = [
  // ... existing sports
  { id: 'cricket', name: 'Cricket', icon: '🏏' },
  { id: 'rugby', name: 'Rugby', icon: '🏉' },
];
```

### Adding New Pages

**Step 1: Create Component**
```typescript
// /sportslotto/components/HistoryPage.tsx
export function HistoryPage({ onBack }: { onBack: () => void }) {
  return (
    <div>
      <h2>Ticket History</h2>
      {/* Your content */}
    </div>
  );
}
```

**Step 2: Add to App Navigation**
```typescript
// Update Page type
export type Page = 'menu' | 'custom' | 'quickpicks' | 'tickets' | 'history';

// Import component
import { HistoryPage } from './components/HistoryPage';

// Add to render
{currentPage === 'history' && (
  <HistoryPage onBack={handleBackToMenu} />
)}
```

### Custom Styling

All styles are in `/sportslotto/src/styles/globals.css`:

```css
/* Add custom utilities */
@layer utilities {
  .custom-gradient {
    background: linear-gradient(135deg, #yourcolor1, #yourcolor2);
  }
  
  .custom-border {
    border: 2px solid rgba(255, 255, 255, 0.2);
  }
}
```

## State Management

### Current Approach (useState)
```typescript
const [tickets, setTickets] = useState<Ticket[]>([]);
```

### Recommended for Production (Context)
```typescript
// Create /sportslotto/contexts/TicketsContext.tsx
export const TicketsProvider = ({ children }) => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  
  const addTicket = (ticket: Ticket) => {
    setTickets(prev => [...prev, ticket]);
  };
  
  return (
    <TicketsContext.Provider value={{ tickets, addTicket }}>
      {children}
    </TicketsContext.Provider>
  );
};

// Use in App.tsx
<TicketsProvider>
  <App />
</TicketsProvider>
```

## Backend Integration Checklist

- [ ] Connect to live sports data API
- [ ] Implement ticket creation endpoint
- [ ] Add ticket status tracking
- [ ] Integrate payment processing
- [ ] Add user authentication
- [ ] Implement bet validation
- [ ] Add odds calculation service
- [ ] Create ticket history storage
- [ ] Add real-time updates (WebSockets)
- [ ] Implement cash-out functionality

## Database Schema (Suggested)

```sql
-- Tickets table
CREATE TABLE sports_tickets (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  type VARCHAR(20), -- 'pending', 'win', 'loss'
  amount DECIMAL(10,2),
  potential DECIMAL(10,2),
  sport VARCHAR(50),
  created_at TIMESTAMP,
  settled_at TIMESTAMP,
  status VARCHAR(20)
);

-- Events table
CREATE TABLE ticket_events (
  id UUID PRIMARY KEY,
  ticket_id UUID REFERENCES sports_tickets(id),
  home_team VARCHAR(100),
  away_team VARCHAR(100),
  league VARCHAR(100),
  event_date TIMESTAMP,
  pick VARCHAR(50),
  result VARCHAR(20)
);
```

## API Endpoints (Suggested)

```
POST   /api/tickets/custom       - Create custom ticket
POST   /api/tickets/quickpicks   - Generate quick picks
GET    /api/tickets              - Get user tickets
GET    /api/tickets/:id          - Get ticket details
PUT    /api/tickets/:id/accept   - Accept ticket
PUT    /api/tickets/:id/reject   - Reject ticket
GET    /api/sports/events        - Get live events
GET    /api/sports/:sport/odds   - Get current odds
```

## Testing

### Component Testing
```bash
# Install testing library
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

### Example Test
```typescript
import { render, screen } from '@testing-library/react';
import { MainMenu } from './components/MainMenu';

test('renders SPORTSLOTTO title', () => {
  render(<MainMenu onSportSelect={() => {}} />);
  expect(screen.getByText('SPORTSLOTTO')).toBeInTheDocument();
});
```

## Deployment

### Build for Production
```bash
cd sportslotto
npm run build
```

### Deploy to Hosting
```bash
# The build output is in /sportslotto/dist
# Upload to your hosting provider
# Configure to serve index.html for all routes
```

### Environment Variables
```bash
# Create .env file
VITE_API_URL=https://api.yoursite.com
VITE_SPORTS_API_KEY=your-api-key
```

## Security Considerations

1. **Validation** - Always validate bet amounts and selections on backend
2. **Authentication** - Require user authentication for ticket creation
3. **Rate Limiting** - Prevent spam ticket generation
4. **Odds Verification** - Verify odds haven't changed before accepting bets
5. **Balance Checks** - Verify sufficient funds before ticket creation

## Next Steps

1. Review current implementation
2. Plan backend API structure
3. Connect to live sports data provider
4. Implement authentication
5. Add payment processing
6. Test thoroughly
7. Deploy to staging
8. User acceptance testing
9. Production deployment

---

For questions or issues, refer to the other documentation files or the main project documentation.
