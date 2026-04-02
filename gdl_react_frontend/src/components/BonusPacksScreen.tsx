import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Check, Sparkles, DollarSign, TrendingUp } from 'lucide-react';
import { getBetOptionsForPickType, BetOption, calculatePotentialWinnings } from '../data/betRules';

interface BonusPacksScreenProps {
  pickType: 2 | 3 | 4 | 5;
  onSelectBets: (selectedBets: { betId: string; amount: number }[]) => void;
  onSkip: () => void;
  initialSelectedBets?: { betId: string; amount: number }[];
}

export const BonusPacksScreen: React.FC<BonusPacksScreenProps> = ({
  pickType,
  onSelectBets,
  onSkip,
  initialSelectedBets = []
}) => {
  // Initialize state with previously selected bets if available
  const [selectedBets, setSelectedBets] = useState<{ [betId: string]: number }>(() => {
    const initial: { [betId: string]: number } = {};
    initialSelectedBets.forEach(bet => {
      initial[bet.betId] = bet.amount;
    });
    return initial;
  });

  // Track pending amounts (typed but not yet added)
  const [pendingAmounts, setPendingAmounts] = useState<{ [betId: string]: string }>({});

  const availableBets = getBetOptionsForPickType(pickType);

  // Only show bonus bets and combo bets (exclude the main straight bet)
  const bonusBets = availableBets.filter(b => !b.id.includes('-straight') && !b.isCombo);
  const comboBets = availableBets.filter(b => b.isCombo);

  const addBet = (betId: string, bet: BetOption) => {
    const amount = pendingAmounts[betId] 
      ? Math.max(bet.minBet, parseInt(pendingAmounts[betId]) || bet.minBet)
      : bet.minBet;
    
    setSelectedBets(prev => ({
      ...prev,
      [betId]: amount
    }));
    
    // Clear pending amount
    setPendingAmounts(prev => {
      const newPending = { ...prev };
      delete newPending[betId];
      return newPending;
    });
  };

  const removeBet = (betId: string) => {
    setSelectedBets(prev => {
      const newState = { ...prev };
      delete newState[betId];
      return newState;
    });
    
    // Clear pending amount
    setPendingAmounts(prev => {
      const newPending = { ...prev };
      delete newPending[betId];
      return newPending;
    });
  };

  const handlePendingAmountChange = (betId: string, value: string) => {
    setPendingAmounts(prev => ({
      ...prev,
      [betId]: value
    }));
  };

  const handleSelectedAmountChange = (betId: string, value: string, minBet: number) => {
    if (value === '') {
      setSelectedBets(prev => ({
        ...prev,
        [betId]: minBet
      }));
      return;
    }
    
    const numValue = parseInt(value);
    if (!isNaN(numValue)) {
      setSelectedBets(prev => ({
        ...prev,
        [betId]: Math.max(minBet, numValue)
      }));
    }
  };

  const handleContinue = () => {
    const selectedBetsArray = Object.entries(selectedBets).map(([betId, amount]) => ({
      betId,
      amount
    }));
    onSelectBets(selectedBetsArray);
  };

  const getTotalCost = () => {
    return Object.entries(selectedBets).reduce((total, [betId, amount]) => {
      const bet = availableBets.find(b => b.id === betId);
      if (bet?.isCombo) {
        return total + (bet.comboCost || 0);
      }
      return total + amount;
    }, 0);
  };

  const getTotalPotentialWinnings = () => {
    return Object.entries(selectedBets).reduce((total, [betId, amount]) => {
      const bet = availableBets.find(b => b.id === betId);
      if (bet) {
        return total + calculatePotentialWinnings(bet, amount);
      }
      return total;
    }, 0);
  };

  const renderBetCard = (bet: BetOption) => {
    const isSelected = !!selectedBets[bet.id];
    const betAmount = selectedBets[bet.id] || bet.minBet;
    const potentialWin = calculatePotentialWinnings(bet, betAmount);
    const isCombo = bet.isCombo;

    return (
      <motion.div
        key={bet.id}
        whileHover={{ scale: 1.02 }}
        className={`relative bg-white/10 backdrop-blur-md border-2 rounded-lg p-3 transition-all ${
          isSelected
            ? 'border-yellow-400 bg-gradient-to-br from-yellow-400/20 to-orange-500/20'
            : 'border-white/20 hover:border-white/40'
        }`}
      >
        {/* Checkmark Badge */}
        {isSelected && (
          <div className="absolute top-2 right-2 w-5 h-5 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center z-10">
            <Check className="w-3 h-3 text-black" />
          </div>
        )}

        {/* Bet Name */}
        <div className="mb-2">
          <h3 className="text-sm font-bold text-white mb-0.5 flex items-center gap-1 flex-wrap">
            {bet.name}
            {isCombo && (
              <span className="text-[9px] px-1.5 py-0.5 bg-purple-500/30 text-purple-300 rounded-full border border-purple-400/50">
                COMBO
              </span>
            )}
          </h3>
          
          {/* Description */}
          <p className="text-white/60 text-[10px] mb-1.5">
            {bet.description}
          </p>

          {/* Odds Display */}
          {!isCombo ? (
            <div className="flex items-center gap-2 text-[10px]">
              <div className="text-cyan-400">
                <span className="text-white/50">Odds:</span> {bet.trueOdds}
              </div>
              <div className="text-green-400">
                <span className="text-white/50">Pays:</span> ${bet.payout}
              </div>
            </div>
          ) : (
            <div className="text-[10px] text-purple-300">
              <span className="text-white/50">Bundle:</span> ${bet.comboCost}
            </div>
          )}
        </div>

        {/* Combo Breakdown */}
        {isCombo && bet.comboIncludes && (
          <div className="mb-2 p-1.5 bg-white/5 rounded border border-white/10">
            <p className="text-[9px] text-white/50 mb-0.5">Includes:</p>
            <div className="text-[9px] text-white/70">
              {bet.comboIncludes.map((includedId, idx) => {
                const includedBet = availableBets.find(b => b.id === includedId);
                return (
                  <div key={idx}>• {includedBet?.name}</div>
                );
              })}
            </div>
          </div>
        )}

        {/* Bet Amount Input & Potential Win (only for non-combo bets) */}
        {!isCombo ? (
          <div className="space-y-1.5">
            {/* Bet Amount Input */}
            <div className="flex items-center gap-1">
              <label className="text-[10px] text-white/70 whitespace-nowrap">Amount:</label>
              <div className="flex items-center flex-1 bg-white/10 rounded border border-white/20 overflow-hidden">
                <span className="text-white text-xs px-1.5">$</span>
                <input
                  type="number"
                  min={bet.minBet}
                  value={isSelected ? betAmount : (pendingAmounts[bet.id] || '')}
                  onChange={(e) => {
                    if (isSelected) {
                      handleSelectedAmountChange(bet.id, e.target.value, bet.minBet);
                    } else {
                      handlePendingAmountChange(bet.id, e.target.value);
                    }
                  }}
                  className="flex-1 bg-transparent text-white px-1 py-1 text-xs focus:outline-none"
                  placeholder={`${bet.minBet}`}
                />
              </div>
            </div>

            {/* Potential Win Display */}
            {isSelected && (
              <div className="flex items-center justify-between p-1.5 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded">
                <span className="text-[10px] text-green-300">Win:</span>
                <span className="text-xs font-bold text-green-300">${potentialWin.toFixed(2)}</span>
              </div>
            )}
          </div>
        ) : (
          /* Fixed Cost for Combo Bets */
          isSelected && (
            <div className="flex items-center justify-between p-1.5 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded">
              <span className="text-[10px] text-green-300">Max Win:</span>
              <span className="text-xs font-bold text-green-300">${potentialWin.toFixed(2)}</span>
            </div>
          )
        )}

        {/* Toggle Button */}
        <button
          onClick={() => {
            if (isSelected) {
              removeBet(bet.id);
            } else {
              addBet(bet.id, bet);
            }
          }}
          className={`w-full mt-2 py-1.5 rounded font-semibold text-xs transition-all ${
            isSelected
              ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black hover:shadow-lg'
              : 'bg-white/10 text-white/70 hover:bg-white/20'
          }`}
        >
          {isSelected ? 'Remove' : 'Add'}
        </button>
      </motion.div>
    );
  };

  return (
    <div className="w-full h-full overflow-y-auto">
      <div className="max-w-7xl mx-auto p-3 md:p-4">
        <div className="text-center mb-4">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="inline-block mb-2"
          >
            <Sparkles className="w-10 h-10 md:w-12 md:h-12 text-yellow-400" />
          </motion.div>
          
          <h2 className="text-xl md:text-2xl font-bold text-white mb-1">
            Select Bonus Bets
          </h2>
          <p className="text-white/70 text-xs md:text-sm mb-3">
            Add bonus bets to maximize your winning potential on Pick {pickType}
          </p>

          {/* Summary Bar */}
          {Object.keys(selectedBets).length > 0 && (
            <div className="max-w-md mx-auto p-3 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-xl">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-white/70">Bets Selected:</span>
                <span className="font-bold text-white">{Object.keys(selectedBets).length}</span>
              </div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-white/70">Total Cost:</span>
                <span className="font-bold text-yellow-300">${getTotalCost().toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/70">Max Win:</span>
                <span className="text-lg font-bold text-green-300">${getTotalPotentialWinnings().toFixed(2)}</span>
              </div>
            </div>
          )}
        </div>

        {/* Bonus Bets */}
        {bonusBets.length > 0 && (
          <div className="mb-4">
            <h3 className="text-base font-bold text-white mb-2 px-1">Bonus Bets</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2 md:gap-3">
              {bonusBets.map(bet => renderBetCard(bet))}
            </div>
          </div>
        )}

        {/* Combo Bets */}
        {comboBets.length > 0 && (
          <div className="mb-4">
            <h3 className="text-base font-bold text-white mb-2 px-1 flex items-center gap-2">
              Combo Bets 
              <span className="text-[10px] px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded-full border border-purple-400/50">
                Best Value!
              </span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 md:gap-3">
              {comboBets.map(bet => renderBetCard(bet))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 mt-4">
          <button
            onClick={onSkip}
            className="flex-1 px-4 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-white font-bold transition-all text-sm"
          >
            Skip Bonus Bets
          </button>
          <button
            onClick={handleContinue}
            disabled={Object.keys(selectedBets).length === 0}
            className={`flex-1 px-4 py-3 rounded-xl text-white font-bold shadow-xl transition-all text-sm md:text-base ${
              Object.keys(selectedBets).length > 0
                ? 'bg-gradient-to-r from-yellow-400 to-orange-500 hover:shadow-2xl'
                : 'bg-white/5 cursor-not-allowed opacity-50'
            }`}
          >
            {Object.keys(selectedBets).length > 0
              ? `Continue ($${getTotalCost().toFixed(2)})`
              : 'Select Bonus Bets'}
          </button>
        </div>
      </div>
    </div>
  );
};