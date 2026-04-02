import React from "react";
import { motion } from "motion/react";
import { OddsCalculator } from "../components/OddsCalculator";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface ResponsibleGamingProps {
  onNavigate: (page: string) => void;
}

export default function ResponsibleGaming({ onNavigate }: ResponsibleGamingProps) {
  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-purple-950">
      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between p-4 md:p-6">
        <button onClick={() => onNavigate('home')} className="flex items-center space-x-3 group">
          <div className="w-10 h-10 md:w-12 md:h-12 rounded-full overflow-hidden ring-2 ring-yellow-400/30 group-hover:ring-yellow-400/50 transition-all">
            <img src={globeLogo} alt="All Lotto Globe" className="w-full h-full object-cover" />
          </div>
          <span className="text-xl md:text-2xl tracking-wide bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-200 bg-clip-text text-transparent" style={{ fontFamily: 'Georgia, serif', fontWeight: 700 }}>
            ALL LOTTO
          </span>
        </button>
        <div className="flex items-center space-x-3 md:space-x-6">
          <button onClick={() => onNavigate('home')} className="hidden sm:block text-white/80 hover:text-white transition-colors text-sm md:text-base">
            Home
          </button>
          <button onClick={() => onNavigate('games')} className="hidden sm:block text-white/80 hover:text-white transition-colors text-sm md:text-base">
            Games
          </button>
          <button onClick={() => onNavigate('about')} className="hidden sm:block text-white/80 hover:text-white transition-colors text-sm md:text-base">
            About
          </button>
          <button className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold transition-all hover:brightness-110 active:scale-95">
            Sign In
          </button>
        </div>
      </nav>

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Responsible <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">Gaming</span>
            </h1>
            <p className="text-white/70 text-lg max-w-3xl mx-auto">
              At All Lotto, we're committed to providing a safe and responsible gaming environment. 
              Gaming should be fun and entertaining, never a source of financial stress.
            </p>
          </div>

          {/* Key Principles */}
          <motion.div
            className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-8 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Our Commitment</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🛡️</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Player Protection</h3>
                <p className="text-white/70">
                  Tools and resources to help you stay in control
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">⏰</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Time & Money Limits</h3>
                <p className="text-white/70">
                  Set personal limits that work for you
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🤝</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Support Network</h3>
                <p className="text-white/70">
                  Access to professional help when needed
                </p>
              </div>
            </div>
          </motion.div>

          {/* Setting Limits */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">💵</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Set Your Limits</h2>
                <p className="text-white/70">
                  Take control of your gaming experience by setting personal limits.
                </p>
              </div>
            </div>
            <div className="space-y-4 mt-6">
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-2">Deposit Limits</h3>
                <p className="text-white/70">
                  Set daily, weekly, or monthly deposit limits to control how much money you can add to your account.
                </p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-2">Loss Limits</h3>
                <p className="text-white/70">
                  Protect yourself by setting maximum loss limits over specific time periods.
                </p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-2">Session Time Limits</h3>
                <p className="text-white/70">
                  Receive reminders or automatic logouts after playing for a set amount of time.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Warning Signs */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">⚠️</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Recognizing Problem Gambling</h2>
                <p className="text-white/70">
                  Be aware of the warning signs that gaming may be becoming a problem.
                </p>
              </div>
            </div>
            <div className="space-y-3 mt-6">
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 mt-1">•</span>
                <p className="text-white/70">Spending more money or time than you can afford</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 mt-1">•</span>
                <p className="text-white/70">Chasing losses by continuing to play to win back money</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 mt-1">•</span>
                <p className="text-white/70">Neglecting work, family, or other responsibilities</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 mt-1">•</span>
                <p className="text-white/70">Borrowing money or selling possessions to fund gaming</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 mt-1">•</span>
                <p className="text-white/70">Lying about or hiding your gaming activities</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 mt-1">•</span>
                <p className="text-white/70">Feeling anxious, irritable, or restless when not gaming</p>
              </div>
            </div>
          </motion.div>

          {/* Self-Exclusion */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">🚫</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Self-Exclusion</h2>
                <p className="text-white/70">
                  Take a break when you need it with our self-exclusion tools.
                </p>
              </div>
            </div>
            <div className="space-y-4 mt-6">
              <p className="text-white/70">
                If you feel that gaming is negatively impacting your life, you can choose to self-exclude 
                from All Lotto for a period of your choosing:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-white mb-1">24 Hours</p>
                  <p className="text-white/60">Cool-off Period</p>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-white mb-1">6 Months</p>
                  <p className="text-white/60">Extended Break</p>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-white mb-1">Permanent</p>
                  <p className="text-white/60">Account Closure</p>
                </div>
              </div>
              <p className="text-white/70">
                During self-exclusion, you will not be able to access your account or participate in any gaming activities.
              </p>
            </div>
          </motion.div>

          {/* Help & Resources */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">📞</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Get Help & Support</h2>
                <p className="text-white/70">
                  Professional organizations are available 24/7 to provide confidential support.
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-3">National Council on Problem Gambling</h3>
                <p className="text-cyan-400 text-2xl font-bold mb-2">1-800-522-4700</p>
                <p className="text-white/70">Free, confidential help 24/7</p>
                <a href="https://www.ncpgambling.org" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 transition-colors">
                  www.ncpgambling.org
                </a>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-3">Gamblers Anonymous</h3>
                <p className="text-cyan-400 text-2xl font-bold mb-2">International Support</p>
                <p className="text-white/70">Peer support groups worldwide</p>
                <a href="https://www.gamblersanonymous.org" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 transition-colors">
                  www.gamblersanonymous.org
                </a>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-3">GamCare (UK)</h3>
                <p className="text-cyan-400 text-2xl font-bold mb-2">0808 802 0133</p>
                <p className="text-white/70">UK-based support and counseling</p>
                <a href="https://www.gamcare.org.uk" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 transition-colors">
                  www.gamcare.org.uk
                </a>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-3">BeGambleAware</h3>
                <p className="text-cyan-400 text-2xl font-bold mb-2">Online Support</p>
                <p className="text-white/70">Information and tools for safer gambling</p>
                <a href="https://www.begambleaware.org" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300 transition-colors">
                  www.begambleaware.org
                </a>
              </div>
            </div>
          </motion.div>

          {/* Age Verification */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">🔞</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Age Verification & Underage Gaming</h2>
                <p className="text-white/70">
                  You must be 18 years or older to use All Lotto.
                </p>
              </div>
            </div>
            <div className="space-y-4 mt-6">
              <p className="text-white/70">
                We take underage gambling seriously. All users must verify their age before participating in 
                any gaming activities. We employ strict verification processes and monitoring to prevent 
                underage access.
              </p>
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                <p className="text-white/90">
                  <strong>Parents:</strong> Consider using parental control software to prevent children from 
                  accessing gambling sites. Learn more about protecting your family at organizations like 
                  Net Nanny or Family Safety.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Tips for Responsible Gaming */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="flex items-start space-x-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">💡</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Tips for Staying in Control</h2>
                <p className="text-white/70">
                  Simple guidelines to help you enjoy gaming responsibly.
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Set a budget before you start and stick to it</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Never chase your losses</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Take regular breaks from gaming</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Don't play when upset or stressed</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Balance gaming with other activities</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Keep track of time and money spent</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Understand that the odds are against you</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-cyan-400 text-xl">✓</span>
                <p className="text-white/70">Seek help early if you're concerned</p>
              </div>
            </div>
          </motion.div>

          {/* Lottery Odds Calculator */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.85 }}
            className="mb-8"
          >
            <OddsCalculator />
          </motion.div>

          {/* Contact CTA */}
          <motion.div
            className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-8 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <h2 className="text-2xl font-bold text-white mb-3">Need Help Managing Your Account?</h2>
            <p className="text-white/70 mb-6">
              Our support team can assist you with setting limits, self-exclusion, or any other responsible gaming tools.
            </p>
            <button
              onClick={() => onNavigate('support')}
              className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold transition-all hover:brightness-110 active:scale-95"
            >
              Contact Support
            </button>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-8 px-6 mt-12">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-white/60">© 2025 All Lotto. All rights reserved.</p>
          <div className="flex items-center space-x-6">
            <button onClick={() => onNavigate('glossary')} className="text-white/60 hover:text-white transition-colors">
              Glossary
            </button>
            <button onClick={() => onNavigate('terms')} className="text-white/60 hover:text-white transition-colors">
              Terms
            </button>
            <button onClick={() => onNavigate('privacy')} className="text-white/60 hover:text-white transition-colors">
              Privacy
            </button>
            <button onClick={() => onNavigate('responsible-gaming')} className="text-white hover:text-white transition-colors">
              Responsible Gaming
            </button>
            <button onClick={() => onNavigate('support')} className="text-white/60 hover:text-white transition-colors">
              Support
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}