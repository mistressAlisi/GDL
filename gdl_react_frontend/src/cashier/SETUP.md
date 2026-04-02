# 🚀 Cashier Component - Setup Guide

## 📋 Quick Setup for Vite

### 1. Install Dependencies

```bash
npm install
```

This will install:
- `react` & `react-dom` - React framework
- `motion` - Animation library (Framer Motion)
- `lucide-react` - Icon library
- `tailwindcss` & `@tailwindcss/vite` - Tailwind CSS v4
- `vite` - Build tool
- TypeScript & type definitions

### 2. File Structure

Your project should look like this:

```
react_cashier/
├── src/
│   ├── styles/
│   │   └── globals.css       # Tailwind CSS imports
│   ├── App.tsx               # Demo/Example usage
│   ├── Cashier.tsx           # Main component
│   └── main.tsx              # Entry point
├── index.html                # HTML template
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript config
├── tsconfig.node.json        # TypeScript config for Node
└── package.json              # Dependencies
```

### 3. Run the Development Server

```bash
npm run dev
```

This will start the Vite dev server at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` folder.

## 🎨 Styling

The component uses **Tailwind CSS v4** with the new `@import "tailwindcss"` syntax.

All styles are in `src/styles/globals.css`:
- Tailwind base imports
- Custom CSS variables
- Responsive font sizing
- Scrollbar styling
- Mobile optimizations

## 📦 What's Included

### ✅ Files Created

1. **src/Cashier.tsx** - Main component (copy from `/cashier/Cashier.tsx`)
2. **src/App.tsx** - Demo app (copy from `/cashier/App.tsx`)
3. **src/main.tsx** - Entry point ✅
4. **src/styles/globals.css** - Tailwind styles ✅
5. **index.html** - HTML template ✅
6. **vite.config.ts** - Vite config with Tailwind plugin ✅
7. **tsconfig.json** - TypeScript config ✅
8. **package.json** - Updated with all dependencies ✅

## 🔧 Copy These Files to Your Project

You need to copy these files from the `/cashier` folder to your `react_cashier/` project:

```bash
# Copy from /cashier to your react_cashier/src/ folder:
cp /cashier/Cashier.tsx react_cashier/src/
cp /cashier/App.tsx react_cashier/src/

# Copy config files to root:
cp /cashier/vite.config.ts react_cashier/
cp /cashier/tsconfig.json react_cashier/
cp /cashier/tsconfig.node.json react_cashier/
cp /cashier/package.json react_cashier/
cp /cashier/index.html react_cashier/

# Copy entry point and styles:
cp /cashier/src/main.tsx react_cashier/src/
cp /cashier/src/styles/globals.css react_cashier/src/styles/
```

## 🎯 Usage Example

```tsx
import React, { useState } from "react";
import { Cashier, Transaction } from "./Cashier";

function App() {
  const [balance, setBalance] = useState(142.75);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const handleDeposit = (transaction: Transaction) => {
    setBalance(prev => prev + transaction.amount);
    setTransactions(prev => [transaction, ...prev]);
  };

  const handleWithdraw = (transaction: Transaction) => {
    setBalance(prev => prev - transaction.amount);
    setTransactions(prev => [transaction, ...prev]);
  };

  return (
    <Cashier
      balance={balance}
      onDeposit={handleDeposit}
      onWithdraw={handleWithdraw}
      recentTransactions={transactions}
    />
  );
}

export default App;
```

## 🐛 Troubleshooting

### Issue: "Cannot find module '@/styles/globals.css'"
**Solution**: Make sure `vite.config.ts` has the path alias configured:
```ts
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
}
```

### Issue: Tailwind classes not working
**Solution**: 
1. Check that `@tailwindcss/vite` plugin is in `vite.config.ts`
2. Verify `globals.css` starts with `@import "tailwindcss";`
3. Restart the dev server

### Issue: Icons not showing
**Solution**: Make sure `lucide-react` is installed:
```bash
npm install lucide-react
```

### Issue: Animations not working
**Solution**: Install motion package:
```bash
npm install motion
```

## 📱 Mobile Testing

Test on mobile devices:
1. Get your local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Access from mobile: `http://YOUR_IP:5173`
3. Or use Vite's `--host` flag:
```bash
npm run dev -- --host
```

## 🎨 Customization

### Change Colors
Edit the gradients in `Cashier.tsx`:
- Deposit button: `from-green-400 to-emerald-500`
- Withdraw button: `from-orange-400 to-red-500`
- Background: `from-purple-900 via-black to-orange-900`

### Adjust Limits
Pass props to the component:
```tsx
<Cashier
  minDeposit={10}
  maxDeposit={10000}
  minWithdrawal={25}
  maxWithdrawal={5000}
/>
```

### Hide Bonus Offer
```tsx
<Cashier showBonusOffer={false} />
```

## 📚 Next Steps

1. ✅ Copy all files to your project
2. ✅ Run `npm install`
3. ✅ Run `npm run dev`
4. 🎨 Customize as needed
5. 🚀 Integrate into your app

## 💡 Tips

- The component is fully responsive
- All buttons are touch-optimized (44px+ targets)
- Form validation is built-in
- Transaction history is optional
- Works standalone or as a modal

Happy coding! 🎉
