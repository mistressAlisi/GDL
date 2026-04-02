import React, { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Wallet,
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
  Loader2,
  Lock,
  Building2,
  type LucideIcon
} from 'lucide-react';
import type { Provider } from './bootstrap';

// Types
export type TransactionType = 'deposit' | 'withdrawal';

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  paymentMethod: string; // Now stores the provider module name
  status: 'pending' | 'completed' | 'failed';
  timestamp: Date;
  description: string;
}

export interface CashierProps {
  // User balance - required
  balance: number;

  // Providers from backend
  providers: {
    deposit: Provider[];
    withdrawal: Provider[];
  };

  // Callbacks - required for integration
  onDeposit: (transaction: Transaction) => void | Promise<void>;
  onWithdraw: (transaction: Transaction, password?: string) => void | Promise<void>;

  // Optional customization
  showBonusOffer?: boolean;
  bonusAmount?: string;
  bonusPercentage?: number;
  onClose?: () => void;

  // Optional transaction history
  recentTransactions?: Transaction[];

  // Optional callbacks for validation/notifications
  onError?: (error: string) => void;
  onSuccess?: (message: string) => void;
}

// Map provider module names to icons
function getProviderIcon(moduleName: string): LucideIcon {
  if (moduleName.includes('ionBlock') || moduleName.includes('coinpayments') || moduleName.includes('hotwallet')) {
    return Bitcoin;
  }
  if (moduleName.includes('sepa')) {
    return Building2;
  }
  if (moduleName.includes('giftcard')) {
    return Gift;
  }
  // Default
  return Wallet;
}

const quickAmounts = [25, 50, 100, 250, 500, 1000];

