# 🚀 BETANY LOTTO - Production Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Django 6 Backend                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Static Files (React Build Output)                  │    │
│  │  - /static/index.html                               │    │
│  │  - /static/assets/js/...                            │    │
│  │  - /static/assets/css/...                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  REST API Endpoints                                 │    │
│  │  - /api/sports/config/                              │    │
│  │  - /api/tickets/recent/                             │    │
│  │  - /api/leaderboard/                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  WebSocket Endpoints (Django Channels)              │    │
│  │  - /ws/ticket-generator/                            │    │
│  │  - /ws/live-results/                                │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Build & Deployment Process

### Step 1: Build React Application

```bash
# From the React app root directory
npm install
npm run build
```

This creates a `dist/` folder with:
```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── ... other assets
└── ... other static files
```

### Step 2: Copy Build Output to Django

#### Option A: Manual Copy
```bash
# Copy dist/ contents to Django's static folder
cp -r dist/* /path/to/django-project/static/

# Or on Windows
xcopy /E /I dist\* C:\path\to\django-project\static\
```

#### Option B: Automated Build Script

Create `build-and-deploy.sh`:
```bash
#!/bin/bash

# Build React app
echo "🔨 Building React application..."
npm run build

# Copy to Django static folder
echo "📦 Copying to Django static folder..."
DJANGO_STATIC="/path/to/django-project/static"
rm -rf $DJANGO_STATIC/*
cp -r dist/* $DJANGO_STATIC/

# Collect static files in Django
echo "📚 Collecting Django static files..."
cd /path/to/django-project
python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
```

Make it executable:
```bash
chmod +x build-and-deploy.sh
```

#### Option C: npm Script

Add to `package.json`:
```json
{
  "scripts": {
    "build": "vite build",
    "deploy": "npm run build && node deploy.js"
  }
}
```

Create `deploy.js`:
```javascript
const fs = require('fs-extra');
const path = require('path');

const distPath = path.join(__dirname, 'dist');
const djangoStaticPath = '/path/to/django-project/static';

console.log('🔨 Copying build to Django...');
fs.copySync(distPath, djangoStaticPath, { overwrite: true });
console.log('✅ Deployment complete!');
```

## ⚙️ Django Configuration

### 1. Settings Configuration

**`settings.py`**:
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Development
    "http://localhost:5173",  # Vite dev server
    "https://yourdomain.com", # Production
]

# For production, you might want same-origin:
# Since React is served from Django, API calls are same-origin
CORS_ALLOW_CREDENTIALS = True

# WebSocket configuration (Django Channels)
ASGI_APPLICATION = 'your_project.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

# Installed apps
INSTALLED_APPS = [
    'daphne',  # Must be first for Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'rest_framework',
    'corsheaders',
    # Your apps
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 2. URL Configuration for SPA

**`urls.py`** (Main URLconf):
```python
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('your_app.api_urls')),
    
    # Serve React app for all other routes (SPA fallback)
    re_path(r'^(?!api|admin|static|ws).*$', TemplateView.as_view(
        template_name='index.html',
        content_type='text/html'
    )),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Alternative (using a custom view for better control):**
```python
from django.shortcuts import render

def spa_view(request):
    """Serve React SPA for all non-API routes"""
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('your_app.api_urls')),
    
    # Catch all other routes and serve React
    re_path(r'^(?!api|admin|static|ws).*$', spa_view),
]
```

### 3. Template Configuration

**`settings.py`** - Update TEMPLATES:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'static'),  # Look for index.html here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 4. ASGI Configuration

**`asgi.py`**:
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import your_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            your_app.routing.websocket_urlpatterns
        )
    ),
})
```

## 🔧 React App Configuration

### Environment Variables

Create `.env.production`:
```bash
# Production - relative paths since served from same domain
VITE_API_BASE_URL=/api
VITE_WS_BASE_URL=/ws

# Or absolute URLs if different domain
# VITE_API_BASE_URL=https://api.betanylotto.com/api
# VITE_WS_BASE_URL=wss://api.betanylotto.com/ws
```

Create `.env.development`:
```bash
# Development - full URLs to Django dev server
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

### Update API Configuration

**`/services/api-config.ts`**:
```typescript
export const API_CONFIG = {
  // Use environment variables with fallbacks
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',
  WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL || '/ws',
  
  // Endpoints (same as before)
  ENDPOINTS: {
    SPORTS_CONFIG: '/sports/config/',
    SPORTS_LIST: '/sports/',
    // ... rest of endpoints
  },
  
  WS_CHANNELS: {
    TICKET_GENERATOR: '/ticket-generator/',
    LIVE_RESULTS: '/live-results/',
    NOTIFICATIONS: '/notifications/',
  },
  
  TIMEOUT: 30000,
  
  // Disable mock data in production
  USE_MOCK_DATA: import.meta.env.DEV, // true in dev, false in production
};

// Helper function to build full URL
export const buildUrl = (endpoint: string, params?: Record<string, string>) => {
  const baseUrl = API_CONFIG.BASE_URL;
  
  // If BASE_URL is relative, prepend window.location.origin
  const fullBaseUrl = baseUrl.startsWith('http') 
    ? baseUrl 
    : `${window.location.origin}${baseUrl}`;
  
  let url = `${fullBaseUrl}${endpoint}`;
  
  // Replace URL parameters
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url = url.replace(`:${key}`, value);
    });
  }
  
  return url;
};

