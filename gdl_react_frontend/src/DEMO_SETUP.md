# WebSocket Ticket Generator - Demo Setup

## ✅ Errors Fixed

The bootstrap errors have been resolved. The system now:

1. **Silently handles missing Django backend** - Shows clean "Demo Mode" banner instead of errors
2. **Uses mock data in development** - Fully functional UI without backend
3. **Gracefully degrades** - WebSocket connections skip when backend unavailable
4. **Provides clear feedback** - Visual indicator when in demo mode

---

## 🎨 View the Demo

The ticket generator demo is now integrated and ready to view!

### Option 1: Standalone Demo Page
Access the dedicated demo at `/demo` route (if routing is configured).

### Option 2: Integration Test
The components are ready for integration into your existing app navigation.

---

## 📋 What You'll See

### Demo Mode Banner
When Django backend is not connected, you'll see:
```
⚠️ Demo Mode
Django backend not connected. WebSocket functionality requires Django + GPU daemon.
UI components are fully functional and ready for backend integration.
```

### Two Tabs Available

#### 1. Custom Tickets
- Configure stake, ticket count, legs, min payout
- Generate button (will show "WebSocket not connected" in demo mode)
- Card layout showing how tickets will display
- Accept/Reject buttons ready for Django integration

#### 2. Quick Picks  
- Simpler interface: stake, count, legs
- 20:1 minimum payout calculation
- Cart summary display
- Purchase button ready for Django integration

---

## 🔌 Connecting to Django Backend

When you're ready to connect to your Django backend:

### 1. Update Django Bootstrap Endpoint

Add `vdomain.uuid` to `/api/v1/bootstrap`:

```python
# cypress/views/bootstrap.py
@require_GET
def bootstrap_handler(request):
    vhost = request.vhost
    vdomain = request.vdomain
    account = request.account
    
    data = {
        "vhost": {
            "uuid": str(vhost.uuid),
            "name": vhost.name,
        },
        "domain": {
            "uuid": str(vdomain.uuid),  # ← ADD THIS
            "fqdn": vdomain.domain_fqdn,
            "name": vdomain.website_name,
            "icon": vdomain.website_icon.url if vdomain.website_icon else None
        },
        # ... rest of your bootstrap data
    }
    
    return JsonResponse(data)
```

### 2. Ensure Django URLs Are Configured

```python
# urls.py
urlpatterns = [
    path('api/v1/bootstrap', bootstrap_handler),
    # ... other URLs
]
```

### 3. WebSocket Routing (Already Configured)

Your Django Channels routing is already set up:
- `/game/stream_tickets` → `GDLTicketStreamConsumer`
- `/game/stream_quickpicks` → `GDLTicketStoreStreamConsumer`

### 4. Start Your Services

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: GPU Daemon
python manage.py run_gdl_daemon

# Terminal 3: React (if separate)
npm run dev
```

### 5. Test Connection

Once connected, you'll see:
- ✅ Console log: `[Bootstrap] Loaded from Django:` (instead of "Using mock data")
- ✅ WebSocket connections establish
- ✅ Ticket generation works in real-time
- ✅ Cart API calls succeed

---

## 🧪 Testing in Demo Mode

Even without Django backend, you can test:

### UI Components
- ✅ Form inputs and controls
- ✅ Layout and responsive design
- ✅ Tab navigation
- ✅ Button states and interactions
- ✅ Card rendering (with mock data)
- ✅ Theme system integration

### What Won't Work (Expected)
- ❌ WebSocket connections (shows "not connected")
- ❌ Generate button (shows error in console)
- ❌ Cart API calls (404 errors)
- ❌ Real ticket data from GPU daemon

---

## 📁 File Structure

```
/contexts/
  BootstrapContext.tsx          # Django session loader (with mock fallback)

/services/
  WebSocketService.ts           # WebSocket manager (matches jQuery pattern)

/hooks/
  useTicketGenerator.ts         # Ticket generation hook
  useCart.ts                    # Cart management hook

/types/
  ticket.ts                     # TypeScript types

/components/
  TicketGeneratorDemo.tsx       # Main demo page with tabs
  tickets/
    CustomTicketsDemo.tsx       # Custom tickets UI
    QuickPicksDemo.tsx          # Quick picks UI

/demo.tsx                       # Standalone demo page
```

---

## 🔍 Console Messages Guide

### Development Mode (No Django)
```
[Bootstrap] Using mock data (Django backend not connected)
[TicketGenerator] Mock mode - WebSocket disabled (Django backend not connected)
```
✅ **This is normal** - UI works with mock data

### Production Mode (Django Connected)
```
[Bootstrap] Loaded from Django: {vhost: {...}, domain: {...}, ...}
[WS] Connected: ws://localhost:8000/game/stream_tickets
```
✅ **Backend connected** - Full functionality active

### Error States
```
[Bootstrap] HTTP error: 404
[Bootstrap] Response: <!DOCTYPE html>...
```
❌ **Bootstrap endpoint missing** - Check Django URLs

```
[WS] WebSocket error
[WS] Disconnected. Reconnecting in 100ms...
```
❌ **WebSocket failed** - Check Django Channels + GPU daemon running

---

## 🚀 Next Steps

### For UI Development
1. Continue styling and layout improvements
2. Add more ticket card variants
3. Build purchase confirmation modal
4. Add sport filter UI

### For Backend Integration
1. Add `vdomain.uuid` to bootstrap endpoint
2. Test bootstrap API returns JSON
3. Start Django + GPU daemon services
4. Test WebSocket connections
5. Verify ticket generation flow

### For Production
1. Build React: `npm run build`
2. Copy `dist/` to Django `static/`
3. Configure Django to serve React app
4. Set up production WebSocket (wss://)
5. Test end-to-end flow

---

## 📚 Full Documentation

See `/WEBSOCKET_INTEGRATION.md` for:
- Complete message protocol specs
- Detailed usage examples
- Integration patterns
- Troubleshooting guide
- Production deployment checklist

---

## ❓ Need Help?

**Common Issues:**

1. **"Bootstrap failed"** → Check Django is running and `/api/v1/bootstrap` exists
2. **"WebSocket not connected"** → Normal in demo mode, needs Django Channels
3. **HTML instead of JSON** → Endpoint returning error page, check Django logs
4. **CORS errors** → Configure Django CORS for your frontend domain

**Working as Expected:**
- ✅ Demo mode banner showing
- ✅ UI fully interactive
- ✅ Forms submittable (even if backend errors)
- ✅ Clean console logs about mock mode
