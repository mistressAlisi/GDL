import React, { useState, useRef } from 'react';
import { motion } from 'motion/react';
import { Camera, User, Mail, Phone, Globe, Clock, Upload, RotateCcw } from 'lucide-react';
import { useProfile } from '../../contexts/ProfileContext';
import { useTranslation } from '../../utils/translations';

export const ProfilePage: React.FC = () => {
  const { userProfile, updateUserProfile } = useProfile();
  const t = useTranslation(userProfile.language);
  
  const [formData, setFormData] = useState({
    username: userProfile.username,
    pronouns: userProfile.pronouns || '',
    email: userProfile.email,
    phone: userProfile.phone || '',
    email2: userProfile.email2 || '',
    language: userProfile.language,
    timezone: userProfile.timezone,
    profilePicture: userProfile.profilePicture || '',
  });

  const [previewImage, setPreviewImage] = useState<string>(userProfile.profilePicture || '');
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        setPreviewImage(result);
        setFormData(prev => ({ ...prev, profilePicture: result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpdateProfile = () => {
    updateUserProfile(formData);
    setShowSuccessMessage(true);
    setTimeout(() => setShowSuccessMessage(false), 3000);
  };

  const handleResetForm = () => {
    setFormData({
      username: userProfile.username,
      pronouns: userProfile.pronouns || '',
      email: userProfile.email,
      phone: userProfile.phone || '',
      email2: userProfile.email2 || '',
      language: userProfile.language,
      timezone: userProfile.timezone,
      profilePicture: userProfile.profilePicture || '',
    });
    setPreviewImage(userProfile.profilePicture || '');
  };

  const commonTimezones = [
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'America/Phoenix',
    'America/Anchorage',
    'Pacific/Honolulu',
    'America/Toronto',
    'America/Mexico_City',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Australia/Sydney',
  ];

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4 md:p-6">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent mb-2">
            {t('profileSettings')}
          </h2>
          <p className="text-white/60 text-sm">{t('personalInformation')}</p>
        </div>

        {/* Success Message */}
        {showSuccessMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-4 p-4 bg-green-500/20 border border-green-500/50 rounded-xl text-green-300 text-sm w-fit"
          >
            ✓ {t('profileUpdated')}
          </motion.div>
        )}

        {/* Profile Picture Section */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 md:p-6 border border-white/10 mb-4 w-fit">
          <label className="block text-white/80 text-sm font-semibold mb-3">
            {t('profilePicture')}
          </label>
          <div className="flex items-center gap-4">
            <div className="relative">
              {previewImage ? (
                <img
                  src={previewImage}
                  alt="Profile"
                  className="w-24 h-24 rounded-full object-cover border-4 border-yellow-400/30"
                />
              ) : (
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center border-4 border-yellow-400/30">
                  <User className="text-white" size={40} />
                </div>
              )}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-0 right-0 p-2 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full hover:shadow-lg transition-all"
              >
                <Camera size={16} className="text-black" />
              </button>
            </div>
            <div>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white text-sm transition-all flex items-center gap-2"
              >
                <Upload size={16} />
                {previewImage ? t('changeImage') : t('uploadImage')}
              </button>
              <p className="text-white/40 text-xs mt-1">JPG, PNG or GIF (max 5MB)</p>
            </div>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
        </div>

        {/* Form Fields - Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          {/* Full Name */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('fullName')}
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
              <input
                type="text"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-yellow-400/50 transition-all"
                placeholder="Your full name"
              />
            </div>
          </div>

          {/* Pronouns */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('pronouns')}
            </label>
            <input
              type="text"
              value={formData.pronouns}
              onChange={(e) => handleInputChange('pronouns', e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-yellow-400/50 transition-all"
              placeholder={t('pronounsPlaceholder')}
            />
          </div>

          {/* Email */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('email')}
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-yellow-400/50 transition-all"
                placeholder="your.email@example.com"
              />
            </div>
          </div>

          {/* Phone */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('phone')}
            </label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-yellow-400/50 transition-all"
                placeholder={t('phonePlaceholder')}
              />
            </div>
          </div>

          {/* Recovery Email */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10 md:col-span-2 lg:col-span-1">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('recoveryEmail')}
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
              <input
                type="email"
                value={formData.email2}
                onChange={(e) => handleInputChange('email2', e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-yellow-400/50 transition-all"
                placeholder={t('recoveryEmailPlaceholder')}
              />
            </div>
          </div>

          {/* Language */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('language')}
            </label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
              <select
                value={formData.language}
                onChange={(e) => handleInputChange('language', e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-yellow-400/50 transition-all appearance-none cursor-pointer"
              >
                <option value="en" className="bg-gray-800">English</option>
                <option value="es" className="bg-gray-800">Español</option>
              </select>
            </div>
          </div>

          {/* Timezone */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
            <label className="block text-white/80 text-sm font-semibold mb-2">
              {t('timezone')}
            </label>
            <div className="relative">
              <Clock className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
              <select
                value={formData.timezone}
                onChange={(e) => handleInputChange('timezone', e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-yellow-400/50 transition-all appearance-none cursor-pointer"
              >
                {commonTimezones.map((tz) => (
                  <option key={tz} value={tz} className="bg-gray-800">
                    {tz.replace(/_/g, ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 w-fit">
          <button
            onClick={handleResetForm}
            className="px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-white font-semibold transition-all flex items-center justify-center gap-2"
          >
            <RotateCcw size={18} />
            {t('resetForm')}
          </button>
          <button
            onClick={handleUpdateProfile}
            className="px-6 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 hover:shadow-xl rounded-xl text-black font-bold transition-all"
          >
            {t('updateProfile')}
          </button>
        </div>
      </div>
    </div>
  );
};