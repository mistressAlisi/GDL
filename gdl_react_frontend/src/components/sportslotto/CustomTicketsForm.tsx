import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { CustomTicketFormData } from '../../sportslotto/services/ticket-websocket-adapter';

// Sport configuration matching Django template
const DEFAULT_SPORTS = [
  { uuid: 'cb1e8376-ac57-49bd-b1cd-12ec6d21c7cc', name: 'American Football', icon: '🏈', id: 'group_1' },
  { uuid: '102fafec-0543-4511-9569-4773a8d855d6', name: 'Baseball', icon: '⚾', id: 'group_2' },
  { uuid: '8a383bae-0770-493a-9b2c-bc77b18e69b7', name: 'Basketball', icon: '🏀', id: 'group_3' },
  { uuid: '6bdfe523-ad42-4c3a-93b8-9cda41b5ed77', name: 'Soccer', icon: '⚽', id: 'group_4' },
  { uuid: '63625c46-eaa1-4ed2-8d70-ce83f56313e2', name: 'Ice Hockey', icon: '🏒', id: 'group_5' },
  { uuid: 'b4d01545-e578-4666-8ed6-6bed82c6ca07', name: 'Tennis', icon: '🎾', id: 'group_6' },
];

const TIMEFRAME_BUTTONS = [
  { value: 43200, label: '12 Hours' },
  { value: 64800, label: '18 Hours' },
  { value: 86400, label: '24 Hours' },
  { value: 108000, label: '30 Hours' },
  { value: 129600, label: '36 Hours' },
  { value: 151200, label: '42 Hours' },
  { value: 172800, label: '48 Hours' },
];

interface CustomTicketsFormProps {
  filterSports?: typeof DEFAULT_SPORTS;
  ruleset?: any;
  vhost: string;
  vdomain: string;
  account?: string;
  onBack: () => void;
  onSubmit: (data: CustomTicketFormData) => void;
}

