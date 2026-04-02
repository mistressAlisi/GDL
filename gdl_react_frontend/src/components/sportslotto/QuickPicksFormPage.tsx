import React, { useState } from 'react';
import { ArrowLeft, DollarSign, Ticket, Sparkles, Trophy } from 'lucide-react';
import { useAuth } from '../../sportslotto/contexts/AuthContext';
import { useCart } from '../../sportslotto/contexts/CartContext';
import {
  generateQuickPicks,
  QuickPickFormData,
  QuickPickCartEntry,
  QuickPickBatchComplete,
  calculateQuickPickReturn
} from '../../sportslotto/services/quickpick-websocket-adapter';
import { acceptTicket, TicketData } from '../../sportslotto/services/api';

// Default sports for Quick Picks (7 sports, all pre-selected and hidden)
const DEFAULT_QUICKPICK_SPORTS = [
  { uuid: 'cb1e8376-ac57-49bd-b1cd-12ec6d21c7cc', name: 'American Football', id: 'group_1' },
  { uuid: '6ae7672b-bd34-4f39-96bb-680ccaec4ffc', name: 'Unknown Sport', id: 'group_2' }, // New sport
  { uuid: '102fafec-0543-4511-9569-4773a8d855d6', name: 'Baseball', id: 'group_3' },
  { uuid: '8a383bae-0770-493a-9b2c-bc77b18e69b7', name: 'Basketball', id: 'group_4' },
  { uuid: '63625c46-eaa1-4ed2-8d70-ce83f56313e2', name: 'Ice Hockey', id: 'group_5' },
  { uuid: '6bdfe523-ad42-4c3a-93b8-9cda41b5ed77', name: 'Soccer', id: 'group_6' },
  { uuid: 'b4d01545-e578-4666-8ed6-6bed82c6ca07', name: 'Tennis', id: 'group_7' },
];

interface QuickPicksFormPageProps {
  filterSports?: typeof DEFAULT_QUICKPICK_SPORTS;
  ruleset?: any;
  vhost?: string;
  vdomain?: string;
  onBack?: () => void;
  onCartUpdated?: (entries: QuickPickCartEntry[]) => void;
  onComplete?: (summary: any) => void;
  onError?: (error: string) => void;
}

