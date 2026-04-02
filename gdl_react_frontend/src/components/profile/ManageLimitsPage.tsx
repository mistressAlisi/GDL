import React, { useState } from 'react';
import { motion } from 'motion/react';
import { DollarSign, Calendar, TrendingDown, AlertTriangle, CheckCircle, Shield } from 'lucide-react';
import { useProfile } from '../../contexts/ProfileContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';

export const ManageLimitsPage: React.FC = () => {
  const { lossLimits, updateLossLimits } = useProfile();
  const [dailyLimit, setDailyLimit] = useState(lossLimits.daily.toString());
  const [weeklyLimit, setWeeklyLimit] = useState(lossLimits.weekly.toString());
  const [monthlyLimit, setMonthlyLimit] = useState(lossLimits.monthly.toString());
  const [limitsActive, setLimitsActive] = useState(lossLimits.isActive);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    const daily = parseFloat(dailyLimit);
    const weekly = parseFloat(weeklyLimit);
    const monthly = parseFloat(monthlyLimit);

    // Validation
    if (isNaN(daily) || isNaN(weekly) || isNaN(monthly)) {
      alert('Please enter valid numbers for all limits');
      return;
    }

    if (daily <= 0 || weekly <= 0 || monthly <= 0) {
      alert('Limits must be greater than zero');
      return;
    }

    if (daily > weekly) {
      alert('Daily limit cannot exceed weekly limit');
      return;
    }

    if (weekly > monthly) {
      alert('Weekly limit cannot exceed monthly limit');
      return;
    }

    updateLossLimits({
      daily,
      weekly,
      monthly,
      isActive: limitsActive,
    });

    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleToggleLimits = (checked: boolean) => {
    setLimitsActive(checked);
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
            Manage Loss Limits
          </h1>
          <p className="text-white/70">Set betting limits to promote responsible gaming</p>
        </div>

        {/* Important Notice */}
        <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-3">
            <Shield className="text-orange-400 flex-shrink-0" size={32} />
            <div>
              <h3 className="text-xl font-bold text-orange-300 mb-2">Responsible Gaming</h3>
              <p className="text-orange-200/90 mb-3">
                Setting deposit and loss limits is an important tool for responsible gaming. These limits help you stay in control of your betting activity and prevent excessive losses.
              </p>
              <div className="text-sm text-orange-200/70">
                <strong>Note:</strong> Once set, limits can be increased after a 24-hour cooling-off period, but decreases take effect immediately.
              </div>
            </div>
          </div>
        </div>

        {/* Enable/Disable Limits */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                limitsActive 
                  ? 'bg-gradient-to-br from-green-400 to-emerald-500'
                  : 'bg-white/10'
              }`}>
                {limitsActive ? (
                  <CheckCircle className="text-white" size={24} />
                ) : (
                  <AlertTriangle className="text-white/60" size={24} />
                )}
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Loss Limits</h3>
                <p className="text-white/60 text-sm">
                  {limitsActive ? 'Limits are currently active' : 'Limits are currently disabled'}
                </p>
              </div>
            </div>
            <Switch
              checked={limitsActive}
              onCheckedChange={handleToggleLimits}
              className="data-[state=checked]:bg-green-500"
            />
          </div>
        </div>

        {/* Limit Settings */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-6">Set Your Limits</h3>
          
          <div className="space-y-6">
            {/* Daily Limit */}
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                  <Calendar className="text-white" size={20} />
                </div>
                <div>
                  <Label className="text-white/90 font-semibold text-lg">Daily Loss Limit</Label>
                  <p className="text-white/60 text-sm">Maximum losses allowed per day</p>
                </div>
              </div>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 text-xl font-bold">$</span>
                <Input
                  type="number"
                  value={dailyLimit}
                  onChange={(e) => setDailyLimit(e.target.value)}
                  disabled={!limitsActive}
                  className="pl-8 h-14 bg-white/5 border-white/20 text-white text-lg disabled:opacity-50"
                />
              </div>
              <p className="text-white/50 text-xs mt-2">Current limit: ${lossLimits.daily.toFixed(2)}/day</p>
            </div>

            {/* Weekly Limit */}
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
                  <TrendingDown className="text-white" size={20} />
                </div>
                <div>
                  <Label className="text-white/90 font-semibold text-lg">Weekly Loss Limit</Label>
                  <p className="text-white/60 text-sm">Maximum losses allowed per week</p>
                </div>
              </div>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 text-xl font-bold">$</span>
                <Input
                  type="number"
                  value={weeklyLimit}
                  onChange={(e) => setWeeklyLimit(e.target.value)}
                  disabled={!limitsActive}
                  className="pl-8 h-14 bg-white/5 border-white/20 text-white text-lg disabled:opacity-50"
                />
              </div>
              <p className="text-white/50 text-xs mt-2">Current limit: ${lossLimits.weekly.toFixed(2)}/week</p>
            </div>

            {/* Monthly Limit */}
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
                  <DollarSign className="text-white" size={20} />
                </div>
                <div>
                  <Label className="text-white/90 font-semibold text-lg">Monthly Loss Limit</Label>
                  <p className="text-white/60 text-sm">Maximum losses allowed per month</p>
                </div>
              </div>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/80 text-xl font-bold">$</span>
                <Input
                  type="number"
                  value={monthlyLimit}
                  onChange={(e) => setMonthlyLimit(e.target.value)}
                  disabled={!limitsActive}
                  className="pl-8 h-14 bg-white/5 border-white/20 text-white text-lg disabled:opacity-50"
                />
              </div>
              <p className="text-white/50 text-xs mt-2">Current limit: ${lossLimits.monthly.toFixed(2)}/month</p>
            </div>
          </div>

          {/* Save Button */}
          <Button
            onClick={handleSave}
            disabled={!limitsActive}
            className="w-full h-12 mt-6 bg-gradient-to-r from-green-400 to-emerald-500 hover:from-green-500 hover:to-emerald-600 text-white font-bold shadow-lg shadow-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saved ? (
              <>
                <CheckCircle size={20} className="mr-2" />
                Limits Saved!
              </>
            ) : (
              'Save Limits'
            )}
          </Button>
        </div>

        {/* Information */}
        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-2xl p-6">
          <h3 className="text-lg font-bold text-white mb-3">How Loss Limits Work</h3>
          <ul className="text-sm text-white/80 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Limits are calculated based on net losses (bets placed minus winnings)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Once a limit is reached, you won't be able to place additional bets until the period resets</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Daily limits reset at midnight in your timezone</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Weekly limits reset every Monday at midnight</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Monthly limits reset on the first day of each month</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Limit increases have a 24-hour cooling-off period before taking effect</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">•</span>
              <span>Limit decreases take effect immediately</span>
            </li>
          </ul>
        </div>
      </motion.div>
    </div>
  );
};
