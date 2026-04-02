import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

export function Login() {
  const { theme } = useTheme();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      await login(username, password);
      // WebSocket connection is automatically initialized in AuthContext after successful login
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentLogin = () => {
    // TODO: Implement agent login
    console.log('Agent login');
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

      {/* Login Card */}
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
          <p className="text-white text-lg">Please login or register below.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="relative space-y-4">
          {/* Username */}
          <div>
            <label className="block text-white text-sm font-bold mb-2">Username*</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none focus:ring-2"
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

          {/* Password */}
          <div>
            <label className="block text-white text-sm font-bold mb-2">Password*</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl text-white font-medium transition-all focus:outline-none focus:ring-2"
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

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-xl px-4 py-3 text-white text-sm">
              {error}
            </div>
          )}

          {/* Login Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl font-bold text-white transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(20, 20, 20, 0.9) 100%)',
              border: `2px solid ${theme.accentColor}`,
              boxShadow: `0 0 30px ${theme.accentColor}60, 0 4px 20px rgba(0, 0, 0, 0.6)`,
              textShadow: `0 0 10px ${theme.accentColor}`,
            }}
          >
            {isLoading ? 'Logging in...' : 'Login!'}
          </button>

          {/* Forgot Password Link */}
          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/recovery')}
              className="text-white underline hover:no-underline transition-all"
              style={{
                textShadow: `0 0 10px ${theme.accentColor}80`,
              }}
            >
              Forgot Password/Account?
            </button>
          </div>

          {/* Register Button */}
          <button
            type="button"
            onClick={() => navigate('/register')}
            className="w-full py-3 rounded-xl font-bold text-white transition-all hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, rgba(60, 180, 100, 0.8) 0%, rgba(40, 150, 80, 0.8) 100%)',
              border: `2px solid ${theme.accentColor}`,
              boxShadow: `0 0 30px ${theme.accentColor}40, 0 4px 20px rgba(0, 0, 0, 0.6)`,
            }}
          >
            Register new account
          </button>

          {/* Agent Login Button */}
          <button
            type="button"
            onClick={handleAgentLogin}
            className="w-full py-3 rounded-xl font-bold text-white transition-all hover:scale-105"
            style={{
              background: 'transparent',
              border: `2px solid ${theme.accentColor}`,
              boxShadow: `0 0 20px ${theme.accentColor}30, inset 0 0 20px rgba(0, 0, 0, 0.5)`,
            }}
          >
            Agent Login
          </button>
        </form>
      </div>
    </div>
  );
}