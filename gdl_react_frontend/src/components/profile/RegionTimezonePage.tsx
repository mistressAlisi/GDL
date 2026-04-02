import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Globe, Clock, MapPin, CheckCircle } from 'lucide-react';
import { useProfile } from '../../contexts/ProfileContext';
import { Button } from '../ui/button';
import { Label } from '../ui/label';

// Common US timezones
const timezones = [
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'America/Phoenix', label: 'Arizona Time (MST)' },
  { value: 'America/Anchorage', label: 'Alaska Time (AKT)' },
  { value: 'Pacific/Honolulu', label: 'Hawaii Time (HST)' },
];

const regions = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

export const RegionTimezonePage: React.FC = () => {
  const { userProfile, updateUserProfile } = useProfile();
  const [selectedTimezone, setSelectedTimezone] = useState(userProfile.timezone);
  const [selectedRegion, setSelectedRegion] = useState(userProfile.region);
  const [autoDetected, setAutoDetected] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // Auto-detect timezone on mount
    try {
      const detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (detectedTimezone && !userProfile.timezone) {
        setSelectedTimezone(detectedTimezone);
        setAutoDetected(true);
      }
    } catch (error) {
      console.error('Could not detect timezone:', error);
    }
  }, []);

  const handleSave = () => {
    updateUserProfile({
      timezone: selectedTimezone,
      region: selectedRegion,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const currentTime = new Date().toLocaleTimeString('en-US', {
    timeZone: selectedTimezone,
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

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
            Region & Timezone
          </h1>
          <p className="text-white/70">Configure your location and time settings</p>
        </div>

        {/* Auto-detect Notice */}
        {autoDetected && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-4 mb-6"
          >
            <div className="flex items-center gap-2 text-green-300">
              <CheckCircle size={20} />
              <span className="font-semibold">Timezone auto-detected!</span>
            </div>
          </motion.div>
        )}

        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          {/* Region Selection */}
          <div className="mb-8">
            <Label className="text-white/90 flex items-center gap-2 mb-3">
              <MapPin size={18} />
              <span className="font-semibold text-lg">Your Region</span>
            </Label>
            <p className="text-white/60 text-sm mb-4">
              Select your state/region. This helps us show you relevant lottery games available in your area.
            </p>
            
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full p-4 rounded-lg bg-white/5 border border-white/20 text-white text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
            >
              <option value="">Select your state...</option>
              {regions.map(region => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>

            {selectedRegion && (
              <div className="mt-3 p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
                <div className="text-cyan-300 text-sm">
                  ✓ Selected Region: <span className="font-bold">{selectedRegion}</span>
                </div>
              </div>
            )}
          </div>

          {/* Timezone Selection */}
          <div className="mb-8">
            <Label className="text-white/90 flex items-center gap-2 mb-3">
              <Clock size={18} />
              <span className="font-semibold text-lg">Your Timezone</span>
            </Label>
            <p className="text-white/60 text-sm mb-4">
              Select your timezone to see accurate draw times and countdowns.
            </p>
            
            <select
              value={selectedTimezone}
              onChange={(e) => setSelectedTimezone(e.target.value)}
              className="w-full p-4 rounded-lg bg-white/5 border border-white/20 text-white text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-yellow-400/50"
            >
              {timezones.map(tz => (
                <option key={tz.value} value={tz.value}>
                  {tz.label}
                </option>
              ))}
            </select>

            {selectedTimezone && (
              <div className="mt-3 p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                <div className="text-purple-300 text-sm flex items-center gap-2">
                  <Globe size={16} />
                  Current time in {timezones.find(tz => tz.value === selectedTimezone)?.label}:
                  <span className="font-bold text-lg">{currentTime}</span>
                </div>
              </div>
            )}
          </div>

          {/* Save Button */}
          <div className="flex items-center gap-4">
            <Button
              onClick={handleSave}
              disabled={!selectedRegion || !selectedTimezone}
              className="flex-1 h-12 bg-gradient-to-r from-green-400 to-emerald-500 hover:from-green-500 hover:to-emerald-600 text-white font-bold shadow-lg shadow-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saved ? (
                <>
                  <CheckCircle size={20} className="mr-2" />
                  Settings Saved!
                </>
              ) : (
                'Save Settings'
              )}
            </Button>
          </div>

          {/* Info Box */}
          <div className="mt-6 bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">ℹ️</div>
              <div>
                <div className="font-bold text-blue-300 mb-1">Why do we need this?</div>
                <ul className="text-sm text-blue-200/80 space-y-1">
                  <li>• Show you lotteries available in your region</li>
                  <li>• Display accurate draw times and countdowns</li>
                  <li>• Ensure compliance with regional lottery regulations</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
