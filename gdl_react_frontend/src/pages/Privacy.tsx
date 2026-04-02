import React from "react";
import { motion } from "motion/react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface PrivacyProps {
  onNavigate: (page: string) => void;
}

export default function Privacy({ onNavigate }: PrivacyProps) {
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
            Privacy <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">Policy</span>
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
              <h2 className="text-2xl font-bold text-white mb-4">1. Introduction</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                At All Lotto, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and 
                safeguard your information when you use our lottery betting platform.
              </p>
              <p className="text-white/80 leading-relaxed">
                By using All Lotto, you agree to the collection and use of information in accordance with this policy. If you 
                do not agree with our policies and practices, please do not use our services.
              </p>
            </motion.div>

            {/* Section 2 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">2. Information We Collect</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                We collect several types of information to provide and improve our services:
              </p>
              
              <h3 className="text-xl font-bold text-white mb-3">Personal Information</h3>
              <ul className="space-y-2 text-white/80 mb-4">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Name, email address, and date of birth</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Account credentials (username and password)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Payment information (processed securely through third-party providers)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Identity verification documents (for regulatory compliance)</span>
                </li>
              </ul>

              <h3 className="text-xl font-bold text-white mb-3">Usage Data</h3>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Betting history and game preferences</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Device information (IP address, browser type, operating system)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Log data and cookies</span>
                </li>
              </ul>
            </motion.div>

            {/* Section 3 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">3. How We Use Your Information</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                We use the collected information for various purposes:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To provide and maintain our lottery betting services</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To process your bets and manage your account</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To verify your identity and comply with legal requirements</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To notify you about account activity and important updates</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To improve our platform and user experience</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To detect and prevent fraud and abuse</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span>To send promotional communications (with your consent)</span>
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
              <h2 className="text-2xl font-bold text-white mb-4">4. Data Security</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                We implement industry-standard security measures to protect your personal information:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>SSL/TLS encryption for all data transmissions</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Secure password hashing and storage</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Regular security audits and penetration testing</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Limited access to personal data by authorized personnel only</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>Secure data centers with 24/7 monitoring</span>
                </li>
              </ul>
              <p className="text-white/60 text-sm mt-4 italic">
                Note: While we strive to protect your information, no method of transmission over the internet is 100% secure.
              </p>
            </motion.div>

            {/* Section 5 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">5. Information Sharing</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                We do not sell, trade, or rent your personal information to third parties. We may share your information only in 
                the following circumstances:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>With payment processors to handle transactions securely</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>With regulatory authorities when required by law</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>With service providers who assist in operating our platform (under strict confidentiality agreements)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span>In connection with a business transfer or merger (with notice to you)</span>
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
              <h2 className="text-2xl font-bold text-white mb-4">6. Your Privacy Rights</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                You have the following rights regarding your personal information:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span><strong>Access:</strong> Request a copy of your personal data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span><strong>Correction:</strong> Update or correct inaccurate information</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span><strong>Deletion:</strong> Request deletion of your account and data</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span><strong>Opt-out:</strong> Unsubscribe from marketing communications</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-400 mr-2">✓</span>
                  <span><strong>Data Portability:</strong> Receive your data in a structured format</span>
                </li>
              </ul>
              <p className="text-white/80 leading-relaxed mt-4">
                To exercise these rights, please contact us through our{" "}
                <button onClick={() => onNavigate('support')} className="text-cyan-400 hover:text-cyan-300 underline">
                  Support page
                </button>.
              </p>
            </motion.div>

            {/* Section 7 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">7. Cookies and Tracking</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                We use cookies and similar tracking technologies to enhance your experience:
              </p>
              <ul className="space-y-2 text-white/80">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong>Essential Cookies:</strong> Required for basic platform functionality</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong>Performance Cookies:</strong> Help us understand how you use our platform</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong>Functionality Cookies:</strong> Remember your preferences and settings</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong>Marketing Cookies:</strong> Deliver relevant advertisements (with your consent)</span>
                </li>
              </ul>
              <p className="text-white/80 leading-relaxed mt-4">
                You can control cookies through your browser settings, though disabling some may affect platform functionality.
              </p>
            </motion.div>

            {/* Section 8 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">8. Data Retention</h2>
              <p className="text-white/80 leading-relaxed">
                We retain your personal information for as long as necessary to provide our services and comply with legal obligations. 
                After account closure, we may retain certain information for a period required by law or for legitimate business purposes 
                such as fraud prevention and regulatory compliance.
              </p>
            </motion.div>

            {/* Section 9 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">9. Changes to This Policy</h2>
              <p className="text-white/80 leading-relaxed">
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new policy on 
                this page and updating the "Last updated" date. Continued use of our services after changes constitutes acceptance of 
                the updated policy.
              </p>
            </motion.div>

            {/* Section 10 */}
            <motion.div
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.1 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">10. Contact Us</h2>
              <p className="text-white/80 leading-relaxed">
                If you have any questions about this Privacy Policy or how we handle your data, please visit our{" "}
                <button onClick={() => onNavigate('support')} className="text-cyan-400 hover:text-cyan-300 underline">
                  Support page
                </button>{" "}
                or contact our privacy team.
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
            <button onClick={() => onNavigate('terms')} className="text-white/60 hover:text-white transition-colors">
              Terms
            </button>
            <button onClick={() => onNavigate('privacy')} className="text-white hover:text-white transition-colors">
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