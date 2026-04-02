# 🎰 BETANY LOTTO - Backend Integration Complete

## 📌 Overview

Your BETANY LOTTO platform is now fully equipped with Django 6 + Channels integration. All sport buttons (Tennis, US Sports, Soccer, NCAA Basketball) now route to the Quick Play form, which uses WebSocket connections for real-time ticket generation from your backend.

## ✅ What's Been Completed

### 1. **Unified Form Flow**
- ✅ All sport buttons route to Quick Play form
- ✅ Custom Tickets button routes to Quick Play form
- ✅ Quick Play button routes to Quick Play form
- ✅ Form respects global ticket rules (sports + timeframe)

### 2. **WebSocket Integration**
- ✅ Real-time ticket generation via Django Channels
- ✅ Automatic reconnection with exponential backoff
- ✅ Request/response correlation system
- ✅ Type-safe message interfaces
- ✅ Mock data mode for offline development

### 3. **REST API Services**
- ✅ Sports configuration endpoint
- ✅ Recent tickets table data
- ✅ User tickets history
- ✅ Leaderboard rankings
- ✅ Platform statistics
- ✅ Ticket validation

### 4. **React Integration**
- ✅ Custom hooks for all API calls
- ✅ Loading states and error handling
- ✅ Auto-refresh capabilities
- ✅ Live results subscription
- ✅ Updated QuickPicksForm with WebSocket

### 5. **Example Components**
- ✅ RecentTicketsTable with auto-refresh
- ✅ LeaderboardDisplay with animations
- ✅ StatisticsDashboard with real-time data
- ✅ DynamicSportsSelector from backend config

### 6. **Documentation**
- ✅ Complete Django setup guide
- ✅ API quick reference
- ✅ Integration summary
- ✅ Example code snippets

## 📁 Key Files Created

```
/services/
├── api-config.ts               # Backend URLs and configuration
├── websocket-service.ts        # WebSocket client with reconnection
├── api-service.ts              # REST API client
└── api-hooks.ts                # React hooks for all endpoints

/components/examples/
├── RecentTicketsTable.tsx      # Full table implementation
├── LeaderboardDisplay.tsx      # Animated leaderboard
├── StatisticsDashboard.tsx     # Platform statistics
└── DynamicSportsSelector.tsx   # Backend-driven sports selector

/
├── DJANGO_INTEGRATION.md       # Complete Django setup guide (200+ lines)
├── API_QUICK_REFERENCE.md      # Developer quick reference
└── API_INTEGRATION_SUMMARY.md  # Integration overview
```

## 🚀 Getting Started (3 Steps)

### Step 1: Configure Your Backend URLs

Edit `/services/api-config.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: 'https://your-django-backend.com/api',
  WS_BASE_URL: 'wss://your-django-backend.com/ws',
  USE_MOCK_DATA: false, // Set to false when backend is ready
};
```

Or use environment variables:
```bash
REACT_APP_API_BASE_URL=https://api.betanylotto.com/api
REACT_APP_WS_BASE_URL=wss://api.betanylotto.com/ws
```

### Step 2: Set Up Django Backend

Follow the complete guide in `DJANGO_INTEGRATION.md`:

1. Install Django Channels + Redis
2. Create WebSocket consumer for `/ws/ticket-generator/`
3. Create REST API endpoints
4. Configure CORS and ASGI

Example Consumer:
```python
# consumers.py
class TicketGeneratorConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'generate_ticket':
            ticket = await generate_ticket_logic(data)
            await self.send(json.dumps({
                'requestId': data['requestId'],
                'success': True,
                'ticket': ticket
            }))
```

### Step 3: Test the Integration

1. **With Mock Data** (default):
   - Leave `USE_MOCK_DATA: true`
   - All features work offline
   - Test UI and flows

2. **With Real Backend**:
   - Set `USE_MOCK_DATA: false`
   - Start Django server
   - Check browser console for WebSocket connection
   - Generate tickets and see real data

## 🎯 How It Works Now

### User Flow:
```
1. User opens SPORTSLOTTO
2. Clicks any sport or Quick Play button
3. Opens Quick Play form
4. User sets:
   - Ticket count (how many tickets)
   - Risk amount per ticket
   - Entries per ticket (3-10 picks)
5. Form uses global ticket rules:
   - Selected sports (from Ticket Rules modal)
   - Timeframe (12h-48h from Ticket Rules modal)
6. Click "ADD TO CART"
7. WebSocket request sent to Django
8. Django generates ticket with real sports data
9. Ticket sent back via WebSocket
10. Display success message
11. Ticket added to cart
```

