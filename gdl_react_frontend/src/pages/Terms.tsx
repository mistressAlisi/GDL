import React from "react";
import { motion } from "motion/react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface TermsProps {
  onNavigate: (page: string) => void;
}

export default function Terms({ onNavigate }: TermsProps) {
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
      <div className="relative z-10 max-w-4xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-bold text-white mb-6">
            Terms & <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Conditions</span>
          </h1>

          <p className="text-white/60 mb-8">Last updated: December 31, 2025</p>

          <div className="space-y-6">
            {/* Section 1 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">1. Acceptance of Terms</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                By accessing and using All Lotto, you accept and agree to be bound by the terms and provisions of this agreement. 
                If you do not agree to these terms, please do not use our service.
              </p>
              <p className="text-white/80 leading-relaxed">
                These Terms & Conditions govern your use of our lottery betting platform and services. We reserve the right to 
                modify these terms at any time, and such modifications shall be effective immediately upon posting.
              </p>
            </motion.div>

            {/* Section 2 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">2. Age Requirements</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                You must be at least 18 years old (or the legal age of majority in your jurisdiction, whichever is higher) to use 
                All Lotto services. By using our platform, you represent and warrant that you meet this age requirement.
              </p>
              <p className="text-white/80 leading-relaxed">
                We reserve the right to request proof of age at any time. Failure to provide such proof may result in account 
                suspension or termination.
              </p>
            </motion.div>

            {/* Section 3 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">3. Lottery Betting vs. Lottery Tickets</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                All Lotto provides lottery betting services, not lottery ticket sales. When you place a bet with us, you are 
                betting on the outcome of official lottery draws, not purchasing official lottery tickets.
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Your bet is with All Lotto, not the official lottery organization</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Winnings are paid by All Lotto based on the official lottery results</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Prize amounts may differ from official lottery prizes</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>All bets are final once placed and cannot be cancelled</span>
                </li>
              </ul>
            </motion.div>

            {/* Section 4 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">4. Account Responsibilities</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                You are responsible for maintaining the confidentiality of your account credentials and for all activities that 
                occur under your account. You agree to:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Provide accurate and complete information during registration</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Keep your password secure and confidential</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Notify us immediately of any unauthorized use of your account</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Maintain only one account per person</span>
                </li>
              </ul>
            </motion.div>

            {/* Section 5 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">5. Responsible Gaming</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                All Lotto is committed to responsible gaming. We encourage all users to play responsibly and within their means:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Set deposit limits and stick to them</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Never bet more than you can afford to lose</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Take regular breaks from betting</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Seek help if you feel you have a gambling problem</span>
                </li>
              </ul>
            </motion.div>

            {/* Section 6 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">6. Prohibited Activities</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                The following activities are strictly prohibited:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">✗</span>
                  <span>Using multiple accounts to circumvent betting limits</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">✗</span>
                  <span>Attempting to manipulate or exploit the platform</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">✗</span>
                  <span>Using automated bots or scripts</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">✗</span>
                  <span>Money laundering or fraudulent activities</span>
                </li>
                <li className="flex items-start">
                  <span className="text-red-400 mr-2">✗</span>
                  <span>Sharing account credentials with others</span>
                </li>
              </ul>
            </motion.div>

            {/* Section 7 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">7. Limitation of Liability</h2>
              <p className="text-white/80 leading-relaxed">
                All Lotto shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting 
                from your use or inability to use the service. We do not guarantee uninterrupted service and are not responsible for 
                technical issues, delays, or interruptions.
              </p>
            </motion.div>

            {/* Section 8 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">8. Contact Information</h2>
              <p className="text-white/80 leading-relaxed">
                If you have any questions about these Terms & Conditions, please contact us through our{" "}
                <button onClick={() => onNavigate('support')} className="text-cyan-400 hover:text-cyan-300 underline">
                  Support page
                </button>.
              </p>
            </motion.div>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-8 px-6 mt-12">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <p className="text-white/60">© 2025 All Lotto. All rights reserved.</p>
          <div className="flex items-center space-x-6">
            <button onClick={() => onNavigate('glossary')} className="text-white/60 hover:text-white transition-colors">
              Glossary
            </button>
            <button onClick={() => onNavigate('terms')} className="text-white hover:text-white transition-colors">
              Terms
            </button>
            <button onClick={() => onNavigate('privacy')} className="text-white/60 hover:text-white transition-colors">
              Privacy
            </button>
            <button onClick={() => onNavigate('responsible-gaming')} className="text-white/60 hover:text-white transition-colors">
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