export function CustomTicketsForm({
  filterSports = DEFAULT_SPORTS,
  ruleset,
  vhost,
  vdomain,
  account,
  onBack,
  onSubmit
}: CustomTicketsFormProps) {

  // Form state - matching Django template defaults
  const [stake, setStake] = useState(1);
  const [depth, setDepth] = useState(7);
  const [minPayout, setMinPayout] = useState(2500);
  const [eventsWithin, setEventsWithin] = useState(129600); // 36 hours default
  const [count, setCount] = useState(40);
  const [selectedSports, setSelectedSports] = useState<string[]>(
    filterSports.map(s => s.uuid)
  );

  const toggleSport = (uuid: string) => {
    setSelectedSports(prev =>
      prev.includes(uuid)
        ? prev.filter(id => id !== uuid)
        : [...prev, uuid]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    console.log('🔍 CustomTicketsForm account prop:', account);

    const formData: CustomTicketFormData = {
      stake,
      depth,
      min_payout: minPayout,
      events_within: eventsWithin,
      sports: selectedSports,
      count,
      vhost,
      vdomain,
      account,
    };

    console.log('🔍 Form data being submitted:', formData);

    onSubmit(formData);
  };

  // Calculate potential win
  const potentialWin = stake * minPayout;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-golden hover:text-yellow-300 transition-colors mb-6"
      >
        <ArrowLeft size={20} />
        <span>Back to Menu</span>
      </button>

      {/* Page Title */}
      <h1 className="text-center mb-8 text-4xl font-bold bg-gradient-to-r from-golden to-yellow-300 bg-clip-text text-transparent">
        Custom Tickets
      </h1>

      {/* Main Form Card */}
      <div
        className="backdrop-blur-xl rounded-3xl border p-8 shadow-2xl relative overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 15, 30, 0.9), rgba(30, 20, 50, 0.9))',
          borderColor: 'rgba(251, 146, 60, 0.3)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
        }}
      >

        {/* Inner glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-transparent to-yellow-500/10 pointer-events-none" />

        {/* Card Header */}
        <div className="text-center mb-6 relative">
          <h2 className="text-white text-2xl font-bold mb-2">Build Custom Ticket</h2>
          <p className="text-white/70">
            Select sports, timeframe, and your risk amount
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 relative">

          {/* Stake, Events, Potential Win - 3 columns */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            {/* STAKE */}
            <div>
              <label className="block text-golden text-sm font-bold mb-2 uppercase">
                Risk
              </label>
              <input
                type="number"
                min="1"
                max="500"
                step="0.01"
                value={stake}
                onChange={(e) => setStake(parseFloat(e.target.value) || 1)}
                className="w-full px-4 py-3 bg-black/50 border border-golden/40 rounded-lg text-white text-center text-xl font-bold focus:outline-none focus:border-golden focus:bg-black/70 transition-all"
              />
            </div>

            {/* EVENTS */}
            <div>
              <label className="block text-golden text-sm font-bold mb-2 uppercase">
                Events
              </label>
              <input
                type="number"
                min="1"
                max="15"
                value={depth}
                onChange={(e) => setDepth(parseInt(e.target.value) || 7)}
                className="w-full px-4 py-3 bg-black/50 border border-golden/40 rounded-lg text-white text-center text-xl font-bold focus:outline-none focus:border-golden focus:bg-black/70 transition-all"
              />
            </div>

            {/* POTENTIAL WIN */}
            <div>
              <label className="block text-golden text-sm font-bold mb-2 uppercase">
                Potential Win
              </label>
              <div
                className="w-full px-4 py-3 border rounded-lg text-green-400 text-center text-xl font-bold relative overflow-hidden"
                style={{
                  background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.15))',
                  borderColor: 'rgba(34, 197, 94, 0.4)',
                  boxShadow: '0 4px 16px rgba(34, 197, 94, 0.2)'
                }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-green-400/10 to-transparent pointer-events-none" />
                <span className="relative">${potentialWin.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Min Payout Multiplier */}
          <div>
            <label className="block text-golden text-sm font-bold mb-2 uppercase">
              Minimum Payout Multiplier
            </label>
            <input
              type="number"
              min="100"
              max="10000"
              step="100"
              value={minPayout}
              onChange={(e) => setMinPayout(parseInt(e.target.value) || 2500)}
              className="w-full px-4 py-3 bg-black/50 border border-golden/40 rounded-lg text-white text-center text-lg font-bold focus:outline-none focus:border-golden focus:bg-black/70 transition-all"
            />
            <p className="text-white/50 text-xs mt-1 text-center">
              Tickets will pay at least {minPayout}x your stake
            </p>
          </div>

          {/* Sports Selection */}
          <div>
            <label className="block text-golden text-sm font-bold mb-3 uppercase">
              Select Sports (at least one)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {filterSports.map((sport) => (
                <button
                  key={sport.uuid}
                  type="button"
                  onClick={() => toggleSport(sport.uuid)}
                  className={`
                    p-4 rounded-xl border-2 transition-all duration-200 relative overflow-hidden
                    ${selectedSports.includes(sport.uuid)
                      ? 'bg-gradient-to-br from-golden/20 to-yellow-600/20 border-golden shadow-lg shadow-golden/20'
                      : 'bg-black/30 border-white/20 hover:border-white/40 hover:bg-black/40'
                    }
                  `}
                >
                  <div className="text-3xl mb-2">{sport.icon}</div>
                  <div className="text-white text-sm font-semibold">{sport.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Timeframe Selection */}
          <div>
            <label className="block text-golden text-sm font-bold mb-3 uppercase">
              Events Starting Within
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
              {TIMEFRAME_BUTTONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setEventsWithin(option.value)}
                  className={`
                    px-3 py-2 rounded-lg border transition-all duration-200 text-sm font-semibold
                    ${eventsWithin === option.value
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 border-purple-400 text-white shadow-lg shadow-purple-500/30'
                      : 'bg-black/30 border-white/20 text-white/70 hover:border-white/40 hover:bg-black/40'
                    }
                  `}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Ticket Count */}
          <div>
            <label className="block text-golden text-sm font-bold mb-2 uppercase">
              Number of Tickets to Generate
            </label>
            <input
              type="number"
              min="1"
              max="100"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value) || 50)}
              className="w-full px-4 py-3 bg-black/50 border border-golden/40 rounded-lg text-white text-center text-lg font-bold focus:outline-none focus:border-golden focus:bg-black/70 transition-all"
            />
          </div>

          {/* Submit Button with Glow */}
          <button
            type="submit"
            disabled={selectedSports.length === 0}
            className={`
              w-full py-4 rounded-xl font-bold text-lg transition-all duration-200 relative overflow-hidden group
              ${selectedSports.length === 0
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-golden via-yellow-500 to-golden text-black hover:scale-[1.02]'
              }
            `}
            style={
              selectedSports.length > 0
                ? {
                    boxShadow: '0 0 30px rgba(251, 146, 60, 0.6), 0 0 60px rgba(251, 191, 36, 0.4)'
                  }
                : {}
            }
          >
            {/* Animated glow on hover */}
            {selectedSports.length > 0 && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000" />
            )}
            <span className="relative">
              {selectedSports.length === 0 ? 'Select at least one sport' : 'Get Tickets! 🎰'}
            </span>
          </button>

        </form>
      </div>
    </div>
  );
}