### Technical Flow:
```
QuickPicksForm
    ↓
useTicketGeneration() hook
    ↓
ticketWebSocket.generateTicket()
    ↓
WebSocket → Django Channels → Ticket Logic
    ↓
Django generates ticket from sports events
    ↓
Response via WebSocket
    ↓
Frontend displays ticket
```

## 📡 Backend Requirements

Your Django backend must provide:

### WebSocket Endpoints (Django Channels):
- `ws://your-backend/ws/ticket-generator/` - Main ticket generation channel

### REST API Endpoints:
- `GET /api/sports/config/` - Sports configuration (what sports are available)
- `GET /api/tickets/recent/?limit=20` - Recent tickets for tables
- `GET /api/tickets/user/?userId=123` - User's ticket history
- `GET /api/leaderboard/?limit=10` - Top players
- `GET /api/statistics/` - Platform-wide statistics

### WebSocket Message Format:

**Request (Frontend → Backend):**
```json
{
  "type": "generate_ticket",
  "requestId": "ticket_1738195200000_abc123",
  "wager": 10,
  "entries": 5,
  "sports": ["tennis", "us-sports", "soccer", "ncaa-basketball"],
  "timeframe": "24h",
  "luckyPick": true,
  "gameType": "quick-play"
}
```

**Response (Backend → Frontend):**
```json
{
  "type": "generate_ticket",
  "requestId": "ticket_1738195200000_abc123",
  "success": true,
  "ticket": {
    "id": "ticket_xyz789",
    "entries": [
      {
        "id": "entry_1",
        "sport": "tennis",
        "sportName": "Tennis",
        "event": "ATP Finals",
        "team1": "Nadal",
        "team2": "Djokovic",
        "prediction": "Win",
        "odds": 2.5,
        "startTime": "2026-01-30T15:00:00Z"
      }
    ],
    "wager": 10,
    "potentialPayout": 312.50,
    "totalOdds": 31.25,
    "drawDate": "2026-01-30T12:00:00Z",
    "generatedAt": "2026-01-29T10:30:00Z"
  }
}
```

## 💻 Usage Examples

### Generate Ticket in Your Component

```typescript
import { useTicketGeneration } from './services/api-hooks';

function MyBettingForm() {
  const { generateTicket, loading, error, response } = useTicketGeneration();
  
  const handleGenerate = () => {
    generateTicket({
      wager: 10,
      entries: 5,
      sports: ['tennis', 'soccer'],
      timeframe: '24h',
      luckyPick: true,
    });
  };
  
  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Ticket'}
      </button>
      {error && <p className="text-red-500">{error}</p>}
      {response?.ticket && (
        <div>Ticket ID: {response.ticket.id}</div>
      )}
    </div>
  );
}
```

### Display Recent Tickets

```typescript
import { useRecentTickets } from './services/api-hooks';

function TicketsTable() {
  const { tickets, loading, error } = useRecentTickets(20, true); // auto-refresh
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <table>
      {tickets.map(ticket => (
        <tr key={ticket.id}>
          <td>{ticket.userName}</td>
          <td>${ticket.wager}</td>
          <td>{ticket.status}</td>
        </tr>
      ))}
    </table>
  );
}
```

### Show Leaderboard

```typescript
import { useLeaderboard } from './services/api-hooks';

function Leaderboard() {
  const { leaderboard, loading } = useLeaderboard(10);
  
  return (
    <div>
      {leaderboard.map((player, i) => (
        <div key={player.userId}>
          {i + 1}. {player.userName} - {player.totalWins} wins
        </div>
      ))}
    </div>
  );
}
```

## 🔍 Debugging

### Check WebSocket Connection

Open browser console:
```javascript
// Check if WebSocket is connected
console.log(ticketWebSocket.ws?.readyState);
// 1 = Connected, 0 = Connecting, 2 = Closing, 3 = Closed

// Test connection manually
const ws = new WebSocket('wss://your-backend.com/ws/ticket-generator/');
ws.onopen = () => console.log('✅ Connected!');
ws.onerror = (e) => console.error('❌ Error:', e);
```

### Check API Endpoints

```bash
# Test sports config
curl https://your-backend.com/api/sports/config/

# Test recent tickets
curl https://your-backend.com/api/tickets/recent/?limit=5

# Test leaderboard
curl https://your-backend.com/api/leaderboard/?limit=10
```