export const Cashier: React.FC<CashierProps> = ({
  balance,
  providers,
  onDeposit,
  onWithdraw,
  showBonusOffer = true,
  bonusAmount = '$500',
  bonusPercentage = 20,
  onClose,
  recentTransactions = [],
  onError,
  onSuccess
}) => {
  // Tab state
  const [activeTab, setActiveTab] = useState<'deposit' | 'withdraw'>('deposit');

  // Password state for withdrawals
  const [password, setPassword] = useState('');
  
  // Form state - selectedMethod now stores the provider module name
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [amount, setAmount] = useState<number>(50);
  const [customAmount, setCustomAmount] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Payment details state
  const [cryptoWallet, setCryptoWallet] = useState('');
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');

  // Get current providers based on tab
  const currentProviders = useMemo(() => {
    return activeTab === 'deposit' ? providers.deposit : providers.withdrawal;
  }, [activeTab, providers]);

  // Set default selected method when providers change
  React.useEffect(() => {
    if (currentProviders.length > 0 && !currentProviders.find(p => p.module === selectedMethod)) {
      setSelectedMethod(currentProviders[0].module);
    }
  }, [currentProviders, selectedMethod]);

  // Get selected provider's limits
  const selectedProvider = useMemo(() => {
    return currentProviders.find(p => p.module === selectedMethod);
  }, [currentProviders, selectedMethod]);

  const minAmount = selectedProvider?.min ?? 10;
  const maxAmount = selectedProvider?.max ?? 10000;

  // Transform providers into display format with icons and styling
  const paymentMethods = useMemo(() => {
    const gradients = [
      { gradient: 'from-orange-500/30 to-yellow-500/30', border: 'border-orange-400/50', shadow: 'shadow-orange-500/20' },
      { gradient: 'from-purple-500/30 to-pink-500/30', border: 'border-purple-400/50', shadow: 'shadow-purple-500/20' },
      { gradient: 'from-blue-500/30 to-cyan-500/30', border: 'border-blue-400/50', shadow: 'shadow-blue-500/20' },
      { gradient: 'from-green-500/30 to-emerald-500/30', border: 'border-green-400/50', shadow: 'shadow-green-500/20' },
    ];

    return currentProviders.map((provider, index) => ({
      id: provider.module,
      name: provider.name,
      icon: getProviderIcon(provider.module),
      subtitle: `${provider.fees > 0 ? `${provider.fees}% fee` : 'No fees'}`,
      min: provider.min,
      max: provider.max,
      ...gradients[index % gradients.length],
    }));
  }, [currentProviders]);

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
    setCryptoWallet('');
    setPassword('');
  }, []);

  const validateForm = useCallback((): string | null => {
    if (amount <= 0) {
      return 'Please enter a valid amount';
    }

    if (!selectedMethod) {
      return 'Please select a payment method';
    }

    if (amount < minAmount) {
      return `Minimum amount is $${minAmount}`;
    }
    if (amount > maxAmount) {
      return `Maximum amount is $${maxAmount}`;
    }

    if (activeTab === 'withdraw') {
      if (amount > balance) {
        return 'Insufficient balance';
      }
      if (!password) {
        return 'Please enter your password';
      }
    }

    // Validate crypto wallet address for crypto providers
    const isCryptoProvider = selectedMethod.includes('ionBlock') ||
                             selectedMethod.includes('coinpayments') ||
                             selectedMethod.includes('hotwallet');
    if (isCryptoProvider && activeTab === 'withdraw') {
      if (!cryptoWallet) {
        return 'Please enter your wallet address';
      }
      if (cryptoWallet.length < 26) {
        return 'Please enter a valid wallet address';
      }
    }

    return null;
  }, [amount, activeTab, minAmount, maxAmount, balance, selectedMethod, cryptoWallet, password]);

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

    // Get provider name for description
    const providerName = selectedProvider?.name || selectedMethod;

    const transaction: Transaction = {
      id: `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: activeTab === 'deposit' ? 'deposit' : 'withdrawal',
      amount,
      paymentMethod: selectedMethod, // This is now the module name
      status: activeTab === 'deposit' ? 'completed' : 'pending',
      timestamp: new Date(),
      description: `${activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'} via ${providerName}`
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
        // Pass password for withdrawals
        await onWithdraw(transaction, password);
        const successMsg = `Withdrawal request for $${amount.toFixed(2)} submitted successfully!`;
        if (onSuccess) {
          onSuccess(successMsg);
        } else {
          alert(successMsg);
        }
      }
      resetForm();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Transaction failed. Please try again.';
      if (onError) {
        onError(errorMsg);
      } else {
        alert(errorMsg);
      }
    } finally {
      setIsProcessing(false);
    }
  }, [validateForm, activeTab, amount, selectedMethod, selectedProvider, onDeposit, onWithdraw, password, resetForm, onError, onSuccess]);

  const handleTabChange = useCallback((tab: 'deposit' | 'withdraw') => {
    setActiveTab(tab);
    // Reset form when changing tabs
    setAmount(50);
    setCustomAmount('');
    setPassword('');
    setCryptoWallet('');
  }, []);

  const isSubmitDisabled = useMemo(() => {
    return isProcessing ||
           amount <= 0 ||
           !selectedMethod ||
           (activeTab === 'withdraw' && (amount < minAmount || amount > balance));
  }, [isProcessing, amount, activeTab, minAmount, balance, selectedMethod]);

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
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl md:rounded-2xl p-4 md:p-6 mb-4 md:mb-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-green-300/80 text-xs md:text-sm mb-1">Current Balance</div>
              <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-green-300">${balance.toFixed(2)}</div>
            </div>
            <div className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-green-500/30 flex items-center justify-center">
              <Wallet className="text-green-300" size={window.innerWidth < 768 ? 24 : 32} />
            </div>
          </div>
        </div>

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
                    <li>• Min withdrawal: ${minAmount}</li>
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
            
            {paymentMethods.length === 0 ? (
              <div className="text-white/60 text-center py-4">
                No payment methods available
              </div>
            ) : (
              <div className={`grid gap-2 md:gap-3 ${paymentMethods.length <= 3 ? 'grid-cols-' + paymentMethods.length : 'grid-cols-3'}`}>
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
                      <div className="text-[9px] md:text-xs text-green-400 mt-0.5 md:mt-1">${method.min} - ${method.max}</div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Amount Selection */}
          <div className="mb-4 md:mb-6">
            <label className="block text-white/90 font-semibold mb-2 md:mb-3 flex items-center gap-2 text-sm md:text-base">
              <DollarSign size={14} className="md:hidden" />
              <DollarSign size={16} className="hidden md:block" />
              2. {activeTab === 'deposit' ? 'Deposit' : 'Withdrawal'} Amount
            </label>
            <p className="text-white/60 text-xs md:text-sm mb-3 md:mb-4">
              Select or enter amount (Min: ${minAmount}, Max: ${maxAmount})
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
                max={activeTab === 'withdraw' ? Math.min(balance, maxAmount) : maxAmount}
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

            <div className="space-y-3 md:space-y-4">
              {/* Crypto wallet address - for crypto providers on withdrawal */}
              {activeTab === 'withdraw' && (selectedMethod.includes('ionBlock') || selectedMethod.includes('coinpayments') || selectedMethod.includes('hotwallet')) && (
                <>
                  <div>
                    <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Cryptocurrency</label>
                    <select
                      value={selectedCrypto}
                      onChange={(e) => setSelectedCrypto(e.target.value)}
                      aria-label="Select cryptocurrency"
                      className="w-full p-2.5 md:p-3 rounded-lg bg-white/5 border border-white/20 text-white text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                    >
                      <option value="ETH">Ethereum (ETH)</option>
                      <option value="BTC">Bitcoin (BTC)</option>
                      <option value="USDT">Tether (USDT)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2">Your Wallet Address</label>
                    <input
                      type="text"
                      value={cryptoWallet}
                      onChange={(e) => setCryptoWallet(e.target.value)}
                      placeholder="Enter your wallet address"
                      aria-label="Crypto wallet address"
                      className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation font-mono"
                    />
                    <p className="text-[10px] md:text-xs text-white/50 mt-1">Double-check address - cannot be recovered</p>
                  </div>
                </>
              )}

              {/* Password - required for withdrawals */}
              {activeTab === 'withdraw' && (
                <div>
                  <label className="block text-white/70 text-xs md:text-sm mb-1.5 md:mb-2 flex items-center gap-2">
                    <Lock size={14} />
                    Account Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password to confirm"
                    aria-label="Account password"
                    className="w-full px-3 md:px-4 py-2.5 md:py-3 bg-white/5 border border-white/20 rounded-lg text-white text-sm md:text-base placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400/50 touch-manipulation"
                  />
                  <p className="text-[10px] md:text-xs text-white/50 mt-1">Required for security verification</p>
                </div>
              )}

              {/* Info message for deposits */}
              {activeTab === 'deposit' && (
                <div className="bg-blue-500/10 border border-blue-500/30 text-blue-300 rounded-lg p-2.5 md:p-3 text-xs md:text-sm">
                  <TrendingUp size={14} className="inline mr-2" />
                  You will be redirected to complete your payment
                </div>
              )}

              {/* Info message for withdrawals */}
              {activeTab === 'withdraw' && (
                <div className="bg-green-500/10 border border-green-500/30 text-green-300 rounded-lg p-2.5 md:p-3 text-xs md:text-sm">
                  <CheckCircle size={14} className="inline mr-2" />
                  Withdrawals are typically processed within 1-24 hours
                </div>
              )}
            </div>
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
