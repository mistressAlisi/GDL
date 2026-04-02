# Quick Reference: Django API Integration

## 🚀 Quick Start

### 1. Enable Backend Connection
```typescript
// Edit /services/api-config.ts
export const API_CONFIG = {
  BASE_URL: 'https://your-django-backend.com/api',
  WS_BASE_URL: 'wss://your-django-backend.com/ws',
  USE_MOCK_DATA: false, // Change to false when ready
};
```

### 2. Use in Components

#### Generate Tickets (WebSocket)
```typescript
import { useTicketGeneration } from './services/api-hooks';

const { generateTicket, loading, error, response } = useTicketGeneration();

generateTicket({
  wager: 10,
  entries: 5,
  sports: ['tennis', 'soccer'],
  timeframe: '24h',
});
```

#### Fetch Recent Tickets
```typescript
import { useRecentTickets } from './services/api-hooks';

const { tickets, loading, error, refresh } = useRecentTickets(20, true);
```

#### Display Leaderboard
```typescript
import { useLeaderboard } from './services/api-hooks';

const { leaderboard, loading, error } = useLeaderboard(10);
```

#### Show Statistics
```typescript
import { useStatistics } from './services/api-hooks';

const { stats, loading, error } = useStatistics();
```

#### Load Sports Config
```typescript
import { useSportsConfig } from './services/api-hooks';

const { config, loading, error } = useSportsConfig();
```

## 📡 WebSocket Messages

### Client → Server (Generate Ticket)
```json
{
  "type": "generate_ticket",
  "requestId": "unique_id",
  "wager": 10,
  "entries": 5,
  "sports": ["tennis", "soccer"],
  "timeframe": "24h"
}
```

### Server → Client (Success)
```json
{
  "type": "generate_ticket",
  "requestId": "unique_id",
  "success": true,
  "ticket": {
    "id": "ticket_123",
    "entries": [...],
    "wager": 10,
    "potentialPayout": 250.00,
    "totalOdds": 25.0
  }
}
```

## 🔌 REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sports/config/` | GET | Get sports configuration |
| `/api/sports/` | GET | List all sports |
| `/api/tickets/recent/?limit=20` | GET | Get recent tickets |
| `/api/tickets/user/?userId=123` | GET | Get user's tickets |
| `/api/leaderboard/?limit=10` | GET | Get top players |
| `/api/statistics/` | GET | Get platform stats |

## 📦 Available Hooks

| Hook | Purpose | Returns |
|------|---------|---------|
| `useTicketGeneration()` | Generate tickets via WebSocket | `{ generateTicket, loading, error, response }` |
| `useSportsConfig()` | Load sports configuration | `{ config, loading, error }` |
| `useRecentTickets(limit, autoRefresh)` | Fetch recent tickets | `{ tickets, loading, error, refresh }` |
| `useLeaderboard(limit)` | Fetch leaderboard | `{ leaderboard, loading, error, refresh }` |
| `useStatistics()` | Fetch platform statistics | `{ stats, loading, error }` |
| `useLiveResults()` | Subscribe to live results | `{ results }` |

## 🎯 Example Components

Check these files for full implementation examples:
- `/components/examples/RecentTicketsTable.tsx` - Ticket table with auto-refresh
- `/components/examples/LeaderboardDisplay.tsx` - Animated leaderboard
- `/components/examples/StatisticsDashboard.tsx` - Stats grid
- `/components/examples/DynamicSportsSelector.tsx` - Backend-driven sports selector

## 🔧 Django Backend Setup

### Install Dependencies
```bash
pip install channels channels-redis djangorestframework django-cors-headers
```

### settings.py
```python
INSTALLED_APPS = [
    'channels',
    'rest_framework',
    'corsheaders',
    # ... your apps
]

ASGI_APPLICATION = 'your_project.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-frontend.com',
]
```

### asgi.py
```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import your_app.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            your_app.routing.websocket_urlpatterns
        )
    ),
})
```

## 🧪 Testing

### Test WebSocket Connection
```javascript
// In browser console:
const ws = new WebSocket('wss://your-backend.com/ws/ticket-generator/');
ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
```

### Test REST API
```bash
curl https://your-backend.com/api/sports/config/
curl https://your-backend.com/api/tickets/recent/?limit=5
```

## 🐛 Debugging

### Enable Logging
```typescript
// In /services/websocket-service.ts
console.log('WebSocket message:', data);

// In /services/api-service.ts
console.log('API request:', url, config);
```

### Check Connection Status
```javascript
// WebSocket status
console.log(ticketWebSocket.ws?.readyState);
// 0 = CONNECTING, 1 = OPEN, 2 = CLOSING, 3 = CLOSED
```

## 🔐 Authentication (Optional)

### Add Token to Requests
```typescript
// In /services/api-service.ts
const token = localStorage.getItem('authToken');
headers: {
  'Authorization': `Bearer ${token}`,
  ...
}
```

### Add Token to WebSocket
```typescript
// In /services/websocket-service.ts
const wsUrl = `${buildWsUrl(channel)}?token=${token}`;
```

## 📊 Data Types

### TicketGenerationRequest
```typescript
{
  wager: number;
  entries: number;
  sports: string[];
  timeframe: string;
  luckyPick?: boolean;
  gameType?: 'quick-play' | 'custom';
}
```

### TicketGenerationResponse
```typescript
{
  success: boolean;
  ticket?: {
    id: string;
    entries: Entry[];
    wager: number;
    potentialPayout: number;
    totalOdds: number;
  };
  error?: string;
}
```

See `/services/api-service.ts` and `/services/websocket-service.ts` for complete type definitions.
