/**
 * API Configuration for BETANY LOTTO Backend
 * Django 6 + Channels
 * 
 * DEPLOYMENT MODEL:
 * - React app is built separately (npm run build)
 * - Build output is copied to Django's static/ folder
 * - Django serves the static React app
 * - React makes API calls back to Django
 * 
 * SETUP INSTRUCTIONS:
 * 1. For development: Use full URLs (http://localhost:8000)
 * 2. For production: Use relative URLs (/api, /ws) since served from same domain
 * 3. Configure via environment variables (.env.development, .env.production)
 */

export const API_CONFIG = {
  // Use environment variables with fallbacks
  // Development: http://localhost:8000
  // Production: '' (relative, same domain)
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '',

  // API Endpoints
  ENDPOINTS: {
    // Account/Auth
    LOGIN: '/api/v1/account/login',
    REGISTER: '/api/v1/account/register/',
    LOGOUT: '/api/v1/account/logout/',

    // Sports configuration
    SPORTS_CONFIG: '/api/v1/sports/config/',
    SPORTS_LIST: '/api/v1/sports/',
    SPORT_SETTINGS: '/api/v1/sports/:sportId/settings/',

    // Ticket generation (REST fallback)
    GENERATE_TICKET: '/api/v1/tickets/generate/',
    VALIDATE_TICKET: '/api/v1/tickets/validate/',

    // Tables and data
    RECENT_TICKETS: '/api/v1/tickets/recent/',
    USER_TICKETS: '/api/v1/tickets/user/',
    LEADERBOARD: '/api/v1/leaderboard/',
    STATISTICS: '/api/v1/statistics/',

    // Ticket rules
    TICKET_RULES: '/api/v1/tickets/rules/',
  },

  // WebSocket Endpoints (Django Channels consumers)
  WS_ENDPOINTS: {
    // Custom form ticket generation (normal betting flow)
    STREAM_TICKETS: '/stream_tickets',

    // Quick picks ticket generation (Lucky Pick button flow)
    STREAM_QUICKPICKS: '/stream_quickpicks',
  },

  // Request timeout (ms)
  TIMEOUT: 30000,

  // Mock mode (automatically disabled in production build)
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
export const buildWsUrl = (endpoint: string) => {
  const baseUrl = API_CONFIG.BASE_URL;

  // Construct WebSocket URL based on current page protocol
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;

  // If BASE_URL is absolute (development), use that host
  if (baseUrl.startsWith('http://') || baseUrl.startsWith('https://')) {
    const url = new URL(baseUrl);
    const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${url.host}${endpoint}`;
  }

  // Otherwise use current page host (production - same domain)
  return `${protocol}//${host}${endpoint}`;
};