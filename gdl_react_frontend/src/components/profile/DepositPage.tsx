import React, { useState } from 'react';
import { motion } from 'motion/react';
import { CreditCard, Wallet, Building2, Smartphone, Gift, DollarSign, Bitcoin, AlertCircle, TrendingUp } from 'lucide-react';
import { useProfile, PaymentMethod } from '../../contexts/ProfileContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

const quickAmounts = [25, 50, 100, 250, 500, 1000];

export const DepositPage: React.FC = () => {
  const { userProfile, addTransaction } = useProfile();
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>('credit-card');
  const [amount, setAmount] = useState<number>(50);
  const [customAmount, setCustomAmount] = useState<string>('');
  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
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

  const handleDeposit = async () => {
    if (amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    // Validate based on payment method
    if (selectedMethod === 'credit-card') {
      if (!cardNumber || !cardName || !expiryDate || !cvv) {
        alert('Please fill in all card details');
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
        type: 'deposit',
        amount,
        paymentMethod: selectedMethod,
        status: 'completed',
        timestamp: new Date(),
        description: `Deposit via ${selectedMethod === 'credit-card' ? 'Credit/Debit Card' : selectedMethod === 'cryptocurrency' ? 'Cryptocurrency' : 'E-Wallet'}`,
      });

      setIsProcessing(false);
      alert(`Successfully deposited $${amount.toFixed(2)}!`);
      
      // Reset form
      setAmount(50);
      setCustomAmount('');
      setCardNumber('');
      setCardName('');
      setExpiryDate('');
      setCvv('');
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
            Deposit Funds
          </h1>
          <p className="text-white/70">Add funds to your betting account</p>
        </div>

        {/* Current Balance */}
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-2xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-green-300/80 text-sm mb-1">Current Balance</div>
              <div className="text-3xl font-bold text-green-300">${userProfile.balance.toFixed(2)}</div>
            </div>
            <div className="w-16 h-16 rounded-full bg-green-500/30 flex items-center justify-center">
              <Wallet className="text-green-300" size={32} />
            </div>
          </div>
        </div>

        {/* Bonus Offer */}
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
              <p className="text-white/90 mb-3">Get 20% match on your first deposit</p>
              <div className="text-2xl font-bold bg-gradient-to-r from-yellow-200 to-orange-300 bg-clip-text text-transparent">
                Up to $500 🎰
              </div>
              <button className="mt-3 px-6 py-2 bg-gradient-to-r from-green-400 to-emerald-500 hover:from-green-500 hover:to-emerald-600 rounded-full text-white font-bold shadow-lg shadow-green-500/30 transition-all">
                <Gift size={16} className="inline mr-2" />
                Claim Bonus Now →
              </button>
            </div>
          </div>
        </motion.div>

        {/* Deposit Form */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          {/* Payment Methods Selection */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <AlertCircle size={16} />
              1. Payment Methods
            </label>
            <p className="text-white/60 text-sm mb-4">Select your preferred funding method:</p>
            
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
              </button>
            </div>
          </div>

          {/* Amount Selection */}
          <div className="mb-6">
            <label className="block text-white/90 font-semibold mb-3 flex items-center gap-2">
              <DollarSign size={16} />
              2. Deposit Amount
            </label>
            <p className="text-white/60 text-sm mb-4">Select amount or enter custom:</p>
            
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
              {quickAmounts.map(value => (
                <button
                  key={value}
                  onClick={() => handleAmountSelect(value)}
                  className={`py-3 rounded-lg font-bold transition-all ${
                    amount === value && !customAmount
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-500/30'
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
                className="pl-8 h-14 bg-white/5 border-white/20 text-white text-lg placeholder:text-white/40"
              />
            </div>
          </div>

          {/* Payment Details */}
          <div className="mb-6">
            {selectedMethod === 'credit-card' && (
              <div className="space-y-4">
                <div>
                  <Label className="text-white/90">Card Number</Label>
                  <Input
                    type="text"
                    value={cardNumber}
                    onChange={(e) => setCardNumber(e.target.value)}
                    placeholder="1234 5678 9012 3456"
                    maxLength={19}
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                </div>
                <div>
                  <Label className="text-white/90">Cardholder Name</Label>
                  <Input
                    type="text"
                    value={cardName}
                    onChange={(e) => setCardName(e.target.value)}
                    placeholder="John Doe"
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white/90">Expiry Date</Label>
                    <Input
                      type="text"
                      value={expiryDate}
                      onChange={(e) => setExpiryDate(e.target.value)}
                      placeholder="MM/YY"
                      maxLength={5}
                      className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                    />
                  </div>
                  <div>
                    <Label className="text-white/90">CVV</Label>
                    <Input
                      type="text"
                      value={cvv}
                      onChange={(e) => setCvv(e.target.value)}
                      placeholder="123"
                      maxLength={4}
                      className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                    />
                  </div>
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
                  <Label className="text-white/90">Wallet Address</Label>
                  <Input
                    type="text"
                    value={cryptoWallet}
                    onChange={(e) => setCryptoWallet(e.target.value)}
                    placeholder="Enter your wallet address"
                    className="bg-white/5 border-white/20 text-white placeholder:text-white/40"
                  />
                </div>
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-sm text-blue-300">
                  <TrendingUp size={16} className="inline mr-2" />
                  Use crypto for 0% fees and faster processing
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
                </div>
              </div>
            )}
          </div>

          {/* Pro Tips */}
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

          {/* Deposit Button */}
          <Button
            onClick={handleDeposit}
            disabled={isProcessing || amount <= 0}
            className="w-full h-14 bg-gradient-to-r from-green-400 via-emerald-500 to-cyan-500 hover:from-green-500 hover:via-emerald-600 hover:to-cyan-600 text-white font-bold text-lg shadow-lg shadow-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? (
              <>Processing...</>
            ) : (
              <>Deposit ${amount.toFixed(2)} →</>
            )}
          </Button>
        </div>
      </motion.div>
    </div>
  );
};
