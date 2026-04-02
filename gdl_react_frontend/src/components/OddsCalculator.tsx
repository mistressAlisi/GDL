import React, { useState } from "react";
import { motion } from "motion/react";
import { Calculator, TrendingUp } from "lucide-react";

export function OddsCalculator() {
  const [selectedLottery, setSelectedLottery] = useState<"powerball" | "mega" | "euro">("powerball");

  const lotteryOdds = {
    powerball: {
      name: "Powerball",
      jackpot: "1 in 292,201,338",
      match5: "1 in 11,688,053",
      match4plus: "1 in 913,129",
      match4: "1 in 36,525",
      match3plus: "1 in 14,494",
      overall: "1 in 24.9"
    },
    mega: {
      name: "Mega Millions",
      jackpot: "1 in 302,575,350",
      match5: "1 in 12,607,306",
      match4plus: "1 in 931,001",
      match4: "1 in 38,792",
      match3plus: "1 in 14,547",
      overall: "1 in 24"
    },
    euro: {
      name: "EuroMillions",
      jackpot: "1 in 139,838,160",
      match5plus1: "1 in 6,991,908",
      match5: "1 in 3,107,515",
      match4plus2: "1 in 621,503",
      match4plus1: "1 in 31,075",
      overall: "1 in 13"
    }
  };

  const odds = lotteryOdds[selectedLottery];

  const comparisons = [
    { event: "Being struck by lightning (in a year)", odds: "1 in 500,000" },
    { event: "Finding a four-leaf clover", odds: "1 in 10,000" },
    { event: "Becoming a movie star", odds: "1 in 1,505,000" },
    { event: "Becoming an astronaut", odds: "1 in 12,100,000" },
    { event: "Dating a supermodel", odds: "1 in 88,000" }
  ];

  return (
    <motion.div
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <div className="flex items-center gap-3 mb-6">
        <Calculator className="text-cyan-400" size={32} />
        <h3 className="text-3xl font-bold text-white">
          Lottery Odds Calculator
        </h3>
      </div>

      <p className="text-white/70 mb-6">
        Understanding the odds helps you play responsibly. Here are the chances of winning at different levels.
      </p>

      {/* Lottery Selection */}
      <div className="flex flex-wrap gap-3 mb-8">
        {Object.entries(lotteryOdds).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setSelectedLottery(key as any)}
            className={`px-6 py-3 rounded-full font-bold transition-all ${
              selectedLottery === key
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
                : "bg-white/10 text-white hover:bg-white/20"
            }`}
          >
            {config.name}
          </button>
        ))}
      </div>

      {/* Odds Display */}
      <div className="space-y-3 mb-8">
        <motion.div
          className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-xl p-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex items-center justify-between">
            <span className="text-white font-bold flex items-center gap-2">
              <span className="text-2xl">🏆</span>
              Jackpot
            </span>
            <span className="text-yellow-400 font-bold text-lg">{odds.jackpot}</span>
          </div>
        </motion.div>

        {Object.entries(odds)
          .filter(([key]) => key !== 'name' && key !== 'jackpot' && key !== 'overall')
          .map(([key, value], idx) => (
            <motion.div
              key={key}
              className="bg-white/5 border border-white/10 rounded-xl p-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + idx * 0.1 }}
            >
              <div className="flex items-center justify-between">
                <span className="text-white/80 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                <span className="text-cyan-400 font-bold">{value}</span>
              </div>
            </motion.div>
          ))}

        <motion.div
          className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
        >
          <div className="flex items-center justify-between">
            <span className="text-white font-bold flex items-center gap-2">
              <TrendingUp className="text-green-400" size={20} />
              Overall Winning Odds
            </span>
            <span className="text-green-400 font-bold text-lg">{odds.overall}</span>
          </div>
        </motion.div>
      </div>

      {/* Fun Comparisons */}
      <div className="bg-slate-900/50 rounded-xl p-6">
        <h4 className="text-xl font-bold text-white mb-4">How Rare is the Jackpot?</h4>
        <p className="text-white/60 text-sm mb-4">
          Winning the jackpot is incredibly rare. Here's how it compares to other unlikely events:
        </p>
        <div className="space-y-2">
          {comparisons.map((comparison, idx) => (
            <motion.div
              key={idx}
              className="flex items-start gap-3 text-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 + idx * 0.1 }}
            >
              <span className="text-purple-400">•</span>
              <div className="flex-1">
                <span className="text-white/70">{comparison.event}: </span>
                <span className="text-purple-400 font-bold">{comparison.odds}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <motion.p
        className="text-center text-white/50 text-sm mt-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        Remember: Play for fun, not as an investment strategy!
      </motion.p>
    </motion.div>
  );
}
