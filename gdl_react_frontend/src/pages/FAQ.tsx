import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Search, Menu, X } from "lucide-react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface FAQProps {
  onNavigate: (page: string) => void;
}

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

const faqData: FAQItem[] = [
  {
    category: "Getting Started",
    question: "What is All Lotto and how does it work?",
    answer: "All Lotto is a lottery betting platform that allows you to bet on the outcomes of official lottery draws from around the world. Instead of buying actual lottery tickets, you place bets on the numbers drawn in official lotteries like Powerball, Mega Millions, and EuroMillions. If your numbers match the official draw results, you win prizes equivalent to the official lottery payouts."
  },
  {
    category: "Getting Started",
    question: "How do I create an account?",
    answer: "Click the 'Sign In' button in the navigation bar, then select 'Register' in the authentication modal. Fill in your username, email, and password to create your account. You can also play as a guest to explore the platform, though betting features will be disabled in guest mode."
  },
  {
    category: "Getting Started",
    question: "What's the difference between registered and guest accounts?",
    answer: "Registered accounts have full access to all betting features, can deposit funds, place bets, and withdraw winnings. Guest accounts are demo-only - you can explore the lottery machine interface and see how everything works, but all betting and money features are disabled. We recommend registering to access the full experience."
  },
  {
    category: "Betting & Playing",
    question: "How do I place a bet on a lottery?",
    answer: "Launch the Lottery Machine, select your desired lottery game from the carousel or grid view, choose your numbers, set your bet amount, and confirm your bet. Your bet will be active for the next official draw of that lottery."
  },
  {
    category: "Betting & Playing",
    question: "Can I bet on multiple lotteries at once?",
    answer: "Yes! You can place bets on as many different lottery games as you like. Each lottery has its own draw schedule, so you can have active bets on Powerball, EuroMillions, and other lotteries simultaneously."
  },
  {
    category: "Betting & Playing",
    question: "What are the minimum and maximum bet amounts?",
    answer: "The minimum bet varies by lottery but typically starts at $1-$5. Maximum bets depend on the specific lottery and your account level. Check each lottery's details in the game selection screen for specific limits."
  },
  {
    category: "Betting & Playing",
    question: "When do lottery draws take place?",
    answer: "Each lottery has its own draw schedule. For example, Powerball draws on Wednesday and Saturday, Mega Millions on Tuesday and Friday, and EuroMillions on Tuesday and Friday. The exact draw times are displayed on each lottery's information card."
  },
  {
    category: "Betting & Playing",
    question: "Can I cancel or edit a bet after placing it?",
    answer: "Once a bet is confirmed, it cannot be cancelled or edited. This policy ensures fairness and prevents manipulation. Always double-check your numbers and bet amount before confirming."
  },
  {
    category: "Betting & Playing",
    question: "What is a multi-draw bet?",
    answer: "Multi-draw allows you to use the same numbers for multiple consecutive draws of the same lottery. For example, you can bet on the next 5 Powerball draws with one transaction, often at a discounted rate compared to placing individual bets."
  },
  {
    category: "Betting & Playing",
    question: "How does the bet multiplier work?",
    answer: "The bet multiplier increases both your stake and potential winnings proportionally. For example, with a 3x multiplier, a $5 bet becomes $15, and if you win $100, you'd receive $300. This feature is available on most lottery games."
  },
  {
    category: "Betting & Playing",
    question: "Can I save my favorite numbers?",
    answer: "Yes! You can save multiple sets of 'Lucky Numbers' in your account. When placing a bet, simply select your saved numbers instead of manually entering them each time. This feature is available in your player profile settings."
  },
  {
    category: "Winnings & Payouts",
    question: "How do I know if I've won?",
    answer: "After each official lottery draw, we automatically check all active bets against the winning numbers. If you win, you'll receive an instant notification and your winnings will be credited to your account balance. You can also check your bet history in the player profile panel."
  },
  {
    category: "Winnings & Payouts",
    question: "How are winnings calculated?",
    answer: "Winnings are calculated based on the official lottery prize tiers you match. If you match all numbers for a jackpot, you win an equivalent jackpot prize. Smaller prizes are awarded for matching fewer numbers, following the official lottery's prize structure."
  },
  {
    category: "Winnings & Payouts",
    question: "How long does it take to receive my winnings?",
    answer: "Winnings are credited to your account balance immediately after the official draw results are verified. You can then withdraw your funds or use them to place more bets. Withdrawal processing times vary by payment method but typically take 1-5 business days."
  },
  {
    category: "Winnings & Payouts",
    question: "Is there a maximum payout limit?",
    answer: "While we match official lottery prize structures, there may be payout limits depending on your account tier and the specific lottery. Premium accounts have higher limits. Check your account settings or contact support for your specific limits."
  },
  {
    category: "Winnings & Payouts",
    question: "What happens if I win a jackpot?",
    answer: "Congratulations! Jackpot wins are verified and credited to your account. For very large jackpots, our team will contact you directly to arrange payout and provide guidance. Major wins may require additional verification for security purposes."
  },
  {
    category: "Winnings & Payouts",
    question: "Do I pay taxes on my lottery winnings?",
    answer: "Tax obligations vary by country and jurisdiction. We recommend consulting with a tax professional about your specific situation. Please note that we do not provide tax documents. In some regions, we may be required to withhold taxes on large winnings."
  },
  {
    category: "Winnings & Payouts",
    question: "Can I choose between lump sum and annuity for jackpots?",
    answer: "For lottery betting, winnings are typically paid as lump sum cash equivalents. Unlike official lottery tickets, annuity options are generally not available. Your full winnings are credited to your account balance for immediate use or withdrawal."
  },
  {
    category: "Winnings & Payouts",
    question: "What are the different prize tiers?",
    answer: "Most lotteries have multiple prize tiers based on how many numbers you match. For example, Powerball has 9 prize tiers from matching just the Powerball to matching all 5 numbers plus the Powerball (jackpot). Each tier has different odds and payouts."
  },
  {
    category: "Account & Payments",
    question: "What payment methods do you accept?",
    answer: "We accept major credit/debit cards, bank transfers, e-wallets, and select cryptocurrencies. Available payment methods may vary by region. Check the deposit section of your account for all available options."
  },
  {
    category: "Account & Payments",
    question: "How do I deposit funds?",
    answer: "Navigate to your player profile panel, click on your balance, select 'Deposit', choose your preferred payment method, enter the amount, and follow the prompts. Deposits are typically processed instantly for most payment methods."
  },
  {
    category: "Account & Payments",
    question: "How do I withdraw my winnings?",
    answer: "Go to your player profile, click on your balance, select 'Withdraw', choose your withdrawal method, enter the amount, and submit. Withdrawals are subject to verification and processing times vary by method (1-5 business days typically)."
  },
  {
    category: "Account & Payments",
    question: "Are there any fees for deposits or withdrawals?",
    answer: "We don't charge fees for deposits. Small withdrawal fees may apply depending on your chosen payment method and amount. Fee details are displayed before you confirm any withdrawal."
  },
  {
    category: "Account & Payments",
    question: "Can I have multiple accounts?",
    answer: "No, each person is allowed only one account to prevent abuse and ensure fair play. Creating multiple accounts is against our terms of service and may result in account suspension and forfeiture of funds."
  },
  {
    category: "Account & Payments",
    question: "How do I update my personal information?",
    answer: "Go to your player profile panel, click on the settings icon, and select 'Account Information'. You can update your email, phone number, and address. Changes to sensitive information may require verification."
  },
  {
    category: "Account & Payments",
    question: "What is the minimum withdrawal amount?",
    answer: "The minimum withdrawal amount is typically $20, though this may vary by payment method. Check the withdrawal page for specific minimums for your chosen payment method. Some premium payment methods may have lower minimums."
  },
  {
    category: "Account & Payments",
    question: "Can I set deposit limits on my account?",
    answer: "Yes! We strongly encourage responsible gaming. You can set daily, weekly, or monthly deposit limits in your account settings under 'Responsible Gaming'. Once set, limits cannot be increased for 24 hours to give you time to reconsider."
  },
  {
    category: "Security & Verification",
    question: "Is All Lotto legal and regulated?",
    answer: "Yes, All Lotto operates under proper licensing and regulation in authorized jurisdictions. We comply with all applicable gaming and betting regulations. Always check your local laws regarding online lottery betting before participating."
  },
  {
    category: "Security & Verification",
    question: "How secure is my personal and financial information?",
    answer: "We use industry-standard 256-bit SSL encryption to protect all data transmission. Your personal and financial information is stored securely and never shared with third parties without your consent. We are fully compliant with data protection regulations."
  },
  {
    category: "Security & Verification",
    question: "Do I need to verify my account?",
    answer: "For regulatory compliance and to protect against fraud, we require identity verification before processing withdrawals. You'll need to provide a government-issued ID and proof of address. This is a one-time process that typically takes 24-48 hours."
  },
  {
    category: "Security & Verification",
    question: "How does two-factor authentication work?",
    answer: "Two-factor authentication (2FA) adds an extra security layer to your account. When enabled, you'll need both your password and a code from your phone to log in. Enable 2FA in your account security settings for maximum protection."
  },
  {
    category: "Security & Verification",
    question: "What documents are needed for verification?",
    answer: "For account verification, you'll need a government-issued photo ID (passport, driver's license, or national ID) and proof of address (utility bill, bank statement, or official letter) dated within the last 3 months. Documents can be uploaded directly through your account."
  },
  {
    category: "Security & Verification",
    question: "How long does account verification take?",
    answer: "Most verifications are completed within 24-48 hours. During peak times, it may take up to 72 hours. You'll receive an email notification once your account is verified. You can still place bets while verification is pending, but withdrawals require completed verification."
  },
  {
    category: "Technical & Features",
    question: "Can I use All Lotto on mobile devices?",
    answer: "Yes! All Lotto is fully responsive and works on all devices including smartphones, tablets, and desktop computers. The interface adapts to your screen size for the best experience."
  },
  {
    category: "Technical & Features",
    question: "What browsers are supported?",
    answer: "All Lotto works best on modern browsers including Chrome, Firefox, Safari, and Edge. We recommend keeping your browser updated to the latest version for optimal performance and security."
  },
  {
    category: "Technical & Features",
    question: "What is the difference between carousel and grid view?",
    answer: "The 3D carousel view displays games in an immersive rotating prism format with animated cards, perfect for browsing featured lotteries. Grid view shows all games in a traditional layout for quick comparison of jackpots and draw times. Switch between them using the view toggle button."
  },
  {
    category: "Technical & Features",
    question: "Can I view past draw results?",
    answer: "Yes! Each lottery game page includes a 'Past Results' section showing recent winning numbers and draw dates. You can also view detailed result history and statistical analysis for most lotteries to help inform your number selections."
  },
  {
    category: "Technical & Features",
    question: "Do you have a mobile app?",
    answer: "Currently, All Lotto is a fully responsive web application that works perfectly on all mobile devices through your browser. A dedicated mobile app is in development and will be available soon. You can add our website to your home screen for app-like access."
  },
  {
    category: "Responsible Gaming",
    question: "Do you have responsible gaming tools?",
    answer: "Yes, we offer multiple responsible gaming features including deposit limits, time limits, self-exclusion options, and reality checks. Access these tools from your account settings or visit our Responsible Gaming page."
  },
  {
    category: "Responsible Gaming",
    question: "How do I set betting limits?",
    answer: "Go to your account settings, select 'Responsible Gaming', and set daily, weekly, or monthly limits for deposits and bets. Once set, these limits cannot be increased for 24 hours to ensure you have time to reconsider."
  },
  {
    category: "Responsible Gaming",
    question: "Can I take a break from betting?",
    answer: "Yes! We offer a 'cool-off period' feature where you can temporarily suspend your account for 24 hours, 7 days, 30 days, or longer. During this time, you cannot place bets or make deposits. Access this feature in your responsible gaming settings."
  },
  {
    category: "Responsible Gaming",
    question: "What if I think I have a gambling problem?",
    answer: "We take responsible gaming seriously. If you're concerned about your gambling behavior, please visit our Responsible Gaming page for resources, self-assessment tools, and links to professional support organizations. You can also contact our support team for assistance with self-exclusion."
  },
  {
    category: "Troubleshooting",
    question: "What if my bet didn't go through?",
    answer: "Check your bet history in your player profile to confirm if the bet was placed. If you were charged but don't see the bet, contact our support team immediately with your transaction details. We'll investigate and resolve the issue promptly."
  },
  {
    category: "Troubleshooting",
    question: "The lottery machine isn't loading. What should I do?",
    answer: "Try refreshing the page, clearing your browser cache, or using a different browser. Ensure you have a stable internet connection and that JavaScript is enabled. If problems persist, contact our technical support team."
  },
  {
    category: "Troubleshooting",
    question: "I forgot my password. How can I reset it?",
    answer: "Click 'Sign In', then select 'Forgot Password' below the login form. Enter your registered email address and we'll send you a password reset link. Follow the instructions in the email to create a new password."
  }
];

