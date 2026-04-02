import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Sparkles, RefreshCw, Copy, History, Plus } from "lucide-react";

interface NumberSet {
  numbers: number[];
  lottery: string;
  timestamp: Date;
}

export function LuckyNumberGenerator() {
  const [numbers, setNumbers] = useState<number[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedLottery, setSelectedLottery] = useState<"powerball" | "mega" | "euro">("powerball");
  const [history, setHistory] = useState<NumberSet[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [numberOfSets, setNumberOfSets] = useState(1);
  const [multipleSets, setMultipleSets] = useState<number[][]>([]);
  const [copySuccess, setCopySuccess] = useState(false);

  const lotteryConfigs = {
    powerball: { main: 5, range: 69, bonus: 1, bonusRange: 26, name: "Powerball", color: "from-red-500 to-pink-600" },
    mega: { main: 5, range: 70, bonus: 1, bonusRange: 25, name: "Mega Millions", color: "from-yellow-400 to-orange-500" },
    euro: { main: 5, range: 50, bonus: 2, bonusRange: 12, name: "EuroMillions", color: "from-blue-500 to-purple-600" }
  };

  const config = lotteryConfigs[selectedLottery];

  const generateSingleSet = () => {
    const mainNums: number[] = [];
    while (mainNums.length < config.main) {
      const num = Math.floor(Math.random() * config.range) + 1;
      if (!mainNums.includes(num)) mainNums.push(num);
    }
    mainNums.sort((a, b) => a - b);

    const bonusNums: number[] = [];
    while (bonusNums.length < config.bonus) {
      const num = Math.floor(Math.random() * config.bonusRange) + 1;
      if (!bonusNums.includes(num)) bonusNums.push(num);
    }

    return [...mainNums, ...bonusNums];
  };

  const generateNumbers = () => {
    setIsGenerating(true);
    
    // Simulate spinning animation
    setTimeout(() => {
      if (numberOfSets === 1) {
        const nums = generateSingleSet();
        setNumbers(nums);
        setMultipleSets([]);
        
        // Add to history
        setHistory(prev => [{
          numbers: nums,
          lottery: config.name,
          timestamp: new Date()
        }, ...prev].slice(0, 10)); // Keep last 10
      } else {
        const sets: number[][] = [];
        for (let i = 0; i < numberOfSets; i++) {
          sets.push(generateSingleSet());
        }
        setMultipleSets(sets);
        setNumbers([]);
        
        // Add all sets to history
        const newHistory = sets.map(nums => ({
          numbers: nums,
          lottery: config.name,
          timestamp: new Date()
        }));
        setHistory(prev => [...newHistory, ...prev].slice(0, 20));
      }
      
      setIsGenerating(false);
    }, 1500);
  };

  const copyToClipboard = (nums: number[]) => {
    const text = `${config.name}: ${nums.slice(0, config.main).join(", ")} | Bonus: ${nums.slice(config.main).join(", ")}`;
    navigator.clipboard.writeText(text);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const loadNumberSet = (nums: number[]) => {
    setNumbers(nums);
    setMultipleSets([]);
    setShowHistory(false);
  };

  return (
    <motion.div
      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-3xl font-bold text-white flex items-center gap-3">
          <Sparkles className="text-yellow-400" size={32} />
          Lucky Number Generator
        </h3>
      </div>

      <p className="text-white/70 mb-6">
        Generate lucky numbers for any lottery! Create single or multiple sets and view your history.
      </p>

      {/* Lottery Selection */}
      <div className="flex flex-wrap gap-3 mb-6">
        {Object.entries(lotteryConfigs).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setSelectedLottery(key as any)}
            className={`px-6 py-3 rounded-full font-bold transition-all ${
              selectedLottery === key
                ? "bg-gradient-to-r from-yellow-400 to-orange-500 text-slate-900"
                : "bg-white/10 text-white hover:bg-white/20"
            }`}
          >
            {config.name}
          </button>
        ))}
      </div>

      {/* Number of Sets Selector */}
      <div className="mb-6 bg-slate-900/50 rounded-xl p-4">
        <label className="text-white/80 text-sm mb-2 block">Number of Sets to Generate:</label>
        <div className="flex gap-2 flex-wrap">
          {[1, 2, 3, 5, 10].map(num => (
            <button
              key={num}
              onClick={() => setNumberOfSets(num)}
              className={`px-4 py-2 rounded-lg font-bold transition-all ${
                numberOfSets === num
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
                  : "bg-white/10 text-white/70 hover:bg-white/20"
              }`}
            >
              {num} {num === 1 ? "Set" : "Sets"}
            </button>
          ))}
        </div>
      </div>

      {/* History Panel */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            className="mb-6 bg-slate-900/50 rounded-xl p-4 border border-cyan-500/30"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h4 className="text-white font-bold mb-3 flex items-center gap-2">
              <History className="text-cyan-400" size={20} />
              Recent History
            </h4>
            {history.length === 0 ? (
              <p className="text-white/50 text-sm">No history yet. Generate some numbers!</p>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {history.map((item, idx) => (
                  <div key={idx} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-white/60 text-xs mb-1">
                        {item.lottery} - {item.timestamp.toLocaleTimeString()}
                      </p>
                      <div className="flex gap-2 flex-wrap">
                        {item.numbers.map((num, i) => (
                          <span key={i} className="text-white font-bold">{num}</span>
                        ))}
                      </div>
                    </div>
                    <button
                      onClick={() => loadNumberSet(item.numbers)}
                      className="p-1 text-cyan-400 hover:text-cyan-300 transition-colors"
                      title="Load"
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Number Display - Single Set */}
      {numberOfSets === 1 && (
        <div className="bg-slate-900/50 rounded-xl p-6 mb-4 min-h-[120px] flex items-center justify-center">
          <AnimatePresence mode="wait">
            {numbers.length === 0 ? (
              <motion.p
                key="empty"
                className="text-white/50 text-lg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                Click "Generate" to get your lucky numbers!
              </motion.p>
            ) : (
              <motion.div
                key="numbers"
                className="flex flex-wrap gap-3 justify-center"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
              >
                {numbers.slice(0, config.main).map((num, idx) => (
                  <motion.div
                    key={idx}
                    className="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center font-bold text-xl text-white shadow-lg"
                    initial={{ opacity: 0, y: -20, rotate: -180 }}
                    animate={{ opacity: 1, y: 0, rotate: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    whileHover={{ scale: 1.1, rotate: 360 }}
                  >
                    {num}
                  </motion.div>
                ))}
                {numbers.slice(config.main).map((num, idx) => (
                  <motion.div
                    key={idx + config.main}
                    className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center font-bold text-xl text-slate-900 shadow-lg"
                    initial={{ opacity: 0, y: -20, rotate: -180 }}
                    animate={{ opacity: 1, y: 0, rotate: 0 }}
                    transition={{ delay: (config.main + idx) * 0.1 }}
                    whileHover={{ scale: 1.1, rotate: 360 }}
                  >
                    {num}
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Multiple Sets Display */}
      {numberOfSets > 1 && multipleSets.length > 0 && (
        <div className="bg-slate-900/50 rounded-xl p-6 mb-4 max-h-[400px] overflow-y-auto">
          <div className="space-y-3">
            {multipleSets.map((set, setIdx) => (
              <motion.div
                key={setIdx}
                className="bg-white/5 rounded-lg p-4 border border-white/10"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: setIdx * 0.1 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white/60 text-sm font-bold">Set {setIdx + 1}</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => copyToClipboard(set)}
                      className="p-1 text-cyan-400 hover:text-cyan-300 transition-colors"
                      title="Copy"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {set.slice(0, config.main).map((num, idx) => (
                    <div
                      key={idx}
                      className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center font-bold text-white shadow-md"
                    >
                      {num}
                    </div>
                  ))}
                  <div className="w-1 border-l-2 border-white/30 mx-1" />
                  {set.slice(config.main).map((num, idx) => (
                    <div
                      key={idx + config.main}
                      className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center font-bold text-slate-900 shadow-md"
                    >
                      {num}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons for Single Set */}
      {numbers.length > 0 && numberOfSets === 1 && !isGenerating && (
        <motion.div
          className="flex gap-3 mb-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <button
            onClick={() => copyToClipboard(numbers)}
            className="flex-1 px-4 py-3 bg-cyan-500/20 border border-cyan-500/50 rounded-lg text-cyan-400 font-bold transition-all hover:bg-cyan-500/30 active:scale-95 flex items-center justify-center gap-2"
          >
            <Copy size={20} />
            {copySuccess ? "Copied!" : "Copy"}
          </button>
        </motion.div>
      )}

      {/* Generate Button */}
      <button
        onClick={generateNumbers}
        disabled={isGenerating}
        className="w-full px-8 py-4 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full text-slate-900 font-bold text-lg shadow-lg shadow-yellow-500/50 transition-all hover:shadow-yellow-500/70 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
      >
        <RefreshCw className={isGenerating ? "animate-spin" : ""} size={24} />
        {isGenerating ? "Generating..." : `Generate ${numberOfSets} ${numberOfSets === 1 ? "Set" : "Sets"}`}
      </button>

      {((numbers.length > 0 && numberOfSets === 1) || multipleSets.length > 0) && !isGenerating && (
        <motion.p
          className="text-center text-white/60 text-sm mt-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          Good luck! Remember, gambling should be fun and responsible. 🍀
        </motion.p>
      )}

      {/* Stats Footer */}
      {history.length > 0 && (
        <motion.div
          className="mt-4 pt-4 border-t border-white/10 text-center text-white/50 text-xs"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {history.length} sets generated
        </motion.div>
      )}
    </motion.div>
  );
}