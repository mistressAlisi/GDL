import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { useTheme } from '../contexts/ThemeContext';

export function Recovery() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleRecover = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement actual recovery logic
    console.log('Recovery email sent to:', email);
    setSubmitted(true);
    setTimeout(() => {
      navigate('/login');
    }, 3000);
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

      {/* Recovery Card */}
      <div
        className="relative w-full max-w-md rounded-3xl p-8 backdrop-blur-xl"
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
        {/* Close Button */}
        <button
          onClick={() => navigate('/login')}
          className="absolute top-4 right-4 w-10 h-10 rounded-lg flex items-center justify-center transition-all hover:scale-110"
          style={{
            background: 'rgba(0, 0, 0, 0.5)',
            border: `2px solid ${theme.accentColor}40`,
            boxShadow: `0 0 20px ${theme.accentColor}20`,
          }}
        >
          <span className="text-white text-2xl">×</span>
        </button>

        {/* Accent glow overlay */}
        <div
          className="absolute inset-0 rounded-3xl opacity-20 pointer-events-none"
          style={{
            background: `radial-gradient(circle at top, ${theme.accentColor}60, transparent 70%)`,
          }}
        />

        {/* Header */}
        <div className="relative text-center mb-6">
          <h2
            className="text-2xl font-bold mb-2"
            style={{
              color: theme.accentColor,
              textShadow: `0 0 20px ${theme.accentColor}80, 0 2px 8px rgba(0, 0, 0, 0.9)`,
            }}
          >
            Account Recovery for SportsLotto.net:
          </h2>
          <div className="w-full h-1 rounded-full mb-4" style={{ background: theme.accentColor }} />
          <h3 className="text-xl font-bold text-white mb-3">Forgot your password?</h3>
          <p className="text-white text-sm">
            Please enter the e-mail associated with your account. We'll send out a recovery password to this address.
          </p>
        </div>

        {/* Form or Success Message */}
        {!submitted ? (
          <form onSubmit={handleRecover} className="relative space-y-5">
            {/* Email */}
            <div>
              <label className="block text-white text-sm font-bold mb-2">Email</label>
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
                onFocus={(e) => {
                  e.target.style.boxShadow = `0 0 30px ${theme.accentColor}40, inset 0 0 20px rgba(0, 0, 0, 0.3)`;
                  e.target.style.borderColor = theme.accentColor;
                }}
                onBlur={(e) => {
                  e.target.style.boxShadow = `0 0 20px ${theme.accentColor}20, inset 0 0 20px rgba(0, 0, 0, 0.3)`;
                  e.target.style.borderColor = `${theme.accentColor}40`;
                }}
              />
            </div>

            {/* Recover Button */}
            <button
              type="submit"
              className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-105"
              style={{
                background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(20, 20, 20, 0.9) 100%)',
                border: `2px solid ${theme.accentColor}`,
                boxShadow: `0 0 30px ${theme.accentColor}60, 0 4px 20px rgba(0, 0, 0, 0.6)`,
                textShadow: `0 0 10px ${theme.accentColor}`,
              }}
            >
              Recover Account!
            </button>
          </form>
        ) : (
          <div className="relative text-center py-8">
            <div
              className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-4"
              style={{
                background: `linear-gradient(135deg, ${theme.accentColor}40, ${theme.accentColor}20)`,
                border: `3px solid ${theme.accentColor}`,
                boxShadow: `0 0 40px ${theme.accentColor}80`,
              }}
            >
              <span className="text-5xl">✓</span>
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Recovery Email Sent!</h3>
            <p className="text-white text-sm mb-4">
              Please check your inbox for password reset instructions.
            </p>
            <p
              className="text-sm"
              style={{
                color: theme.accentColor,
                textShadow: `0 0 10px ${theme.accentColor}80`,
              }}
            >
              Redirecting to login...
            </p>
          </div>
        )}

        {/* Back to Login */}
        {!submitted && (
          <div className="relative text-center mt-4">
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-white underline hover:no-underline transition-all"
              style={{
                textShadow: `0 0 10px ${theme.accentColor}80`,
              }}
            >
              Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