// Helper function to build WebSocket URL
export const buildWsUrl = (channel: string) => {
  const wsBase = API_CONFIG.WS_BASE_URL;
  
  // Determine protocol based on current page
  if (wsBase.startsWith('ws://') || wsBase.startsWith('wss://')) {
    return `${wsBase}${channel}`;
  }
  
  // Relative path - construct full WebSocket URL
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}${wsBase}${channel}`;
};
```

### Update Vite Configuration

**`vite.config.ts`**:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  // Development server proxy (optional, for local development)
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false, // Set to true for debugging
    
    // Optimize chunk splitting
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router'],
          ui: ['lucide-react'],
        },
      },
    },
  },
});
```

## 🚀 Deployment Steps

### Development Workflow

1. **Start Django backend:**
```bash
cd /path/to/django-project
python manage.py runserver
daphne -p 8000 your_project.asgi:application  # For WebSockets
```

2. **Start React dev server:**
```bash
cd /path/to/react-app
npm run dev
```

3. **Develop and test** using React dev server (hot reload)

### Production Deployment

1. **Build React app:**
```bash
cd /path/to/react-app
npm run build
```

2. **Copy to Django static:**
```bash
cp -r dist/* /path/to/django-project/static/
```

3. **Collect static files:**
```bash
cd /path/to/django-project
python manage.py collectstatic --noinput
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Start production server:**
```bash
# Option A: Gunicorn + Daphne (recommended)
daphne -b 0.0.0.0 -p 8000 your_project.asgi:application

# Option B: Gunicorn + Nginx + Daphne
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
daphne -u /tmp/daphne.sock your_project.asgi:application
```

## 🐳 Docker Deployment (Optional)

**`Dockerfile`**:
```dockerfile
FROM node:18 AS frontend-builder
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.11
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy Django project
COPY . .

# Copy React build from previous stage
COPY --from=frontend-builder /frontend/dist /app/static

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "your_project.asgi:application"]
```

## 📝 Project Structure

```
django-project/
├── your_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── your_app/
│   ├── api_urls.py
│   ├── consumers.py
│   ├── routing.py
│   └── views.py
├── static/                    # React build output goes here
│   ├── index.html
│   └── assets/
│       ├── index-[hash].js
│       └── index-[hash].css
├── staticfiles/               # Django collectstatic output
├── manage.py
└── requirements.txt

react-app/                     # Separate from Django
├── src/
├── public/
├── dist/                      # Build output (copied to Django)
├── package.json
└── vite.config.ts
```

## ✅ Checklist

### React App
- [ ] Environment variables configured (`.env.production`, `.env.development`)
- [ ] API config uses relative paths for production
- [ ] Build command works (`npm run build`)
- [ ] Build output goes to `dist/` folder

### Django Backend
- [ ] Static files directory configured
- [ ] Templates directory includes static folder
- [ ] CORS settings allow frontend origin (dev) or same-origin (prod)
- [ ] URL routing serves React SPA for non-API routes
- [ ] Django Channels configured for WebSockets
- [ ] API endpoints return JSON (not HTML)
- [ ] `collectstatic` works correctly

### Deployment
- [ ] Build script copies React to Django static folder
- [ ] Django serves index.html for all non-API routes
- [ ] API endpoints accessible at `/api/*`
- [ ] WebSocket endpoints accessible at `/ws/*`
- [ ] Static assets load correctly
- [ ] React Router navigation works (no 404s)

## 🔍 Testing Production Build Locally

1. **Build React app:**
```bash
npm run build
```

2. **Copy to Django:**
```bash
cp -r dist/* /path/to/django/static/
```

3. **Collect static:**
```bash
python manage.py collectstatic --noinput
```

4. **Run Django with static files:**
```bash
python manage.py runserver --insecure  # Serves static in DEBUG=False
```

5. **Test in browser:**
```
http://localhost:8000/          # Should load React app
http://localhost:8000/api/...   # Should return JSON
ws://localhost:8000/ws/...      # Should connect WebSocket
```

## 🐛 Common Issues

### React Router 404s
**Problem:** Refreshing on `/about` gives 404
**Solution:** Django catch-all route must serve `index.html` for all non-API paths

### Static Files Not Loading
**Problem:** CSS/JS files return 404
**Solution:** Run `collectstatic` and verify `STATIC_URL` is correct

### CORS Errors
**Problem:** API calls blocked by CORS
**Solution:** Add frontend origin to `CORS_ALLOWED_ORIGINS` in Django settings

### WebSocket Connection Failed
**Problem:** WebSocket can't connect
**Solution:** Check protocol (ws:// vs wss://), verify Daphne is running, check ASGI config

### API Returns HTML Instead of JSON
**Problem:** API endpoints serve React app
**Solution:** Ensure API paths are excluded in URL routing pattern: `(?!api|admin|static|ws)`

## 📚 Additional Resources

- [Django Static Files](https://docs.djangoproject.com/en/5.0/howto/static-files/)
- [Django Channels](https://channels.readthedocs.io/)
- [Vite Build](https://vitejs.dev/guide/build.html)
- [WhiteNoise (Static Files)](http://whitenoise.evans.io/)

---

**Summary:** Build React → Copy to Django static → Configure URLs → Deploy! 🚀
