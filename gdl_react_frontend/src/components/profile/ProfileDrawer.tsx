import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, User, FileText, Wallet, Settings, DollarSign, TrendingUp, Trophy, Shield, Globe, Lock, AlertTriangle } from 'lucide-react';
import { useProfile } from '../../contexts/ProfileContext';
import { useTranslation } from '../../utils/translations';
import { OpenTicketsPage } from './OpenTicketsPage';
import { GradedTicketsPage } from './GradedTicketsPage';
import { DepositPage } from './DepositPage';
import { WithdrawPage } from './WithdrawPage';
import { RegionTimezonePage } from './RegionTimezonePage';
import { SecuritySettingsPage } from './SecuritySettingsPage';
import { ManageLimitsPage } from './ManageLimitsPage';
import { AccountLockoutPage } from './AccountLockoutPage';
import { ProfilePage } from './ProfilePage';

interface ProfileDrawerProps {
  isMobile?: boolean;
}

type MenuItem = 'profile' | 'open-tickets' | 'graded-tickets' | 'deposit' | 'withdraw' | 'region-timezone' | 'security' | 'manage-limits' | 'account-lockout';

export const ProfileDrawer: React.FC<ProfileDrawerProps> = ({ isMobile = false }) => {
  const { userProfile, currentProfilePage, setCurrentProfilePage, profileDrawerOpen, setProfileDrawerOpen } = useProfile();
  const t = useTranslation(userProfile.language);

  const handleMenuClick = (page: MenuItem) => {
    setCurrentProfilePage(page);
  };

  const handleClose = () => {
    setCurrentProfilePage(null);
    setProfileDrawerOpen(false);
  };

  const handleBackToMenu = () => {
    setCurrentProfilePage(null);
  };

  const renderPage = () => {
    switch (currentProfilePage) {
      case 'profile':
        return <ProfilePage />;
      case 'open-tickets':
        return <OpenTicketsPage />;
      case 'graded-tickets':
        return <GradedTicketsPage />;
      case 'deposit':
        return <DepositPage />;
      case 'withdraw':
        return <WithdrawPage />;
      case 'region-timezone':
        return <RegionTimezonePage />;
      case 'security':
        return <SecuritySettingsPage />;
      case 'manage-limits':
        return <ManageLimitsPage />;
      case 'account-lockout':
        return <AccountLockoutPage />;
      default:
        return null;
    }
  };

  // Navigation menu component (reusable for both mobile and desktop)
  const NavigationMenu = ({ showCloseButton = false }: { showCloseButton?: boolean }) => (
    <div className="p-4">
      {showCloseButton && (
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent">
            {t('profile')}
          </h2>
          <button
            onClick={handleClose}
            className="p-2 text-white/60 hover:text-white transition-colors rounded-lg hover:bg-white/10"
          >
            <X size={24} />
          </button>
        </div>
      )}

      {/* Balance Display */}
      <div className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-2xl p-6 mb-4">
        <div className="text-yellow-300/80 text-sm mb-1">{t('balance')}</div>
        <div className="text-4xl font-bold text-yellow-300 mb-4">
          ${userProfile.balance.toFixed(2)}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-cyan-300/80 text-sm mb-1">
            <FileText size={14} />
            <span>{t('activeBets')}</span>
          </div>
          <div className="text-2xl font-bold text-cyan-300">{userProfile.activeBetsCount}</div>
        </div>
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4">
          <div className="flex items-center gap-2 text-green-300/80 text-sm mb-1">
            <Trophy size={14} />
            <span>{t('totalWins')}</span>
          </div>
          <div className="text-2xl font-bold text-green-300">${userProfile.totalWins.toFixed(2)}</div>
        </div>
      </div>

      {/* User Name - Clickable to go to Profile Page */}
      <button
        onClick={() => handleMenuClick('profile')}
        className="w-full bg-white/10 backdrop-blur-md border border-white/20 hover:border-yellow-400/50 rounded-xl p-4 mb-6 transition-all hover:bg-white/15"
      >
        <div className="flex items-center gap-3">
          {userProfile.profilePicture ? (
            <img
              src={userProfile.profilePicture}
              alt={userProfile.username}
              className="w-12 h-12 rounded-full object-cover border-2 border-purple-400"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
              <User className="text-white" size={24} />
            </div>
          )}
          <div className="text-left flex-1">
            <div className="text-white/60 text-sm">{t('loggedInAs')}</div>
            <div className="text-white font-bold text-lg">{userProfile.username}</div>
            {userProfile.pronouns && (
              <div className="text-white/50 text-xs italic">({userProfile.pronouns})</div>
            )}
          </div>
          <Settings className="text-white/40" size={18} />
        </div>
      </button>

      {/* Menu Items */}
      <div className="space-y-4">
        {/* Tickets Section */}
        <div className="space-y-2">
          <div className="text-white/40 text-xs uppercase tracking-wider px-2 mb-2">{t('tickets')}</div>
          <button
            onClick={() => handleMenuClick('open-tickets')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <FileText className="text-cyan-400" size={18} />
            <span className="text-white font-medium">{t('openTickets')}</span>
          </button>

          <button
            onClick={() => handleMenuClick('graded-tickets')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <Trophy className="text-green-400" size={18} />
            <span className="text-white font-medium">{t('gradedTickets')}</span>
          </button>
        </div>

        {/* Cashier Section */}
        <div className="space-y-2">
          <div className="text-white/40 text-xs uppercase tracking-wider px-2 mb-2">{t('cashier')}</div>
          <button
            onClick={() => handleMenuClick('deposit')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <TrendingUp className="text-green-400" size={18} />
            <span className="text-white font-medium">{t('deposit')}</span>
          </button>

          <button
            onClick={() => handleMenuClick('withdraw')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <DollarSign className="text-orange-400" size={18} />
            <span className="text-white font-medium">{t('withdraw')}</span>
          </button>
        </div>

        {/* Settings Section */}
        <div className="space-y-2">
          <div className="text-white/40 text-xs uppercase tracking-wider px-2 mb-2">{t('settings')}</div>
          <button
            onClick={() => handleMenuClick('region-timezone')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <Globe className="text-blue-400" size={18} />
            <span className="text-white font-medium">{t('regionTimezone')}</span>
          </button>

          <button
            onClick={() => handleMenuClick('security')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <Shield className="text-purple-400" size={18} />
            <span className="text-white font-medium">{t('security')}</span>
          </button>

          <button
            onClick={() => handleMenuClick('manage-limits')}
            className="w-full flex items-center gap-3 p-3 bg-white/10 hover:bg-white/15 border border-white/20 rounded-lg transition-all"
          >
            <Lock className="text-indigo-400" size={18} />
            <span className="text-white font-medium">{t('manageLimits')}</span>
          </button>

          <button
            onClick={() => handleMenuClick('account-lockout')}
            className="w-full flex items-center gap-3 p-3 bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 rounded-lg transition-all"
          >
            <AlertTriangle className="text-red-400" size={18} />
            <span className="text-red-300 font-medium">{t('accountLockout')}</span>
          </button>
        </div>
      </div>
    </div>
  );

  // Desktop Layout: Sidebar + Main Canvas Content
  if (!isMobile && profileDrawerOpen) {
    return (
      <AnimatePresence>
        {profileDrawerOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={handleClose}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            />

            {/* Desktop: Drawer from right with menu */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed top-0 right-0 h-full w-[380px] bg-gradient-to-br from-slate-900 via-blue-950 to-purple-950 border-l border-white/10 overflow-y-auto z-50"
            >
              <NavigationMenu showCloseButton={true} />
            </motion.div>

            {/* Main Canvas Content - Shows selected page */}
            <AnimatePresence>
              {currentProfilePage && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="fixed top-16 left-4 right-[400px] bottom-4 bg-gradient-to-br from-slate-900/95 via-blue-950/95 to-purple-950/95 backdrop-blur-xl border border-white/20 rounded-2xl overflow-hidden z-50 shadow-2xl"
                >
                  <div className="h-full flex flex-col">
                    {/* Page Header */}
                    <div className="flex-shrink-0 bg-white/5 border-b border-white/10 p-4">
                      <div className="flex items-center justify-between">
                        <h2 className="text-xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent">
                          My Account
                        </h2>
                        <button
                          onClick={handleBackToMenu}
                          className="px-4 py-2 text-cyan-400 hover:text-cyan-300 text-sm flex items-center gap-2 bg-cyan-500/10 hover:bg-cyan-500/20 rounded-lg transition-all border border-cyan-500/30"
                        >
                          ← Back to Menu
                        </button>
                      </div>
                    </div>

                    {/* Page Content */}
                    <div className="flex-1 overflow-y-auto">
                      {renderPage()}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}
      </AnimatePresence>
    );
  }

  // Mobile Layout: Full-screen drawer or main canvas content
  return (
    <AnimatePresence>
      {profileDrawerOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Mobile Drawer or Page Content */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 via-blue-950 to-purple-950 overflow-hidden"
          >
            <div className="h-full flex flex-col">
              {/* Header */}
              <div className="flex-shrink-0 bg-white/5 border-b border-white/10 p-4">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent">
                    {currentProfilePage ? 'My Account' : 'Profile'}
                  </h2>
                  <button
                    onClick={handleClose}
                    className="p-2 text-white/60 hover:text-white transition-colors rounded-lg hover:bg-white/10"
                  >
                    <X size={24} />
                  </button>
                </div>

                {/* Back Button (when on a subpage) */}
                {currentProfilePage && (
                  <button
                    onClick={handleBackToMenu}
                    className="text-cyan-400 hover:text-cyan-300 text-sm flex items-center gap-1"
                  >
                    ← Back to Menu
                  </button>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto">
                {currentProfilePage ? (
                  // Render the selected page
                  <div className="h-full">
                    {renderPage()}
                  </div>
                ) : (
                  // Render the menu
                  <NavigationMenu />
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};