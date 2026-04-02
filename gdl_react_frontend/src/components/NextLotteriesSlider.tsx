import React from 'react';
import { motion } from 'motion/react';
import { ChevronLeft, ChevronRight, Clock, DollarSign } from 'lucide-react';
import { LotteryGame } from '../data/lotteryData';

interface NextLotteriesSliderProps {
  lotteries: LotteryGame[];
  currentPage: number;
  onPageChange: (page: number) => void;
  itemsPerPage?: number;
  onLotterySelect?: (lottery: LotteryGame) => void;
}

export const NextLotteriesSlider: React.FC<NextLotteriesSliderProps> = ({
  lotteries,
  currentPage,
  onPageChange,
  itemsPerPage = 4,
  onLotterySelect
}) => {
  const totalPages = Math.ceil(lotteries.length / itemsPerPage);
  const startIndex = currentPage * itemsPerPage;
  const visibleLotteries = lotteries.slice(startIndex, startIndex + itemsPerPage);

  const canGoPrev = currentPage > 0;
  const canGoNext = currentPage < totalPages - 1;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3 md:mb-4">
        <h3 className="text-lg md:text-xl lg:text-2xl font-bold text-white">
          Next Draws
        </h3>
        <div className="text-white/70 text-xs md:text-sm">
          {startIndex + 1}-{Math.min(startIndex + itemsPerPage, lotteries.length)} of {lotteries.length}
        </div>
      </div>

      <div className="relative">
        {/* Navigation Buttons */}
        <button
          onClick={() => canGoPrev && onPageChange(currentPage - 1)}
          disabled={!canGoPrev}
          className={`absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 z-10 w-8 h-8 md:w-10 md:h-10 rounded-full bg-black/80 backdrop-blur-md border border-white/20 flex items-center justify-center transition-all ${
            canGoPrev
              ? 'hover:bg-white/20 hover:scale-110 cursor-pointer'
              : 'opacity-30 cursor-not-allowed'
          }`}
        >
          <ChevronLeft className="w-4 h-4 md:w-5 md:h-5 text-white" />
        </button>

        <button
          onClick={() => canGoNext && onPageChange(currentPage + 1)}
          disabled={!canGoNext}
          className={`absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-10 w-8 h-8 md:w-10 md:h-10 rounded-full bg-black/80 backdrop-blur-md border border-white/20 flex items-center justify-center transition-all ${
            canGoNext
              ? 'hover:bg-white/20 hover:scale-110 cursor-pointer'
              : 'opacity-30 cursor-not-allowed'
          }`}
        >
          <ChevronRight className="w-4 h-4 md:w-5 md:h-5 text-white" />
        </button>

        {/* Lottery Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 md:gap-3 lg:gap-4 px-4 md:px-6">
          {visibleLotteries.map((lottery, index) => (
            <motion.div
              key={lottery.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onLotterySelect?.(lottery)}
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-2.5 md:p-4 lg:p-5 hover:bg-white/10 hover:border-yellow-400/50 transition-all group cursor-pointer"
            >
              {/* State Badge */}
              <div className="flex items-center justify-between mb-2 md:mb-3">
                <div className="px-1.5 md:px-2 py-0.5 md:py-1 bg-blue-500 rounded text-white text-[9px] md:text-xs font-bold">
                  {lottery.stateAbbr}
                </div>
                <div className="px-1.5 md:px-2 py-0.5 md:py-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded text-black text-[9px] md:text-xs font-bold">
                  Pick {lottery.pickType}
                </div>
              </div>

              {/* Lottery Name */}
              <h4 className="font-bold text-white text-[11px] md:text-base mb-1.5 md:mb-2 group-hover:text-yellow-400 transition-colors line-clamp-2">
                {lottery.name}
              </h4>

              {/* Draw Time */}
              <div className="flex items-center gap-1 md:gap-2 text-white/70 text-[9px] md:text-xs mb-1.5 md:mb-2">
                <Clock className="w-2.5 h-2.5 md:w-3 md:h-3 flex-shrink-0" />
                <span className="truncate">{lottery.nextDraw}</span>
              </div>

              {/* Jackpot */}
              <div className="flex items-center gap-1 text-yellow-400 text-[10px] md:text-sm font-bold">
                <DollarSign className="w-3 h-3 md:w-4 md:h-4" />
                <span>{lottery.jackpot.toLocaleString()}</span>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Page Indicators */}
        <div className="flex items-center justify-center gap-2 mt-4">
          {Array.from({ length: totalPages }).map((_, index) => (
            <button
              key={index}
              onClick={() => onPageChange(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentPage
                  ? 'bg-yellow-400 w-6'
                  : 'bg-white/30 hover:bg-white/50'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};