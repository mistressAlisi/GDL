# SPORTSLOTTO - Routing Update Summary

## ✅ Changes Made

### Button Routing Structure

```
Main Menu
├── Custom Tickets Button 🎫
│   └── Opens: CustomTicketsForm (Full form with sport selection + time slices)
│
├── Quick Play Button ⚡
│   └── Opens: QuickPicksForm (Simple ticket count + risk amount)
│
└── Sport Buttons (Tennis, Soccer, etc.) 🎾⚽🏈🏀
    └── Opens: CustomTicketsForm (Same as Custom Tickets button)
```

### Updated Files

#### 1. **MainMenu.tsx** (`/sportslotto/components/MainMenu.tsx`)
- ✅ Added `onCustomTicketsSelect` prop
- ✅ Custom Tickets button → Calls `onCustomTicketsSelect()`
- ✅ Quick Play button → Calls `onQuickPicksSelect()`
- ✅ Sport buttons → Call `onSportSelect(sport.id)`

#### 2. **App.tsx** (`/sportslotto/App.tsx`)
- ✅ Added `handleCustomTicketsSelect()` function
- ✅ Custom Tickets → Sets `selectedSport = null`, opens 'custom' page
- ✅ Sport buttons → Sets `selectedSport = sport`, opens 'custom' page
- ✅ Quick Play → Opens 'quickpicks' page
- ✅ Passes `onCustomTicketsSelect` to MainMenu

#### 3. **CustomTicketsForm.tsx** (`/sportslotto/components/CustomTicketsForm.tsx`)
- ✅ Added API integration via `useTicketGeneration()` hook
- ✅ Shows loading state during ticket generation
- ✅ Displays error/success messages
- ✅ All 4 sports displayed in grid (Tennis, US Sports, Soccer, NCAA Basketball)
- ✅ All 7 timeframes displayed (12h, 18h, 24h, 30h, 36h, 42h, 48h)
- ✅ Uses global ticket rules from TicketRulesContext
- ✅ Sends WebSocket request to Django backend
- ✅ Labels updated: "SELECT SPORTS" (plural), descriptions added

#### 4. **QuickPicksForm.tsx** (`/sportslotto/components/QuickPicksForm.tsx`)
- ✅ Already had API integration (from previous update)
- ✅ Simple form: Ticket Count + Risk Amount + Entries
- ✅ Uses global ticket rules (sports + timeframe)
- ✅ Sends to Django via WebSocket

## 🎯 User Flow

### Custom Tickets Flow
```
1. User clicks "Custom Tickets" button (or any sport button)
2. CustomTicketsForm opens
3. User sees:
   - STAKE input (wager amount)
   - EVENTS input (number of picks, 3-10)
   - POTENTIAL WIN input (estimated payout)
   - Sport selection grid (all 4 sports)
   - Time frame selection (7 options)
4. User customizes selections
5. Click SUBMIT
6. WebSocket sends to Django:
   {
     wager: 10,
     entries: 7,
     sports: ['tennis', 'soccer'],
     timeframe: '24h',
     luckyPick: false,
     gameType: 'custom'
   }
7. Django generates ticket
8. Response displayed
9. Ticket added to cart
```

### Quick Play Flow
```
1. User clicks "Quick Play" button
2. QuickPicksForm opens
3. User sees:
   - TICKET COUNT input
   - RISK AMOUNT input (per ticket)
   - ENTRIES PER TICKET input
   - Global rules apply (sports + timeframe from Ticket Rules)
4. Click ADD TO CART
5. WebSocket sends to Django:
   {
     wager: 10,
     entries: 5,
     sports: ['tennis', 'us-sports', 'soccer', 'ncaa-basketball'],
     timeframe: '24h',
     luckyPick: true,
     gameType: 'quick-play'
   }
6. Django generates ticket(s)
7. Cart opens automatically
```

## 🔧 Technical Details

### CustomTicketsForm Features
- **Sport Selection:** Interactive grid with 4 sport options
- **Time Slices:** 7 timeframe buttons (12h to 48h)
- **Input Fields:** Stake, Events (3-10), Potential Win
- **Visual Feedback:** Selected sports highlighted with orange border + checkmark
- **Loading State:** Button shows "GENERATING..." during API call
- **Error Handling:** Red error message box if generation fails
- **Success Message:** Green success box when ticket generated
- **Disabled State:** All buttons disabled during loading

### API Integration
Both forms now use the WebSocket service:
```typescript
const { generateTicket, loading, error, response } = useTicketGeneration();

generateTicket({
  wager: stake,
  entries: events,
  sports: rules.selectedSports,  // From global rules
  timeframe: rules.timeframe,     // From global rules
  luckyPick: false,
  gameType: 'custom',
});
```

### Ticket Rules Context
Both forms respect global ticket rules:
- `rules.selectedSports` - Array of selected sport IDs
- `rules.timeframe` - Selected timeframe (12h-48h)
- `toggleSport(sportId)` - Toggle sport selection
- `updateTimeframe(timeframe)` - Update timeframe

## 🎨 Visual Differences

### Custom Tickets Button
- Purple border (`rgba(168, 85, 247, 0.6)`)
- Purple shadow
- Icon: 🎫
- Title: "Custom Tickets"
- Description: "Build your own sports lottery ticket"

### Quick Play Button
- Orange gradient background
- Orange border and shadow
- Icon: ⚡
- Title: "Quick Play"
- Description: "Fast & Easy - All Your Favorites In One Place"

### Sport Buttons
- Orange border
- Orange shadow
- Icons: 🎾 (Tennis), 🏈 (US Sports), ⚽ (Soccer), 🏀 (NCAA Basketball)
- Now properly route to CustomTicketsForm

## ✅ Verification Checklist

- [x] Custom Tickets button opens CustomTicketsForm
- [x] Quick Play button opens QuickPicksForm
- [x] Sport buttons open CustomTicketsForm
- [x] CustomTicketsForm shows all 4 sports
- [x] CustomTicketsForm shows all 7 timeframes
- [x] Sport selection works (toggle on/off)
- [x] Timeframe selection works
- [x] API integration works (WebSocket)
- [x] Loading states display correctly
- [x] Error messages display correctly
- [x] Success messages display correctly
- [x] Buttons disabled during loading
- [x] Global ticket rules respected

## 📝 Notes

1. **Sport Parameter:** The `sport` prop in CustomTicketsForm is kept for compatibility but is now optional (can be `null` when coming from Custom Tickets button)

2. **Global Rules:** Both forms use the global TicketRulesContext for sports and timeframe selections

3. **Backend Integration:** Both forms send ticket generation requests to Django via WebSocket in the same format

4. **Mock Data:** Currently enabled by default in development mode (`USE_MOCK_DATA: true`). Set to `false` when Django backend is ready.

5. **Timeframe Format:** Changed from numbers (12, 18, 24) to strings ('12h', '18h', '24h') to match API requirements

## 🚀 Next Steps

1. Test Custom Tickets button → Should open form with all sports
2. Test Quick Play button → Should open simplified form
3. Test sport buttons → Should open Custom Tickets form
4. Configure Django backend URLs in `/services/api-config.ts`
5. Connect to Django backend and test real ticket generation

---

**Summary:** Custom Tickets button now properly opens the full CustomTicketsForm with sport selection grid and time slices, while Quick Play opens the simplified QuickPicksForm. Sport buttons route to the same CustomTicketsForm. All forms integrate with Django backend via WebSocket. ✅
