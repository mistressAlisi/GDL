import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

export function Register() {
  const { theme } = useTheme();
  const { register } = useAuth();
  const navigate = useNavigate();
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
    
    setIsLoading(true);
    
    try {
      // Use email as username for simplicity
      await register(email, email, password);
      // WebSocket connection is automatically initialized in AuthContext after successful registration
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: `linear-gradient(135deg, rgba(0, 0, 0, 0.95) 0%, rgba(10, 20, 10, 0.95) 50%, rgba(0, 0, 0, 0.95) 100%)`,
      }}
    >
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-20 animate-pulse"
          style={{ background: theme.accentColor }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-20 animate-pulse"
          style={{ background: theme.cardGlow, animationDelay: '1s' }}
        />
      </div>

      {/* Register Card */}
      <div
        className="relative w-full max-w-lg rounded-3xl p-8 backdrop-blur-xl my-8"
        style={{
          background: 'linear-gradient(135deg, rgba(0, 40, 0, 0.6) 0%, rgba(0, 20, 0, 0.8) 100%)',
          border: `3px solid ${theme.cardBorder}`,
          boxShadow: `
            0 0 80px ${theme.cardGlow}80,
            0 0 40px ${theme.accentColor}40,
            0 20px 60px rgba(0, 0, 0, 0.8),
            inset 0 0 40px rgba(255, 255, 255, 0.05),
            inset 0 0 80px ${theme.accentColor}10
          `,
        }}
      >
        {/* Accent glow overlay */}
        <div
          className="absolute inset-0 rounded-3xl opacity-20 pointer-events-none"
          style={{
            background: `radial-gradient(circle at top, ${theme.accentColor}60, transparent 70%)`,
          }}
        />

        {/* Logo */}
        <div className="relative text-center mb-6">
          <div className="inline-flex items-center gap-3 mb-4">
            <div
              className="w-16 h-16 rounded-xl flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, ${theme.accentColor}40, ${theme.accentColor}20)`,
                border: `2px solid ${theme.accentColor}`,
                boxShadow: `0 0 30px ${theme.accentColor}60`,
              }}
            >
              <span className="text-3xl">🎰</span>
            </div>
            <div className="text-left">
              <div
                className="text-2xl font-bold tracking-wider"
                style={{
                  color: theme.accentColor,
                  textShadow: `0 0 20px ${theme.accentColor}80, 0 2px 8px rgba(0, 0, 0, 0.9)`,
                }}
              >
                SPORTS
              </div>
              <div className="text-sm text-gray-300">LOTTO.net</div>
            </div>
          </div>
          <h2 className="text-white text-2xl font-bold mb-2">Create new account</h2>
        </div>

        {/* Form */}
        <form onSubmit={handleSignup} className="relative space-y-5">
          {/* Email */}
          <div>
            <p className="text-white text-sm mb-2">
              Welcome! Get <span className="font-bold text-green-400">1,500</span> in points for registering with your email:
            </p>
            <label className="block text-white text-sm font-bold mb-2">Email*</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none"
              style={{
                background: 'linear-gradient(135deg, rgba(80, 200, 120, 0.6) 0%, rgba(60, 180, 100, 0.6) 100%)',
                border: `2px solid ${theme.accentColor}40`,
                boxShadow: `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
            />
          </div>

          {/* Phone */}
          <div>
            <p className="text-white text-sm mb-2">
              Get <span className="font-bold text-green-400">2,500</span> points for registering your mobile phone:
            </p>
            <label className="block text-white text-sm font-bold mb-2">Phone</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1"
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none"
              style={{
                background: 'linear-gradient(135deg, rgba(80, 200, 120, 0.6) 0%, rgba(60, 180, 100, 0.6) 100%)',
                border: `2px solid ${theme.accentColor}40`,
                boxShadow: `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
            />
          </div>

          {/* Validation */}
          <div>
            <p className="text-white text-sm mb-2">
              Earn an extra <span className="font-bold text-green-400">1,000</span> points for also validating your phone:
            </p>
            <label className="block text-white text-sm font-bold mb-2">Validation</label>
            <select
              value={validation}
              onChange={(e) => setValidation(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none"
              style={{
                background: 'linear-gradient(135deg, rgba(40, 40, 40, 0.9) 0%, rgba(30, 30, 30, 0.9) 100%)',
                border: `2px solid ${theme.accentColor}40`,
                boxShadow: `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
            >
              <option value="none">None</option>
              <option value="sms">SMS</option>
              <option value="call">Phone Call</option>
            </select>
            <p className="text-xs text-gray-400 mt-1">
              By selecting a method; you opt-in to receive one 2FA message.
            </p>
          </div>

          {/* Password */}
          <div>
            <p className="text-white text-sm mb-2">
              Please enter and confirm your password for your new account:
            </p>
            <label className="block text-white text-sm font-bold mb-2">Password*</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none"
              style={{
                background: 'linear-gradient(135deg, rgba(80, 200, 120, 0.6) 0%, rgba(60, 180, 100, 0.6) 100%)',
                border: `2px solid ${theme.accentColor}40`,
                boxShadow: `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
            />
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-white text-sm font-bold mb-2">Confirm Password*</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none"
              style={{
                background: 'linear-gradient(135deg, rgba(80, 200, 120, 0.6) 0%, rgba(60, 180, 100, 0.6) 100%)',
                border: `2px solid ${theme.accentColor}40`,
                boxShadow: `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
            />
          </div>

          {/* Referral Code */}
          <div>
            <p className="text-white text-sm mb-2">
              If you have a Referral code, enter it below:
            </p>
            <label className="block text-white text-sm font-bold mb-2">Referral Code</label>
            <input
              type="text"
              value={referralCode}
              onChange={(e) => setReferralCode(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none"
              style={{
                background: 'linear-gradient(135deg, rgba(80, 200, 120, 0.6) 0%, rgba(60, 180, 100, 0.6) 100%)',
                border: `2px solid ${theme.accentColor}40`,
                boxShadow: `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`,
              }}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-xl px-4 py-3 text-white text-sm">
              {error}
            </div>
          )}

          {/* Signup Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(20, 20, 20, 0.9) 100%)',
              border: `2px solid ${theme.accentColor}`,
              boxShadow: `0 0 30px ${theme.accentColor}60, 0 4px 20px rgba(0, 0, 0, 0.6)`,
              textShadow: `0 0 10px ${theme.accentColor}`,
            }}
          >
            {isLoading ? 'Creating account...' : 'Signup Now!'}
          </button>

          {/* Back to Login */}
          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-white underline hover:no-underline transition-all"
              style={{
                textShadow: `0 0 10px ${theme.accentColor}80`,
              }}
            >
              Already have an account? Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}