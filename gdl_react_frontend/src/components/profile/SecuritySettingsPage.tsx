import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Lock, Key, Bell, CheckCircle, Eye, EyeOff, AlertTriangle } from 'lucide-react';
import { useProfile } from '../../contexts/ProfileContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';

export const SecuritySettingsPage: React.FC = () => {
  const { securitySettings, updateSecuritySettings, changePassword } = useProfile();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordChanged, setPasswordChanged] = useState(false);

  const daysSincePasswordChange = Math.floor(
    (Date.now() - securitySettings.lastPasswordChange.getTime()) / (1000 * 60 * 60 * 24)
  );

  const handlePasswordChange = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      alert('Please fill in all password fields');
      return;
    }

    if (newPassword !== confirmPassword) {
      alert('New passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      alert('New password must be at least 8 characters long');
      return;
    }

    setIsChangingPassword(true);

    try {
      const success = await changePassword(currentPassword, newPassword);
      if (success) {
        setPasswordChanged(true);
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setTimeout(() => setPasswordChanged(false), 5000);
      }
    } catch (error) {
      alert('Failed to change password. Please try again.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleToggleLoginNotifications = () => {
    updateSecuritySettings({
      loginNotifications: !securitySettings.loginNotifications,
    });
  };

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
            Security Settings
          </h1>
          <p className="text-white/70">Manage your account security and password</p>
        </div>

        {/* Password Section */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
              <Key className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Change Password</h2>
              <p className="text-white/60 text-sm">
                Last changed {daysSincePasswordChange} days ago
              </p>
            </div>
          </div>

          {daysSincePasswordChange > 90 && (
            <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 mb-4">
              <div className="flex items-start gap-2 text-orange-300 text-sm">
                <AlertTriangle size={16} className="flex-shrink-0 mt-0.5" />
                <span>
                  It's been over 90 days since you changed your password. For security, we recommend changing it regularly.
                </span>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <Label className="text-white/90">Current Password</Label>
              <div className="relative">
                <Input
                  type={showCurrentPassword ? 'text' : 'password'}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Enter current password"
                  className="bg-white/5 border-white/20 text-white placeholder:text-white/40 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80"
                >
                  {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div>
              <Label className="text-white/90">New Password</Label>
              <div className="relative">
                <Input
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password (min 8 characters)"
                  className="bg-white/5 border-white/20 text-white placeholder:text-white/40 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80"
                >
                  {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div>
              <Label className="text-white/90">Confirm New Password</Label>
              <div className="relative">
                <Input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  className="bg-white/5 border-white/20 text-white placeholder:text-white/40 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80"
                >
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <Button
              onClick={handlePasswordChange}
              disabled={isChangingPassword || !currentPassword || !newPassword || !confirmPassword}
              className="w-full h-12 bg-gradient-to-r from-orange-400 to-red-500 hover:from-orange-500 hover:to-red-600 text-white font-bold shadow-lg shadow-orange-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isChangingPassword ? 'Changing Password...' : passwordChanged ? (
                <>
                  <CheckCircle size={20} className="mr-2" />
                  Password Changed!
                </>
              ) : 'Change Password'}
            </Button>
          </div>
        </div>

        {/* Login Notifications */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
              <Bell className="text-white" size={24} />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-white">Login Notifications</h2>
              <p className="text-white/60 text-sm">
                Get notified when someone logs into your account
              </p>
            </div>
            <Switch
              checked={securitySettings.loginNotifications}
              onCheckedChange={handleToggleLoginNotifications}
              className="data-[state=checked]:bg-green-500"
            />
          </div>

          <div className="text-white/60 text-sm">
            {securitySettings.loginNotifications 
              ? '✓ You will receive email notifications for new login attempts'
              : 'Login notifications are disabled'}
          </div>
        </div>

        {/* Security Tips */}
        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-2xl p-6">
          <div className="flex items-start gap-3">
            <Lock className="text-blue-300 flex-shrink-0" size={24} />
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Security Tips</h3>
              <ul className="text-sm text-white/80 space-y-2">
                <li>• Use a strong, unique password that you don't use elsewhere</li>
                <li>• Never share your password or login credentials with anyone</li>
                <li>• Change your password regularly (every 90 days recommended)</li>
                <li>• Be cautious of phishing emails claiming to be from us</li>
                <li>• Always log out when using a shared or public computer</li>
                <li>• Keep your recovery email up to date in case you need to reset your password</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
