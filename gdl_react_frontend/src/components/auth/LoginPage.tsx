import React, { useState } from 'react';
import { useTheme } from '../../sportslotto/contexts/ThemeContext';
import { useAuth } from '../../sportslotto/contexts/AuthContext';
import { LogIn, UserPlus, Key } from 'lucide-react';
import logoImage from 'figma:asset/301f5cf1a3c9c295c85742209667068b3698ba89.png';

interface LoginPageProps {
  onNavigateToRegister: () => void;
  onNavigateToRecovery: () => void;
}

export function LoginPage({ onNavigateToRegister, onNavigateToRecovery }: LoginPageProps) {
  const { theme } = useTheme();
  const { login } = useAuth();
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
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
        {/* Top left glow */}
        <div
          className="absolute -top-40 -left-40 w-96 h-96 rounded-full blur-3xl opacity-30 animate-pulse"
          style={{
            background: `radial-gradient(circle, ${theme.accentColor}60, transparent 70%)`,
            animationDuration: '4s'
          }}
        />
        {/* Bottom right glow */}
        <div
          className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full blur-3xl opacity-30 animate-pulse"
          style={{
            background: `radial-gradient(circle, ${theme.cardGlow}60, transparent 70%)`,
            animationDelay: '2s',
            animationDuration: '4s'
          }}
        />
        {/* Center accent */}
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl opacity-20"
          style={{
            background: `radial-gradient(circle, ${theme.accentColor}40, transparent 70%)`,
          }}
        />
        {/* Floating orbs */}
        <div
          className="absolute top-1/4 right-1/4 w-32 h-32 rounded-full blur-2xl opacity-20 animate-pulse"
          style={{
            background: theme.accentColor,
            animationDelay: '1s',
            animationDuration: '3s'
          }}
        />
        <div
          className="absolute bottom-1/4 left-1/3 w-40 h-40 rounded-full blur-2xl opacity-20 animate-pulse"
          style={{
            background: theme.cardGlow,
            animationDelay: '0.5s',
            animationDuration: '3.5s'
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-4 mb-6">
            {/* Logo Image */}
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center overflow-hidden backdrop-blur-xl"
              style={{
                background: 'rgba(0, 0, 0, 0.5)',
                border: `2px solid ${theme.accentColor}60`,
                boxShadow: `0 0 40px ${theme.accentColor}40, inset 0 0 40px ${theme.accentColor}10`,
              }}
            >
              <img
                src={logoImage}
                alt="SPORTS LOTTO"
                className="w-full h-full object-contain"
                style={{
                  filter: 'brightness(1.1)',
                }}
              />
            </div>
            {/* Brand Text */}
            <div className="text-left">
              <div
                className="text-4xl font-bold tracking-wider mb-1"
                style={{
                  background: `linear-gradient(135deg, ${theme.accentColor}, ${theme.cardGlow})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: `0 0 40px ${theme.accentColor}60`,
                  filter: `drop-shadow(0 0 20px ${theme.accentColor}40)`,
                }}
              >
                SPORTS
              </div>
              <div className="text-lg text-gray-300 tracking-wide">LOTTO</div>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400">Sign in to continue betting</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-6">
          {/* Username Field */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2">Username</label>
            <div className="relative">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-4 py-4 pl-12 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                placeholder="Enter your username"
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
              <LogIn
                className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
              />
            </div>
          </div>

          {/* Password Field */}
          <div>
            <label className="block text-white text-sm font-semibold mb-2">Password</label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-4 pl-12 rounded-xl text-white font-medium transition-all focus:outline-none backdrop-blur-xl"
                placeholder="Enter your password"
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
              <Key
                className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
              />
            </div>
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

          {/* Forgot Password */}
          <div className="text-right">
            <button
              type="button"
              onClick={onNavigateToRecovery}
              className="text-sm transition-all hover:brightness-125"
              style={{
                color: theme.accentColor,
                textShadow: `0 0 10px ${theme.accentColor}60`,
              }}
            >
              Forgot Password?
            </button>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-xl"
            style={{
              background: `linear-gradient(135deg, ${theme.accentColor}80, ${theme.cardGlow}60)`,
              border: `1px solid ${theme.accentColor}60`,
              boxShadow: `0 0 40px ${theme.accentColor}40, 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 40px ${theme.accentColor}20`,
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
            }}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div
                className="w-full border-t"
                style={{ borderColor: `${theme.accentColor}20` }}
              />
            </div>
            <div className="relative flex justify-center text-sm">
              <span
                className="px-4 backdrop-blur-xl rounded-full"
                style={{
                  background: 'rgba(0, 0, 0, 0.5)',
                  color: 'rgba(255, 255, 255, 0.6)',
                }}
              >
                New to SPORTS LOTTO?
              </span>
            </div>
          </div>

          {/* Register Button */}
          <button
            type="button"
            onClick={onNavigateToRegister}
            className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-[1.02] active:scale-[0.98] backdrop-blur-xl flex items-center justify-center gap-2"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${theme.accentColor}40`,
              boxShadow: `0 0 30px ${theme.accentColor}20, inset 0 0 40px rgba(0, 0, 0, 0.3)`,
            }}
          >
            <UserPlus className="w-5 h-5" />
            Create Account
          </button>

          {/* Agent Login Button */}
          <button
            type="button"
            onClick={() => window.location.href = '/management/'}
            className="w-full py-4 rounded-xl font-bold text-white transition-all hover:scale-[1.02] active:scale-[0.98] backdrop-blur-xl flex items-center justify-center gap-2"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${theme.accentColor}40`,
              boxShadow: `0 0 30px ${theme.accentColor}20, inset 0 0 40px rgba(0, 0, 0, 0.3)`,
            }}
          >
            <Key className="w-5 h-5" />
            Agent Login
          </button>
        </form>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-xs text-gray-500">
            © 2026 SPORTS LOTTO. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}