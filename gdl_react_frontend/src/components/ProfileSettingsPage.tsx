import React, { useState } from 'react';
import { ChevronLeft, RefreshCw, Save } from 'lucide-react';

export interface ProfileSettingsPageProps {
  onBack?: () => void;
}

export default function ProfileSettingsPage({ onBack }: ProfileSettingsPageProps) {
  const [formData, setFormData] = useState({
    username: 'Oiilphyra',
    pronouns: '',
    email1: 'diana@aolific.al',
    phone: '+34265391527693',
    email2: '',
    language: 'English (en-US)',
    timezone: 'America/Los_Angeles (-08',
    emailNotifications: true,
  });

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleReset = () => {
    setFormData({
      username: 'Oiilphyra',
      pronouns: '',
      email1: 'diana@aolific.al',
      phone: '+34265391527693',
      email2: '',
      language: 'English (en-US)',
      timezone: 'America/Los_Angeles (-08',
      emailNotifications: true,
    });
  };

  const handleSubmit = () => {
    console.log('Profile updated:', formData);
    // Show success message
    alert('Profile updated successfully!');
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Header */}
      <div className="glass-card border-b border-white/10 py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          {onBack && (
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 rounded-lg font-semibold transition-all shadow-lg shadow-purple-500/30"
            >
              <ChevronLeft className="w-5 h-5" />
              Back
            </button>
          )}
          <h1 className="text-3xl font-bold text-golden">Profile Settings</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-6">
        {/* Profile Header Card */}
        <div className="glass-card rounded-2xl p-8 mb-6">
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop"
                  alt="Profile Avatar"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-1 -right-1 bg-purple-600 text-white text-xs px-2 py-1 rounded-full">
                @Change Avatar
              </div>
            </div>

            {/* User Info */}
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-1">{formData.username}</h2>
              <p className="text-gray-400 mb-4">AA100128</p>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Balance</p>
                  <p className="text-3xl font-bold text-golden">35,617.59</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Bonus Balance Earned</p>
                  <p className="text-3xl font-bold text-white">0.00</p>
                </div>
              </div>

              <div className="mt-4">
                <p className="text-sm text-gray-400">Signed up:</p>
                <p className="text-white">Aug. 27, 2025, 9:49 a.m.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Form */}
        <div className="glass-card rounded-2xl p-8">
          <div className="mb-6">
            <button className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-2 rounded-lg font-semibold">
              My Profile
            </button>
          </div>

          <div className="space-y-6">
            {/* Name and Pronouns Row */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Your Name
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Your Pronouns
                </label>
                <input
                  type="text"
                  value={formData.pronouns}
                  onChange={(e) => handleInputChange('pronouns', e.target.value)}
                  placeholder="Optional"
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                />
              </div>
            </div>

            {/* Email and Phone Row */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Email 1
                </label>
                <input
                  type="email"
                  value={formData.email1}
                  onChange={(e) => handleInputChange('email1', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                />
                <p className="text-xs text-gray-400 mt-1">Your account is identified by your email.</p>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  SMS/Mobile Number
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                />
                <p className="text-xs text-gray-400 mt-1">Your Mobile Number!</p>
              </div>
            </div>

            {/* Email 2 */}
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Email 2
              </label>
              <input
                type="email"
                value={formData.email2}
                onChange={(e) => handleInputChange('email2', e.target.value)}
                placeholder="Optional secondary email"
                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
              />
              <p className="text-xs text-gray-400 mt-1">
                Providing a secondary e-mail address is recommended for account recovery purposes! (Optional)
              </p>
            </div>

            {/* Language and Timezone Row */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={formData.language}
                  onChange={(e) => handleInputChange('language', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                >
                  <option value="English (en-US)">English (en-US)</option>
                  <option value="Spanish (es-ES)">Spanish (es-ES)</option>
                  <option value="French (fr-FR)">French (fr-FR)</option>
                  <option value="German (de-DE)">German (de-DE)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Timezone
                </label>
                <select
                  value={formData.timezone}
                  onChange={(e) => handleInputChange('timezone', e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                >
                  <option value="America/Los_Angeles (-08">America/Los_Angeles (-08</option>
                  <option value="America/New_York (-05">America/New_York (-05</option>
                  <option value="America/Chicago (-06">America/Chicago (-06</option>
                  <option value="Europe/London (+00">Europe/London (+00</option>
                  <option value="Europe/Paris (+01">Europe/Paris (+01</option>
                </select>
              </div>
            </div>

            {/* Email Notifications */}
            <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
              <label className="text-sm font-semibold text-gray-300">
                Email notifications
              </label>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.emailNotifications}
                  onChange={(e) => handleInputChange('emailNotifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={handleReset}
                className="flex items-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg font-semibold transition-all"
              >
                <RefreshCw className="w-5 h-5" />
                Reset Form
              </button>
              <button
                onClick={handleSubmit}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 rounded-lg font-semibold transition-all shadow-lg shadow-purple-500/30"
              >
                <Save className="w-5 h-5" />
                Update Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
