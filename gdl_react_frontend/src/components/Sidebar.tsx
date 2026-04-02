import React, { useState } from 'react';
import {
  Ticket,
  CheckCircle2,
  XCircle,
  Wallet,
  DollarSign,
  Settings,
  LogOut,
  MessageSquare,
  Menu,
  X,
  Palette,
  Sliders
} from 'lucide-react';
import { useAuth } from '../sportslotto/contexts/AuthContext';

interface SidebarProps {
  onGetTickets?: () => void;
  onOpenTickets?: () => void;
  onGradedTickets?: () => void;
  onBalance?: () => void;
  onCashier?: () => void;
  onSettings?: () => void;
  onThemeSettings?: () => void;
  onTicketRules?: () => void;
  onMessages?: () => void;
  onLogout?: () => void;
}

export function Sidebar({
  onGetTickets,
  onOpenTickets,
  onGradedTickets,
  onBalance,
  onCashier,
  onSettings,
  onThemeSettings,
  onTicketRules,
  onMessages,
  onLogout,
}: SidebarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user } = useAuth();


  const menuItems = [
    { icon: Ticket, label: 'Get Tickets', onClick: onGetTickets },
    {
      icon: CheckCircle2,
      label: 'Open Tickets',
      onClick: () => {
        if (onOpenTickets) {
          onOpenTickets();
        } else {
          navigate('/tickets/pending');
        }
      }
    },
    {
      icon: XCircle,
      label: 'Graded Tickets',
      onClick: () => {
        if (onGradedTickets) {
          onGradedTickets();
        } else {
          navigate('/tickets/graded');
        }
      }
    },
    { icon: Wallet, label: 'Balance', onClick: onBalance },
    { icon: DollarSign, label: 'Cashier', onClick: onCashier },
    { icon: Sliders, label: 'Ticket Defaults', onClick: onTicketRules },
    { icon: Palette, label: 'Theme Settings', onClick: onThemeSettings },
    { icon: Settings, label: 'Settings', onClick: onSettings },
    { icon: LogOut, label: 'Logout', onClick: onLogout },
  ];

  const handleMenuClick = (onClick?: () => void) => {
    onClick?.();
    setMobileMenuOpen(false); // Close menu on mobile after clicking
  };

  return (
    <>
      {/* Mobile Hamburger Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg shadow-lg"
      >
        {mobileMenuOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <Menu className="w-6 h-6 text-white" />
        )}
      </button>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        w-64 bg-gradient-to-b from-gray-900/95 to-gray-800/95 backdrop-blur-xl border-r border-white/10 flex flex-col h-screen
        fixed lg:relative z-40
        transition-transform duration-300
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <Ticket className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-white text-lg">BETANY LOTTO</h2>
              <p className="text-xs text-gray-400">Premium Betting</p>
            </div>
          </div>
        </div>

        {/* User Profile */}
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center overflow-hidden">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt="User Avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-2xl">👤</span>
              )}
            </div>
            <div className="flex-1">
              {/* Show acctname if set, otherwise show acctnum as the name */}
              <h3 className="text-white font-semibold text-sm">
                {user?.acctname || user?.acctnum || user?.username || 'Guest'}
              </h3>
              {/* Show acctnum below name if acctname is set */}
              {user?.acctname && (
                <p className="text-gray-400 text-xs">{user.acctnum}</p>
              )}
            </div>
          </div>

          {/* Balance Stats */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-[10px] text-gray-400 uppercase">Bal.</p>
              <p className="text-sm font-bold text-golden">${user?.balance?.toFixed(2) || '0.00'}</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-400 uppercase">FP</p>
              <p className="text-sm font-bold text-white">${user?.bonus?.toFixed(2) || '0.00'}</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-400 uppercase">Pen.</p>
              <p className="text-sm font-bold text-white">${user?.pending?.toFixed(2) || '0.00'}</p>
            </div>
          </div>

          <div className="mt-2">
            <p className="text-[10px] text-gray-400 uppercase">Avail.</p>
            <p className="text-lg font-bold text-white">${user?.available?.toFixed(2) || '0.00'}</p>
          </div>

          {/* Messages */}
          <button
            onClick={onMessages}
            className="w-full mt-3 flex items-center justify-center gap-2 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all border border-white/10"
          >
            <MessageSquare className="w-4 h-4" />
            <span className="text-sm">Messages</span>
            {user?.message_count && user.message_count > 0 && (
              <span className="ml-auto bg-purple-600 text-white text-xs px-2 py-0.5 rounded-full">
                {user.message_count}
              </span>
            )}
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {menuItems.map((item) => (
            <button
              key={item.label}
              onClick={() => handleMenuClick(item.onClick)}
              className="w-full flex items-center gap-3 px-4 py-3 text-gray-300 hover:bg-white/10 hover:text-white rounded-lg transition-all group"
            >
              <item.icon className="w-5 h-5 group-hover:text-purple-400 transition-colors" />
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 text-center">
          <p className="text-xs text-gray-500">© 2026 BETANY LOTTO</p>
        </div>
      </div>
    </>
  );
}