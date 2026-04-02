import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Menu, X } from "lucide-react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface AboutProps {
  onNavigate: (page: string) => void;
}

export default function About({ onNavigate }: AboutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavigation = (page: string) => {
    setMobileMenuOpen(false);
    onNavigate(page);
  };

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
          <button onClick={() => onNavigate('faq')} className="hidden sm:block text-white/80 hover:text-white transition-colors text-sm md:text-base">
            FAQ
          </button>
          <button className="hidden sm:block px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold transition-all hover:brightness-110 active:scale-95">
            Sign In
          </button>
          {/* Mobile Menu Button */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="sm:hidden p-2 text-white/80 hover:text-white transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 sm:hidden"
            />
            
            {/* Menu Panel */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed top-0 right-0 h-full w-64 bg-slate-900/95 backdrop-blur-xl border-l border-white/10 z-50 sm:hidden"
            >
              <div className="flex flex-col h-full p-6">
                {/* Close button */}
                <button 
                  onClick={() => setMobileMenuOpen(false)}
                  className="self-end p-2 text-white/80 hover:text-white transition-colors mb-8"
                >
                  <X size={24} />
                </button>

                {/* Menu Items */}
                <nav className="flex flex-col space-y-4">
                  <button 
                    onClick={() => handleNavigation('home')}
                    className="text-left text-white/80 hover:text-white transition-colors text-lg py-2"
                  >
                    Home
                  </button>
                  <button 
                    onClick={() => handleNavigation('games')}
                    className="text-left text-white/80 hover:text-white transition-colors text-lg py-2"
                  >
                    Games
                  </button>
                  <button 
                    onClick={() => handleNavigation('about')}
                    className="text-left text-white/80 hover:text-white transition-colors text-lg py-2"
                  >
                    About
                  </button>
                  <button 
                    onClick={() => handleNavigation('faq')}
                    className="text-left text-white/80 hover:text-white transition-colors text-lg py-2"
                  >
                    FAQ
                  </button>
                  
                  <div className="pt-4 border-t border-white/10">
                    <button className="w-full px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold transition-all hover:brightness-110 active:scale-95">
                      Sign In
                    </button>
                  </div>
                </nav>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-bold text-white mb-6">
            About <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">All Lotto</span>
          </h1>

          {/* Mission Statement */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
              <div className="p-8">
                <h2 className="text-3xl font-bold text-white mb-4">Our Mission</h2>
                <p className="text-white/80 text-lg leading-relaxed mb-4">
                  All Lotto revolutionizes the lottery betting experience by bringing you a futuristic, 
                  space-themed platform where dreams become reality. We believe everyone deserves a chance 
                  to win big, regardless of where they are in the world.
                </p>
                <p className="text-white/80 text-lg leading-relaxed">
                  Our mission is to provide a safe, legal, and exciting way for players worldwide to participate 
                  in lottery betting, offering access to the biggest jackpots from around the globe through our 
                  innovative 3D interface.
                </p>
              </div>
              <div className="hidden md:block relative h-full min-h-[300px]">
                <img 
                  src="https://images.unsplash.com/photo-1633421878925-ac220d8f6e4f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnbG9iZSUyMHdvcmxkJTIwbmV0d29ya3xlbnwxfHx8fDE3NjcyMjY3MDh8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                  alt="Global network"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900/50 to-transparent" />
              </div>
            </div>
          </motion.div>

          {/* What We Offer */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h2 className="text-3xl font-bold text-white mb-6">What We Offer</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-bold text-white mb-3 flex items-center">
                  <span className="text-2xl mr-3">🌍</span>
                  Global Access
                </h3>
                <p className="text-white/70">
                  Bet on lottery outcomes from Powerball to EuroMillions, Mega Millions to Australian Lotto. 
                  Access the world's biggest jackpots from anywhere.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-3 flex items-center">
                  <span className="text-2xl mr-3">🎡</span>
                  Immersive 3D Experience
                </h3>
                <p className="text-white/70">
                  Our cutting-edge 3D carousel interface provides an unparalleled gaming experience with 
                  stunning visuals and smooth animations.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-3 flex items-center">
                  <span className="text-2xl mr-3">⚖️</span>
                  100% Legal & Regulated
                </h3>
                <p className="text-white/70">
                  We operate under strict regulatory compliance, ensuring all betting activities are legal, 
                  fair, and transparent.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-3 flex items-center">
                  <span className="text-2xl mr-3">🔒</span>
                  Secure Platform
                </h3>
                <p className="text-white/70">
                  Your security is our priority. We use industry-standard encryption and security measures 
                  to protect your data and transactions.
                </p>
              </div>
            </div>
          </motion.div>

          {/* How It's Different */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2 className="text-3xl font-bold text-white mb-4">How We're Different</h2>
            <p className="text-white/80 text-lg leading-relaxed mb-4">
              Unlike traditional lottery ticket purchases, All Lotto allows you to bet on the outcomes of 
              official lottery draws. This means:
            </p>
            <ul className="space-y-3 text-white/80 text-lg">
              <li className="flex items-start">
                <span className="text-green-400 mr-3 mt-1">✓</span>
                <span>No geographic restrictions - play from anywhere in the world</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-400 mr-3 mt-1">✓</span>
                <span>Instant digital access with no physical tickets needed</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-400 mr-3 mt-1">✓</span>
                <span>Bet on multiple international lotteries from one platform</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-400 mr-3 mt-1">✓</span>
                <span>Win based on matching the official lottery draw numbers</span>
              </li>
            </ul>
          </motion.div>

          {/* Company Values */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h2 className="text-3xl font-bold text-white mb-6">Our Values</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🎯</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Transparency</h3>
                <p className="text-white/70">
                  We believe in complete transparency with our players about how betting works and how odds are calculated.
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🤝</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Integrity</h3>
                <p className="text-white/70">
                  Operating with the highest standards of integrity and fairness in every aspect of our platform.
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">💡</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Innovation</h3>
                <p className="text-white/70">
                  Constantly pushing boundaries with cutting-edge technology to deliver the best gaming experience.
                </p>
              </div>
            </div>
          </motion.div>
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