const categories = Array.from(new Set(faqData.map(item => item.category)));

export default function FAQ({ onNavigate }: FAQProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const handleNavigation = (page: string) => {
    setMobileMenuOpen(false);
    onNavigate(page);
  };

  // First filter by category
  const categoryFilteredFAQs = selectedCategory === "All" 
    ? faqData 
    : faqData.filter(item => item.category === selectedCategory);

  // Then filter by search query
  const filteredFAQs = searchQuery.trim() === ""
    ? categoryFilteredFAQs
    : categoryFilteredFAQs.filter(item => 
        item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.answer.toLowerCase().includes(searchQuery.toLowerCase())
      );

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

      {/* Hero Section */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Hero Banner */}
          <div className="relative overflow-hidden rounded-3xl mb-12 h-64 md:h-80">
            <img 
              src="https://images.unsplash.com/photo-1633613286848-e6f43bbafb8d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzcGFjZSUyMHF1ZXN0aW9uJTIwbWFya3xlbnwxfHx8fDE3NjcyMzAzMjV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
              alt="FAQ Hero"
              className="absolute inset-0 w-full h-full object-cover opacity-40"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/50 to-blue-900/50" />
            <div className="relative h-full flex flex-col items-center justify-center text-center px-6">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: "spring" }}
                className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center mb-6"
              >
                <span className="text-5xl">❓</span>
              </motion.div>
              <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
                Frequently Asked <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Questions</span>
              </h1>
              <p className="text-lg md:text-xl text-white/80 max-w-2xl">
                Find answers to common questions about All Lotto, betting, payments, and more.
              </p>
            </div>
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2 md:gap-3 mb-8 justify-center">
            <button
              onClick={() => setSelectedCategory("All")}
              className={`px-4 md:px-6 py-2 rounded-full text-sm md:text-base font-bold transition-all ${
                selectedCategory === "All"
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
                  : "bg-white/10 text-white/80 hover:bg-white/20"
              }`}
            >
              All
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 md:px-6 py-2 rounded-full text-sm md:text-base font-bold transition-all ${
                  selectedCategory === category
                    ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white"
                    : "bg-white/10 text-white/80 hover:bg-white/20"
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* Search Bar */}
          <div className="relative mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search questions..."
              className="w-full px-4 py-3 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl text-white/80 leading-relaxed focus:outline-none focus:border-cyan-500"
            />
            <Search className="absolute right-4 top-3.5 text-white/60" />
          </div>

          {/* FAQ List */}
          <div className="space-y-4 mb-12">
            {filteredFAQs.length === 0 ? (
              <motion.div
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-12 text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-5xl">🔍</span>
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">No Results Found</h3>
                <p className="text-white/70 mb-6">
                  We couldn't find any questions matching your search. Try different keywords or browse by category.
                </p>
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedCategory("All");
                  }}
                  className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold transition-all hover:brightness-110"
                >
                  Clear Search
                </button>
              </motion.div>
            ) : (
              filteredFAQs.map((faq, index) => (
                <motion.div
                  key={index}
                  className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <button
                    onClick={() => toggleFAQ(index)}
                    className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                  >
                    <div className="flex-1">
                      <span className="text-sm text-cyan-400 font-bold mb-1 block">
                        {faq.category}
                      </span>
                      <span className="text-lg font-bold text-white">
                        {faq.question}
                      </span>
                    </div>
                    <motion.div
                      animate={{ rotate: openIndex === index ? 180 : 0 }}
                      transition={{ duration: 0.3 }}
                      className="ml-4 text-white text-2xl"
                    >
                      ▼
                    </motion.div>
                  </button>
                  <motion.div
                    initial={false}
                    animate={{
                      height: openIndex === index ? "auto" : 0,
                      opacity: openIndex === index ? 1 : 0,
                    }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-4 text-white/80 leading-relaxed">
                      {faq.answer}
                    </div>
                  </motion.div>
                </motion.div>
              ))
            )}
          </div>

          {/* Still Have Questions Section */}
          <motion.div
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="w-20 h-20 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">💬</span>
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">
              Still Have Questions?
            </h2>
            <p className="text-lg text-white/70 mb-6 max-w-2xl mx-auto">
              Can't find what you're looking for? Our support team is available 24/7 
              to help you with any questions or concerns.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => onNavigate('support')}
                className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full text-white font-bold transition-all hover:brightness-110"
              >
                Contact Support
              </button>
              <button 
                onClick={() => onNavigate('glossary')}
                className="px-8 py-3 bg-white/10 border border-white/20 rounded-full text-white font-bold transition-all hover:bg-white/20"
              >
                View Glossary
              </button>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-8 px-6 mt-12">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-white/60">© 2025 All Lotto. All rights reserved.</p>
          <div className="flex flex-wrap items-center justify-center gap-4 md:gap-6">
            <button onClick={() => onNavigate('about')} className="text-white/60 hover:text-white transition-colors">
              About
            </button>
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