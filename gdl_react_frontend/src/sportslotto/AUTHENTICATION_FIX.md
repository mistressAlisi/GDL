# Authentication & WebSocket Fix

## Problem
The WebSocket service was automatically initializing when the application loaded, **before** users logged in. This violates the requirement that WebSocket connections should only be established after successful authentication.

## Solution
Implemented a complete authentication system with proper WebSocket lifecycle management.

### 1. Created AuthContext (`/sportslotto/contexts/AuthContext.tsx`)
- Manages user authentication state
- Handles login, logout, and registration
- **Initializes WebSocket connection ONLY after successful login/registration**
- **Disconnects WebSocket on logout**
- Persists authentication state in localStorage
- Provides authentication status to all components

### 2. Updated WebSocket Service (`/services/websocket-service.ts`)
- **Removed automatic connection from constructor**
- Added public `connect()` method that must be called manually
- Added `disconnect()` method for cleanup
- Added `isConnected` flag to prevent duplicate connections
- WebSocket now only connects when explicitly called by AuthContext after login

### 3. Updated RootLayout (`/sportslotto/components/RootLayout.tsx`)
- Wraps app in `AuthProvider` to provide authentication context
- Ensures all routes have access to authentication state

### 4. Updated Login Page (`/sportslotto/pages/Login.tsx`)
- Uses `useAuth()` hook to access login function
- Calls `login()` which automatically initializes WebSocket on success
- Added error handling and loading states
- Shows error messages to users

### 5. Updated Register Page (`/sportslotto/pages/Register.tsx`)
- Uses `useAuth()` hook to access register function
- Calls `register()` which automatically initializes WebSocket on success
- Added error handling and loading states
- Shows error messages to users

### 6. Updated Main App (`/sportslotto/App.tsx`)
- Uses `useAuth()` hook to access logout function
- Logout properly disconnects WebSocket via AuthContext

### 7. Created ProtectedRoute Component (`/sportslotto/components/ProtectedRoute.tsx`)
- Protects routes that require authentication
- Redirects unauthenticated users to login page
- Shows loading state while checking authentication

### 8. Updated Routes (`/sportslotto/routes.tsx`)
- Wrapped main app route with `ProtectedRoute`
- Public routes (login, register, recovery) remain unprotected

## WebSocket Connection Flow

### Before Login
1. User opens app → Not authenticated → Redirected to /login
2. **No WebSocket connection initiated**

### During Login
1. User enters credentials → Clicks "Login"
2. `AuthContext.login()` is called
3. Mock authentication succeeds (TODO: replace with Django API call)
4. User data is stored in state and localStorage
5. **WebSocket connection is initialized via `ticketWebSocket.connect()`**
6. User is redirected to main app

### During App Use
1. User is authenticated
2. WebSocket is connected and available for real-time features
3. Ticket generation and live updates work via WebSocket

### During Logout
1. User clicks logout in sidebar
2. `AuthContext.logout()` is called
3. User data is cleared from state and localStorage
4. **WebSocket connection is disconnected via `ticketWebSocket.disconnect()`**
5. User is redirected to login page

## Session Persistence
- Authentication state is saved in localStorage as `betany_user`
- On app reload, AuthContext checks localStorage
- If valid session found, user is automatically logged in
- **WebSocket is automatically reconnected for existing sessions**

## Development Mode
- `API_CONFIG.USE_MOCK_DATA = true` in development
- WebSocket uses mock data instead of real connections
- Prevents connection errors during development without Django backend

## Production Integration (TODO)
When integrating with Django backend:

1. Replace mock login in `AuthContext.login()`:
```typescript
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password }),
});
const data = await response.json();
```

2. Replace mock register in `AuthContext.register()`:
```typescript
const response = await fetch('/api/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, email, password }),
});
const data = await response.json();
```

3. Add logout endpoint call in `AuthContext.logout()`:
```typescript
await fetch('/api/auth/logout/', { method: 'POST' });
```

4. Store JWT tokens from Django responses
5. Include tokens in WebSocket connection and API requests
6. Implement token refresh logic

## Testing
1. Open app → Should redirect to /login
2. Login with any credentials → Should connect to app and initialize WebSocket
3. Use app features → WebSocket should be available
4. Logout → WebSocket should disconnect, redirect to /login
5. Reload page while logged in → Should maintain session and reconnect WebSocket

## Files Modified
- `/sportslotto/contexts/AuthContext.tsx` (NEW)
- `/sportslotto/components/ProtectedRoute.tsx` (NEW)
- `/sportslotto/components/RootLayout.tsx`
- `/sportslotto/pages/Login.tsx`
- `/sportslotto/pages/Register.tsx`
- `/sportslotto/App.tsx`
- `/sportslotto/routes.tsx`
- `/services/websocket-service.ts`

## Key Benefits
✅ WebSocket only connects after authentication
✅ Proper connection cleanup on logout
✅ Session persistence across page reloads
✅ Protected routes prevent unauthorized access
✅ Error handling and user feedback
✅ Ready for Django backend integration
