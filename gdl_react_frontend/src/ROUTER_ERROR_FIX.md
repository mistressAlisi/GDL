# Router Context Error Fix

## Problem
Error: `useNavigate() may be used only in the context of a <Router> component.`

## Root Cause
The `/sportslotto/App.tsx` component was importing and calling `useNavigate()` from `react-router`, but:
1. The hook was never actually used in the component (assigned but not called)
2. The main `/App.tsx` does not use React Router - it uses state management for navigation
3. When `/sportslotto/App.tsx` is rendered from the main app, there's no Router context available

## Solution
Removed the unused `useNavigate` import and variable declaration from `/sportslotto/App.tsx`.

### Changes Made
**File: `/sportslotto/App.tsx`**
- ❌ Removed: `import { useNavigate } from "react-router";`
- ❌ Removed: `const navigate = useNavigate();`

## Architecture Notes

### Main App Structure
The main application (`/App.tsx`) uses:
- **State-based navigation** with `useState<Page>` 
- **Callback props** passed to child components for navigation
- **No React Router** - pages are conditionally rendered based on state

### SportsLotto Standalone Structure
The sportslotto folder has its own routing setup for standalone use:
- `/sportslotto/src/main.tsx` - Sets up RouterProvider
- `/sportslotto/routes.tsx` - Defines routes with createBrowserRouter
- `/sportslotto/pages/` - Login, Register, Recovery pages (not used in main app)

### Integration Approach
When `/sportslotto/App.tsx` is used within the main app:
- It receives navigation callbacks as props (`onBalanceClick`, `onCashierClick`, etc.)
- It uses internal state management for its own page navigation
- It does NOT use React Router hooks or components

## Other Files with React Router
These files still use React Router but are only loaded in standalone mode:
- `/sportslotto/components/ProtectedRoute.tsx` - Uses `useNavigate`
- `/sportslotto/pages/Login.tsx` - Uses `useNavigate`
- `/sportslotto/pages/Register.tsx` - Uses `useNavigate`
- `/sportslotto/pages/Recovery.tsx` - Uses `useNavigate`

These are safe because they're only rendered when the sportslotto app runs standalone with its own RouterProvider.

## Verification
✅ Main app uses state-based navigation
✅ SportsLotto app uses callbacks when embedded
✅ No Router context required in main app
✅ Standalone sportslotto app still has routing capability
✅ All useNavigate usage removed from embedded components

## Date
January 29, 2026
