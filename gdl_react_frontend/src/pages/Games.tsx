import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Menu, X } from "lucide-react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface GamesProps {
  onNavigate: (page: string) => void;
  onLaunchMachine: () => void;
}

const lotteryGames = [
  {
    name: "Powerball",
    country: "USA",
    icon: "🇺🇸",
    jackpot: "$250M",
    drawTime: "Wed & Sat",
    color: "from-red-500 to-blue-600",
    description: "America's favorite lottery with massive jackpots",
  },
  {
    name: "Mega Millions",
    country: "USA",
    icon: "🇺🇸",
    jackpot: "$180M",
    drawTime: "Tue & Fri",
    color: "from-yellow-400 to-orange-500",
    description: "One of the world's largest lottery games",
  },
  {
    name: "EuroMillions",
    country: "Europe",
    icon: "🇪🇺",
    jackpot: "€95M",
    drawTime: "Tue & Fri",
    color: "from-blue-400 to-purple-600",
    description: "Europe's premier multi-national lottery",
  },
  {
    name: "SuperEnalotto",
    country: "Italy",
    icon: "🇮🇹",
    jackpot: "€45M",
    drawTime: "Tue, Thu & Sat",
    color: "from-green-400 to-emerald-600",
    description: "Italy's legendary lottery with no jackpot cap",
  },
  {
    name: "UK Lotto",
    country: "United Kingdom",
    icon: "🇬🇧",
    jackpot: "£15M",
    drawTime: "Wed & Sat",
    color: "from-pink-400 to-rose-600",
    description: "The UK's national lottery game",
  },
  {
    name: "El Gordo",
    country: "Spain",
    icon: "🇪🇸",
    jackpot: "€120M",
    drawTime: "Sunday",
    color: "from-red-500 to-yellow-500",
    description: "Spain's massive lottery with huge prize pools",
  },
  {
    name: "Oz Lotto",
    country: "Australia",
    icon: "🇦🇺",
    jackpot: "AU$30M",
    drawTime: "Tuesday",
    color: "from-cyan-400 to-blue-600",
    description: "Australia's favorite Tuesday night draw",
  },
  {
    name: "Powerball AU",
    country: "Australia",
    icon: "🇦🇺",
    jackpot: "AU$40M",
    drawTime: "Thursday",
    color: "from-orange-400 to-red-600",
    description: "Australia's biggest jackpot lottery",
  },
  {
    name: "Lotto 6/49",
    country: "Canada",
    icon: "🇨🇦",
    jackpot: "CA$25M",
    drawTime: "Wed & Sat",
    color: "from-red-500 to-red-700",
    description: "Canada's classic lottery game",
  },
  {
    name: "La Primitiva",
    country: "Spain",
    icon: "🇪🇸",
    jackpot: "€35M",
    drawTime: "Mon, Thu & Sat",
    color: "from-purple-400 to-pink-600",
    description: "Spain's traditional lottery",
  },
  {
    name: "French Lotto",
    country: "France",
    icon: "🇫🇷",
    jackpot: "€15M",
    drawTime: "Mon, Wed & Sat",
    color: "from-blue-500 to-purple-600",
    description: "France's national lottery",
  },
  {
    name: "Irish Lotto",
    country: "Ireland",
    icon: "🇮🇪",
    jackpot: "€10M",
    drawTime: "Wed & Sat",
    color: "from-green-500 to-emerald-700",
    description: "Ireland's beloved lottery game",
  },
];

export default function Games({ onNavigate, onLaunchMachine }: GamesProps) {
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
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-white mb-6">
              Available <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">Lottery Games</span>
            </h1>
            <p className="text-xl text-white/70 max-w-3xl mx-auto mb-8">
              Bet on the outcomes of the world's biggest lotteries. From American Powerball to European EuroMillions,
              your next big win is just a click away.
            </p>
            <motion.button
              className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold text-lg shadow-lg shadow-cyan-500/50 transition-all hover:shadow-cyan-500/70"
              onClick={onLaunchMachine}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Launch Lottery Machine 🚀
            </motion.button>
          </div>

          {/* Games Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lotteryGames.map((game, index) => (
              <motion.div
                key={game.name}
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all cursor-pointer"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 bg-gradient-to-br ${game.color} rounded-lg flex items-center justify-center`}>
                      <span className="text-2xl">{game.icon}</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{game.name}</h3>
                      <p className="text-white/60 text-sm">{game.country}</p>
                    </div>
                  </div>
                </div>

                <p className="text-white/70 text-sm mb-4">{game.description}</p>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-white/60 text-sm">Current Jackpot</span>
                    <span className="text-white font-bold">{game.jackpot}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white/60 text-sm">Draw Time</span>
                    <span className="text-white/80 text-sm">{game.drawTime}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Additional Info */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mt-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h2 className="text-3xl font-bold text-white mb-4 text-center">Why Bet With All Lotto?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🌍</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Global Access</h3>
                <p className="text-white/70">
                  Play any lottery from anywhere in the world without geographic restrictions.
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">⚡</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Instant Results</h3>
                <p className="text-white/70">
                  Get results immediately after official draws with automatic win notifications.
                </p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🔒</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Secure Platform</h3>
                <p className="text-white/70">
                  100% legal, regulated, and secure betting with industry-standard protection.
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