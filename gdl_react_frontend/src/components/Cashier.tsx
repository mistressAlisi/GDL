import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  CreditCard, 
  Wallet, 
  Building2, 
  Smartphone, 
  Gift, 
  DollarSign, 
  Bitcoin, 
  AlertCircle, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  X,
  ArrowDownToLine,
  ArrowUpFromLine
} from 'lucide-react';
import { useTheme } from '../sportslotto/contexts/ThemeContext';

// Types
export type PaymentMethod = 'credit-card' | 'cryptocurrency' | 'e-wallet' | 'bank-transfer';
export type TransactionType = 'deposit' | 'withdrawal';

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  paymentMethod: PaymentMethod;
  status: 'pending' | 'completed' | 'failed';
  timestamp: Date;
  description: string;
}

export interface CashierProps {
  // User balance - required
  balance: number;
  
  // Callbacks - required for integration
  onDeposit: (transaction: Transaction) => void | Promise<void>;
  onWithdraw: (transaction: Transaction) => void | Promise<void>;
  
  // Optional customization
  minWithdrawal?: number;
  maxWithdrawal?: number;
  minDeposit?: number;
  maxDeposit?: number;
  showBonusOffer?: boolean;
  bonusAmount?: string;
  bonusPercentage?: number;
  onClose?: () => void;
  onBalanceClick?: () => void; // Navigate to balance page
  onBackToMenu?: () => void; // Navigate back to main menu
  
  // Optional transaction history
  recentTransactions?: Transaction[];
}

const quickAmounts = [25, 50, 100, 250, 500, 1000];