export function QuickPicksFormPage({
  filterSports = DEFAULT_QUICKPICK_SPORTS,
  ruleset,
  vhost,
  vdomain,
  onBack,
  onCartUpdated,
  onComplete,
  onError
}: QuickPicksFormPageProps) {
  const { user } = useAuth();
  const { addToCart } = useCart();

  // Form state - matching Django template defaults
  const [count, setCount] = useState(5);
  const [stake, setStake] = useState(1);
  const [possibleReturn, setPossibleReturn] = useState(20);

  // Hidden fields (matching Django template)
  const minPayout = 20;
  const eventsWithin = 129600; // 36 hours
  const depth = 4; // Quick picks use 4 events

  // UI state
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCount, setGeneratedCount] = useState(0);

  // Calculate return whenever stake changes
  const handleStakeChange = (value: number) => {
    setStake(value);
    setPossibleReturn(calculateQuickPickReturn(value));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (count < 5) {
      onError?.('Minimum purchase is 5 tickets');
      alert('Minimum purchase is 5 tickets');
      return;
    }

    if (!user?.id) {
      onError?.('User not authenticated');
      alert('Please log in to generate quick picks');
      return;
    }

    setIsGenerating(true);
    setGeneratedCount(0);

    // Build form data matching Django format
    const formData: QuickPickFormData = {
      stake,
      count,
      min_payout: minPayout,
      events_within: eventsWithin,
      depth,
      sports: filterSports.map(s => s.uuid),
      ruleset: ruleset ? JSON.stringify(ruleset) : undefined,
      vhost,
      vdomain,
      account: user.id,
    };

    console.log('🎫 Generating quick picks with form data:', formData);

    const entries: QuickPickCartEntry[] = [];

    generateQuickPicks(
      formData,
      (entry) => {
        // Add to cart
        entries.push(entry);
        setGeneratedCount(entries.length);
        onCartUpdated?.(entries);
      },
      (summary) => {
        // Generation complete
        console.log('Quick picks complete:', summary);
        setIsGenerating(false);
        setGeneratedCount(0);
        onComplete?.(summary);
      },
      (error) => {
        console.error('Quick pick error:', error);
        setIsGenerating(false);
        setGeneratedCount(0);
        onError?.(error);
      }
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">

      {/* Back Button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 px-4 py-2 text-white/80 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Menu
      </button>

      {/* Balance Card */}
      <div
        className="backdrop-blur-xl rounded-2xl border p-6 relative overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 15, 30, 0.85), rgba(30, 20, 50, 0.85))',
          borderColor: 'rgba(168, 85, 247, 0.3)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
        }}
      >
        {/* Inner glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-pink-500/10 pointer-events-none" />
        <div className="relative grid grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-white/60 text-sm mb-1">Balance</div>
            <div className="text-white text-xl font-bold">${user?.balance?.toFixed(2) || '0.00'}</div>
          </div>
          <div>
            <div className="text-white/60 text-sm mb-1">Pending</div>
            <div className="text-white text-xl font-bold">${user?.pending?.toFixed(2) || '0.00'}</div>
          </div>
          <div>
            <div className="text-white/60 text-sm mb-1">Free Play</div>
            <div className="text-white text-xl font-bold">${user?.bonus?.toFixed(2) || '0.00'}</div>
          </div>
          <div>
            <div className="text-white/60 text-sm mb-1">Avail.</div>
            <div className="text-green-400 text-xl font-bold">${user?.available?.toFixed(2) || '0.00'}</div>
          </div>
        </div>
      </div>

      {/* Quick Picks Form */}
      <div
        className="backdrop-blur-xl rounded-2xl border p-8 relative overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 15, 30, 0.9), rgba(30, 20, 50, 0.9))',
          borderColor: 'rgba(168, 85, 247, 0.3)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
        }}
      >
        {/* Inner glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-pink-500/10 pointer-events-none" />

        <div className="relative">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-bold text-white mb-3 flex items-center justify-center gap-3">
              <Sparkles className="w-8 h-8 text-purple-400 animate-pulse" />
              Quick Picks!
            </h1>
            <p className="text-white/70 text-lg">
              Quick picks are AI-chosen tickets on 4 events to win roughly 20 for 1 risked. (Minimum purchase 5 tickets.)
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Ticket Count */}
              <div className="space-y-2">
                <label htmlFor="count" className="flex items-center gap-2 text-white font-semibold text-sm">
                  <Ticket className="w-4 h-4" />
                  Ticket Count:
                </label>
                <input
                  type="number"
                  id="count"
                  name="count"
                  min="5"
                  max="9999"
                  value={count}
                  onChange={(e) => setCount(parseInt(e.target.value))}
                  className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/20 text-white focus:outline-none focus:border-purple-400 focus:bg-black/60 transition-all"
                />
              </div>

              {/* Risk Amount */}
              <div className="space-y-2">
                <label htmlFor="stake" className="flex items-center gap-2 text-white font-semibold text-sm">
                  <DollarSign className="w-4 h-4" />
                  Risk Amount:
                </label>
                <input
                  type="number"
                  id="stake"
                  name="stake"
                  min="1"
                  max="10"
                  step="0.01"
                  value={stake}
                  onChange={(e) => handleStakeChange(parseFloat(e.target.value))}
                  className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/20 text-white focus:outline-none focus:border-purple-400 focus:bg-black/60 transition-all"
                />
              </div>

            </div>

            {/* Possible Returns Display */}
            <div
              className="p-4 rounded-xl border border-green-500/40 relative overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(22, 163, 74, 0.1))',
                boxShadow: '0 4px 16px rgba(34, 197, 94, 0.2)'
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-green-400/10 to-transparent pointer-events-none" />
              <div className="relative flex items-center justify-between">
                <span className="text-white font-semibold flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-green-400" />
                  Possible Return per ticket (20 to 1):
                </span>
                <span className="text-2xl font-bold text-green-400">
                  ${possibleReturn.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Submit Button with Glow */}
            <button
              type="submit"
              disabled={isGenerating}
              className="w-full py-4 rounded-xl font-bold text-lg text-white transition-all relative overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                background: isGenerating
                  ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.5), rgba(236, 72, 153, 0.5))'
                  : 'linear-gradient(135deg, #a855f7, #ec4899)',
                boxShadow: isGenerating ? 'none' : '0 0 30px rgba(168, 85, 247, 0.6), 0 0 60px rgba(236, 72, 153, 0.4)'
              }}
            >
              {/* Animated glow on hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000" />
              <span className="relative flex items-center justify-center gap-2">
                <Sparkles className="w-5 h-5" />
                {isGenerating ? `Generating... (${generatedCount}/${count})` : 'Get Quick Picks!'}
              </span>
            </button>

          </form>
        </div>
      </div>

      {/* Loading Progress */}
      {isGenerating && (
        <div
          className="backdrop-blur-xl rounded-2xl border p-6"
          style={{
            background: 'linear-gradient(135deg, rgba(15, 15, 30, 0.85), rgba(30, 20, 50, 0.85))',
            borderColor: 'rgba(168, 85, 247, 0.3)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
          }}
        >
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-white text-lg">Generating your quick picks... ({generatedCount}/{count})</p>
            <div className="w-full max-w-md mx-auto bg-white/10 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
                style={{ width: `${(generatedCount / count) * 100}%` }}
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}