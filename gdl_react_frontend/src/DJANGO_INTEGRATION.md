# Django Backend Integration Guide

## Overview

BETANY LOTTO uses Django 6 + Django Channels for real-time ticket generation via WebSockets and REST APIs for configuration and data tables.

## 🔧 Setup Instructions

### 1. Configure Backend URLs

Edit `/services/api-config.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: 'https://your-backend-api.com/api',
  WS_BASE_URL: 'wss://your-backend-api.com/ws',
  USE_MOCK_DATA: false, // Set to false when backend is ready
};
```

Or use environment variables:
```bash
REACT_APP_API_BASE_URL=https://your-backend-api.com/api
REACT_APP_WS_BASE_URL=wss://your-backend-api.com/ws
```

### 2. WebSocket Integration (Django Channels)

#### Channel: `/ws/ticket-generator/`

**Purpose**: Real-time ticket generation based on form configuration

**Client Request Format**:
```json
{
  "type": "generate_ticket",
  "requestId": "ticket_1738195200000_abc123",
  "wager": 10,
  "entries": 5,
  "drawDate": "2026-01-30T12:00:00Z",
  "sports": ["tennis", "us-sports", "soccer", "ncaa-basketball"],
  "timeframe": "24h",
  "luckyPick": true,
  "gameType": "quick-play",
  "userId": "user_123",
  "sessionId": "session_abc"
}
```

**Server Response Format**:
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

**Error Response**:
```json
{
  "type": "generate_ticket",
  "requestId": "ticket_1738195200000_abc123",
  "success": false,
  "error": "Insufficient events available for selected timeframe",
  "message": "Please try a longer timeframe or fewer entries"
}
```

#### Django Channels Consumer Example:

```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TicketGeneratorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("✅ Client connected to ticket generator")
    
    async def disconnect(self, close_code):
        print(f"🔌 Client disconnected: {close_code}")
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'generate_ticket':
            await self.handle_generate_ticket(data)
        elif message_type == 'subscribe':
            await self.handle_subscribe(data)
    
    async def handle_generate_ticket(self, data):
        request_id = data.get('requestId')
        wager = data.get('wager')
        entries_count = data.get('entries')
        sports = data.get('sports', [])
        timeframe = data.get('timeframe', '24h')
        
        try:
            # Your ticket generation logic here
            ticket = await self.generate_ticket_logic(
                wager=wager,
                entries_count=entries_count,
                sports=sports,
                timeframe=timeframe
            )
            
            # Send success response
            await self.send(text_data=json.dumps({
                'type': 'generate_ticket',
                'requestId': request_id,
                'success': True,
                'ticket': ticket
            }))
            
        except Exception as e:
            # Send error response
            await self.send(text_data=json.dumps({
                'type': 'generate_ticket',
                'requestId': request_id,
                'success': False,
                'error': str(e)
            }))
```

#### Routing Configuration:

```python
# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ticket-generator/$', consumers.TicketGeneratorConsumer.as_asgi()),
    re_path(r'ws/live-results/$', consumers.LiveResultsConsumer.as_asgi()),
]
```

### 3. REST API Endpoints

#### GET `/api/sports/config/`

**Purpose**: Get sports configuration and settings

**Response**:
```json
{
  "sports": [
    {
      "id": "tennis",
      "name": "Tennis",
      "icon": "🎾",
      "enabled": true,
      "settings": {
        "minOdds": 1.5,
        "maxOdds": 5.0,
        "defaultTimeframe": "24h",
        "availableTimeframes": ["12h", "18h", "24h", "30h", "36h", "42h", "48h"]
      }
    }
  ],
  "customTickets": {
    "enabled": true,
    "availableSports": ["tennis", "us-sports", "soccer", "ncaa-basketball"],
    "defaultSports": ["tennis", "us-sports", "soccer", "ncaa-basketball"]
  }
}
```

