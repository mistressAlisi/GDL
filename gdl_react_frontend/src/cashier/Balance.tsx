import React from 'react';
import { motion } from 'motion/react';
import { 
  Wallet, 
  Gift, 
  Clock, 
  TrendingUp,
  DollarSign,
  Plus,
  Minus,
  FileText,
  CheckCircle,
  Diamond
} from 'lucide-react';

export interface BalanceData {
  availableBalance: number;
  freePlay: number;
  currentBalance: number;
  pendingBalance: number;
  pendingRollover: number;
}

export interface BalanceProps {
  balanceData: BalanceData;
  onAddFunds?: () => void;
  onWithdraw?: () => void;
  onOpenTickets?: () => void;
  onGradedTickets?: () => void;
  onSportsLottoClick?: () => void;
}

export const Balance: React.FC<BalanceProps> = ({
  balanceData,
  onAddFunds,
  onWithdraw,
  onOpenTickets,
  onGradedTickets,
  onSportsLottoClick
}) => {
  const {
    availableBalance,
    freePlay,
    currentBalance,
    pendingBalance,
    pendingRollover
  } = balanceData;

  return (
    <div className="w-full h-full min-h-screen bg-gradient-to-br from-purple-900 via-black to-orange-900 overflow-y-auto">
      <div className="max-w-6xl mx-auto p-3 sm:p-4 md:p-6 pb-8">
        {/* Header */}
        <div className="mb-4 md:mb-6">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent mb-1 md:mb-2">
            Account Balance
          </h1>
          <p className="text-white/70 text-xs sm:text-sm md:text-base">View your funds and betting balances</p>
        </div>

        {/* Top Cards - Available Balance & Free Play */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 md:gap-4 mb-4 md:mb-6">
          {/* Available Balance */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 backdrop-blur-md border border-gray-700/50 rounded-xl md:rounded-2xl p-6 md:p-8 relative overflow-hidden"
          >
            {/* Purple glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-transparent pointer-events-none" />
            
            <div className="relative z-10">
              <div className="text-gray-300/90 text-sm md:text-base mb-3">Available Balance</div>
              <div className="text-4xl sm:text-5xl md:text-6xl font-bold text-transparent bg-gradient-to-r from-purple-300 via-purple-200 to-purple-300 bg-clip-text mb-3 drop-shadow-[0_0_20px_rgba(168,85,247,0.5)]">
                ${availableBalance.toFixed(2)}
              </div>
              <div className="text-gray-400 text-xs md:text-sm">Your current available funds</div>
            </div>
          </motion.div>

          {/* Free Play */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="bg-gradient-to-br from-emerald-800/60 to-teal-900/60 backdrop-blur-md border border-emerald-600/40 rounded-xl md:rounded-2xl p-6 md:p-8 relative overflow-hidden"
          >
            {/* Green glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-400/20 via-transparent to-transparent pointer-events-none" />
            
            <div className="relative z-10">
              <div className="text-emerald-200/90 text-sm md:text-base mb-3">Free Play</div>
              <div className="text-4xl sm:text-5xl md:text-6xl font-bold text-emerald-100 mb-3 drop-shadow-[0_0_20px_rgba(52,211,153,0.4)]">
                ${freePlay.toFixed(2)}
              </div>
              <div className="text-emerald-300/80 text-xs md:text-sm">Use for wagers</div>
            </div>
          </motion.div>
        </div>

        {/* Middle Cards - Current, Pending, Rollover */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 mb-4 md:mb-6">
          {/* Current Balance */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className="bg-gradient-to-br from-purple-800/40 to-pink-800/40 backdrop-blur-md border border-purple-600/30 rounded-xl p-5 md:p-6 relative overflow-hidden"
          >
            <div className="absolute top-4 right-4">
              <Diamond className="w-5 h-5 md:w-6 md:h-6 text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.6)]" />
            </div>
            
            {/* Pink/Purple icon square */}
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-gradient-to-br from-pink-400 to-pink-500 mb-3 md:mb-4" />
            
            <div className="text-purple-200/90 text-xs md:text-sm mb-2">Current Balance</div>
            <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1">
              ${currentBalance.toFixed(2)}
            </div>
            <div className="text-purple-300/70 text-xs">Total funds in account</div>
          </motion.div>

          {/* Pending Balance */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            className="bg-gradient-to-br from-blue-800/40 to-indigo-800/40 backdrop-blur-md border border-blue-600/30 rounded-xl p-5 md:p-6 relative overflow-hidden"
          >
            <div className="absolute top-4 right-4">
              <Diamond className="w-5 h-5 md:w-6 md:h-6 text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.6)]" />
            </div>
            
            {/* Blue icon square */}
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-gradient-to-br from-blue-400 to-blue-500 mb-3 md:mb-4" />
            
            <div className="text-blue-200/90 text-xs md:text-sm mb-2">Pending Balance</div>
            <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1">
              ${pendingBalance.toFixed(2)}
            </div>
            <div className="text-blue-300/70 text-xs">Tickets awaiting settlement</div>
          </motion.div>

          {/* Pending Rollover */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.4 }}
            className="bg-gradient-to-br from-orange-800/40 to-amber-800/40 backdrop-blur-md border border-orange-600/30 rounded-xl p-5 md:p-6 relative overflow-hidden sm:col-span-2 lg:col-span-1"
          >
            <div className="absolute top-4 right-4">
              <Diamond className="w-5 h-5 md:w-6 md:h-6 text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.6)]" />
            </div>
            
            {/* Orange icon square */}
            <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-gradient-to-br from-orange-400 to-orange-500 mb-3 md:mb-4" />
            
            <div className="text-orange-200/90 text-xs md:text-sm mb-2">Pending Rollover</div>
            <div className="text-2xl sm:text-3xl md:text-4xl font-bold text-white mb-1">
              ${pendingRollover.toFixed(2)}
            </div>
            <div className="text-orange-300/70 text-xs">Pending rollover</div>
          </motion.div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-2 md:gap-3 mb-4 md:mb-6">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onAddFunds}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-3 md:py-4 px-4 md:px-6 rounded-lg md:rounded-xl shadow-lg shadow-green-500/30 transition-all flex items-center justify-center gap-2 text-sm md:text-base"
          >
            <DollarSign className="w-4 h-4 md:w-5 md:h-5" />
            Add Funds
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onWithdraw}
            className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold py-3 md:py-4 px-4 md:px-6 rounded-lg md:rounded-xl shadow-lg shadow-red-500/30 transition-all flex items-center justify-center gap-2 text-sm md:text-base"
          >
            <TrendingUp className="w-4 h-4 md:w-5 md:h-5" />
            Withdraw
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onOpenTickets}
            className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-3 md:py-4 px-4 md:px-6 rounded-lg md:rounded-xl shadow-lg shadow-blue-500/30 transition-all flex items-center justify-center gap-2 text-sm md:text-base"
          >
            <FileText className="w-4 h-4 md:w-5 md:h-5" />
            Open Tickets
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onGradedTickets}
            className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-bold py-3 md:py-4 px-4 md:px-6 rounded-lg md:rounded-xl shadow-lg shadow-purple-500/30 transition-all flex items-center justify-center gap-2 text-sm md:text-base"
          >
            <CheckCircle className="w-4 h-4 md:w-5 md:h-5" />
            Graded Tickets
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onSportsLottoClick}
            className="bg-gradient-to-r from-yellow-500 via-yellow-400 to-yellow-500 hover:from-yellow-600 hover:via-yellow-500 hover:to-yellow-600 text-black font-bold py-3 md:py-4 px-4 md:px-6 rounded-lg md:rounded-xl shadow-lg shadow-yellow-500/50 transition-all flex items-center justify-center gap-2 text-sm md:text-base"
          >
            <span className="text-xl">⚽</span>
            SPORTSLOTTO
          </motion.button>
        </div>

        {/* Balance Breakdown */}
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.5 }}
          className="bg-gradient-to-br from-gray-900/80 to-black/80 backdrop-blur-md border border-gray-700/50 rounded-xl md:rounded-2xl p-5 md:p-6"
        >
          <div className="flex items-center gap-2 mb-4 md:mb-5">
            <Wallet className="w-5 h-5 md:w-6 md:h-6 text-gray-300" />
            <h2 className="text-lg md:text-xl font-bold text-white">Balance Breakdown</h2>
          </div>

          <div className="space-y-3 md:space-y-4">
            {/* Current Balance */}
            <div className="flex items-center justify-between py-2 border-b border-gray-700/50">
              <span className="text-white/90 text-sm md:text-base">Current Balance:</span>
              <span className="text-white font-bold text-sm md:text-base">${currentBalance.toFixed(2)}</span>
            </div>

            {/* Pending (Locked) */}
            <div className="flex items-center justify-between py-2 border-b border-gray-700/50">
              <span className="text-yellow-400/90 text-sm md:text-base">Pending (Locked):</span>
              <span className="text-yellow-400 font-bold text-sm md:text-base">-${pendingBalance.toFixed(2)}</span>
            </div>

            {/* Divider */}
            <div className="border-t border-gray-600/50 pt-3 md:pt-4">
              {/* Available for Betting */}
              <div className="flex items-center justify-between py-2 mb-3">
                <span className="text-green-400/90 font-semibold text-sm md:text-base">Available for Betting:</span>
                <span className="text-green-400 font-bold text-base md:text-lg">${availableBalance.toFixed(2)}</span>
              </div>

              {/* Bonus / Free Play */}
              <div className="flex items-center justify-between py-2">
                <span className="text-emerald-400/90 font-semibold text-sm md:text-base">Bonus / Free Play:</span>
                <span className="text-emerald-400 font-bold text-base md:text-lg">${freePlay.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Balance;