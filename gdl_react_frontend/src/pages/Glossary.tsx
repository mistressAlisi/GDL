import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Menu, X } from "lucide-react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface GlossaryProps {
  onNavigate: (page: string) => void;
}

export default function Glossary({ onNavigate }: GlossaryProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleNavigation = (page: string) => {
    setMobileMenuOpen(false);
    onNavigate(page);
  };

  const glossaryTerms = [
    {
      term: "Bet Multiplier",
      definition: "A feature that allows you to increase your bet amount, which proportionally increases your potential winnings. For example, a 2x multiplier doubles both your bet and potential payout.",
      category: "Betting"
    },
    {
      term: "Draw Time",
      definition: "The scheduled date and time when the official lottery numbers are drawn and winning combinations are determined.",
      category: "Lottery"
    },
    {
      term: "EuroMillions",
      definition: "A transnational lottery game available across Europe, featuring two draws per week with jackpots starting at €17 million. Players select 5 main numbers and 2 Lucky Stars.",
      category: "Games"
    },
    {
      term: "Grid View",
      definition: "An alternative display mode showing all lottery games in a traditional grid layout, allowing for quick browsing and comparison of jackpots.",
      category: "Interface"
    },
    {
      term: "Guest Mode",
      definition: "A demo account option that allows users to explore the platform interface without registering. Guest users can view games but cannot place real bets or access money features.",
      category: "Account"
    },
    {
      term: "Jackpot",
      definition: "The largest prize available in a lottery game, awarded to players who match all required numbers. Jackpots often increase (rollover) if not won.",
      category: "Lottery"
    },
    {
      term: "Lottery Betting",
      definition: "A form of gambling where you bet on the outcome of official lottery draws rather than purchasing actual lottery tickets. If your numbers match the official draw, you win based on the betting odds.",
      category: "Betting"
    },
    {
      term: "Lucky Numbers",
      definition: "Numbers that a player believes will bring good fortune. Players can save their favorite lucky numbers for quick selection in future games.",
      category: "Lottery"
    },
    {
      term: "Mega Millions",
      definition: "One of America's two biggest lottery games with drawings twice per week. Players select 5 numbers from 1-70 and one Mega Ball from 1-25.",
      category: "Games"
    },
    {
      term: "Odds",
      definition: "The mathematical probability of winning a specific prize tier in a lottery game. Higher jackpots typically have longer odds (lower probability).",
      category: "Lottery"
    },
    {
      term: "Powerball",
      definition: "America's most popular lottery game with record-breaking jackpots. Players choose 5 numbers from 1-69 and one Powerball from 1-26.",
      category: "Games"
    },
    {
      term: "Prize Tier",
      definition: "Different levels of prizes available in a lottery game based on how many numbers you match. Most lotteries have multiple prize tiers.",
      category: "Lottery"
    },
    {
      term: "Rollover",
      definition: "When a jackpot is not won in a draw, the prize money rolls over to the next draw, creating increasingly larger jackpots.",
      category: "Lottery"
    },
    {
      term: "Sync Across Devices",
      definition: "The ability to access your account, tickets, and game history seamlessly across desktop, mobile, and tablet devices with real-time synchronization.",
      category: "Features"
    },
    {
      term: "Ticket",
      definition: "A digital record of your lottery bet, including your selected numbers, bet amount, and draw date. Tickets are stored in your account history.",
      category: "Betting"
    },
    {
      term: "Winning Combination",
      definition: "The set of numbers drawn in an official lottery that determines prize winners. Players win by matching numbers to this combination.",
      category: "Lottery"
    },
    {
      term: "Annuity Option",
      definition: "A payout method for large lottery jackpots where the prize is paid out over multiple years (typically 20-30 years) in scheduled installments, often resulting in a higher total payout than the lump sum option.",
      category: "Lottery"
    },
    {
      term: "Lump Sum",
      definition: "A one-time cash payout option for lottery jackpots, where winners receive the entire present cash value immediately, though at a reduced amount compared to the annuity value.",
      category: "Lottery"
    },
    {
      term: "Box Bet",
      definition: "A flexible betting option where you win if your selected numbers are drawn in any order, not just the exact order you chose. This increases your winning chances but typically offers lower payouts.",
      category: "Betting"
    },
    {
      term: "Straight Bet",
      definition: "A bet where you must match the winning numbers in the exact order drawn. This betting type offers higher payouts but lower odds of winning compared to box bets.",
      category: "Betting"
    },
    {
      term: "System Bet",
      definition: "An advanced betting method that allows you to select more numbers than required, automatically generating all possible combinations. This increases your chances but requires a higher stake.",
      category: "Betting"
    },
    {
      term: "Combination Bet",
      definition: "A bet that covers multiple number combinations in a single transaction, allowing you to play several different sets of numbers across multiple draws or games.",
      category: "Betting"
    },
    {
      term: "Hot Numbers",
      definition: "Numbers that have been drawn frequently in recent lottery draws. Some players believe these numbers are 'lucky' and more likely to appear again, though each draw is statistically independent.",
      category: "Lottery"
    },
    {
      term: "Cold Numbers",
      definition: "Numbers that have not been drawn for an extended period. Some players select these believing they are 'due' to be drawn, though lottery draws are random events.",
      category: "Lottery"
    },
    {
      term: "Syndicate",
      definition: "A group of players who pool their money to purchase multiple lottery tickets together, sharing any winnings proportionally. This increases the chances of winning while reducing individual costs.",
      category: "Betting"
    },
    {
      term: "Subscription",
      definition: "An automated service that purchases lottery tickets for you on a recurring basis for specified games and draws, ensuring you never miss a draw of your favorite lottery.",
      category: "Features"
    },
    {
      term: "Wheeling System",
      definition: "A strategic method of playing multiple number combinations to guarantee a win if certain numbers are drawn. This system covers various permutations of your chosen numbers.",
      category: "Betting"
    },
    {
      term: "Bonus Ball",
      definition: "An additional number drawn in certain lotteries (like Powerball or Mega Millions) that offers extra prize tiers and increases overall winning opportunities when matched.",
      category: "Lottery"
    },
    {
      term: "Multi-Draw",
      definition: "A feature allowing you to use the same numbers for multiple consecutive lottery draws, typically at a discounted rate compared to purchasing individual tickets for each draw.",
      category: "Features"
    },
    {
      term: "Second Chance Drawing",
      definition: "A supplementary lottery promotion where non-winning tickets can be entered for additional prize draws, giving players another opportunity to win with their original ticket.",
      category: "Lottery"
    },
    {
      term: "Pari-Mutuel",
      definition: "A prize distribution system where all bets are pooled together, and winners share the total prize pool proportionally based on the number of winning tickets. Common in European lotteries.",
      category: "Lottery"
    },
    {
      term: "Fixed Odds",
      definition: "A betting system where the payout odds are predetermined and do not change regardless of how many people bet or win. Your potential winnings are known when you place your bet.",
      category: "Betting"
    },
    {
      term: "RTP (Return to Player)",
      definition: "The percentage of all wagered money that a lottery or game is expected to pay back to players over time. For example, a 60% RTP means that for every $100 wagered, $60 is returned as prizes.",
      category: "Betting"
    },
    {
      term: "Minimum Bet",
      definition: "The lowest amount you can wager on a single lottery bet or ticket. This varies by game and ensures all players meet a baseline stake requirement.",
      category: "Betting"
    },
    {
      term: "Maximum Bet",
      definition: "The highest amount allowed for a single bet or ticket purchase, set by the lottery operator to manage risk and ensure responsible gaming practices.",
      category: "Betting"
    }
  ];

  const categories = ["All", "Interface", "Betting", "Lottery", "Games", "Account", "Features"];
  const [selectedCategory, setSelectedCategory] = useState("All");

  const filteredTerms = glossaryTerms.filter(item => {
    const matchesSearch = item.term.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         item.definition.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "All" || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

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
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Lottery <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">Glossary</span>
            </h1>
            <p className="text-white/70 text-lg max-w-2xl mx-auto">
              Your comprehensive guide to lottery betting terms, features, and concepts used in All Lotto.
            </p>
          </div>

          {/* Search and Filter Section */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {/* Search Bar */}
            <div className="mb-6">
              <input
                type="text"
                placeholder="Search terms..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-6 py-3 bg-white/10 border border-white/20 rounded-full text-white placeholder-white/50 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    selectedCategory === category
                      ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
                      : "bg-white/10 text-white/70 hover:bg-white/20"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Glossary Terms */}
          <motion.div
            className="space-y-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            {filteredTerms.length === 0 ? (
              <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-12 text-center">
                <p className="text-white/60 text-lg">No terms found matching your search.</p>
              </div>
            ) : (
              filteredTerms.map((item, index) => (
                <motion.div
                  key={item.term}
                  className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-3">
                    <h3 className="text-2xl font-bold text-white">{item.term}</h3>
                    <span className="inline-block px-3 py-1 bg-cyan-500/20 border border-cyan-500/30 rounded-full text-cyan-300 text-sm font-medium w-fit">
                      {item.category}
                    </span>
                  </div>
                  <p className="text-white/70 text-lg leading-relaxed">{item.definition}</p>
                </motion.div>
              ))
            )}
          </motion.div>

          {/* Help CTA */}
          <motion.div
            className="mt-12 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-8 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h2 className="text-2xl font-bold text-white mb-3">Still Have Questions?</h2>
            <p className="text-white/70 mb-6">
              Our support team is here to help you understand everything about All Lotto.
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
            <button onClick={() => onNavigate('glossary')} className="text-white hover:text-white transition-colors">
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