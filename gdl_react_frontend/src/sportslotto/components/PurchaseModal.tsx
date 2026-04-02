import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, ShoppingBag, Gift, Loader2, CheckCircle, TrendingUp, Sparkles } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface PurchaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  ticketCount: number;
  totalRisk: number;
  totalReturns: number;
  bonusBalance: number;
  onConfirm: (useBonus: boolean) => Promise<any>;
  onSuccess?: () => void;
}

interface PurchaseResponse {
  res: string;
  silent?: string;
  total_stake?: string;
  available?: string;
  bonus?: string;
  pending?: string;
  balance?: string;
}

export const PurchaseModal: React.FC<PurchaseModalProps> = ({
  isOpen,
  onClose,
  ticketCount,
  totalRisk,
  totalReturns,
  bonusBalance,
  onConfirm,
  onSuccess,
}) => {
  const { theme } = useTheme();
  const [useBonus, setUseBonus] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);
  const [purchaseData, setPurchaseData] = useState<PurchaseResponse | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => {
        setPurchaseSuccess(false);
        setPurchaseData(null);
        setUseBonus(false);
        setShowConfetti(false);
      }, 300);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setIsProcessing(true);
    try {
      const response = await onConfirm(useBonus);
      console.log('Purchase response:', response);
      setPurchaseData(response);
      setPurchaseSuccess(true);
      setShowConfetti(true);

      // Auto-close after showing success animation
      setTimeout(() => {
        onClose();
        if (onSuccess) onSuccess();
      }, 3000);
    } catch (error) {
      console.error('Purchase failed:', error);
      setIsProcessing(false);
    }
  };

  // Parse numeric values from response
  const parseValue = (val: string | undefined) => {
    return val ? parseFloat(val) : 0;
  };

  return createPortal(
    <div className="fixed inset-0 flex items-center justify-center p-4" style={{ zIndex: 99999 }}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-all"
        onClick={purchaseSuccess ? undefined : onClose}
        style={{
          background: purchaseSuccess
            ? 'radial-gradient(circle at center, rgba(16, 185, 129, 0.3) 0%, rgba(0, 0, 0, 0.8) 100%)'
            : 'rgba(0, 0, 0, 0.6)',
        }}
      />

      {/* Confetti Effect */}
      {showConfetti && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {[...Array(30)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: '-20px',
                background: ['#FFD700', '#FFA500', '#FF69B4', '#00FF00', '#00BFFF'][i % 5],
                animation: `confetti-fall ${2 + Math.random() * 2}s linear forwards`,
                animationDelay: `${Math.random() * 0.5}s`,
                transform: `rotate(${Math.random() * 360}deg)`,
              }}
            />
          ))}
        </div>
      )}

      {/* Modal */}
      <div
        className="relative w-full max-w-md transition-all duration-500"
        style={{
          background: `linear-gradient(135deg, 
            rgba(10, 10, 30, 0.95) 0%, 
            rgba(20, 20, 50, 0.98) 50%, 
            rgba(10, 10, 30, 0.95) 100%)`,
          backdropFilter: 'blur(20px)',
          border: `1px solid ${purchaseSuccess ? '#10B981' : theme.cardBorder}`,
          borderRadius: '24px',
          boxShadow: purchaseSuccess
            ? `0 20px 60px rgba(16, 185, 129, 0.6), 0 0 80px rgba(16, 185, 129, 0.4)`
            : `0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px ${theme.cardGlow}`,
          transform: purchaseSuccess ? 'scale(1.05)' : 'scale(1)',
        }}
      >
        {!purchaseSuccess ? (
          <>
            {/* Header */}
            <div
              className="relative px-6 py-5 border-b"
              style={{
                borderColor: theme.cardBorder,
                background: `linear-gradient(135deg, ${theme.glassOverlay}, transparent)`,
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="p-2.5 rounded-xl"
                    style={{
                      background: theme.gradient,
                      boxShadow: `0 4px 12px ${theme.cardGlow}`,
                    }}
                  >
                    <ShoppingBag className="w-5 h-5 text-white" />
                  </div>
                  <h2
                    className="text-2xl font-bold"
                    style={{
                      background: theme.gradient,
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                    }}
                  >
                    Purchase Tickets!
                  </h2>
                </div>
                <button
                  onClick={onClose}
                  disabled={isProcessing}
                  className="p-2 rounded-lg transition-all hover:scale-110"
                  style={{
                    background: theme.cardBg,
                    border: `1px solid ${theme.cardBorder}`,
                  }}
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="px-6 py-6 space-y-5">
              {/* Ticket Summary */}
              <div
                className="p-5 rounded-2xl text-center"
                style={{
                  background: `linear-gradient(135deg, ${theme.cardBg}80, ${theme.cardBg}40)`,
                  border: `1px solid ${theme.cardBorder}`,
                  boxShadow: `inset 0 1px 1px ${theme.glassHighlight}`,
                }}
              >
                <p className="text-lg text-gray-300">
                  You've picked{' '}
                  <span
                    className="font-bold text-2xl"
                    style={{
                      color: theme.accentColor,
                      textShadow: `0 0 20px ${theme.cardGlow}`,
                    }}
                  >
                    {ticketCount}
                  </span>{' '}
                  {ticketCount === 1 ? 'ticket' : 'tickets'}
                </p>
                <div className="mt-3 flex items-center justify-center gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Risking</p>
                    <p className="text-xl font-bold text-red-400">
                      ${totalRisk.toFixed(2)}
                    </p>
                  </div>
                  <div
                    className="w-px h-12"
                    style={{ background: theme.cardBorder }}
                  />
                  <div>
                    <p className="text-sm text-gray-400">Returns</p>
                    <p className="text-xl font-bold text-green-400">
                      ${totalReturns.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Bonus Toggle */}
              {bonusBalance > 0 && (
                <div
                  className="p-4 rounded-2xl cursor-pointer transition-all hover:scale-[1.02]"
                  style={{
                    background: useBonus
                      ? `linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1))`
                      : theme.cardBg,
                    border: `1px solid ${useBonus ? '#10B981' : theme.cardBorder}`,
                    boxShadow: useBonus ? `0 4px 16px rgba(16, 185, 129, 0.3)` : 'none',
                  }}
                  onClick={() => !isProcessing && setUseBonus(!useBonus)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="p-2 rounded-lg"
                        style={{
                          background: `linear-gradient(135deg, #10B981, rgba(16, 185, 129, 0.8))`,
                          boxShadow: `0 4px 12px rgba(16, 185, 129, 0.3)`,
                        }}
                      >
                        <Gift className="w-5 h-5 text-white" />
                      </div>
                      <div className="text-left">
                        <p className="font-semibold text-white">
                          Use Free Play Balance
                        </p>
                        <p className="text-sm text-gray-400">
                          Available:{' '}
                          <span className="font-bold text-green-400">
                            ${bonusBalance.toFixed(2)}
                          </span>
                        </p>
                      </div>
                    </div>
                    {/* Toggle Switch */}
                    <div
                      className="relative w-12 h-6 rounded-full transition-all"
                      style={{
                        background: useBonus
                          ? `linear-gradient(135deg, #10B981, rgba(16, 185, 129, 0.8))`
                          : theme.cardBg,
                        border: `1px solid ${useBonus ? '#10B981' : theme.cardBorder}`,
                      }}
                    >
                      <div
                        className="absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform"
                        style={{
                          transform: useBonus ? 'translateX(24px)' : 'translateX(0)',
                          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Confirmation Text */}
              <div className="text-center">
                <p className="text-sm text-gray-400">
                  Press the button below to complete your purchase:
                </p>
              </div>

              {/* Confirm Button */}
              <button
                onClick={handleConfirm}
                disabled={isProcessing}
                className="w-full py-4 rounded-2xl font-bold text-lg text-white transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                style={{
                  background: theme.buttonGradient,
                  boxShadow: `0 8px 24px ${theme.cardGlow}, 0 0 40px ${theme.cardGlow}`,
                }}
              >
                {isProcessing ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Processing...
                  </span>
                ) : (
                  'Complete Purchase'
                )}
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Success View */}
            <div className="px-6 py-8">
              {/* Success Icon with Animation */}
              <div className="flex justify-center mb-6">
                <div
                  className="relative"
                  style={{
                    animation: 'success-bounce 0.6s ease-out',
                  }}
                >
                  <div
                    className="absolute inset-0 rounded-full blur-2xl"
                    style={{
                      background: 'radial-gradient(circle, rgba(16, 185, 129, 0.6) 0%, transparent 70%)',
                      animation: 'pulse-glow 1.5s ease-in-out infinite',
                    }}
                  />
                  <div
                    className="relative p-6 rounded-full"
                    style={{
                      background: 'linear-gradient(135deg, #10B981, rgba(16, 185, 129, 0.8))',
                      boxShadow: '0 8px 32px rgba(16, 185, 129, 0.5)',
                    }}
                  >
                    <CheckCircle className="w-16 h-16 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </div>

              {/* Success Title */}
              <h2
                className="text-3xl font-bold text-center mb-2"
                style={{
                  background: 'linear-gradient(135deg, #10B981, #34D399)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  animation: 'fade-in-up 0.5s ease-out 0.2s both',
                }}
              >
                Purchase Successful! 🎉
              </h2>

              <p
                className="text-center text-gray-300 mb-6"
                style={{
                  animation: 'fade-in-up 0.5s ease-out 0.3s both',
                }}
              >
                Your tickets are confirmed!
              </p>

              {/* Updated Balances */}
              {purchaseData && (
                <div
                  className="space-y-3"
                  style={{
                    animation: 'fade-in-up 0.5s ease-out 0.4s both',
                  }}
                >
                  {/* Total Stake */}
                  <div
                    className="flex items-center justify-between p-4 rounded-xl"
                    style={{
                      background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05))',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                    }}
                  >
                    <span className="text-gray-300 font-medium">Total Stake</span>
                    <span className="text-xl font-bold text-red-400">
                      ${parseValue(purchaseData.total_stake).toFixed(2)}
                    </span>
                  </div>

                  {/* New Balance - Highlight */}
                  <div
                    className="flex items-center justify-between p-5 rounded-xl"
                    style={{
                      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1))',
                      border: '2px solid rgba(16, 185, 129, 0.5)',
                      boxShadow: '0 4px 20px rgba(16, 185, 129, 0.3)',
                    }}
                  >
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-green-400" />
                      <span className="text-white font-bold text-lg">New Balance</span>
                    </div>
                    <span className="text-2xl font-bold text-green-400">
                      ${parseValue(purchaseData.balance).toFixed(2)}
                    </span>
                  </div>

                  {/* Grid: Available, Bonus, Pending */}
                  <div className="grid grid-cols-3 gap-2 mt-4">
                    <div
                      className="p-3 rounded-lg text-center"
                      style={{
                        background: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.2)',
                      }}
                    >
                      <p className="text-xs text-gray-400 mb-1">Available</p>
                      <p className="text-sm font-bold text-green-400">
                        ${parseValue(purchaseData.available).toFixed(2)}
                      </p>
                    </div>
                    <div
                      className="p-3 rounded-lg text-center"
                      style={{
                        background: 'rgba(16, 185, 129, 0.1)',
                        border: '1px solid rgba(16, 185, 129, 0.2)',
                      }}
                    >
                      <p className="text-xs text-gray-400 mb-1">Bonus</p>
                      <p className="text-sm font-bold text-green-400">
                        ${parseValue(purchaseData.bonus).toFixed(2)}
                      </p>
                    </div>
                    <div
                      className="p-3 rounded-lg text-center"
                      style={{
                        background: 'rgba(251, 191, 36, 0.1)',
                        border: '1px solid rgba(251, 191, 36, 0.2)',
                      }}
                    >
                      <p className="text-xs text-gray-400 mb-1">Pending</p>
                      <p className="text-sm font-bold text-yellow-400">
                        ${parseValue(purchaseData.pending).toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Auto-closing message */}
              <p
                className="text-center text-gray-400 text-sm mt-6"
                style={{
                  animation: 'fade-in 0.5s ease-out 0.5s both',
                }}
              >
                Closing automatically...
              </p>
            </div>
          </>
        )}
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes confetti-fall {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }

        @keyframes success-bounce {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          50% {
            transform: scale(1.2);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes pulse-glow {
          0%, 100% {
            opacity: 0.5;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.1);
          }
        }

        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
      `}</style>
    </div>,
    document.body
  );
};

export default PurchaseModal;