export const Cashier: React.FC<CashierProps> = ({
  balance,
  onDeposit,
  onWithdraw,
  minWithdrawal = 25,
  maxWithdrawal = 10000,
  minDeposit = 25,
  maxDeposit = 10000,
  showBonusOffer = true,
  bonusAmount = '$500',
  bonusPercentage = 20,
  onClose,
  onBalanceClick,
  onBackToMenu,
  recentTransactions = []
}) => {
  // Tab state
  const [activeTab, setActiveTab] = useState<'deposit' | 'withdraw'>('deposit');
  
  // Form state
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>('credit-card');
  const [amount, setAmount] = useState<number>(50);
  const [customAmount, setCustomAmount] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Payment details state
  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [cryptoWallet, setCryptoWallet] = useState('');
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [eWalletEmail, setEWalletEmail] = useState('');
  const [selectedEWallet, setSelectedEWallet] = useState('paypal');

  const handleAmountSelect = (value: number) => {
    setAmount(value);
    setCustomAmount('');
  };

  const handleCustomAmountChange = (value: string) => {
    setCustomAmount(value);
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setAmount(numValue);
    }
  };

  const resetForm = () => {
    setAmount(50);
    setCustomAmount('');
    setCardNumber('');
    setCardName('');
    setExpiryDate('');
    setCvv('');
    setCryptoWallet('');
    setEWalletEmail('');
  };

  const validateForm = (): string | null => {
    if (amount <= 0) {
      return 'Please enter a valid amount';
    }

    if (activeTab === 'withdraw') {
      if (amount < minWithdrawal) {
        return `Minimum withdrawal is $${minWithdrawal}`;
      }
      if (amount > maxWithdrawal) {
        return `Maximum withdrawal is $${maxWithdrawal}`;
      }
      if (amount > balance) {
        return 'Insufficient balance';
      }
    } else if (activeTab === 'deposit') {
      if (amount < minDeposit) {
        return `Minimum deposit is $${minDeposit}`;
      }
      if (amount > maxDeposit) {
        return `Maximum deposit is $${maxDeposit}`;
      }
    }

    // Validate based on payment method
    if (selectedMethod === 'credit-card') {
      if (activeTab === 'deposit' && (!cardNumber || !cardName || !expiryDate || !cvv)) {
        return 'Please fill in all card details';
      }
      if (activeTab === 'withdraw' && !cardNumber) {
        return 'Please enter your card number';
      }
    } else if (selectedMethod === 'cryptocurrency') {
      if (!cryptoWallet) {
        return 'Please enter your wallet address';
      }
    } else if (selectedMethod === 'e-wallet') {
      if (!eWalletEmail) {
        return 'Please enter your e-wallet email';
      }
    }

    return null;
  };

  const handleSubmit = async () => {
    const error = validateForm();
    if (error) {
      alert(error);
      return;
    }

    setIsProcessing(true);

    const transaction: Transaction = {
      id: `txn_${Date.now()}`,
      type: activeTab === 'deposit' ? 'deposit' : 'withdrawal',
      amount,
      paymentMethod: selectedMethod,
      status: activeTab === 'deposit' ? 'completed' : 'pending',
      timestamp: new Date(),
      description: `${activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'} via ${
        selectedMethod === 'credit-card' ? 'Credit/Debit Card' : 
        selectedMethod === 'cryptocurrency' ? 'Cryptocurrency' : 
        selectedMethod === 'e-wallet' ? 'E-Wallet' :
        'Bank Transfer'
      }`
    };

    try {
      if (activeTab === 'deposit') {
        await onDeposit(transaction);
        alert(`Successfully deposited $${amount.toFixed(2)}!`);
      } else {
        await onWithdraw(transaction);
        alert(`Withdrawal request for $${amount.toFixed(2)} submitted successfully! Processing time: 1-3 business days.`);
      }
      resetForm();
    } catch (error) {
      alert('Transaction failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const paymentMethods = [
    { 
      id: 'credit-card' as PaymentMethod, 
      name: 'Credit/Debit Card', 
      icon: CreditCard,
      subtitle: 'Visa, Mastercard',
      processingTime: activeTab === 'deposit' ? 'Instant' : '2-3 days',
      gradient: 'from-purple-500/30 to-pink-500/30',
      border: 'border-purple-400/50',
      shadow: 'shadow-purple-500/20'
    },
    { 
      id: 'cryptocurrency' as PaymentMethod, 
      name: 'Cryptocurrency', 
      icon: Bitcoin,
      subtitle: 'BTC, ETH, USDT, LTC',
      processingTime: activeTab === 'deposit' ? 'Instant' : 'Instant - 1 hour',
      gradient: 'from-orange-500/30 to-yellow-500/30',
      border: 'border-orange-400/50',
      shadow: 'shadow-orange-500/20'
    },
    { 
      id: 'e-wallet' as PaymentMethod, 
      name: 'E-Wallets', 
      icon: Smartphone,
      subtitle: 'PayPal, Apple Pay',
      processingTime: activeTab === 'deposit' ? 'Instant' : '1-2 days',
      gradient: 'from-blue-500/30 to-cyan-500/30',
      border: 'border-blue-400/50',
      shadow: 'shadow-blue-500/20'
    }
  ];

  // Filter payment methods - only cryptocurrency for withdrawals
  const availablePaymentMethods = activeTab === 'withdraw' 
    ? paymentMethods.filter(method => method.id === 'cryptocurrency')
    : paymentMethods;

  // Auto-select cryptocurrency when switching to withdraw tab
  React.useEffect(() => {
    if (activeTab === 'withdraw' && selectedMethod !== 'cryptocurrency') {
      setSelectedMethod('cryptocurrency');
    }
  }, [activeTab]);

  const { theme } = useTheme();

  return (
    <div 
      className="w-full h-full min-h-screen overflow-y-auto relative"
      style={{ background: theme.backgroundGradient }}
    >
      {/* Glassmorphism overlay layers */}
      <div className="absolute inset-0 pointer-events-none">
        <div 
          className="absolute inset-0 opacity-30"
          style={{ background: theme.glassOverlay }}
        />
        <div 
          className="absolute inset-0 backdrop-blur-[100px] opacity-20"
          style={{ background: theme.glassHighlight }}
        />
      </div>

      {/* Animated particles */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" style={{
        backgroundImage: `radial-gradient(2px 2px at 20% 30%, white, transparent),
                         radial-gradient(2px 2px at 60% 70%, ${theme.accentColor}, transparent),
                         radial-gradient(1px 1px at 50% 50%, white, transparent),
                         radial-gradient(1px 1px at 80% 10%, ${theme.accentColor}, transparent),
                         radial-gradient(2px 2px at 90% 60%, white, transparent),
                         radial-gradient(1px 1px at 33% 80%, ${theme.accentColor}, transparent)`,
        backgroundSize: '200% 200%',
        animation: 'particle-float 20s ease-in-out infinite'
      }}></div>

      <div className="relative z-10 max-w-4xl mx-auto p-4 md:p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent mb-2">
              Cashier
            </h1>
            <p className="text-white/70">Manage your betting account funds</p>
          </div>
          <div className="flex items-center gap-2">
            {onBackToMenu && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onBackToMenu}
                className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-bold py-2 px-4 md:py-3 md:px-6 rounded-lg shadow-lg shadow-purple-500/30 transition-all flex items-center gap-2 text-sm md:text-base"
              >
                ← <span className="hidden sm:inline">Back to Main Menu</span><span className="sm:hidden">Back</span>
              </motion.button>
            )}
            {onClose && (
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
              >
                <X className="w-5 h-5 text-white" />
              </button>
            )}
          </div>
        </div>

        {/* Current Balance */}
        <button
          onClick={onBalanceClick}
          disabled={!onBalanceClick}
          className={`w-full bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-2xl p-6 mb-6 text-left ${
            onBalanceClick ? 'cursor-pointer hover:from-green-500/25 hover:to-emerald-500/25 hover:border-green-500/40 active:from-green-500/30 active:to-emerald-500/30 transition-all' : ''
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-green-300/80 text-sm mb-1">Current Balance</div>
              <div className="text-3xl md:text-4xl font-bold text-green-300">${balance.toFixed(2)}</div>
            </div>
            <div className="w-16 h-16 rounded-full bg-green-500/30 flex items-center justify-center">
              <Wallet className="text-green-300" size={32} />
            </div>
          </div>
        </button>

        {/* Tabs */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={() => setActiveTab('deposit')}
            className={`flex-1 py-4 rounded-xl font-bold text-lg transition-all ${
              activeTab === 'deposit'
                ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white shadow-lg shadow-green-500/30'
                : 'bg-white/10 text-white/60 hover:bg-white/20'
            }`}
          >
            <ArrowDownToLine className="inline mr-2" size={20} />
            Deposit
          </button>
          <button
            onClick={() => setActiveTab('withdraw')}
            className={`flex-1 py-4 rounded-xl font-bold text-lg transition-all ${
              activeTab === 'withdraw'
                ? 'bg-gradient-to-r from-orange-400 to-red-500 text-white shadow-lg shadow-orange-500/30'
                : 'bg-white/10 text-white/60 hover:bg-white/20'
            }`}
          >
            <ArrowUpFromLine className="inline mr-2" size={20} />
            Withdraw
          </button>
        </div>

        {/* Bonus Offer - Only show on deposit tab */}
        {activeTab === 'deposit' && showBonusOffer && (
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-orange-500/20 border-2 border-yellow-500/40 rounded-2xl p-6 mb-6 relative overflow-hidden"
          >
            <div className="absolute top-2 right-2">
              <div className="bg-yellow-400/30 backdrop-blur-sm border border-yellow-400/50 rounded-full px-3 py-1 text-xs font-bold text-yellow-200 flex items-center gap-1">
                <Gift size={12} /> Limited Offer
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-yellow-500/30">
                <Gift className="text-white" size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">First Deposit Bonus!</h3>
                <p className="text-white/90 mb-3">Get {bonusPercentage}% match on your first deposit</p>
                <div className="text-2xl font-bold bg-gradient-to-r from-yellow-200 to-orange-300 bg-clip-text text-transparent">
                  Up to {bonusAmount} 🎰
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Withdrawal Notice */}
        {activeTab === 'withdraw' && (
          <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-orange-400 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <div className="font-bold text-orange-300 mb-1">Important Withdrawal Information</div>
                <ul className="text-sm text-orange-200/80 space-y-1">
                  <li>• Minimum withdrawal: ${minWithdrawal}</li>
                  <li>• Maximum withdrawal: ${maxWithdrawal}</li>
                  <li>• Processing time: 1-3 business days</li>
                  <li>• You may be required to verify your identity</li>
                  <li>• Withdrawals can only be made to verified payment methods</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Main Form */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          {/* Payment Methods */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <AlertCircle size={16} />
              1. Payment Method
            </label>
            <p className="text-white/60 text-sm mb-4">
              {activeTab === 'deposit' ? 'Select your preferred funding method:' : 'Choose where you want to receive your funds:'}
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {availablePaymentMethods.map((method) => {
                const Icon = method.icon;
                const isSelected = selectedMethod === method.id;
                return (
                  <button
                    key={method.id}
                    onClick={() => setSelectedMethod(method.id)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      isSelected
                        ? `bg-gradient-to-br ${method.gradient} ${method.border} shadow-lg ${method.shadow}`
                        : 'bg-white/5 border-white/20 hover:bg-white/10'
                    }`}
                  >
                    <Icon className="mx-auto mb-2 text-white" size={32} />
                    <div className="font-bold text-white mb-1">{method.name}</div>
                    <div className="text-xs text-white/60">{method.subtitle}</div>
                    <div className="text-xs text-green-400 mt-1">{method.processingTime}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Amount Selection */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <DollarSign size={16} />
              2. {activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'} Amount
            </label>
            <p className="text-white/60 text-sm mb-4">
              {activeTab === 'deposit' 
                ? 'Select amount or enter custom:' 
                : `Select amount or enter custom (Min: $${minWithdrawal}, Max: $${maxWithdrawal}):`
              }
            </p>
            
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
              {quickAmounts.map(value => {
                const isDisabled = activeTab === 'withdraw' && value > balance;
                return (
                  <button
                    key={value}
                    onClick={() => handleAmountSelect(value)}
                    disabled={isDisabled}
                    className={`py-3 rounded-lg font-bold transition-all ${
                      amount === value && !customAmount
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-500/30'
                        : isDisabled
                        ? 'bg-white/5 text-white/30 cursor-not-allowed'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    ${value}
                  </button>
                );
              })}
            </div>

            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 text-xl font-bold">$</span>
              <input
                type="number"
                value={customAmount}
                onChange={(e) => handleCustomAmountChange(e.target.value)}
                placeholder="Enter custom amount"
                max={activeTab === 'withdraw' ? balance : undefined}
                className="w-full pl-8 h-14 bg-white/5 border border-white/20 rounded-lg text-white text-lg placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
              />
            </div>
          </div>

          {/* Payment Details */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <Wallet size={16} />
              3. Payment Details
            </label>

            {selectedMethod === 'credit-card' && (
              <div className="space-y-4">
                {activeTab === 'deposit' && (
                  <>
                    <div>
                      <label className="block text-white/70 text-sm mb-2">Card Number</label>
                      <input
                        type="text"
                        value={cardNumber}
                        onChange={(e) => setCardNumber(e.target.value)}
                        placeholder="1234 5678 9012 3456"
                        maxLength={19}
                        className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                      />
                    </div>
                    <div>
                      <label className="block text-white/70 text-sm mb-2">Cardholder Name</label>
                      <input
                        type="text"
                        value={cardName}
                        onChange={(e) => setCardName(e.target.value)}
                        placeholder="John Doe"
                        className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-white/70 text-sm mb-2">Expiry Date</label>
                        <input
                          type="text"
                          value={expiryDate}
                          onChange={(e) => setExpiryDate(e.target.value)}
                          placeholder="MM/YY"
                          maxLength={5}
                          className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                        />
                      </div>
                      <div>
                        <label className="block text-white/70 text-sm mb-2">CVV</label>
                        <input
                          type="text"
                          value={cvv}
                          onChange={(e) => setCvv(e.target.value)}
                          placeholder="123"
                          maxLength={4}
                          className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                        />
                      </div>
                    </div>
                  </>
                )}
                {activeTab === 'withdraw' && (
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Card Number (Last 4 digits for verification)</label>
                    <input
                      type="text"
                      value={cardNumber}
                      onChange={(e) => setCardNumber(e.target.value)}
                      placeholder="**** **** **** 1234"
                      maxLength={19}
                      className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                    />
                    <p className="text-xs text-white/50 mt-1">Funds will be returned to the card used for deposit</p>
                  </div>
                )}
              </div>
            )}

            {selectedMethod === 'cryptocurrency' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white/70 text-sm mb-2">Select Cryptocurrency</label>
                  <select
                    value={selectedCrypto}
                    onChange={(e) => setSelectedCrypto(e.target.value)}
                    className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                  >
                    <option value="BTC">Bitcoin (BTC)</option>
                    <option value="ETH">Ethereum (ETH)</option>
                    <option value="USDT">Tether (USDT)</option>
                    <option value="LTC">Litecoin (LTC)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white/70 text-sm mb-2">
                    {activeTab === 'deposit' ? 'Wallet Address' : 'Your Wallet Address'}
                  </label>
                  <input
                    type="text"
                    value={cryptoWallet}
                    onChange={(e) => setCryptoWallet(e.target.value)}
                    placeholder="Enter your wallet address"
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                  />
                  {activeTab === 'withdraw' && (
                    <p className="text-xs text-white/50 mt-1">⚠️ Double-check your wallet address. Incorrect addresses cannot be recovered.</p>
                  )}
                </div>
                <div className={`${activeTab === 'deposit' ? 'bg-blue-500/10 border-blue-500/30 text-blue-300' : 'bg-green-500/10 border-green-500/30 text-green-300'} border rounded-lg p-3 text-sm`}>
                  {activeTab === 'deposit' ? (
                    <>
                      <TrendingUp size={16} className="inline mr-2" />
                      Use crypto for 0% fees and faster processing
                    </>
                  ) : (
                    <>
                      <CheckCircle size={16} className="inline mr-2" />
                      Crypto withdrawals are processed within 1 hour
                    </>
                  )}
                </div>
              </div>
            )}

            {selectedMethod === 'e-wallet' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-white/70 text-sm mb-2">Select E-Wallet</label>
                  <select
                    value={selectedEWallet}
                    onChange={(e) => setSelectedEWallet(e.target.value)}
                    className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                  >
                    <option value="paypal">PayPal</option>
                    <option value="applepay">Apple Pay</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white/70 text-sm mb-2">Email Address</label>
                  <input
                    type="email"
                    value={eWalletEmail}
                    onChange={(e) => setEWalletEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
                  />
                  {activeTab === 'withdraw' && (
                    <p className="text-xs text-white/50 mt-1">Must match your verified e-wallet email</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Pro Tips - Only on deposit */}
          {activeTab === 'deposit' && (
            <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                  💡
                </div>
                <div>
                  <div className="font-bold text-white mb-2">Pro Tips</div>
                  <ul className="text-sm text-white/80 space-y-1">
                    <li>• Use crypto for 0% fees and faster processing</li>
                    <li>• Check promotions before depositing for extra bonuses</li>
                    <li>• Set deposit limits in settings for responsible gaming</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={isProcessing || amount <= 0 || (activeTab === 'withdraw' && (amount < minWithdrawal || amount > balance))}
            className={`w-full h-14 rounded-xl font-bold text-lg shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
              activeTab === 'deposit'
                ? 'bg-gradient-to-r from-green-400 via-emerald-500 to-cyan-500 hover:from-green-500 hover:via-emerald-600 hover:to-cyan-600 text-white shadow-green-500/30'
                : 'bg-gradient-to-r from-orange-400 via-red-500 to-pink-500 hover:from-orange-500 hover:via-red-600 hover:to-pink-600 text-white shadow-orange-500/30'
            }`}
          >
            {isProcessing ? (
              <>Processing...</>
            ) : activeTab === 'deposit' ? (
              <>Deposit ${amount.toFixed(2)} →</>
            ) : (
              <>Request Withdrawal ${amount.toFixed(2)} →</>
            )}
          </button>

          {activeTab === 'withdraw' && amount > balance && (
            <p className="text-red-400 text-sm mt-2 text-center">
              Insufficient balance. Available: ${balance.toFixed(2)}
            </p>
          )}
        </div>

        {/* Recent Transactions */}
        {recentTransactions.length > 0 && (
          <div className="mt-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {recentTransactions.slice(0, 5).map((txn) => (
                <div key={txn.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full ${
                      txn.type === 'deposit' ? 'bg-green-500/20' : 'bg-orange-500/20'
                    } flex items-center justify-center`}>
                      {txn.type === 'deposit' ? (
                        <ArrowDownToLine className="text-green-400" size={20} />
                      ) : (
                        <ArrowUpFromLine className="text-orange-400" size={20} />
                      )}
                    </div>
                    <div>
                      <div className="text-white font-semibold">{txn.description}</div>
                      <div className="text-white/50 text-xs">{txn.timestamp.toLocaleString()}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${txn.type === 'deposit' ? 'text-green-400' : 'text-orange-400'}`}>
                      {txn.type === 'deposit' ? '+' : '-'}${txn.amount.toFixed(2)}
                    </div>
                    <div className={`text-xs ${
                      txn.status === 'completed' ? 'text-green-400' : 
                      txn.status === 'pending' ? 'text-yellow-400' : 
                      'text-red-400'
                    }`}>
                      {txn.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Cashier;