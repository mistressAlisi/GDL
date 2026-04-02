# 🎰 BETANY LOTTO - Deployment Model

## Architecture

This is a **Django-served React SPA** architecture:

```
┌──────────────────────────────────────────────────────────┐
│                                                           │
│                    Django Server                          │
│                   (Single Domain)                         │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Static Files (React Build)                      │   │
│  │  /static/index.html                              │   │
│  │  /static/assets/...                              │   │
│  │  Serves at: /                                    │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↕                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  REST API                                        │   │
│  │  /api/sports/config/                             │   │
│  │  /api/tickets/recent/                            │   │
│  │  /api/leaderboard/                               │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↕                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  WebSocket (Django Channels)                     │   │
│  │  /ws/ticket-generator/                           │   │
│  │  /ws/live-results/                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Development vs Production

### Development (Separate Servers)

```
React Dev Server          Django Dev Server
localhost:3000     →      localhost:8000
   (Vite)                 (manage.py runserver)
                          + Daphne (WebSockets)
```

- React runs on port 3000 with hot reload
- Django runs on port 8000
- CORS configured to allow cross-origin
- Full URLs in API config: `http://localhost:8000/api`

### Production (Single Server)

```
Django Server (localhost:8000 or your-domain.com)
    ├── / → React App (static files)
    ├── /api → REST API
    └── /ws → WebSocket
```

- React built and copied to Django's `static/` folder
- Django serves everything
- Same origin - no CORS needed
- Relative URLs: `/api`, `/ws`

## Quick Start

### 1. Development Setup

```bash
# Terminal 1: Start Django
cd /path/to/django-project
python manage.py runserver
# And Daphne for WebSockets:
daphne -p 8000 your_project.asgi:application

# Terminal 2: Start React (dev mode with hot reload)
cd /path/to/react-app
npm install
npm run dev
# Visit: http://localhost:3000
```

### 2. Production Build

```bash
# Build React app
cd /path/to/react-app
npm run build

# Copy to Django (manual)
cp -r dist/* /path/to/django-project/static/

# OR use automated script
./build-for-django.sh  # Linux/Mac
build-for-django.bat   # Windows

# Collect static files in Django
cd /path/to/django-project
python manage.py collectstatic --noinput

# Start Django
daphne -p 8000 your_project.asgi:application
# Visit: http://localhost:8000
```

## Build Scripts

### Linux/Mac: `build-for-django.sh`

```bash
# Set Django project path
export DJANGO_PROJECT_PATH=/path/to/your/django-project

# Make executable
chmod +x build-for-django.sh

# Run
./build-for-django.sh
```

### Windows: `build-for-django.bat`

```cmd
REM Set Django project path
set DJANGO_PROJECT_PATH=C:\path\to\your\django-project

REM Run
build-for-django.bat
```

The scripts will:
1. ✅ Clean previous build
2. ✅ Build React app (`npm run build`)
3. ✅ Copy to Django static folder
4. ✅ Optionally run `collectstatic`

## Environment Variables

### `.env.development` (Dev mode)
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

### `.env.production` (Production build)
```bash
VITE_API_BASE_URL=/api
VITE_WS_BASE_URL=/ws
```

These are automatically used by Vite during build.

## Django Configuration

### Required Django Settings

```python
# settings.py

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # React build goes here
]

# CORS (for development)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite alternative port
]

# Templates (to serve React's index.html)
TEMPLATES = [{
    'DIRS': [os.path.join(BASE_DIR, 'static')],
    # ... rest of config
}]
```

### URL Configuration

```python
# urls.py
from django.urls import path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('your_app.api_urls')),
    
    # Serve React app for all other routes (SPA fallback)
    re_path(r'^(?!api|admin|static|ws).*$', 
            TemplateView.as_view(template_name='index.html')),
]
```

## File Structure

```
project-root/
│
├── react-app/                      # Your React frontend (this folder)
│   ├── src/
│   ├── services/
│   │   ├── api-config.ts          # ✅ Updated for deployment
│   │   ├── websocket-service.ts
│   │   ├── api-service.ts
│   │   └── api-hooks.ts
│   ├── .env.development           # ✅ Created
│   ├── .env.production            # ✅ Created
│   ├── build-for-django.sh        # ✅ Created
│   ├── build-for-django.bat       # ✅ Created
│   ├── package.json
│   ├── vite.config.ts
│   └── dist/                      # Build output (created by npm run build)
│
└── django-project/                 # Your Django backend (separate folder)
    ├── your_project/
    │   ├── settings.py
    │   ├── urls.py
    │   └── asgi.py
    ├── your_app/
    │   ├── consumers.py           # WebSocket handlers
    │   ├── routing.py
    │   └── views.py               # REST API views
    ├── static/                    # React build copied here
    │   ├── index.html
    │   └── assets/
    ├── staticfiles/               # collectstatic output
    └── manage.py
```

## API Integration

All API calls are handled via services:

```typescript
// Automatically uses correct URLs based on environment
import { useTicketGeneration } from './services/api-hooks';

function MyComponent() {
  const { generateTicket, loading } = useTicketGeneration();
  
  generateTicket({
    wager: 10,
    entries: 5,
    sports: ['tennis', 'soccer'],
    timeframe: '24h',
  });
}
```

Mock data is automatically enabled in development:
- `npm run dev` → Mock data ON
- `npm run build` → Mock data OFF

## Testing Production Build Locally

```bash
# 1. Build React
npm run build

# 2. Copy to Django
cp -r dist/* /path/to/django/static/

# 3. Run Django with static serving
cd /path/to/django
python manage.py collectstatic --noinput
python manage.py runserver --insecure  # --insecure allows static in DEBUG=False

# 4. Test
# Visit: http://localhost:8000
```

## Deployment Checklist

### React App
- [ ] Environment variables configured
- [ ] `npm run build` successful
- [ ] Build output in `dist/` folder
- [ ] All assets load in production build

### Django
- [ ] Static files directory configured
- [ ] Templates include static folder
- [ ] CORS settings correct (dev only)
- [ ] URL routing serves React for non-API routes
- [ ] Django Channels configured
- [ ] WebSocket endpoints working

### Integration
- [ ] Build copied to Django static folder
- [ ] `collectstatic` runs successfully
- [ ] Django serves React app at `/`
- [ ] API endpoints work at `/api/*`
- [ ] WebSockets connect at `/ws/*`
- [ ] React Router navigation works

## Common Issues

### 404 on Page Refresh
**Problem:** Navigating to `/about` works, but refreshing gives 404  
**Fix:** Django URL pattern must catch all non-API routes and serve `index.html`

### Static Assets Not Loading
**Problem:** JS/CSS files return 404  
**Fix:** Run `python manage.py collectstatic` and check `STATIC_URL` setting

### API Calls Fail
**Problem:** Network errors when calling API  
**Fix:** Check environment variables and Django CORS settings (dev only)

### WebSocket Won't Connect
**Problem:** WebSocket connection refused  
**Fix:** Ensure Daphne is running and ASGI is configured correctly

## Documentation

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment guide with Django setup
- **[DJANGO_INTEGRATION.md](./DJANGO_INTEGRATION.md)** - Django Channels and REST API setup
- **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** - Quick API reference
- **[BACKEND_INTEGRATION_README.md](./BACKEND_INTEGRATION_README.md)** - Backend integration overview

## Summary

1. **Develop:** React dev server (port 3000) + Django (port 8000)
2. **Build:** `npm run build` creates `dist/` folder
3. **Deploy:** Copy `dist/` to Django's `static/` folder
4. **Serve:** Django serves everything from one domain

Simple, efficient, and no CORS issues in production! 🚀
