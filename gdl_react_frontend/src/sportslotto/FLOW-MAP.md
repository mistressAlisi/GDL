# SPORTSLOTTO Application Flow Map

## Visual Navigation Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        BALANCE BAR (Always Visible)              │
│  BALANCE: $1,250.00 | PENDING: $450.00 | FREE PLAY: $50.00 |   │
│  AVAIL.: $850.00                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          MAIN MENU                               │
│                      [SPORTSLOTTO Logo]                          │
│                                                                   │
│  ┌────────────────────┐         ┌────────────────────┐          │
│  │  Custom Tickets    │         │   Quick Picks      │          │
│  │  🎫                │         │   ⚡                │          │
│  │  [Purple/Pink]     │         │   [Blue/Cyan]      │          │
│  └────────────────────┘         └────────────────────┘          │
│                                                                   │
│  Sport Categories:                                               │
│  [🎾 Tennis] [🏈 US Sports] [⚽ Soccer] [🏀 NCAA Basketball]    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         ↓                                    ↓
    [Custom]                            [Quick Picks]
         ↓                                    ↓
┌─────────────────────────┐    ┌──────────────────────────┐
│  CUSTOM TICKETS FORM    │    │  QUICK PICKS FORM        │
│                         │    │                          │
│  • Stake Input          │    │  • Ticket Count Input    │
│  • Events Input         │    │  • Risk Amount Input     │
│  • Win Input            │    │  • Per Ticket Display    │
│  • Sport Selection (6)  │    │  • Potential Win Display │
│  • Time Frame (4)       │    │  • Sport Selection (6)   │
│                         │    │                          │
│  [Reset][Cancel][Submit]│    │  [Reset][Cancel][Generate]│
└─────────────────────────┘    └──────────────────────────┘
         ↓                                    ↓
         └──────────────┬─────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                        TICKETS GRID                              │
│                                                                   │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐             │
│  │Ticket│  │Ticket│  │Ticket│  │Ticket│  │Ticket│             │
│  │ 2499 │  │ 2428 │  │ 2524 │  │ 2454 │  │ 2431 │             │
│  │      │  │      │  │      │  │      │  │      │             │
│  │[✕][✓]│  │[✕][✓]│  │[✕][✓]│  │[✕][✓]│  │[✕][✓]│             │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘             │
│    ↑ Click to Flip                           ↑ Click Details    │
│                                                                   │
│  [← Back to Menu]                                                │
└─────────────────────────────────────────────────────────────────┘
         ↓ (Click on ticket)              ↓ (Click DETAILS button)
         ↓                                ↓
┌────────────────┐              ┌─────────────────────────────────┐
│  FLIPPED CARD  │              │   TICKET DETAILS PANEL          │
│                │              │   (Modal Overlay)               │
│   TICKET WINS  │              │                                 │
│      2542      │              │  Risking 1 returns 2409:        │
│                │              │  Across 7 events                │
│  CLICK TO      │              │                                 │
│  REVEAL!       │              │  ┌─────────────────────────┐   │
│                │              │  │ Dinamo Zagreb vs        │   │
│   [✕]  [✓]     │              │  │ FC Midtjylland          │   │
└────────────────┘              │  │ UEFA Europa League      │   │
                                │  └─────────────────────────┘   │
                                │  ┌─────────────────────────┐   │
                                │  │ Metaloglobus vs         │   │
                                │  │ CFR Cluj                │   │
                                │  │ Romania Liga 1          │   │
                                │  └─────────────────────────┘   │
                                │  ... (5 more events)            │
                                │                                 │
                                │  [Reject] [Close] [Accept!]    │
                                └─────────────────────────────────┘
```

## State Flow Diagram

```
                           App State
                               │
                ┌──────────────┼──────────────┐
                ↓              ↓              ↓
          currentPage      tickets        balance
                │              │              │
    ┌───────────┼────────┐     │     ┌────────┼────────┐
    │           │        │     │     │        │        │
  'menu'    'custom' 'quickpicks' │ balance pending freePlay
                │        │     │     │
                ↓        ↓     ↓     ↓
          CustomForm QuickForm Ticket Balance
                │        │    Array    Data
                ↓        ↓     │
          handleSubmit    │    ↓
                │         │  TicketCard
                └────┬────┘    │
                     ↓         ↓
              generateTickets  │
                     │         │
                     ├─────────┤
                     ↓         ↓
                setTickets   onFlip
                     │         │
                     ↓         ↓
              'tickets'    flipped: true/false
                 page
