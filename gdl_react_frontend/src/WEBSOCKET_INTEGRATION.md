# WebSocket Ticket Generation - React Integration

## Overview

This document describes the React implementation of the Django WebSocket ticket generation system. The system provides real-time, GPU-accelerated parlay ticket generation with two modes:

1. **Custom Tickets** (`/stream_tickets`) - User-configured tickets displayed for accept/reject
2. **Quick Picks** (`/stream_quickpicks`) - Auto-saved instant tickets with 20:1 minimum payout

---

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (WebSocket)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Django Channels  │
│   Consumer      │  ← Proxy layer
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GPU Daemon     │
│  (PyTorch)      │  ← Ticket generator
└─────────────────┘
```

---

## Django Backend Requirements

### 1. Bootstrap Endpoint

**Add `vdomain.uuid` to `/api/v1/bootstrap` response:**

```python
# cypress/views/bootstrap.py
"domain": {
    "uuid": str(vdomain.uuid),  # ← ADD THIS
    "fqdn": vdomain.domain_fqdn,
    "name": vdomain.website_name,
    "icon": icon_url
},
```

### 2. WebSocket Routing

Already configured in your Django:
- `/game/stream_tickets` → `GDLTicketStreamConsumer`
- `/game/stream_quickpicks` → `GDLTicketStoreStreamConsumer`

### 3. REST API Endpoints

Already implemented:
- `POST /api/v1/game/tickets/accept/` - Add ticket to cart
- `POST /api/v1/game/tickets/reject/{uuid}?ng=1` - Remove ticket
- `GET /api/v1/game/tickets/cart/` - Get cart contents
- `DELETE /api/v1/game/tickets/cart/empty` - Empty cart

---

## React Components

### Core Services

#### `BootstrapContext.tsx`
Loads Django session context on app startup:
```typescript
const { bootstrap } = useBootstrap();
// bootstrap.vhost.uuid
// bootstrap.account.uuid
// bootstrap.domain.uuid
```

#### `WebSocketService.ts`
Matches your jQuery `WSManager` pattern:
- Request/response pairing via `request_id`
- Queue management with inflight tracking
- Auto-reconnection with exponential backoff
- Heartbeat/ping support

### Hooks

#### `useTicketGenerator()`
Main hook for ticket generation:
```typescript
const { tickets, isGenerating, generate, replace } = useTicketGenerator({
  streamName: 'custom_tickets',
  endpoint: '/game/stream_tickets',
  onTicket: (ticket) => { /* handle ticket */ },
  onComplete: (data) => { /* generation done */ },
  onError: (error) => { /* handle error */ },
  onEmpty: (data) => { /* not enough events */ },
});

// Generate tickets
generate({
  stake: 10,
  count: 5,
  depth: 3,
  min_payout: 200,
});

// Replace rejected ticket
replace(oldUuid, { stake: 10, depth: 3, min_payout: 200 });
```

#### `useCart()`
Cart management:
```typescript
const { 
  cartEntries, 
  cartCount, 
  totalRisk, 
  totalWins,
  fetchCart,
  acceptTicket,
  rejectTicket,
  emptyCart 
} = useCart();
```

---

## Message Protocol

### Request Format

```javascript
{
  "action": "generate",
  "request_id": "uuid-v4",
  "old_uuid": "uuid",  // Optional: for replacements
  "settings": {
    // Django context (from bootstrap)
    "vhost": "uuid",
    "account": "uuid",
    "vdomain": "uuid",
    
    // Generation parameters
    "stake": 10.0,
    "count": 5,
    "depth": 3,
    "min_payout": 200.0,
    "events_within": 129600,  // 36 hours
    
    // Dynamic sport filters
    "sport_0": "sport-uuid",
    "sport_1": "sport-uuid",
    "group_0": "group-uuid",
  }
}
```

### Response Types

#### Ticket
```javascript
{
  "type": "ticket",
  "uuid": "...",  // Only present for QuickPicks
  "lines": ["line-uuid", ...],
  "muuids": ["match-uuid", ...],
  "outcomes": ["home", "away", "draw"],
  "total_odds": 150,
  "total_returns": 1500,
  "total_stake": 10,
  "status": "C",  // C=Created, P=Pending, W=Won, L=Lost
  "depth": 3,
  "legs": [...],
  "outcome_meta": {...},
  "old_uuid": "..."  // Echoed back if replacement
}
```

#### Complete (Custom Tickets)
```javascript
{
  "type": "complete",
  "message": "Generation finished: 5/5 tickets",
  "trials": 1234,
  "failed": 567
}
```

#### Complete (Quick Picks)
```javascript
{
  "type": "complete",
  "ticket_count": 5,
  "total_risk": 50,
  "total_wins": 1000,
  "trials": 1234,
  "failed": 567
}
```

#### Empty
```javascript
{
  "type": "empty",
  "incomplete": true,
  "error": "Not enough Odds"
}
```

#### Error
```javascript
{
  "type": "error",
  "error": "Error message"
}
```

---

## Usage Examples

### Custom Tickets Flow

```typescript
import { useTicketGenerator } from '../hooks/useTicketGenerator';
import { useCart } from '../hooks/useCart';

