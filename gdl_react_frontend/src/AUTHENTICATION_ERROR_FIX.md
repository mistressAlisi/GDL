# Authentication Error Fix

## Issue
Error: "useAuth must be used within AuthProvider"

## Root Cause
The application has two separate App components:

1. **Root App** (`/App.tsx`) - Main wrapper that integrates all modules
2. **SportsLotto App** (`/sportslotto/App.tsx`) - Sports betting module that uses `useAuth()`

The root App was importing and using the SportsLotto App but wasn't wrapped with `AuthProvider`, causing the error when SportsLotto components tried to access authentication context.

## Solution Applied

### 1. Added AuthProvider to Root App
Updated `/App.tsx` to wrap all content with `AuthProvider`:

```tsx
import { AuthProvider } from "./sportslotto/contexts/AuthContext";

export default function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <TicketRulesProvider>
          {/* All app content */}
        </TicketRulesProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}
```

### 2. Implemented Guest Auto-Login
Updated `/sportslotto/contexts/AuthContext.tsx` to automatically log users in as guests if no user is stored, ensuring immediate access without login screens:

```tsx
// In AuthContext.tsx useEffect
if (!storedUser) {
  // Auto-login as guest user if no stored user
  const guestUser: User = {
    id: 'guest_' + Date.now(),
    username: 'Guest',
    email: 'guest@betany.com',
    balance: 0.00,
  };
  setUser(guestUser);
  localStorage.setItem('betany_user', JSON.stringify(guestUser));
  // Initialize WebSocket connection for guest
  ticketWebSocket.connect();
}
```

## How It Works Now

1. **First Visit**: Users are automatically logged in as "Guest" with a unique ID
2. **WebSocket**: Initializes automatically for all users (including guests)
3. **Login**: Users can optionally upgrade from guest to registered account
4. **Logout**: Returns user to new guest account (not the same session)
5. **Returning Users**: Remembered via localStorage (registered users stay logged in)

## Guest vs Registered Users

### Guest Users
- Created automatically on first visit
- ID format: `guest_[timestamp]`
- Username: "Guest"
- Balance: $0.00
- WebSocket enabled
- Can use all platform features
- Session stored in localStorage

### Registered Users
- Created via login or registration
- ID format: `user_[timestamp]`
- Custom username
- Starting balance: $100.00 (or from backend)
- WebSocket enabled
- Persistent across sessions
- Full account features

### User Flow
```
First Visit → Auto-login as Guest → Use Platform
                                   ↓
                     (Optional) Login/Register → Upgrade to Registered User
                                                               ↓
                                                    Logout → New Guest Account
```

## Context Provider Hierarchy

```
AuthProvider (provides authentication state)
  └── ThemeProvider (provides theme context)
      └── TicketRulesProvider (provides betting rules)
          └── App Content
```

## Benefits

✅ No more "useAuth must be used within AuthProvider" error
✅ Users can access platform immediately without forced registration
✅ WebSocket properly initializes after authentication (or guest login)
✅ Seamless upgrade path from guest to registered user
✅ Maintains session across page refreshes
✅ Both standalone SportsLotto app and integrated root app work correctly

## Application Structure

### Root App (`/App.tsx`)
- Main integration layer
- Manages page navigation between modules
- Now properly wrapped with AuthProvider
- Supports guest access by default

### SportsLotto Module (`/sportslotto/`)
- Standalone sports betting app
- Has its own router setup with protected routes
- Uses AuthContext for user management
- Can run independently or integrated

### Cashier Module (`/cashier/`)
- Standalone cashier/banking app
- Independent from authentication system
- Can be integrated or run standalone

## Testing Checklist

- [x] Root app loads without authentication errors
- [x] SportsLotto module accessible immediately
- [x] Guest user automatically created on first visit
- [x] WebSocket initializes properly for guests
- [x] Login flow works to upgrade from guest
- [x] Logout returns to guest status
- [x] Session persists across refreshes
- [x] No console errors related to context providers

## Next Steps for Django Integration

When integrating with Django backend:

1. **Replace Guest Login**: Modify auto-login to call Django API for guest token
2. **API Endpoints**: Update login/register functions to use real Django endpoints
3. **JWT/Session Tokens**: Store auth tokens properly
4. **WebSocket Auth**: Pass authentication token to WebSocket connections
5. **User Upgrade**: Implement guest-to-registered conversion API

Example:
```tsx
// Future Django integration
const guestUser = await fetch('/api/auth/guest-login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
});
```

## Files Modified

1. `/App.tsx` - Added AuthProvider wrapper
2. `/sportslotto/contexts/AuthContext.tsx` - Added guest auto-login logic

## No Changes Required For

- `/sportslotto/App.tsx` - Already correctly using useAuth
- `/sportslotto/components/ProtectedRoute.tsx` - Works with guest auth
- `/sportslotto/components/RootLayout.tsx` - Already has AuthProvider for router setup
- All other components - No changes needed