#### Django View Example:

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def sports_config(request):
    config = {
        'sports': [
            {
                'id': 'tennis',
                'name': 'Tennis',
                'icon': '🎾',
                'enabled': True,
                'settings': {
                    'minOdds': 1.5,
                    'maxOdds': 5.0,
                    'defaultTimeframe': '24h',
                    'availableTimeframes': ['12h', '18h', '24h', '30h', '36h', '42h', '48h']
                }
            },
            # ... other sports
        ],
        'customTickets': {
            'enabled': True,
            'availableSports': ['tennis', 'us-sports', 'soccer', 'ncaa-basketball'],
            'defaultSports': ['tennis', 'us-sports', 'soccer', 'ncaa-basketball']
        }
    }
    return Response(config)
```

#### GET `/api/tickets/recent/?limit=20`

**Purpose**: Fetch recent tickets for display

**Response**:
```json
[
  {
    "id": "ticket_123",
    "userId": "user_456",
    "userName": "Player123",
    "wager": 10.00,
    "potentialPayout": 250.00,
    "totalOdds": 25.0,
    "entries": 5,
    "status": "pending",
    "createdAt": "2026-01-29T10:00:00Z",
    "drawDate": "2026-01-30T12:00:00Z"
  }
]
```

#### GET `/api/leaderboard/?limit=10`

**Purpose**: Get top players/winners

**Response**:
```json
[
  {
    "rank": 1,
    "userId": "user_123",
    "userName": "Champion1",
    "totalWins": 45,
    "totalWager": 5000.00,
    "totalPayout": 12500.00,
    "winRate": 35.5
  }
]
```

#### URLs Configuration:

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/sports/config/', views.sports_config),
    path('api/sports/', views.sports_list),
    path('api/tickets/recent/', views.recent_tickets),
    path('api/tickets/user/', views.user_tickets),
    path('api/leaderboard/', views.leaderboard),
    path('api/statistics/', views.statistics),
]
```

## 🎯 Frontend Usage

### Generating Tickets with WebSocket

```typescript
import { useTicketGeneration } from './services/api-hooks';

function MyComponent() {
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
      {error && <p>Error: {error}</p>}
      {response?.ticket && <TicketDisplay ticket={response.ticket} />}
    </div>
  );
}
```

### Fetching Sports Configuration

```typescript
import { useSportsConfig } from './services/api-hooks';

function SportsSelector() {
  const { config, loading, error } = useSportsConfig();
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {config?.sports.map(sport => (
        <div key={sport.id}>
          {sport.icon} {sport.name}
        </div>
      ))}
    </div>
  );
}
```

### Displaying Recent Tickets

```typescript
import { useRecentTickets } from './services/api-hooks';

function TicketsTable() {
  const { tickets, loading, error, refresh } = useRecentTickets(20, true); // Auto-refresh
  
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

## 🔐 Authentication (Optional)

If you need to add authentication tokens:

```typescript
// In api-service.ts, modify the request method:
private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('authToken');
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  };
  // ... rest of the code
}
```

## 🧪 Testing

The app currently uses `USE_MOCK_DATA: true` mode with realistic mock data. To switch to real backend:

1. Set `USE_MOCK_DATA: false` in `/services/api-config.ts`
2. Configure your backend URLs
3. Ensure your Django backend is running and accessible
4. Check browser console for WebSocket connection status

## 📊 Data Models

The frontend expects the following data structures. Ensure your Django models serialize to these formats:

- **Ticket**: See `TicketGenerationResponse` interface
- **SportConfig**: See `SportConfig` interface  
- **TicketRecord**: See `TicketRecord` interface
- **LeaderboardEntry**: See `LeaderboardEntry` interface

## 🚀 Deployment Considerations

1. **WebSocket URL**: Use `wss://` (secure) in production
2. **CORS**: Configure Django CORS settings to allow your frontend domain
3. **Django Channels**: Ensure Redis or another channel layer is configured
4. **Environment Variables**: Use `.env` files for different environments

## 📝 Notes

- All timeframes are in hours: '12h', '18h', '24h', '30h', '36h', '42h', '48h'
- Sports IDs: 'tennis', 'us-sports', 'soccer', 'ncaa-basketball'
- Ticket status: 'pending', 'won', 'lost', 'void'
- All timestamps are ISO 8601 format
