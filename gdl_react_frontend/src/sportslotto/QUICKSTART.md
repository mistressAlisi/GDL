# SPORTSLOTTO - Quick Start Guide

## Installation

1. Navigate to the sportslotto directory:
```bash
cd sportslotto
```

2. Run the setup script:

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

## Running the Application

Start the development server:
```bash
npm run dev
```

The application will automatically open at: **http://localhost:5174**

## Application Flow

### 1. Main Menu
- Choose between **Custom Tickets** or **Quick Picks**
- Select a sport category (Tennis, US Sports, Soccer, NCAA Basketball)

### 2. Custom Tickets Mode
- Set your **STAKE** (bet amount)
- Choose number of **EVENTS** (games to include)
- Set target **WIN** amount
- Select **SPORT** from available options
- Choose **TIME FRAME** (24hrs, 48hrs, 1 week, All)
- Click **SUBMIT** to generate tickets

### 3. Quick Picks Mode
- Set **TICKET COUNT** (how many tickets to generate)
- Set **RISK AMOUNT** (total amount to bet)
- Select **SPORT**
- Click **GENERATE** to create tickets

### 4. Tickets Display
- View all generated tickets in a grid
- **Click on a ticket** to flip and reveal details
- Use **RED button** (✕) to reject a ticket
- Use **GREEN button** (✓) to accept a ticket
- Click **DETAILS** button to see full event list

### 5. Ticket Details Panel
- Shows complete list of all events/games
- Displays matchups, leagues, and dates
- Actions: **Reject**, **Close**, or **Accept!**

## Features

✨ **Glass-morphism Design** - Premium frosted glass effects
🏆 **Multiple Sports** - Tennis, Soccer, Basketball, and more
🎫 **Custom Betting** - Full control over stake and selections
⚡ **Quick Picks** - Automated ticket generation
🔄 **3D Flip Cards** - Interactive ticket reveals
📊 **Balance Tracking** - Real-time balance display
🎨 **Golden Gradients** - Luxurious color scheme

## Next Steps

- Integrate with existing cashier for real transactions
- Add backend API for live sports data
- Implement ticket history and tracking
- Add user authentication and profiles

## Port Configuration

The SPORTSLOTTO app runs on port **5174** (different from the cashier on 5173) so both can run simultaneously.

## Support

For issues or questions, refer to the full README.md in this directory.