```

## Component Hierarchy

```
App.tsx
├── Balance Bar Component (inline)
│
├── MainMenu.tsx
│   ├── Game Mode Cards
│   │   ├── Custom Tickets Button
│   │   └── Quick Picks Button
│   └── Sport Category Grid
│       └── Sport Buttons (4)
│
├── CustomTicketsForm.tsx
│   ├── Input Fields (Stake, Events, Win)
│   ├── Sport Selection Grid (6 sports)
│   ├── Time Frame Buttons (4 options)
│   └── Action Buttons (Reset, Cancel, Submit)
│
├── QuickPicksForm.tsx
│   ├── Input Fields (Ticket Count, Risk Amount)
│   ├── Calculation Display
│   ├── Sport Selection Grid (6 sports)
│   └── Action Buttons (Reset, Cancel, Generate)
│
├── TicketsGrid.tsx
│   ├── Grid Container
│   └── TicketCard (multiple)
│       ├── Front Face
│       │   ├── Ticket Info
│       │   ├── Details Button
│       │   └── Action Buttons (✕, ✓)
│       └── Back Face
│           ├── Win Amount
│           └── Action Buttons (✕, ✓)
│
└── TicketDetailsPanel.tsx
    ├── Modal Overlay
    ├── Header (with close button)
    ├── Ticket Summary
    ├── Events List (scrollable)
    │   └── Event Card (multiple)
    │       ├── Teams
    │       ├── League
    │       └── Date/Time
    └── Footer Actions (Reject, Close, Accept!)
```

## Data Flow

```
User Action → Component Handler → State Update → Re-render

Examples:

1. Custom Ticket Creation:
   User fills form → Clicks Submit → handleCustomSubmit()
   → generateCustomTickets() → setTickets() → Navigate to tickets page

2. Ticket Flip:
   User clicks ticket → onFlip(ticketId) → setTickets(map with flip toggle)
   → Ticket re-renders with flipped state

3. Show Details:
   User clicks Details → handleShowDetails(ticket)
   → setSelectedTicket() → setShowDetails(true)
   → TicketDetailsPanel renders

4. Balance Update:
   Ticket accepted → handleTicketSelect('accept')
   → setBalance() → Balance bar updates
```

## Page Navigation Map

```
         ┌──────────┐
         │   menu   │ ← Initial page
         └────┬─────┘
              │
    ┌─────────┴──────────┐
    ↓                    ↓
┌─────────┐        ┌──────────┐
│ custom  │        │quickpicks│
└────┬────┘        └────┬─────┘
     │                  │
     └────────┬─────────┘
              ↓
         ┌─────────┐
         │ tickets │
         └─────────┘
              │
         [Details Modal]
         (overlay - not a page)
```

## Ticket States

```
Ticket Object:
{
  id: string
  type: 'pending' | 'win' | 'loss'
  amount: number
  potential: number
  events: Event[]
  sport: Sport
  timestamp: Date
  flipped: boolean ← Controls flip animation
}

Visual States:
• Pending:  Purple border, "1 RETURNS: XXXX", Shows details button
• Win:      Gold border, "TICKET WINS", Shows amount
• Loss:     Blue border (future), Shows loss amount
• Flipped:  Shows back face with different content
```

## Interaction Flow

```
1. Landing
   MainMenu → Click "Custom Tickets" → Navigate to Custom Form

2. Create Custom Ticket
   CustomForm → Fill inputs → Select sport → Choose time frame
   → Click Submit → Generate ticket → Navigate to Tickets Grid

3. Create Quick Picks
   QuickPicksForm → Set count & amount → Select sport
   → Click Generate → Generate multiple tickets → Navigate to Tickets Grid

4. View Tickets
   TicketsGrid → Display all tickets in grid → Hover effects

5. Flip Ticket
   Click on ticket → Toggle flipped state → Smooth 3D rotation

6. View Details
   Click Details button → Open modal → Show all events → Scroll to view

7. Accept/Reject
   Click ✓ or ✕ → Process selection → Update balance (future)
   → Remove/update ticket (future)
```

## Color Coding

```
• Golden (#ffd700)     → Branding, Balance, Wins
• Purple (#a855f7)     → Custom Tickets, Pending state
• Blue (#3b82f6)       → Quick Picks, Default borders
• Cyan (#06b6d4)       → Accents, Secondary info
• Pink (#ec4899)       → Accents with purple
• Green (#10b981)      → Accept buttons, Free Play
• Red (#ef4444)        → Reject buttons, Warnings
• Gray (#6b7280)       → Secondary text, Cancel buttons
```

This map provides a complete visual reference for understanding how the entire SPORTSLOTTO application flows and connects! 🗺️
