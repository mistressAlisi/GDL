import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Lock, AlertTriangle, Clock, Shield, Info } from 'lucide-react';
import { useProfile } from '../../contexts/ProfileContext';
import { Button } from '../ui/button';
import { Label } from '../ui/label';

export const AccountLockoutPage: React.FC = () => {
  const { lockAccount } = useProfile();
  const [selectedDuration, setSelectedDuration] = useState<number>(0);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const lockoutOptions = [
    { duration: 1, label: '24 Hours', description: 'Lock your account for 1 day' },
    { duration: 3, label: '3 Days', description: 'Lock your account for 3 days' },
    { duration: 7, label: '1 Week', description: 'Lock your account for 7 days' },
    { duration: 30, label: '30 Days', description: 'Lock your account for 1 month' },
    { duration: 90, label: '90 Days', description: 'Lock your account for 3 months' },
    { duration: 180, label: '6 Months', description: 'Lock your account for 6 months' },
    { duration: 365, label: '1 Year', description: 'Lock your account for 1 year' },
    { duration: -1, label: 'Permanent', description: 'Permanently close your account' },
  ];

  const handleLockAccount = () => {
    if (selectedDuration === 0) {
      alert('Please select a lockout duration');
      return;
    }
    setShowConfirmation(true);
  };

  const confirmLockout = () => {
    lockAccount(selectedDuration);
    setShowConfirmation(false);
    setSelectedDuration(0);
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
            Account Lockout
          </h1>
          <p className="text-white/70">Temporarily or permanently lock your account</p>
        </div>

        {/* Warning Notice */}
        <div className="bg-gradient-to-r from-red-500/20 to-orange-500/20 border-2 border-red-500/40 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-red-400 flex-shrink-0" size={32} />
            <div>
              <h3 className="text-xl font-bold text-red-300 mb-2">⚠️ Important Warning</h3>
              <p className="text-red-200/90 mb-3">
                Account lockout is a serious responsible gaming measure. Once activated:
              </p>
              <ul className="text-sm text-red-200/80 space-y-1">
                <li>• You will be immediately logged out of your account</li>
                <li>• You will NOT be able to access your account during the lockout period</li>
                <li>• You will NOT be able to place bets or make deposits</li>
                <li>• The lockout CANNOT be reversed or canceled early</li>
                <li>• Any pending bets will still be processed</li>
                <li>• Withdrawals may be delayed until after the lockout period</li>
              </ul>
            </div>
          </div>
        </div>

        {/* When to Use Section */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-3 mb-4">
            <Info className="text-blue-400 flex-shrink-0" size={24} />
            <div>
              <h3 className="text-lg font-bold text-white mb-2">When Should I Use Account Lockout?</h3>
              <p className="text-white/80 text-sm mb-3">
                Consider locking your account if:
              </p>
              <ul className="text-sm text-white/70 space-y-1">
                <li>• You feel you're betting more than you can afford</li>
                <li>• Betting is affecting your personal relationships or work</li>
                <li>• You need a break to reassess your betting habits</li>
                <li>• You're chasing losses or betting impulsively</li>
                <li>• You want to take a predetermined break from betting</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Lockout Options */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Clock size={24} className="text-yellow-400" />
            Select Lockout Duration
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {lockoutOptions.map((option) => (
              <button
                key={option.duration}
                onClick={() => setSelectedDuration(option.duration)}
                className={`p-4 rounded-xl border-2 transition-all text-left ${
                  selectedDuration === option.duration
                    ? option.duration === -1
                      ? 'bg-gradient-to-br from-red-500/30 to-pink-500/30 border-red-400/50 shadow-lg shadow-red-500/20'
                      : 'bg-gradient-to-br from-orange-500/30 to-yellow-500/30 border-orange-400/50 shadow-lg shadow-orange-500/20'
                    : 'bg-white/5 border-white/20 hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    selectedDuration === option.duration
                      ? option.duration === -1
                        ? 'bg-red-500/40'
                        : 'bg-orange-500/40'
                      : 'bg-white/10'
                  }`}>
                    {option.duration === -1 ? (
                      <Lock className="text-white" size={20} />
                    ) : (
                      <Clock className="text-white" size={20} />
                    )}
                  </div>
                  <div>
                    <div className="font-bold text-white">{option.label}</div>
                    <div className="text-xs text-white/60">{option.description}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Lock Account Button */}
        {selectedDuration !== 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Button
              onClick={handleLockAccount}
              className="w-full h-14 bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-600 hover:to-orange-700 text-white font-bold text-lg shadow-lg shadow-red-500/30"
            >
              <Lock size={20} className="mr-2" />
              Lock Account for {lockoutOptions.find(o => o.duration === selectedDuration)?.label}
            </Button>
          </motion.div>
        )}

        {/* Support Resources */}
        <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-2xl p-6">
          <div className="flex items-start gap-3">
            <Shield className="text-green-400 flex-shrink-0" size={24} />
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Need Help?</h3>
              <p className="text-white/80 text-sm mb-3">
                If you're struggling with problem gambling, we're here to help. Consider these resources:
              </p>
              <ul className="text-sm text-white/70 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">•</span>
                  <span>
                    <strong>National Council on Problem Gambling:</strong>{' '}
                    <a href="tel:1-800-522-4700" className="text-green-400 hover:text-green-300 underline">
                      1-800-522-4700
                    </a>
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">•</span>
                  <span>
                    <strong>Gamblers Anonymous:</strong>{' '}
                    <a href="https://www.gamblersanonymous.org" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 underline">
                      www.gamblersanonymous.org
                    </a>
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 mt-0.5">•</span>
                  <span>Contact our Support Team for additional assistance and resources</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Confirmation Modal */}
        {showConfirmation && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-gradient-to-br from-slate-900 to-slate-800 border-2 border-red-500/40 rounded-2xl p-6 max-w-md w-full"
            >
              <div className="text-center mb-6">
                <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
                  <AlertTriangle className="text-red-400" size={32} />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Final Confirmation</h2>
                <p className="text-white/80">
                  Are you absolutely sure you want to lock your account for{' '}
                  <strong className="text-red-400">
                    {lockoutOptions.find(o => o.duration === selectedDuration)?.label}
                  </strong>?
                </p>
              </div>

              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
                <p className="text-red-300 text-sm">
                  <strong>This action cannot be undone.</strong> You will be logged out immediately and won't be able to access your account until the lockout period ends.
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={() => setShowConfirmation(false)}
                  variant="outline"
                  className="flex-1 bg-white/10 border-white/20 text-white hover:bg-white/20"
                >
                  Cancel
                </Button>
                <Button
                  onClick={confirmLockout}
                  className="flex-1 bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-600 hover:to-orange-700 text-white font-bold"
                >
                  Yes, Lock My Account
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </motion.div>
    </div>
  );
};