### Enable Debug Logging

Uncomment logging in the service files:
```typescript
// In /services/websocket-service.ts
console.log('📤 Sending:', request);
console.log('📥 Received:', response);
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `DJANGO_INTEGRATION.md` | Complete Django Channels + REST setup guide |
| `API_QUICK_REFERENCE.md` | Quick lookup for hooks, endpoints, and examples |
| `API_INTEGRATION_SUMMARY.md` | Overview of what was implemented |
| `BACKEND_INTEGRATION_README.md` | This file - getting started guide |

## 🎨 Example Components

Pre-built components ready to use:

1. **RecentTicketsTable** - `/components/examples/RecentTicketsTable.tsx`
   - Displays recent tickets in a table
   - Auto-refreshes every 30 seconds
   - Status badges and formatting

2. **LeaderboardDisplay** - `/components/examples/LeaderboardDisplay.tsx`
   - Top 10 players with rankings
   - Trophy icons for top 3
   - Win rate and profit calculations

3. **StatisticsDashboard** - `/components/examples/StatisticsDashboard.tsx`
   - Platform-wide statistics grid
   - Total tickets, wagers, payouts
   - Active users, biggest win, etc.

4. **DynamicSportsSelector** - `/components/examples/DynamicSportsSelector.tsx`
   - Loads sports from backend configuration
   - Shows odds ranges per sport
   - Selection state management

Import and use them directly:
```typescript
import { RecentTicketsTable } from './components/examples/RecentTicketsTable';

function MyPage() {
  return <RecentTicketsTable />;
}
```

## 🔐 Authentication (Optional)

To add authentication tokens:

```typescript
// In /services/api-service.ts
const token = localStorage.getItem('authToken');
headers: {
  'Authorization': `Bearer ${token}`,
  ...
}

// In /services/websocket-service.ts
const wsUrl = `${buildWsUrl(channel)}?token=${token}`;
```

## ⚙️ Configuration Options

### Toggle Mock Data

```typescript
// /services/api-config.ts
export const API_CONFIG = {
  USE_MOCK_DATA: true,  // Use mock data for development
  USE_MOCK_DATA: false, // Use real backend
};
```

### Change Timeouts

```typescript
export const API_CONFIG = {
  TIMEOUT: 30000, // API request timeout (30 seconds)
};
```

### Reconnection Settings

```typescript
// /services/websocket-service.ts
private maxReconnectAttempts = 5;  // Max reconnect attempts
private reconnectDelay = 1000;      // Initial delay (1 second)
```

## 🎯 Next Steps

1. **Set up your Django backend** using `DJANGO_INTEGRATION.md`
2. **Configure your backend URLs** in `/services/api-config.ts`
3. **Test with mock data** first (already enabled by default)
4. **Connect to real backend** by setting `USE_MOCK_DATA: false`
5. **Use example components** or build your own with the hooks
6. **Monitor the console** for WebSocket connection status
7. **Add authentication** if needed

## 🆘 Troubleshooting

**WebSocket won't connect:**
- Check URL format: `wss://` for HTTPS, `ws://` for HTTP
- Verify Django Channels is running
- Check CORS settings in Django
- Look for firewall/proxy issues

**API requests fail:**
- Verify REST API endpoints exist
- Check CORS headers
- Confirm Django REST framework is installed
- Test endpoints with curl/Postman

**Mock data not showing:**
- Ensure `USE_MOCK_DATA: true`
- Check console for errors
- Verify imports are correct

## 🎉 Summary

Your BETANY LOTTO platform now has:
- ✅ Complete WebSocket integration for real-time ticket generation
- ✅ REST API integration for tables and data display
- ✅ All sport buttons route to unified Quick Play form
- ✅ Ticket rules (sports + timeframe) apply to all tickets
- ✅ Mock data mode for offline development
- ✅ Example components ready to use
- ✅ Complete documentation and setup guides

**The frontend is ready!** Just connect your Django backend and you'll have real-time sports lottery ticket generation! 🚀🎰

---

**Quick Links:**
- 📖 [Django Setup Guide](./DJANGO_INTEGRATION.md)
- ⚡ [Quick Reference](./API_QUICK_REFERENCE.md)
- 📊 [Integration Summary](./API_INTEGRATION_SUMMARY.md)
- 🎨 [Example Components](./components/examples/)

**Need Help?** Check the browser console for detailed error messages and connection status.
