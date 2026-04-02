import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ShoppingCart, X, ChevronDown, ChevronUp, Trash2 } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useProfile } from '../contexts/ProfileContext';
import { useTranslation } from '../utils/translations';
import { getBetOptionsForPickType, calculatePotentialWinnings } from '../data/betRules';

interface CartPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onCheckout?: () => void;
}

export const CartPanel: React.FC<CartPanelProps> = ({ isOpen, onClose, onCheckout }) => {
  const { cart, removeFromCart, getCartTotal, getCartByPickType, clearCart } = useCart();
  const { userProfile } = useProfile();
  const t = useTranslation(userProfile.language);
  const [expandedPickTypes, setExpandedPickTypes] = useState<Set<number>>(new Set());

  const togglePickType = (pickType: number) => {
    setExpandedPickTypes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(pickType)) {
        newSet.delete(pickType);
      } else {
        newSet.add(pickType);
      }
      return newSet;
    });
  };

  const cartByPickType = getCartByPickType();
  const sortedPickTypes = Object.keys(cartByPickType)
    .map(Number)
    .sort((a, b) => a - b);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[55]"
      />

      {/* Cart Panel */}
      <motion.div
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="fixed right-0 top-0 h-full w-full md:w-96 lg:w-[420px] xl:w-[480px] bg-gradient-to-br from-purple-900/95 via-black/95 to-orange-900/95 backdrop-blur-xl border-l-2 border-white/20 z-[60] flex flex-col"
      >
        {/* Header */}
        <div className="p-3 sm:p-4 md:p-5 lg:p-6 border-b border-white/10">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 sm:gap-3">
              <ShoppingCart className="w-5 h-5 sm:w-6 sm:h-6 text-yellow-400" />
              <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white">{t('cart')}</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 sm:p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-white/70 text-xs sm:text-sm">
              {cart.length} {cart.length === 1 ? 'bet' : 'bets'} in cart
            </p>
            {cart.length > 0 && sortedPickTypes.length > 1 && (
              <button
                onClick={() => {
                  if (expandedPickTypes.size === sortedPickTypes.length) {
                    // Collapse all
                    setExpandedPickTypes(new Set());
                  } else {
                    // Expand all
                    setExpandedPickTypes(new Set(sortedPickTypes));
                  }
                }}
                className="text-xs sm:text-sm text-yellow-400 hover:text-yellow-300 font-semibold transition-colors flex items-center gap-1"
              >
                {expandedPickTypes.size === sortedPickTypes.length ? (
                  <>
                    <ChevronUp className="w-3 h-3 sm:w-4 sm:h-4" />
                    Collapse All
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4" />
                    Expand All
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-5 lg:p-6">
          {cart.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <ShoppingCart className="w-16 h-16 text-white/20 mb-4" />
              <p className="text-white/50 text-lg">Your cart is empty</p>
              <p className="text-white/30 text-sm mt-2">Add bets to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sortedPickTypes.map(pickType => {
                const items = cartByPickType[pickType];
                const isExpanded = expandedPickTypes.has(pickType);
                
                // Sort items by state within pick type
                const sortedItems = [...items].sort((a, b) => 
                  a.lottery.stateAbbr.localeCompare(b.lottery.stateAbbr)
                );

                return (
                  <div key={pickType} className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden">
                    {/* Pick Type Header */}
                    <button
                      onClick={() => togglePickType(pickType)}
                      className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="px-3 py-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-md text-black text-sm font-bold">
                          Pick {pickType}
                        </div>
                        <span className="text-white font-semibold">
                          {items.length} {items.length === 1 ? 'bet' : 'bets'}
                        </span>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-white" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-white" />
                      )}
                    </button>

                    {/* Expanded Items */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: "auto" }}
                          exit={{ height: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="p-2 space-y-2 bg-black/20">
                            {sortedItems.map((item) => (
                              <div
                                key={item.id}
                                className="bg-white/5 rounded-lg p-3 border border-white/5"
                              >
                                {/* State & Lottery */}
                                <div className="flex items-start justify-between mb-2">
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <span className="px-2 py-0.5 bg-blue-500 rounded text-white text-xs font-bold">
                                        {item.lottery.stateAbbr}
                                      </span>
                                      <span className="text-white text-sm font-semibold">
                                        {item.lottery.name}
                                      </span>
                                    </div>
                                    <div className="text-white/50 text-xs mt-1">
                                      {item.betType}
                                    </div>
                                  </div>
                                  <button
                                    onClick={() => removeFromCart(item.id)}
                                    className="p-1 hover:bg-red-500/20 rounded transition-colors"
                                  >
                                    <Trash2 className="w-4 h-4 text-red-400" />
                                  </button>
                                </div>

                                {/* Numbers */}
                                <div className="flex flex-wrap gap-1 mb-2">
                                  {item.numbers.map((row, idx) => (
                                    <div key={idx} className="flex gap-1">
                                      {row.map((num, numIdx) => (
                                        <div
                                          key={numIdx}
                                          className="w-7 h-7 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-black font-bold text-xs"
                                        >
                                          {num}
                                        </div>
                                      ))}
                                    </div>
                                  ))}
                                </div>

                                {/* Bonus Bets */}
                                {(item.bonusBets && item.bonusBets.length > 0) && (() => {
                                  const availableBets = getBetOptionsForPickType(item.lottery.pickType);
                                  const bonusBetsCost = item.bonusBets.reduce((sum, b) => sum + b.amount, 0);
                                  const bonusBetsWin = item.bonusBets.reduce((sum, selectedBet) => {
                                    const bet = availableBets.find(b => b.id === selectedBet.betId);
                                    return sum + (bet ? calculatePotentialWinnings(bet, selectedBet.amount) : 0);
                                  }, 0);
                                  
                                  return (
                                    <div className="text-xs mb-2 p-2 bg-yellow-400/10 rounded border border-yellow-400/20">
                                      <div className="flex justify-between items-center mb-1">
                                        <span className="text-yellow-400 font-semibold">
                                          +{item.bonusBets.length} Bonus {item.bonusBets.length === 1 ? 'Bet' : 'Bets'}
                                        </span>
                                        <span className="text-yellow-300 text-[10px]">${bonusBetsCost.toFixed(2)}</span>
                                      </div>
                                      <div className="text-[10px] text-green-300/80">
                                        Max Win: ${bonusBetsWin.toFixed(2)}
                                      </div>
                                    </div>
                                  );
                                })()}
                                {/* Legacy Bonus Packs support */}
                                {(item.bonusPacks && item.bonusPacks.length > 0) && (
                                  <div className="text-xs text-yellow-400 mb-2">
                                    +{item.bonusPacks.length} Bonus {item.bonusPacks.length === 1 ? 'Pack' : 'Packs'}
                                  </div>
                                )}

                                {/* Cost */}
                                <div className="flex items-center justify-between text-xs">
                                  <span className="text-white/50">
                                    ${item.betAmount} × {item.daysToRun} {item.daysToRun === 1 ? 'day' : 'days'}
                                  </span>
                                  <span className="text-white font-bold">
                                    ${item.totalCost.toFixed(2)}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        {cart.length > 0 && (
          <div className="p-4 md:p-6 border-t border-white/10 bg-black/40">
            <div className="flex items-center justify-between mb-4">
              <span className="text-white/70 text-lg">Total:</span>
              <span className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                ${getCartTotal().toFixed(2)}
              </span>
            </div>

            <div className="flex gap-3">
              <button
                onClick={clearCart}
                className="flex-1 px-4 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-white font-bold transition-all"
              >
                Clear All
              </button>
              <button
                onClick={onCheckout}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 hover:shadow-2xl rounded-xl text-black font-bold text-lg transition-all"
              >
                Checkout
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </>
  );
};