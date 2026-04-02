# ⚡ Quick Reference - Cashier Component

## 🏃‍♂️ Fast Setup (3 Steps)

### Step 1: Copy Files
Copy all files from `/cashier` to your `react_cashier/` project:
- Copy `Cashier.tsx` → `react_cashier/src/`
- Copy `App.tsx` → `react_cashier/src/`
- Copy all config files to root

### Step 2: Install
```bash
cd react_cashier
npm install
```

### Step 3: Run
```bash
npm run dev
```

Open: http://localhost:5173 🎉

---

## 📦 Required Packages

Already in package.json:
- ✅ react (^18.3.1)
- ✅ react-dom (^18.3.1)
- ✅ motion (^10.18.0) - animations
- ✅ lucide-react (^0.460.0) - icons
- ✅ tailwindcss (^4.0.0)
- ✅ @tailwindcss/vite (^4.0.0)
- ✅ vite (^5.4.11)

---

## 🎯 Essential Commands

```bash
npm install              # Install all dependencies
npm run dev              # Start dev server
npm run dev -- --host    # Dev server + mobile access
npm run build            # Production build
npm run preview          # Preview production build
```

---

## 🔧 Vite Config (Already Done)

File: `vite.config.ts`
```ts
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') }
  }
})
```

---

## 🎨 Tailwind Setup (Already Done)

File: `src/styles/globals.css`
```css
@import "tailwindcss";
/* All Tailwind classes now work! */
```

File: `src/main.tsx`
```tsx
import './styles/globals.css'
```

---

## 💻 Component Usage

```tsx
import { Cashier, Transaction } from "./Cashier";

<Cashier
  balance={142.75}
  onDeposit={(txn) => console.log(txn)}
  onWithdraw={(txn) => console.log(txn)}
  minWithdrawal={25}
  maxWithdrawal={10000}
  showBonusOffer={true}
/>
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| No styles | Check `globals.css` has `@import "tailwindcss"` |
| Module errors | Run `npm install` |
| Port in use | Use `npm run dev -- --port 3000` |
| Icons missing | Install `lucide-react` |
| Build fails | Check all files in `src/` folder |

---

## 📱 Mobile Testing

1. Start dev server with `--host`:
   ```bash
   npm run dev -- --host
   ```

2. Find your IP:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`

3. Access from phone:
   ```
   http://YOUR_IP:5173
   ```

---

## 🎨 Key Features

✅ Deposit & Withdrawal tabs
✅ 3 Payment methods (Card, Crypto, E-Wallet)
✅ Quick amount buttons ($25-$1000)
✅ Custom amount input
✅ Form validation
✅ Transaction history
✅ Bonus offer banner
✅ Fully mobile responsive
✅ Touch-optimized (44px+ buttons)
✅ Smooth animations
✅ Loading states
✅ Error handling

---

## 📂 File Checklist

In `react_cashier/`:
```
✓ src/Cashier.tsx
✓ src/App.tsx
✓ src/main.tsx
✓ src/styles/globals.css
✓ index.html
✓ vite.config.ts
✓ tsconfig.json
✓ tsconfig.node.json
✓ package.json
```

---

## 🚀 Ready to Go!

All configuration is done. Just:
1. Copy files
2. `npm install`
3. `npm run dev`

That's it! 🎉
