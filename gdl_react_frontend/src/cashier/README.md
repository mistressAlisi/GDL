# Cashier Component

A standalone, production-ready cashier component for deposit and withdrawal transactions with premium glass-morphism design and full mobile optimization.

## 📦 What's Included

- `Cashier.tsx` - The complete cashier component
- `App.tsx` - Example integration/demo

## 🚀 Quick Start

### Installation

This component requires the following dependencies:

```bash
npm install react motion lucide-react
```

Or with yarn:

```bash
yarn add react motion lucide-react
```

### Basic Usage

```tsx
import { Cashier, Transaction } from './Cashier';

function App() {
  const [balance, setBalance] = useState(142.75);
  
  const handleDeposit = (transaction: Transaction) => {
    setBalance(prev => prev + transaction.amount);
    console.log('Deposit:', transaction);
  };

  const handleWithdraw = (transaction: Transaction) => {
    setBalance(prev => prev - transaction.amount);
    console.log('Withdraw:', transaction);
  };

  return (
    <Cashier
      balance={balance}
      onDeposit={handleDeposit}
      onWithdraw={handleWithdraw}
    />
  );
}
```

## 📋 Props

### Required Props

| Prop | Type | Description |
|------|------|-------------|
| `balance` | `number` | Current user balance |
| `onDeposit` | `(transaction: Transaction) => void \| Promise<void>` | Callback when deposit is processed |
| `onWithdraw` | `(transaction: Transaction) => void \| Promise<void>` | Callback when withdrawal is processed |

### Optional Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `minWithdrawal` | `number` | `25` | Minimum withdrawal amount |
| `maxWithdrawal` | `number` | `10000` | Maximum withdrawal amount |
| `minDeposit` | `number` | `10` | Minimum deposit amount |
| `maxDeposit` | `number` | `10000` | Maximum deposit amount |
| `showBonusOffer` | `boolean` | `true` | Show/hide bonus offer banner |
| `bonusAmount` | `string` | `"$500"` | Bonus amount text |
| `bonusPercentage` | `number` | `20` | Bonus percentage |
| `onClose` | `() => void` | `undefined` | Close button callback |
| `recentTransactions` | `Transaction[]` | `[]` | Array of recent transactions |
| `onError` | `(error: string) => void` | `undefined` | Custom error handler |
| `onSuccess` | `(message: string) => void` | `undefined` | Custom success handler |

## 🔧 Transaction Type

```typescript
interface Transaction {
  id: string;
  type: 'deposit' | 'withdrawal';
  amount: number;
  paymentMethod: 'credit-card' | 'cryptocurrency' | 'e-wallet' | 'bank-transfer';
  status: 'pending' | 'completed' | 'failed';
  timestamp: Date;
  description: string;
}
```

## 🎨 Features

### ✅ Deposit & Withdrawal
- Dual-tab interface for deposits and withdrawals
- Quick amount selection buttons ($25, $50, $100, $250, $500, $1000)
- Custom amount input field
- Real-time balance validation

### 💳 Payment Methods
- **Credit/Debit Card** - Visa, Mastercard
- **Cryptocurrency** - BTC, ETH, USDT, LTC
- **E-Wallets** - PayPal, Apple Pay

### 📱 Mobile Optimized
- Fully responsive design (mobile-first)
- Touch-friendly buttons (44px+ targets)
- Optimized input modes (`inputMode="numeric"`, `inputMode="email"`)
- Adaptive text sizes and spacing
- Smooth animations and transitions

### ♿ Accessibility
- Full ARIA labels
- Keyboard navigation
- Screen reader support
- Semantic HTML

### 🎯 Form Validation
- Amount limits (min/max)
- Payment method validation
- Email validation (e-wallet)
- Crypto wallet address validation
- Card details validation
- Insufficient balance checks

### 🎁 Bonus Features
- Animated bonus offer banner (deposit only)
- Withdrawal information notice
- Recent transaction history
- Processing time indicators
- Pro tips section

## 🎭 Styling

The component uses:
- **Tailwind CSS v4** - Utility-first styling
- **Glass-morphism** - Backdrop blur effects
- **Premium gradients** - Golden yellow accents
- **Dark theme** - Purple-black-orange gradient background

## 🔌 Integration Examples

### With Custom Error/Success Handlers

```tsx
<Cashier
  balance={balance}
  onDeposit={handleDeposit}
  onWithdraw={handleWithdraw}
  onError={(error) => toast.error(error)}
  onSuccess={(message) => toast.success(message)}
/>
```

### With Transaction History

```tsx
const [transactions, setTransactions] = useState<Transaction[]>([]);

const handleDeposit = (transaction: Transaction) => {
  setBalance(prev => prev + transaction.amount);
  setTransactions(prev => [transaction, ...prev]);
};

<Cashier
  balance={balance}
  onDeposit={handleDeposit}
  onWithdraw={handleWithdraw}
  recentTransactions={transactions}
/>
```

### As a Modal/Drawer

```tsx
const [showCashier, setShowCashier] = useState(false);

<Cashier
  balance={balance}
  onDeposit={handleDeposit}
  onWithdraw={handleWithdraw}
  onClose={() => setShowCashier(false)}
/>
```

### With Custom Limits

```tsx
<Cashier
  balance={balance}
  onDeposit={handleDeposit}
  onWithdraw={handleWithdraw}
  minDeposit={50}
  maxDeposit={25000}
  minWithdrawal={100}
  maxWithdrawal={5000}
/>
```

## 🛠️ Customization

The component is fully customizable via props. You can:
- Adjust min/max transaction limits
- Show/hide bonus offers
- Customize bonus amounts and percentages
- Add custom error/success handlers
- Pass transaction history
- Add close button functionality

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📝 Notes

- All monetary values use 2 decimal places
- Transaction IDs are auto-generated with timestamp + random string
- Deposits are marked as "completed", withdrawals as "pending"
- Form validation runs before submission
- Component is fully typed with TypeScript
- Uses React hooks (useState, useMemo, useCallback)

## 🔒 Security Considerations

This is a **frontend component only**. For production use:
- Implement backend validation
- Use HTTPS for all transactions
- Implement proper authentication
- Add CSRF protection
- Validate transactions server-side
- Never trust client-side validation alone
- Consider PCI compliance for card payments
- Implement rate limiting
- Add fraud detection

## 📄 License

This component is provided as-is for integration into your project.
