import React from 'react';
import { motion } from 'motion/react';
import { allStates } from '../data/lotteryData';

interface StateSelectorProps {
  onSelectState: (stateAbbr: string) => void;
}

export const StateSelector: React.FC<StateSelectorProps> = ({ onSelectState }) => {
  return (
    <div className="w-full">      
      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 2xl:grid-cols-13 gap-2 md:gap-3 max-h-[50vh] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-yellow-400/50 scrollbar-track-white/5">
        {allStates.map((state) => {
          const hasGames = state.lotteryCount > 0;
          return (
            <motion.button
              key={state.abbr}
              whileHover={hasGames ? { scale: 1.05 } : {}}
              whileTap={hasGames ? { scale: 0.95 } : {}}
              onClick={() => hasGames && onSelectState(state.abbr)}
              disabled={!hasGames}
              className={`relative aspect-square backdrop-blur-md border rounded-xl p-2 md:p-3 flex flex-col items-center justify-center gap-1 transition-all ${
                hasGames
                  ? 'bg-white/10 border-white/20 hover:bg-gradient-to-br hover:from-yellow-400/20 hover:to-orange-500/20 cursor-pointer group'
                  : 'bg-white/5 border-white/10 opacity-40 cursor-not-allowed'
              }`}
            >
              <div className={`text-xl md:text-2xl font-bold transition-colors ${
                hasGames ? 'text-white group-hover:text-yellow-400' : 'text-white/30'
              }`}>
                {state.abbr}
              </div>
              <div className={`text-[10px] md:text-xs transition-colors ${
                hasGames ? 'text-white/70 group-hover:text-white' : 'text-white/20'
              }`}>
                {hasGames ? `${state.lotteryCount} ${state.lotteryCount === 1 ? 'game' : 'games'}` : 'No games'}
              </div>
              
              {/* Golden glow on hover - only for active states */}
              {hasGames && (
                <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/0 to-orange-500/0 group-hover:from-yellow-400/10 group-hover:to-orange-500/10 rounded-xl transition-all" />
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};
