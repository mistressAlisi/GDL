import React, { useState } from 'react';
import { useTheme } from '../../sportslotto/contexts/ThemeContext';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';

interface RecoveryPageProps {
  onNavigateToLogin: () => void;
}

export function RecoveryPage({ onNavigateToLogin }: RecoveryPageProps) {
  const { theme } = useTheme();
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleRecover = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement actual recovery logic
    console.log('Recovery email sent to:', email);
    setSubmitted(true);
    setTimeout(() => {
      onNavigateToLogin();
    }, 3000);
  };

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center relative overflow-hidden"
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
      <div className="relative z-10 w-full max-w-md px-6">
        {!submitted && (
          <button
            onClick={onNavigateToLogin}
            className="mb-6 flex items-center gap-2 text-gray-400 hover:text-white transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm">Back to Login</span>
          </button>
        )}

        {/* Logo */}
        <div className="text-center mb-10">
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
        </div>

        {/* Content */}
        {!submitted ? (
          <>
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-white mb-2">Forgot Password?</h1>
              <p className="text-gray-400">
                No worries! Enter your email and we'll send you reset instructions.
              </p>
            </div>

            <form onSubmit={handleRecover} className="space-y-6">
              {/* Email Field */}
              <div>
                <label className="block text-white text-sm font-semibold mb-2">Email Address</label>
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

              {/* Submit Button */}
              <button
                type="submit"
                className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-[1.02] active:scale-[0.98] backdrop-blur-xl"
                style={{
                  background: `linear-gradient(135deg, ${theme.accentColor}80, ${theme.cardGlow}60)`,
                  border: `1px solid ${theme.accentColor}60`,
                  boxShadow: `0 0 40px ${theme.accentColor}40, 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 40px ${theme.accentColor}20`,
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
                }}
              >
                Send Reset Link
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-8">
            {/* Success Icon */}
            <div 
              className="inline-flex items-center justify-center w-24 h-24 rounded-full mb-6 backdrop-blur-xl"
              style={{
                background: `linear-gradient(135deg, ${theme.accentColor}20, ${theme.accentColor}10)`,
                border: `2px solid ${theme.accentColor}60`,
                boxShadow: `0 0 60px ${theme.accentColor}60, inset 0 0 40px ${theme.accentColor}10`,
              }}
            >
              <CheckCircle 
                className="w-16 h-16"
                style={{ color: theme.accentColor }}
              />
            </div>

            {/* Success Message */}
            <h2 className="text-2xl font-bold text-white mb-3">Check Your Email!</h2>
            <p className="text-gray-300 mb-2">
              We've sent password reset instructions to
            </p>
            <p 
              className="font-semibold mb-6"
              style={{ color: theme.accentColor }}
            >
              {email}
            </p>
            <p className="text-sm text-gray-400 mb-8">
              Didn't receive the email? Check your spam folder or try again.
            </p>

            {/* Auto-redirect notice */}
            <div 
              className="inline-block px-6 py-3 rounded-xl backdrop-blur-xl"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: `1px solid ${theme.accentColor}30`,
              }}
            >
              <p className="text-sm text-gray-300">
                Redirecting to login in{' '}
                <span 
                  className="font-bold"
                  style={{ color: theme.accentColor }}
                >
                  3 seconds
                </span>
                ...
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-xs text-gray-500">
            © 2026 BETANY LOTTO. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}
