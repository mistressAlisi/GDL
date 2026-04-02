# Quick Test Guide - Authentication Fix

## Test the Fix

### 1. Test Root App (Integrated Version)
If your main entry point uses `/App.tsx`:

```bash
# Start the app
npm run dev
# or
vite

# Expected behavior:
✅ App loads without "useAuth must be used within AuthProvider" error
✅ Console shows: Guest user created automatically
✅ WebSocket connects successfully
✅ SportsLotto features are accessible
✅ LocalStorage contains 'betany_user' with guest data
```

### 2. Test Standalone SportsLotto
If using the sportslotto standalone app:

```bash
cd sportslotto
npm run dev

# Expected behavior:
✅ App loads at http://localhost:5174
✅ Guest user auto-logged in
✅ No redirect to /login
✅ All betting features accessible
✅ Can navigate to /login to upgrade account
```

### 3. Test Guest → Login → Logout Flow

1. **Initial Load (Guest)**
   - Open app → Guest user created
   - Check localStorage: `betany_user` has `id: "guest_[timestamp]"`
   - WebSocket connected

2. **Login (Upgrade)**
   - Navigate to login (if standalone) or click login button
   - Enter credentials: any username/password
   - After login: User upgraded to registered account
   - Check localStorage: `id: "user_[timestamp]"`, `balance: 1250.00`

3. **Logout (Back to Guest)**
   - Click logout button
   - New guest account created (different ID)
   - Check localStorage: New `guest_[timestamp]` ID
   - WebSocket reconnected

### 4. Test Session Persistence

```bash
# Test registered user persistence:
1. Login with username/password
2. Refresh page (F5)
3. User should still be logged in (not guest)
4. Balance and username preserved

# Test guest persistence:
1. First visit → Guest created
2. Close tab
3. Reopen → Same guest session restored (same ID)
```

### 5. Console Checks

Open browser DevTools → Console

**Expected (Good):**
```
✅ WebSocket connected
✅ User authenticated: Guest
✅ Auth context initialized
```

**Not Expected (Bad):**
```
❌ useAuth must be used within AuthProvider
❌ Cannot read properties of undefined
❌ WebSocket connection failed
❌ Context provider missing
```

### 6. localStorage Inspection

Open DevTools → Application → Local Storage

**Expected Entry:**
```json
Key: "betany_user"
Value: {
  "id": "guest_1234567890" or "user_1234567890",
  "username": "Guest" or "YourUsername",
  "email": "guest@betany.com" or "user@example.com",
  "balance": 0.00 or 1250.00
}
```

### 7. Network Tab (WebSocket)

Open DevTools → Network → WS filter

**Expected:**
```
✅ WebSocket connection established
✅ Status: 101 Switching Protocols (or Connected)
✅ Messages being sent/received
```

## Common Issues & Solutions

### Issue: Still getting "useAuth must be used within AuthProvider"

**Solution:**
1. Clear browser cache and localStorage
2. Restart dev server
3. Check that `/App.tsx` has AuthProvider import
4. Verify you're using the correct entry point

### Issue: WebSocket not connecting

**Solution:**
1. Check if WebSocket service URL is correct
2. Ensure backend is running (if not using mocks)
3. Check console for WebSocket errors
4. Verify auth token is passed correctly

### Issue: Guest user not created

**Solution:**
1. Check browser console for errors
2. Clear localStorage: `localStorage.clear()`
3. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. Check AuthContext.tsx has guest auto-login code

### Issue: Login doesn't upgrade from guest

**Solution:**
1. Check login API endpoint (currently mock)
2. Verify form submission works
3. Check if new user replaces guest in localStorage
4. Console log should show new user data

## Test Scenarios Checklist

- [ ] Fresh install → Guest created
- [ ] Guest can place bets
- [ ] Guest can view tickets
- [ ] Guest can access all features
- [ ] Login works (guest → registered)
- [ ] Register works (guest → registered)
- [ ] Logout works (registered → new guest)
- [ ] Session persists on refresh
- [ ] Multiple tabs share same session
- [ ] WebSocket connects for guests
- [ ] WebSocket connects for registered users
- [ ] No console errors
- [ ] No redirect loops
- [ ] ProtectedRoute doesn't block guests
- [ ] Theme changes persist
- [ ] Balance updates work

## Browser Compatibility

Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari
- [ ] Mobile Chrome (Android)
- [ ] Mobile Safari (iOS)

## Performance Checks

- [ ] Initial load time < 2 seconds
- [ ] Guest creation < 100ms
- [ ] WebSocket connects < 1 second
- [ ] No memory leaks on logout/login cycle
- [ ] localStorage size reasonable (< 5MB)

## Ready for Django Integration?

Once all tests pass, you're ready to:
1. Replace mock login with Django API calls
2. Replace mock guest creation with backend endpoint
3. Add JWT/session token management
4. Implement WebSocket authentication
5. Add proper error handling for API failures

## Quick Commands Reference

```bash
# Clear localStorage (browser console)
localStorage.clear()

# View current user (browser console)
console.log(JSON.parse(localStorage.getItem('betany_user')))

# Check if user exists
console.log(!!localStorage.getItem('betany_user'))

# Force new guest (browser console)
localStorage.removeItem('betany_user')
location.reload()

# Check WebSocket status (if exposed)
ticketWebSocket.isConnected()
```

## Success Criteria

✅ No authentication errors in console
✅ Guest users can access platform immediately
✅ Login/register flows work correctly
✅ WebSocket initializes properly for all users
✅ Session management works (persist/logout)
✅ No redirect loops or infinite loading
✅ All platform features accessible to guests
✅ Smooth transition from guest to registered user

## Need Help?

If issues persist:
1. Check `/AUTHENTICATION_ERROR_FIX.md` for detailed explanation
2. Verify all files in "Files Modified" section were updated
3. Ensure no cached builds (delete `node_modules/.vite` or `dist`)
4. Try in incognito/private window
5. Check for conflicting authentication code elsewhere

## Next Steps After Testing

Once verified working:
1. Document the auth flow in your team docs
2. Plan Django backend integration
3. Design guest-to-registered upgrade UX
4. Implement proper error handling
5. Add loading states for auth operations
6. Set up analytics for guest vs registered users
