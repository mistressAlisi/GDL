import React, { useState, useMemo, useCallback } from 'react';
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
  ArrowUpFromLine,
  Loader2
} from 'lucide-react';

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
  
  // Optional transaction history
  recentTransactions?: Transaction[];
  
  // Optional callbacks for validation/notifications
  onError?: (error: string) => void;
  onSuccess?: (message: string) => void;
}

const quickAmounts = [25, 50, 100, 250, 500, 1000];

export const Cashier: React.FC<CashierProps> = ({
  balance,
  onDeposit,
  onWithdraw,
  minWithdrawal = 25,
  maxWithdrawal = 10000,
  minDeposit = 10,
  maxDeposit = 10000,
  showBonusOffer = true,
  bonusAmount = '$500',
  bonusPercentage = 20,
  onClose,
  onBalanceClick,
  recentTransactions = [],
  onError,
  onSuccess
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

  // Memoized payment methods
  const paymentMethods = useMemo(() => [
    { 
      id: 'credit-card' as PaymentMethod, 
      name: 'Credit/Debit', 
      icon: CreditCard,
      subtitle: 'Visa, Mastercard',
      processingTime: activeTab === 'deposit' ? 'Instant' : '2-3 days',
      gradient: 'from-purple-500/30 to-pink-500/30',
      border: 'border-purple-400/50',
      shadow: 'shadow-purple-500/20'
    },
    { 
      id: 'cryptocurrency' as PaymentMethod, 
      name: 'Crypto', 
      icon: Bitcoin,
      subtitle: 'BTC, ETH, USDT',
      processingTime: activeTab === 'deposit' ? 'Instant' : '< 1 hour',
      gradient: 'from-orange-500/30 to-yellow-500/30',
      border: 'border-orange-400/50',
      shadow: 'shadow-orange-500/20'
    },
    { 
      id: 'e-wallet' as PaymentMethod, 
      name: 'E-Wallet', 
      icon: Smartphone,
      subtitle: 'PayPal, Apple Pay',
      processingTime: activeTab === 'deposit' ? 'Instant' : '1-2 days',
      gradient: 'from-blue-500/30 to-cyan-500/30',
      border: 'border-blue-400/50',
      shadow: 'shadow-blue-500/20'
    }
  ], [activeTab]);

  const handleAmountSelect = useCallback((value: number) => {
    setAmount(value);
    setCustomAmount('');
  }, []);

  const handleCustomAmountChange = useCallback((value: string) => {
    setCustomAmount(value);
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue > 0) {
      setAmount(numValue);
    }
  }, []);

  const resetForm = useCallback(() => {
    setAmount(50);
    setCustomAmount('');
    setCardNumber('');
    setCardName('');
    setExpiryDate('');
    setCvv('');
    setCryptoWallet('');
    setEWalletEmail('');
  }, []);

  const validateForm = useCallback((): string | null => {
    if (amount <= 0) {
      return 'Please enter a valid amount';
    }

    if (activeTab === 'deposit') {
      if (amount < minDeposit) {
        return `Minimum deposit is $${minDeposit}`;
      }
      if (amount > maxDeposit) {
        return `Maximum deposit is $${maxDeposit}`;
      }
    } else {
      if (amount < minWithdrawal) {
        return `Minimum withdrawal is $${minWithdrawal}`;
      }
      if (amount > maxWithdrawal) {
        return `Maximum withdrawal is $${maxWithdrawal}`;
      }
      if (amount > balance) {
        return 'Insufficient balance';
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
      // Basic validation for crypto wallet
      if (cryptoWallet.length < 26) {
        return 'Please enter a valid wallet address';
      }
    } else if (selectedMethod === 'e-wallet') {
      if (!eWalletEmail) {
        return 'Please enter your e-wallet email';
      }
      // Basic email validation
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(eWalletEmail)) {
        return 'Please enter a valid email address';
      }
    }

    return null;
  }, [amount, activeTab, minDeposit, maxDeposit, minWithdrawal, maxWithdrawal, balance, selectedMethod, cardNumber, cardName, expiryDate, cvv, cryptoWallet, eWalletEmail]);

  const handleSubmit = useCallback(async () => {
    const error = validateForm();
    if (error) {
      if (onError) {
        onError(error);
      } else {
        alert(error);
      }
      return;
    }

    setIsProcessing(true);

    const transaction: Transaction = {
      id: `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
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
        const successMsg = `Successfully deposited $${amount.toFixed(2)}!`;
        if (onSuccess) {
          onSuccess(successMsg);
        } else {
          alert(successMsg);
        }
      } else {
        await onWithdraw(transaction);
        const successMsg = `Withdrawal request for $${amount.toFixed(2)} submitted successfully! Processing time: 1-3 business days.`;
        if (onSuccess) {
          onSuccess(successMsg);
        } else {
          alert(successMsg);
        }
      }
      resetForm();
    } catch (error) {
      const errorMsg = 'Transaction failed. Please try again.';
      if (onError) {
        onError(errorMsg);
      } else {
        alert(errorMsg);
      }
    } finally {
      setIsProcessing(false);
    }
  }, [validateForm, activeTab, amount, selectedMethod, onDeposit, onWithdraw, resetForm, onError, onSuccess]);

  const handleTabChange = useCallback((tab: 'deposit' | 'withdraw') => {
    setActiveTab(tab);
    // Reset form when changing tabs
    setAmount(50);
    setCustomAmount('');
  }, []);

  const isSubmitDisabled = useMemo(() => {
    return isProcessing || 
           amount <= 0 || 
           (activeTab === 'withdraw' && (amount < minWithdrawal || amount > balance));
  }, [isProcessing, amount, activeTab, minWithdrawal, balance]);

  return (
    <div className="w-full h-full min-h-screen bg-gradient-to-br from-purple-900 via-black to-orange-900 overflow-y-auto">
      <div className="max-w-4xl mx-auto p-3 sm:p-4 md:p-6 pb-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 md:mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent mb-1 md:mb-2">
              Cashier
            </h1>
            <p className="text-white/70 text-xs sm:text-sm md:text-base">Manage your betting account funds</p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              aria-label="Close cashier"
              className="w-9 h-9 md:w-10 md:h-10 rounded-full bg-white/10 hover:bg-white/20 active:bg-white/30 flex items-center justify-center transition-colors touch-manipulation"
            >
              <X className="w-4 h-4 md:w-5 md:h-5 text-white" />
            </button>
          )}
        </div>

        {/* Current Balance */}
        <button
          onClick={onBalanceClick}
          disabled={!onBalanceClick}
          className={`w-full bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl md:rounded-2xl p-4 md:p-6 mb-4 md:mb-6 text-left ${
            onBalanceClick ? 'cursor-pointer hover:from-green-500/25 hover:to-emerald-500/25 hover:border-green-500/40 active:from-green-500/30 active:to-emerald-500/30 transition-all' : ''
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-green-300/80 text-xs md:text-sm mb-1">Current Balance</div>
              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-green-300">${balance.toFixed(2)}</div>
            </div>
            <div className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-green-500/30 flex items-center justify-center">
              <Wallet className="text-green-300" size={window.innerWidth < 768 ? 24 : 32} />
            </div>
          </div>
        </button>

        {/* Tabs */}
        <div className="flex gap-2 md:gap-3 mb-4 md:mb-6">
          <button
            onClick={() => handleTabChange('deposit')}
            aria-label="Switch to deposit"
            className={`flex-1 py-3 md:py-4 rounded-xl font-bold text-base md:text-lg transition-all touch-manipulation ${
              activeTab === 'deposit'
                ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white shadow-lg shadow-green-500/30'
                : 'bg-white/10 text-white/60 hover:bg-white/20 active:bg-white/30'
            }`}
          >
            <ArrowDownToLine className="inline mr-1 md:mr-2" size={18} />
            <span className="hidden xs:inline">Deposit</span>
            <span className="inline xs:hidden">+</span>
          </button>
          <button
            onClick={() => handleTabChange('withdraw')}
            aria-label="Switch to withdraw"
            className={`flex-1 py-3 md:py-4 rounded-xl font-bold text-base md:text-lg transition-all touch-manipulation ${
              activeTab === 'withdraw'
                ? 'bg-gradient-to-r from-orange-400 to-red-500 text-white shadow-lg shadow-orange-500/30'
                : 'bg-white/10 text-white/60 hover:bg-white/20 active:bg-white/30'
            }`}
          >
            <ArrowUpFromLine className="inline mr-1 md:mr-2" size={18} />
            <span className="hidden xs:inline">Withdraw</span>
            <span className="inline xs:hidden">-</span>
          </button>
        </div>

        {/* Bonus Offer - Only show on deposit tab */}
        <AnimatePresence mode="wait">
          {activeTab === 'deposit' && showBonusOffer && (
            <motion.div
              key="bonus-offer"
              initial={{ scale: 0.95, opacity: 0, height: 0 }}
              animate={{ scale: 1, opacity: 1, height: 'auto' }}
              exit={{ scale: 0.95, opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-orange-500/20 border-2 border-yellow-500/40 rounded-xl md:rounded-2xl p-4 md:p-6 mb-4 md:mb-6 relative overflow-hidden"
            >
              <div className="absolute top-2 right-2">
                <div className="bg-yellow-400/30 backdrop-blur-sm border border-yellow-400/50 rounded-full px-2 md:px-3 py-1 text-[10px] md:text-xs font-bold text-yellow-200 flex items-center gap-1">
                  <Gift size={10} className="md:hidden" />
                  <Gift size={12} className="hidden md:block" />
                  <span className="hidden sm:inline">Limited Offer</span>
                </div>
              </div>
              <div className="flex items-start gap-3 md:gap-4">
                <div className="w-10 h-10 md:w-12 md:h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center flex-shrink-0 shadow-lg shadow-yellow-500/30">
                  <Gift className="text-white" size={window.innerWidth < 768 ? 20 : 24} />
                </div>
                <div>
                  <h3 className="text-base md:text-xl font-bold text-white mb-1 md:mb-2">First Deposit Bonus!</h3>
                  <p className="text-white/90 text-xs md:text-base mb-2 md:mb-3">Get {bonusPercentage}% match on your first deposit</p>
                  <div className="text-lg md:text-2xl font-bold bg-gradient-to-r from-yellow-200 to-orange-300 bg-clip-text text-transparent">
                    Up to {bonusAmount} 🎰
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Withdrawal Notice */}
          {activeTab === 'withdraw' && (
            <motion.div
              key="withdrawal-notice"
              initial={{ scale: 0.95, opacity: 0, height: 0 }}
              animate={{ scale: 1, opacity: 1, height: 'auto' }}
              exit={{ scale: 0.95, opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-3 md:p-4 mb-4 md:mb-6"
            >
              <div className="flex items-start gap-2 md:gap-3">
                <AlertTriangle className="text-orange-400 flex-shrink-0 mt-0.5" size={18} />
                <div>
                  <div className="font-bold text-orange-300 mb-1 text-sm md:text-base">Important Information</div>
                  <ul className="text-xs md:text-sm text-orange-200/80 space-y-0.5 md:space-y-1">
                    <li>• Min withdrawal: ${minWithdrawal}</li>
                    <li>• Processing: 1-3 business days</li>
                    <li className="hidden sm:block">• Identity verification may be required</li>
                    <li className="hidden sm:block">• Withdrawals to verified methods only</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Form */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl md:rounded-2xl p-4 md:p-6">
          {/* Payment Methods */}
          <div className="mb-4 md:mb-6">
            <label className="block text-white/90 font-semibold mb-2 md:mb-3 flex items-center gap-2 text-sm md:text-base">
              <AlertCircle size={14} className="md:hidden" />
              <AlertCircle size={16} className="hidden md:block" />
              1. Payment Method
            </label>
            <p className="text-white/60 text-xs md:text-sm mb-3 md:mb-4">
              {activeTab === 'deposit' ? 'Select funding method:' : 'Choose receiving method:'}
            </p>
            
            <div className="grid grid-cols-3 gap-2 md:gap-3">
              {paymentMethods.map((method) => {
                const Icon = method.icon;
                const isSelected = selectedMethod === method.id;
                return (
                  <button
                    key={method.id}
                    onClick={() => setSelectedMethod(method.id)}
                    aria-label={`Select ${method.name}`}
                    className={`p-3 md:p-4 rounded-lg md:rounded-xl border-2 transition-all touch-manipulation ${
                      isSelected
                        ? `bg-gradient-to-br ${method.gradient} ${method.border} shadow-lg ${method.shadow}`
                        : 'bg-white/5 border-white/20 hover:bg-white/10 active:bg-white/15'
                    }`}
                  >
                    <Icon className="mx-auto mb-1 md:mb-2 text-white" size={window.innerWidth < 768 ? 24 : 32} />
                    <div className="font-bold text-white mb-0.5 md:mb-1 text-xs md:text-sm">{method.name}</div>
                    <div className="text-[10px] md:text-xs text-white/60 hidden sm:block">{method.subtitle}</div>
                    <div className="text-[9px] md:text-xs text-green-400 mt-0.5 md:mt-1">{method.processingTime}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Amount Selection */}
          <div className="mb-4 md:mb-6">
            <label className="block text-white/90 font-semibold mb-2 md:mb-3 flex items-center gap-2 text-sm md:text-base">
              <DollarSign size={14} className="md:hidden" />
              <DollarSign size={16} className="hidden md:block" />
              2. {activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'} Amount
            </label>
            <p className="text-white/60 text-xs md:text-sm mb-3 md:mb-4">
              {activeTab === 'deposit' 
                ? `Select or enter amount (Min: $${minDeposit})` 
                : `Select or enter amount (Min: $${minWithdrawal})`
              }
            </p>
            
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-3 md:mb-4">
              {quickAmounts.map(value => {
                const isDisabled = activeTab === 'withdraw' && value > balance;
                return (
                  <button
                    key={value}
                    onClick={() => handleAmountSelect(value)}
                    disabled={isDisabled}
                    aria-label={`Select ${value} dollars`}
                    className={`py-2.5 md:py-3 rounded-lg font-bold text-sm md:text-base transition-all touch-manipulation ${
                      amount === value && !customAmount
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-500/30'
                        : isDisabled
                        ? 'bg-white/5 text-white/30 cursor-not-allowed'
                        : 'bg-white/10 text-white hover:bg-white/20 active:bg-white/30'
                    }`}
                  >
                    ${value}
                  </button>
                );
              })}
            </div>

            <div className="relative">
              <span className="absolute left-3 md:left-4 top-1/2 -translate-y-1/2 text-white/80 text-lg md:text-xl font-bold pointer-events-none">$</span>
              <input
                type="number"
                inputMode="decimal"
                value={customAmount}
                onChange={(e) => handleCustomAmountChange(e.target.value)}
                placeholder="Enter custom amount"
                max={activeTab === 'withdraw' ? balance : maxDeposit}
                aria-label="Custom amount"
                className="w-full pl-7 md:pl-8 pr-3 md:pr-4 h-12 md:h-14 bg-white/5 border border-white/20 rounded-lg text-white text-base md:text-lg placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
              />
            </div>
          </div>

          {/* Payment Details */}
          <div className="mb-4 md:mb-6">
            <label className="block text-white/90 font-semibold mb-2 md:mb-3 flex items-center gap-2 text-sm md:text-base">
              <Wallet size={14} className="md:hidden" />
              <Wallet size={16} className="hidden md:block" />
              3. Payment Details
            </label>

            {selectedMethod === 'credit-card' && (
              <div className="space-y-3 md:space-y-4">
                {activeTab === 'deposit' && (
                  <>
                    <div>
                      <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Card Number</label>
                      <input
                        type="text"
                        inputMode="numeric"
                        value={cardNumber}
                        onChange={(e) => setCardNumber(e.target.value)}
                        placeholder="1234 5678 9012 3456"
                        maxLength={19}
                        aria-label="Card number"
                        className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                      />
                    </div>
                    <div>
                      <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Cardholder Name</label>
                      <input
                        type="text"
                        value={cardName}
                        onChange={(e) => setCardName(e.target.value)}
                        placeholder="John Doe"
                        aria-label="Cardholder name"
                        className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3 md:gap-4">
                      <div>
                        <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Expiry</label>
                        <input
                          type="text"
                          inputMode="numeric"
                          value={expiryDate}
                          onChange={(e) => setExpiryDate(e.target.value)}
                          placeholder="MM/YY"
                          maxLength={5}
                          aria-label="Expiry date"
                          className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                        />
                      </div>
                      <div>
                        <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">CVV</label>
                        <input
                          type="text"
                          inputMode="numeric"
                          value={cvv}
                          onChange={(e) => setCvv(e.target.value)}
                          placeholder="123"
                          maxLength={4}
                          aria-label="CVV"
                          className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                        />
                      </div>
                    </div>
                  </>
                )}
                {activeTab === 'withdraw' && (
                  <div>
                    <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Card Number (Last 4 digits)</label>
                    <input
                      type="text"
                      inputMode="numeric"
                      value={cardNumber}
                      onChange={(e) => setCardNumber(e.target.value)}
                      placeholder="**** **** **** 1234"
                      maxLength={19}
                      aria-label="Card number for verification"
                      className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                    />
                    <p className="text-[10px] md:text-xs text-white/50 mt-1">Funds returned to deposit card</p>
                  </div>
                )}
              </div>
            )}

            {selectedMethod === 'cryptocurrency' && (
              <div className="space-y-3 md:space-y-4">
                <div>
                  <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Cryptocurrency</label>
                  <select
                    value={selectedCrypto}
                    onChange={(e) => setSelectedCrypto(e.target.value)}
                    aria-label="Select cryptocurrency"
                    className="w-full p-2.5 md:p-3 rounded-lg bg-white/5 border border-white/20 text-white text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                  >
                    <option value="BTC">Bitcoin (BTC)</option>
                    <option value="ETH">Ethereum (ETH)</option>
                    <option value="USDT">Tether (USDT)</option>
                    <option value="LTC">Litecoin (LTC)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">
                    {activeTab === 'deposit' ? 'Wallet Address' : 'Your Wallet Address'}
                  </label>
                  <input
                    type="text"
                    value={cryptoWallet}
                    onChange={(e) => setCryptoWallet(e.target.value)}
                    placeholder="Enter wallet address"
                    aria-label="Crypto wallet address"
                    className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation font-mono"
                  />
                  {activeTab === 'withdraw' && (
                    <p className="text-[10px] md:text-xs text-white/50 mt-1">⚠️ Double-check address - cannot be recovered</p>
                  )}
                </div>
                <div className={`${activeTab === 'deposit' ? 'bg-blue-500/10 border-blue-500/30 text-blue-300' : 'bg-green-500/10 border-green-500/30 text-green-300'} border rounded-lg p-2.5 md:p-3 text-xs md:text-sm`}>
                  {activeTab === 'deposit' ? (
                    <>
                      <TrendingUp size={14} className="inline mr-2" />
                      0% fees, instant processing
                    </>
                  ) : (
                    <>
                      <CheckCircle size={14} className="inline mr-2" />
                      Processed within 1 hour
                    </>
                  )}
                </div>
              </div>
            )}

            {selectedMethod === 'e-wallet' && (
              <div className="space-y-3 md:space-y-4">
                <div>
                  <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">E-Wallet</label>
                  <select
                    value={selectedEWallet}
                    onChange={(e) => setSelectedEWallet(e.target.value)}
                    aria-label="Select e-wallet"
                    className="w-full p-2.5 md:p-3 rounded-lg bg-white/5 border border-white/20 text-white text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                  >
                    <option value="paypal">PayPal</option>
                    <option value="applepay">Apple Pay</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Email Address</label>
                  <input
                    type="email"
                    inputMode="email"
                    value={eWalletEmail}
                    onChange={(e) => setEWalletEmail(e.target.value)}
                    placeholder="your@email.com"
                    aria-label="E-wallet email"
                    className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                  />
                  {activeTab === 'withdraw' && (
                    <p className="text-[10px] md:text-xs text-white/50 mt-1">Must match verified email</p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Pro Tips - Only on deposit */}
          {activeTab === 'deposit' && (
            <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-3 md:p-4 mb-4 md:mb-6">
              <div className="flex items-start gap-2 md:gap-3">
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0 text-sm md:text-base">
                  💡
                </div>
                <div>
                  <div className="font-bold text-white mb-1.5 md:mb-2 text-sm md:text-base">Pro Tips</div>
                  <ul className="text-[11px] md:text-sm text-white/80 space-y-0.5 md:space-y-1">
                    <li>• Use crypto for 0% fees</li>
                    <li>• Check promotions first</li>
                    <li className="hidden sm:block">• Set deposit limits for responsible gaming</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={isSubmitDisabled}
            aria-label={activeTab === 'deposit' ? 'Submit deposit' : 'Submit withdrawal'}
            className={`w-full h-12 md:h-14 rounded-xl font-bold text-base md:text-lg shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation ${
              activeTab === 'deposit'
                ? 'bg-gradient-to-r from-green-400 via-emerald-500 to-cyan-500 hover:from-green-500 hover:via-emerald-600 hover:to-cyan-600 active:from-green-600 active:via-emerald-700 active:to-cyan-700 text-white shadow-green-500/30'
                : 'bg-gradient-to-r from-orange-400 via-red-500 to-pink-500 hover:from-orange-500 hover:via-red-600 hover:to-pink-600 active:from-orange-600 active:via-red-700 active:to-pink-700 text-white shadow-orange-500/30'
            }`}
          >
            {isProcessing ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="animate-spin" size={18} />
                Processing...
              </span>
            ) : activeTab === 'deposit' ? (
              <>Deposit ${amount.toFixed(2)} →</>
            ) : (
              <>Withdraw ${amount.toFixed(2)} →</>
            )}
          </button>

          {activeTab === 'withdraw' && amount > balance && (
            <motion.p 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-400 text-xs md:text-sm mt-2 text-center"
            >
              Insufficient balance. Available: ${balance.toFixed(2)}
            </motion.p>
          )}
        </div>

        {/* Recent Transactions */}
        {recentTransactions.length > 0 && (
          <div className="mt-4 md:mt-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl md:rounded-2xl p-4 md:p-6">
            <h3 className="text-lg md:text-xl font-bold text-white mb-3 md:mb-4">Recent Activity</h3>
            <div className="space-y-2 md:space-y-3">
              {recentTransactions.slice(0, 5).map((txn) => (
                <div key={txn.id} className="flex items-center justify-between p-2.5 md:p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-2 md:gap-3 min-w-0 flex-1">
                    <div className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex-shrink-0 ${
                      txn.type === 'deposit' ? 'bg-green-500/20' : 'bg-orange-500/20'
                    } flex items-center justify-center`}>
                      {txn.type === 'deposit' ? (
                        <ArrowDownToLine className="text-green-400" size={16} />
                      ) : (
                        <ArrowUpFromLine className="text-orange-400" size={16} />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-white font-semibold text-xs md:text-sm truncate">{txn.description}</div>
                      <div className="text-white/50 text-[10px] md:text-xs">{new Date(txn.timestamp).toLocaleDateString()}</div>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0 ml-2">
                    <div className={`font-bold text-xs md:text-sm ${txn.type === 'deposit' ? 'text-green-400' : 'text-orange-400'}`}>
                      {txn.type === 'deposit' ? '+' : '-'}${txn.amount.toFixed(2)}
                    </div>
                    <div className={`text-[10px] md:text-xs capitalize ${
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