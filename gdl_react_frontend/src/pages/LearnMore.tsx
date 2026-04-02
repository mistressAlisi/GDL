import React from "react";
import { motion } from "motion/react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface LearnMoreProps {
  onNavigate: (page: string) => void;
  onLaunchMachine: () => void;
}

export default function LearnMore({ onNavigate, onLaunchMachine }: LearnMoreProps) {
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
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Experience the Future of <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">Lottery Gaming</span>
          </h1>

          {/* Hero Introduction */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="h-64 overflow-hidden relative">
              <img 
                src="https://images.unsplash.com/photo-1681673819379-a183d9acf860?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzcGFjZSUyMG5lYnVsYSUyMGNvc21pY3xlbnwxfHx8fDE3NjcyMjY3MDN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                alt="Space nebula"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/70 to-transparent" />
            </div>
            <div className="p-8">
              <p className="text-white/80 text-lg leading-relaxed mb-4">
                All Lotto combines cutting-edge technology with the excitement of lottery gaming to deliver 
                an unprecedented experience. Our futuristic, space-themed platform transforms traditional lottery 
                betting into an immersive journey through the cosmos.
              </p>
              <p className="text-white/80 text-lg leading-relaxed">
                Whether you're on desktop or mobile, our 3D rotating carousel interface brings lottery games 
                to life with stunning visuals, smooth animations, and intuitive controls.
              </p>
            </div>
          </motion.div>

          {/* Key Features */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h2 className="text-3xl font-bold text-white mb-6">Revolutionary Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="h-40 overflow-hidden relative">
                  <img 
                    src="https://images.unsplash.com/photo-1756908992154-c8a89f5e517f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neSUyMGhvbG9ncmFwaGljfGVufDF8fHx8MTc2NzIyNjcwM3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                    alt="3D Interface"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
                </div>
                <div className="p-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-2xl">🖥️</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">3D Carousel Interface</h3>
                  <p className="text-white/70">
                    Navigate through games with our revolutionary 3D rotating prism carousel. Each game card 
                    comes to life with dynamic animations and real-time jackpot updates.
                  </p>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="h-40 overflow-hidden relative">
                  <img 
                    src="https://images.unsplash.com/photo-1652715564391-38cc4475b7f5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzeW5jJTIwZGV2aWNlcyUyMGNvbm5lY3RlZHxlbnwxfHx8fDE3NjcyMjY3MDh8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                    alt="Synced devices"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
                </div>
                <div className="p-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-2xl">📱</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">Cross-Platform Perfection</h3>
                  <p className="text-white/70">
                    Seamlessly switch between desktop and mobile. Your account, tickets, and progress sync 
                    instantly across all devices for uninterrupted gameplay.
                  </p>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="h-40 overflow-hidden relative">
                  <img 
                    src="https://images.unsplash.com/photo-1659018604802-85127de7e0bb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmYXN0JTIwc3BlZWQlMjBtb3Rpb258ZW58MXx8fHwxNjcyMjI2NzA1fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                    alt="Fast performance"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
                </div>
                <div className="p-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-2xl">⚡</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">Lightning-Fast Performance</h3>
                  <p className="text-white/70">
                    Enjoy buttery-smooth 60 FPS animations with optimized performance. No lag, no stuttering - 
                    just pure, responsive gaming excellence.
                  </p>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="h-40 overflow-hidden relative">
                  <img 
                    src="https://images.unsplash.com/photo-1759661966728-4a02e3c6ed91?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkYXRhJTIwdmlzdWFsaXphdGlvbiUyMGRhc2hib2FyZHxlbnwxfHx8fDE3NjcyMjY3MDR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                    alt="Smart selection"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 to-transparent" />
                </div>
                <div className="p-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-2xl">🎯</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">Smart Number Selection</h3>
                  <p className="text-white/70">
                    Choose your numbers manually with visual feedback and intuitive 
                    controls that make selecting your lucky numbers a breeze.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* How It Works */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
              <div className="p-8">
                <h2 className="text-3xl font-bold text-white mb-6">How All Lotto Works</h2>
                <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-white">1</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Sign In or Play as Guest</h3>
                  <p className="text-white/70">
                    Create an account to access all features and manage your balance, or try our demo mode 
                    as a guest to explore the interface risk-free.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-white">2</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Browse 12 Exciting Games</h3>
                  <p className="text-white/70">
                    Explore our collection of lottery games using the 3D carousel or switch to grid view. 
                    Each game displays live jackpot amounts, draw times, and odds.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-white">3</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Select Your Numbers</h3>
                  <p className="text-white/70">
                    Choose your lucky numbers with our intuitive number picker and adjust your bet amount 
                    to match your preferred betting strategy.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-white">4</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Place Your Bet & Win</h3>
                  <p className="text-white/70">
                    Confirm your bet and wait for the draw. Match the numbers to win based on the official 
                    lottery results. Winnings are credited instantly!
                  </p>
                </div>
              </div>
                </div>
              </div>
              
              <div className="hidden md:block relative h-full min-h-[400px]">
                <img 
                  src="https://images.unsplash.com/photo-1605108222700-0d605d9ebafe?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2JpbGUlMjBwaG9uZSUyMGFwcHxlbnwxfHx8fDE3NjcxOTk1NjR8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                  alt="Mobile app"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900/50 to-transparent" />
              </div>
            </div>
          </motion.div>

          {/* Platform Highlights */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="h-48 overflow-hidden relative">
              <img 
                src="https://images.unsplash.com/photo-1763370356302-4439026d83cb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZWN1cmUlMjBsb2NrJTIwdGVjaG5vbG9neXxlbnwxfHx8fDE3NjcyMjY3MDd8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral" 
                alt="Platform security"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/80 to-transparent" />
            </div>
            <div className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6">Platform Highlights</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-3xl">🌟</span>
                  <h3 className="text-xl font-bold text-white">Premium Design</h3>
                </div>
                <p className="text-white/70">
                  Glass-morphism aesthetics with cosmic gradients create a stunning visual experience 
                  that's both modern and immersive.
                </p>
              </div>

              <div>
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-3xl">🔐</span>
                  <h3 className="text-xl font-bold text-white">Secure & Safe</h3>
                </div>
                <p className="text-white/70">
                  Your data and transactions are protected with industry-standard encryption and security 
                  protocols.
                </p>
              </div>

              <div>
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-3xl">📊</span>
                  <h3 className="text-xl font-bold text-white">Real-Time Stats</h3>
                </div>
                <p className="text-white/70">
                  Track your balance, betting history, and favorite games from your personalized player 
                  profile panel.
                </p>
              </div>
            </div>
            </div>
          </motion.div>

          {/* CTA Section */}
          <motion.div
            className="bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-8 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Experience the Future?</h2>
            <p className="text-white/80 text-lg mb-6 max-w-2xl mx-auto">
              Join thousands of players who have discovered the next generation of lottery gaming. 
              Launch the All Lotto machine and start your cosmic journey today.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <motion.button
                className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold text-lg shadow-lg shadow-cyan-500/50 transition-all hover:shadow-cyan-500/70"
                onClick={onLaunchMachine}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Launch Lottery Machine 🚀
              </motion.button>
              <motion.button
                className="w-full sm:w-auto px-8 py-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-white font-bold text-lg transition-all hover:bg-white/20"
                onClick={() => onNavigate('about')}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Learn About Us
              </motion.button>
            </div>
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