function CustomTicketsPage() {
  const { tickets, generate, replace } = useTicketGenerator({
    streamName: 'custom',
    endpoint: '/game/stream_tickets',
    onComplete: (data) => console.log('Done!', data),
  });

  const { acceptTicket } = useCart();

  const handleGenerate = () => {
    generate({
      stake: 10,
      count: 5,
      depth: 3,
      min_payout: 200,
    });
  };

  const handleAccept = async (ticket) => {
    const formData = new FormData();
    formData.append('matches', ticket.muuids.join(','));
    formData.append('type', ticket.outcomes.join(','));
    formData.append('stake', ticket.total_stake);
    formData.append('returns', ticket.total_returns);
    formData.append('lines', ticket.lines.join(','));
    formData.append('outcome_meta', JSON.stringify(ticket.outcome_meta));
    
    await acceptTicket(formData);
  };

  const handleReject = (ticket) => {
    // Request replacement
    replace(ticket.lines[0], {
      stake: 10,
      depth: 3,
      min_payout: 200,
    });
  };

  return (
    <div>
      <button onClick={handleGenerate}>Generate</button>
      {tickets.map(ticket => (
        <TicketCard
          key={ticket.lines.join('-')}
          ticket={ticket}
          onAccept={() => handleAccept(ticket)}
          onReject={() => handleReject(ticket)}
        />
      ))}
    </div>
  );
}
```

### Quick Picks Flow

```typescript
import { useTicketGenerator } from '../hooks/useTicketGenerator';
import { useCart } from '../hooks/useCart';

function QuickPicksPage() {
  const { isGenerating, generate } = useTicketGenerator({
    streamName: 'quickpicks',
    endpoint: '/game/stream_quickpicks',
    onComplete: (data) => {
      alert(`${data.ticket_count} tickets added to cart!`);
      fetchCart();
    },
  });

  const { cartCount, totalRisk, totalWins, fetchCart } = useCart();

  const handleGenerate = () => {
    generate({
      stake: 1,
      count: 5,
      depth: 3,
      min_payout: 20,  // 20:1 odds
    });
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={isGenerating}>
        Generate Quick Picks
      </button>
      
      <div>
        Cart: {cartCount} tickets
        Risk: ${totalRisk}
        Win: ${totalWins}
      </div>
    </div>
  );
}
```

---

## Key Differences from jQuery Implementation

### 1. State Management
- **jQuery**: Manual DOM manipulation with `$(selector)`
- **React**: Declarative state with `useState` and hooks

### 2. WebSocket Lifecycle
- **jQuery**: Manual event binding, global variables
- **React**: `useEffect` cleanup, ref-based instances

### 3. Card Rendering
- **jQuery**: `$("<div/>")` creation, `.append()`
- **React**: JSX components with props

### 4. Form Handling
- **jQuery**: `new FormData(form[0])`, `.serialize()`
- **React**: Controlled inputs, programmatic FormData

---

## Testing Checklist

### Custom Tickets
- [ ] Generate tickets with different parameters
- [ ] Accept ticket → appears in cart
- [ ] Reject ticket → triggers replacement
- [ ] Handle "not enough events" error
- [ ] WebSocket reconnection after disconnect
- [ ] Multiple simultaneous generations

### Quick Picks
- [ ] Generate tickets → auto-added to cart
- [ ] Complete message shows totals
- [ ] Cart syncs with backend
- [ ] Purchase flow works
- [ ] Empty cart functionality

### Edge Cases
- [ ] Not authenticated → error handling
- [ ] Bootstrap missing vdomain.uuid
- [ ] WebSocket connection fails
- [ ] Backend returns incomplete=true
- [ ] Rapid generate requests (queue handling)

---

## Production Deployment

### 1. Environment Variables
```bash
# Django settings.py
GDL_DAEMON_URI = "ws://localhost:19002"  # or production GPU daemon
```

### 2. CORS / WebSocket Settings
Ensure Django Channels allows WebSocket connections from your frontend domain.

### 3. Session Cookies
Django session cookies must be sent with WebSocket connections:
```typescript
// Already handled in WebSocketService via browser's WebSocket API
// Cookies are automatically included
```

### 4. Build React
```bash
npm run build
# Copy build/ contents to Django static/
```

---

## Troubleshooting

### "WebSocket not connected"
- Check Django Channels is running
- Verify GPU daemon is accessible
- Check browser console for connection errors

### "Not authenticated"
- Bootstrap endpoint must return `account` object
- Django session middleware must be active
- Cookies must be sent with requests

### "Missing vhost/account/vdomain"
- Ensure bootstrap endpoint includes all three UUIDs
- Check `BootstrapContext` is wrapping app

### Tickets not generating
- Check Django consumer logs for errors
- Verify GPU daemon is processing requests
- Check odds/matches are available in database

---

## Next Steps

1. **Add Purchase Flow**
   - Create purchase confirmation modal
   - Submit cart to Django endpoint
   - Update balance after purchase

2. **Add Sport Filters**
   - UI for selecting sports/groups
   - Dynamic `sport_X` / `group_X` in settings

3. **Add Ticket Details Modal**
   - Show full leg breakdown
   - Display match times, odds, outcomes

4. **Add Balance Integration**
   - Sync balance from bootstrap
   - Update after purchases
   - Show insufficient funds warnings

5. **Add Bonus Balance**
   - Toggle in purchase modal
   - Send `use_bonus` flag to backend

---

## Files Reference

```
/contexts/BootstrapContext.tsx        # Django session context
/services/WebSocketService.ts         # WebSocket manager
/hooks/useTicketGenerator.ts          # Ticket generation hook
/hooks/useCart.ts                     # Cart management hook
/types/ticket.ts                      # TypeScript types
/components/tickets/
  CustomTicketsDemo.tsx               # Custom tickets UI
  QuickPicksDemo.tsx                  # Quick picks UI
/components/TicketGeneratorDemo.tsx   # Demo page
```

---

## Support

For issues or questions:
1. Check Django consumer logs
2. Check GPU daemon logs
3. Check browser console for WebSocket errors
4. Verify bootstrap endpoint response format
