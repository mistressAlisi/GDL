import React, { useState } from 'react';
import { motion } from 'motion/react';
import { CreditCard, Wallet, Bitcoin, Smartphone, DollarSign, AlertTriangle, CheckCircle } from 'lucide-react';
import { useProfile, PaymentMethod } from '../../contexts/ProfileContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

const quickAmounts = [25, 50, 100, 250, 500, 1000];

export const WithdrawPage: React.FC = () => {
  const { userProfile, addTransaction } = useProfile();
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>('credit-card');
  const [amount, setAmount] = useState<number>(50);
  const [customAmount, setCustomAmount] = useState<string>('');
  const [cardNumber, setCardNumber] = useState('');
  const [cryptoWallet, setCryptoWallet] = useState('');
  const [selectedCrypto, setSelectedCrypto] = useState('BTC');
  const [eWalletEmail, setEWalletEmail] = useState('');
  const [selectedEWallet, setSelectedEWallet] = useState('paypal');
  const [isProcessing, setIsProcessing] = useState(false);

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

  const handleWithdraw = async () => {
    if (amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    if (amount > userProfile.balance) {
      alert('Insufficient balance');
      return;
    }

    // Validate based on payment method
    if (selectedMethod === 'credit-card') {
      if (!cardNumber) {
        alert('Please enter your card number');
        return;
      }
    } else if (selectedMethod === 'cryptocurrency') {
      if (!cryptoWallet) {
        alert('Please enter your wallet address');
        return;
      }
    } else if (selectedMethod === 'e-wallet') {
      if (!eWalletEmail) {
        alert('Please enter your e-wallet email');
        return;
      }
    }

    setIsProcessing(true);

    // Simulate API call
    setTimeout(() => {
      addTransaction({
        id: `txn_${Date.now()}`,
        type: 'withdrawal',
        amount,
        paymentMethod: selectedMethod,
        status: 'pending',
        timestamp: new Date(),
        description: `Withdrawal via ${selectedMethod === 'credit-card' ? 'Credit/Debit Card' : selectedMethod === 'cryptocurrency' ? 'Cryptocurrency' : 'E-Wallet'}`,
      });

      setIsProcessing(false);
      alert(`Withdrawal request for $${amount.toFixed(2)} submitted successfully! Processing time: 1-3 business days.`);
      
      // Reset form
      setAmount(50);
      setCustomAmount('');
      setCardNumber('');
      setCryptoWallet('');
      setEWalletEmail('');
    }, 2000);
  };

  return (
    <div className="w-full h-full overflow-y-auto p-4 md:p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent mb-2">
            Withdraw Funds
          </h1>
          <p className="text-white/70">Request a withdrawal from your betting account</p>
        </div>

        {/* Current Balance */}
        <div className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-2xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-yellow-300/80 text-sm mb-1">Available Balance</div>
              <div className="text-3xl font-bold text-yellow-300">${userProfile.balance.toFixed(2)}</div>
            </div>
            <div className="w-16 h-16 rounded-full bg-yellow-500/30 flex items-center justify-center">
              <Wallet className="text-yellow-300" size={32} />
            </div>
          </div>
        </div>

        {/* Important Notice */}
        <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-orange-400 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <div className="font-bold text-orange-300 mb-1">Important Withdrawal Information</div>
              <ul className="text-sm text-orange-200/80 space-y-1">
                <li>• Minimum withdrawal: $25</li>
                <li>• Processing time: 1-3 business days</li>
                <li>• You may be required to verify your identity</li>
                <li>• Withdrawals can only be made to verified payment methods</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Withdraw Form */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          {/* Payment Methods Selection */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <Wallet size={16} />
              1. Select Withdrawal Method
            </label>
            <p className="text-white/60 text-sm mb-4">Choose where you want to receive your funds:</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <button
                onClick={() => setSelectedMethod('credit-card')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  selectedMethod === 'credit-card'
                    ? 'bg-gradient-to-br from-purple-500/30 to-pink-500/30 border-purple-400/50 shadow-lg shadow-purple-500/20'
                    : 'bg-white/5 border-white/20 hover:bg-white/10'
                }`}
              >
                <CreditCard className="mx-auto mb-2 text-white" size={32} />
                <div className="font-bold text-white mb-1">Credit/Debit Card</div>
                <div className="text-xs text-white/60">Visa, Mastercard</div>
                <div className="text-xs text-green-400 mt-1">2-3 days</div>
              </button>

              <button
                onClick={() => setSelectedMethod('cryptocurrency')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  selectedMethod === 'cryptocurrency'
                    ? 'bg-gradient-to-br from-orange-500/30 to-yellow-500/30 border-orange-400/50 shadow-lg shadow-orange-500/20'
                    : 'bg-white/5 border-white/20 hover:bg-white/10'
                }`}
              >
                <Bitcoin className="mx-auto mb-2 text-white" size={32} />
                <div className="font-bold text-white mb-1">Cryptocurrency</div>
                <div className="text-xs text-white/60">BTC, ETH, USDT, LTC</div>
                <div className="text-xs text-green-400 mt-1">Instant - 1 hour</div>
              </button>

              <button
                onClick={() => setSelectedMethod('e-wallet')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  selectedMethod === 'e-wallet'
                    ? 'bg-gradient-to-br from-blue-500/30 to-cyan-500/30 border-blue-400/50 shadow-lg shadow-blue-500/20'
                    : 'bg-white/5 border-white/20 hover:bg-white/10'
                }`}
              >
                <Smartphone className="mx-auto mb-2 text-white" size={32} />
                <div className="font-bold text-white mb-1">E-Wallets</div>
                <div className="text-xs text-white/60">PayPal, Apple Pay</div>
                <div className="text-xs text-green-400 mt-1">1-2 days</div>
              </button>
            </div>
          </div>

          {/* Amount Selection */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <DollarSign size={16} />
              2. Withdrawal Amount
            </label>
            <p className="text-white/60 text-sm mb-4">Select amount or enter custom (Min: $25):</p>
            
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
              {quickAmounts.map(value => (
                <button
                  key={value}
                  onClick={() => handleAmountSelect(value)}
                  disabled={value > userProfile.balance}
                  className={`py-3 rounded-lg font-bold transition-all ${
                    amount === value && !customAmount
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-500/30'
                      : value > userProfile.balance
                      ? 'bg-white/5 text-white/30 cursor-not-allowed'
                      : 'bg-white/10 text-white hover:bg-white/20'
                  }`}
                >
                  ${value}
                </button>
              ))}
            </div>

            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 text-xl font-bold">$</span>
              <Input
                type="number"
                value={customAmount}
                onChange={(e) => handleCustomAmountChange(e.target.value)}
                placeholder="Enter custom amount"
                max={userProfile.balance}
                className="pl-8 h-14 bg-white/5 border-white/20 text-white text-lg placeholder:text-white/40"
              />
            </div>
          </div>

          {/* Payment Details */}
          <div className="mb-6">
            {selectedMethod === 'credit-card' && (
              <div className="space-y-4">
                <div>
                  <Label className="text-white/90">Card Number (Last 4 digits for verification)</Label>
                  <Input
                    type="text"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    placeholder="**** **** **** 1234"
                    maxLength={19}
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                  <p className="text-xs text-white/50 mt-1">Funds will be returned to the card used for deposit</p>
                </div>
              </div>
            )}

            {selectedMethod === 'cryptocurrency' && (
              <div className="space-y-4">
                <div>
                  <Label className="text-white/90">Select Cryptocurrency</Label>
                  <select
                    value={selectedCrypto}
                    onChange={(e) => setSelectedCrypto(e.target.value)}
                    className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white"
                  >
                    <option value="BTC">Bitcoin (BTC)</option>
                    <option value="ETH">Ethereum (ETH)</option>
                    <option value="USDT">Tether (USDT)</option>
                    <option value="LTC">Litecoin (LTC)</option>
                  </select>
                </div>
                <div>
                  <Label className="text-white/90">Your Wallet Address</Label>
                  <Input
                    type="text"
                    value={cryptoWallet}
                    onChange={(e) => setCryptoWallet(e.target.value)}
                    placeholder="Enter your wallet address"
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                  <p className="text-xs text-white/50 mt-1">⚠️ Double-check your wallet address. Incorrect addresses cannot be recovered.</p>
                </div>
                <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-sm text-green-300">
                  <CheckCircle size={16} className="inline mr-2" />
                  Crypto withdrawals are processed within 1 hour
                </div>
              </div>
            )}

            {selectedMethod === 'e-wallet' && (
              <div className="space-y-4">
                <div>
                  <Label className="text-white/90">Select E-Wallet</Label>
                  <select
                    value={selectedEWallet}
                    onChange={(e) => setSelectedEWallet(e.target.value)}
                    className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white"
                  >
                    <option value="paypal">PayPal</option>
                    <option value="applepay">Apple Pay</option>
                  </select>
                </div>
                <div>
                  <Label className="text-white/90">Email Address</Label>
                  <Input
                    type="email"
                    value={eWalletEmail}
                    onChange={(e) => setEWalletEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                  <p className="text-xs text-white/50 mt-1">Must match your verified e-wallet email</p>
                </div>
              </div>
            )}
          </div>

          {/* Withdraw Button */}
          <Button
            onClick={handleWithdraw}
            disabled={isProcessing || amount <= 0 || amount < 25 || amount > userProfile.balance}
            className="w-full h-14 bg-gradient-to-r from-orange-400 via-red-500 to-pink-500 hover:from-orange-500 hover:via-red-600 hover:to-pink-600 text-white font-bold text-lg shadow-lg shadow-orange-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>Processing...</>
            ) : (
              <>Request Withdrawal ${amount.toFixed(2)} →</>
            )}
          </Button>

          {amount > userProfile.balance && (
            <p className="text-red-400 text-sm mt-2 text-center">
              Insufficient balance. Available: ${userProfile.balance.toFixed(2)}
            </p>
          )}
        </div>

        {/* Recent Withdrawals */}
        <div className="mt-6 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Recent Activity</h3>
          <div className="text-white/60 text-sm">
            Your latest transactions
          </div>
          <div className="mt-4 space-y-2">
            {/* This would be populated with actual transaction data */}
            <div className="text-white/50 text-sm text-center py-4">
              No recent withdrawals
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
