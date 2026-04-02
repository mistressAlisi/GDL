import React, { useState } from 'react';
import { useTheme } from '../../sportslotto/contexts/ThemeContext';
import { useAuth } from '../../sportslotto/contexts/AuthContext';
import { UserPlus, Mail, Phone, Lock, Gift, ArrowLeft } from 'lucide-react';

interface RegisterPageProps {
  onNavigateToLogin: () => void;
}

export function RegisterPage({ onNavigateToLogin }: RegisterPageProps) {
  const { theme } = useTheme();
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [validation, setValidation] = useState('none');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [referralCode, setReferralCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match!');
      return;
    }
    
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Use email as username for simplicity
      await register(email.split('@')[0], email, password);
      // WebSocket connection is automatically initialized in AuthContext after successful registration
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center relative overflow-hidden py-12"
      style={{
        background: `linear-gradient(135deg, 
          rgba(0, 0, 0, 0.98) 0%, 
          rgba(10, 10, 30, 0.98) 25%,
          rgba(20, 0, 40, 0.98) 50%,
          rgba(10, 10, 30, 0.98) 75%,
          rgba(0, 0, 0, 0.98) 100%)`,
      }}
    >
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-40 -left-40 w-96 h-96 rounded-full blur-3xl opacity-30 animate-pulse"
          style={{ 
            background: `radial-gradient(circle, ${theme.accentColor}60, transparent 70%)`,
            animationDuration: '4s'
          }}
        />
        <div
          className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full blur-3xl opacity-30 animate-pulse"
          style={{ 
            background: `radial-gradient(circle, ${theme.cardGlow}60, transparent 70%)`,
            animationDelay: '2s',
            animationDuration: '4s'
          }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl opacity-20"
          style={{ 
            background: `radial-gradient(circle, ${theme.accentColor}40, transparent 70%)`,
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-lg px-6">
        {/* Back Button */}
        <button
          onClick={onNavigateToLogin}
          className="mb-6 flex items-center gap-2 text-gray-400 hover:text-white transition-all"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm">Back to Login</span>
        </button>

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-4 mb-6">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center backdrop-blur-xl"
              style={{
                background: `linear-gradient(135deg, ${theme.accentColor}20, ${theme.accentColor}10)`,
                border: `2px solid ${theme.accentColor}60`,
                boxShadow: `0 0 40px ${theme.accentColor}40, inset 0 0 40px ${theme.accentColor}10`,
              }}
            >
              <span className="text-4xl">🎰</span>
            </div>
            <div className="text-left">
              <div
                className="text-3xl font-bold tracking-wider mb-1"
                style={{
                  background: `linear-gradient(135deg, ${theme.accentColor}, ${theme.cardGlow})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  filter: `drop-shadow(0 0 20px ${theme.accentColor}40)`,
                }}
              >
                BETANY
              </div>
              <div className="text-base text-gray-300 tracking-wide">LOTTO</div>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Create Your Account</h1>
          <p className="text-gray-400">Start winning with exclusive bonuses</p>
        </div>

        {/* Bonus Banner */}
        <div 
          className="mb-6 p-4 rounded-xl backdrop-blur-xl flex items-center gap-3"
          style={{
            background: `linear-gradient(135deg, ${theme.accentColor}10, ${theme.cardGlow}05)`,
            border: `1px solid ${theme.accentColor}30`,
            boxShadow: `0 0 30px ${theme.accentColor}20`,
          }}
        >
          <Gift 
            className="w-8 h-8 flex-shrink-0"
            style={{ color: theme.accentColor }}
          />
          <div className="text-sm">
            <p className="text-white font-semibold">Welcome Bonus!</p>
            <p className="text-gray-300">Get up to 5,000 points for signing up</p>
          </div>
        </div>

        {/* Register Form */}
        <form onSubmit={handleSignup} className="space-y-5">
          {/* Email */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2 flex items-center gap-2">
              Email
              <span 
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ 
                  background: `${theme.accentColor}20`,
                  color: theme.accentColor,
                }}
              >
                +1,500 points
              </span>
            </label>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-4 pl-12 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                placeholder="your@email.com"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${theme.accentColor}30`,
                  boxShadow: `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
                }}
                onFocus={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.target.style.borderColor = `${theme.accentColor}60`;
                  e.target.style.boxShadow = `0 0 30px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`;
                }}
                onBlur={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                  e.target.style.borderColor = `${theme.accentColor}30`;
                  e.target.style.boxShadow = `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`;
                }}
              />
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>

          {/* Phone */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2 flex items-center gap-2">
              Phone (Optional)
              <span 
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ 
                  background: `${theme.accentColor}20`,
                  color: theme.accentColor,
                }}
              >
                +2,500 points
              </span>
            </label>
            <div className="relative">
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
                className="w-full px-4 py-4 pl-12 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${theme.accentColor}30`,
                  boxShadow: `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
                }}
                onFocus={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.target.style.borderColor = `${theme.accentColor}60`;
                }}
                onBlur={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                  e.target.style.borderColor = `${theme.accentColor}30`;
                }}
              />
              <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>

          {/* Validation */}
          {phone && (
            <div>
              <label className="block text-white text-sm font-semibold mb-2 flex items-center gap-2">
                Phone Validation
                <span 
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ 
                    background: `${theme.accentColor}20`,
                    color: theme.accentColor,
                  }}
                >
                  +1,000 points
                </span>
              </label>
              <select
                value={validation}
                onChange={(e) => setValidation(e.target.value)}
                className="w-full px-4 py-4 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${theme.accentColor}30`,
                  boxShadow: `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
                }}
              >
                <option value="none" className="bg-gray-900">None</option>
                <option value="sms" className="bg-gray-900">SMS Verification</option>
                <option value="call" className="bg-gray-900">Phone Call</option>
              </select>
              <p className="text-xs text-gray-400 mt-2">
                One-time verification message. Standard rates may apply.
              </p>
            </div>
          )}

          {/* Password */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2">Password</label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-4 pl-12 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                placeholder="Create a strong password"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${theme.accentColor}30`,
                  boxShadow: `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
                }}
                onFocus={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.target.style.borderColor = `${theme.accentColor}60`;
                }}
                onBlur={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                  e.target.style.borderColor = `${theme.accentColor}30`;
                }}
              />
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2">Confirm Password</label>
            <div className="relative">
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full px-4 py-4 pl-12 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                placeholder="Re-enter your password"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${theme.accentColor}30`,
                  boxShadow: `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
                }}
                onFocus={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.target.style.borderColor = `${theme.accentColor}60`;
                }}
                onBlur={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                  e.target.style.borderColor = `${theme.accentColor}30`;
                }}
              />
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>

          {/* Referral Code */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2">
              Referral Code (Optional)
            </label>
            <input
              type="text"
              value={referralCode}
              onChange={(e) => setReferralCode(e.target.value)}
              className="w-full px-4 py-4 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
              placeholder="Enter referral code"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: `1px solid ${theme.accentColor}30`,
                boxShadow: `0 0 20px ${theme.accentColor}10, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
              onFocus={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.08)';
                e.target.style.borderColor = `${theme.accentColor}60`;
              }}
              onBlur={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                e.target.style.borderColor = `${theme.accentColor}30`;
              }}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div 
              className="backdrop-blur-xl rounded-xl px-4 py-3 text-white text-sm border"
              style={{
                background: 'rgba(220, 38, 38, 0.1)',
                borderColor: 'rgba(220, 38, 38, 0.5)',
                boxShadow: '0 0 20px rgba(220, 38, 38, 0.2)',
              }}
            >
              {error}
            </div>
          )}

          {/* Sign Up Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-xl flex items-center justify-center gap-2"
            style={{
              background: `linear-gradient(135deg, ${theme.accentColor}80, ${theme.cardGlow}60)`,
              border: `1px solid ${theme.accentColor}60`,
              boxShadow: `0 0 40px ${theme.accentColor}40, 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 40px ${theme.accentColor}20`,
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
            }}
          >
            <UserPlus className="w-5 h-5" />
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>

          {/* Terms */}
          <p className="text-xs text-gray-400 text-center">
            By creating an account, you agree to our{' '}
            <span className="underline cursor-pointer hover:text-white">Terms of Service</span>
            {' '}and{' '}
            <span className="underline cursor-pointer hover:text-white">Privacy Policy</span>
          </p>
        </form>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">
            © 2026 BETANY LOTTO. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}
