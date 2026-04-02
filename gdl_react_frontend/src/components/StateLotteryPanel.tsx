import React from 'react';
import { motion } from 'motion/react';
import { X, Clock } from 'lucide-react';
import { getLotteriesByState, LotteryGame } from '../data/lotteryData';

interface StateLotteryPanelProps {
  stateAbbr: string;
  onClose: () => void;
  onSelectLottery: (lottery: LotteryGame) => void;
}

export const StateLotteryPanel: React.FC<StateLotteryPanelProps> = ({
  stateAbbr,
  onClose,
  onSelectLottery
}) => {
  const lotteries = getLotteriesByState(stateAbbr);

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
      />

      {/* Panel */}
      <motion.div
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        exit={{ y: "100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed bottom-0 left-0 right-0 bg-gradient-to-br from-purple-900/95 via-black/95 to-orange-900/95 backdrop-blur-xl border-t-2 border-white/20 z-50 max-h-[70vh] md:max-h-[75vh] lg:max-h-[80vh] overflow-y-auto"
      >
        <div className="p-3 sm:p-4 md:p-5 lg:p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-3 md:mb-4 lg:mb-6">
            <div>
              <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-white">
                {stateAbbr} Lotteries
              </h2>
              <p className="text-white/70 text-xs sm:text-sm md:text-base mt-1">
                {lotteries.length} available {lotteries.length === 1 ? 'game' : 'games'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 sm:p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </button>
          </div>

          {/* Lotteries Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
            {lotteries.map((lottery) => (
              <motion.button
                key={lottery.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onSelectLottery(lottery)}
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 text-left hover:bg-white/10 hover:border-yellow-400/50 transition-all group"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-bold text-white text-base md:text-lg group-hover:text-yellow-400 transition-colors">
                    {lottery.name}
                  </h3>
                  <div className="px-2 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-md text-black text-xs font-bold">
                    Pick {lottery.pickType}
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-white/70 text-sm">
                  <Clock className="w-4 h-4" />
                  <span>{lottery.drawTime}</span>
                </div>
                
                <div className="mt-2 text-white/60 text-xs">
                  Next Draw: <span className="text-white font-semibold">{lottery.nextDraw}</span>
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>
    </>
  );
};