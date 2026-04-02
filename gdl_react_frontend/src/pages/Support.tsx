import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Menu, X } from "lucide-react";
import globeLogo from 'figma:asset/ec9141a2fb78da64a7d122701f7402ff367746de.png';

interface SupportProps {
  onNavigate: (page: string) => void;
}

export default function Support({ onNavigate }: SupportProps) {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [formSubmitted, setFormSubmitted] = useState(false);

  const handleNavigation = (page: string) => {
    setMobileMenuOpen(false);
    onNavigate(page);
  };

  const faqs = [
    {
      question: "What is lottery betting?",
      answer: "Lottery betting allows you to bet on the outcome of official lottery draws without purchasing an actual lottery ticket. You select your numbers just like you would in a traditional lottery, and if your numbers match the official draw, you win prizes from All Lotto based on the official results.",
    },
    {
      question: "How is this different from buying a lottery ticket?",
      answer: "When you bet with All Lotto, you're placing a bet on the outcome rather than buying an official ticket. Your winnings come from All Lotto, not the official lottery organization. This allows you to play from anywhere in the world without geographic restrictions.",
    },
    {
      question: "How do I know the results are fair?",
      answer: "All results are based on official lottery draws from recognized lottery organizations worldwide. We do not conduct our own draws - we simply allow you to bet on the outcomes of these official, independently verified lottery draws.",
    },
    {
      question: "How do I deposit and withdraw funds?",
      answer: "You can deposit funds using various payment methods including credit cards, debit cards, and e-wallets. Withdrawals are processed to the same method used for deposits. All transactions are secured with industry-standard encryption.",
    },
    {
      question: "What happens if I win?",
      answer: "When you win, your account is automatically credited with the prize amount. You can choose to use these funds for more bets or withdraw them to your preferred payment method. Large wins may require identity verification for security purposes.",
    },
    {
      question: "Is there a limit to how much I can bet?",
      answer: "We implement responsible gaming limits to protect our users. You can set your own deposit and betting limits in your account settings. These limits help ensure you play within your means.",
    },
    {
      question: "Can I play from my country?",
      answer: "All Lotto is available in most countries worldwide. However, some jurisdictions have restrictions on online betting. Please check your local laws before using our service. We are not available in the United States at this time.",
    },
    {
      question: "What is the 'Guest Mode'?",
      answer: "Guest mode allows you to explore the lottery machine interface without creating an account. In guest mode, all betting features are disabled - you can view games and practice number selection, but cannot place real bets or access money features.",
    },
    {
      question: "How do I set up responsible gaming limits?",
      answer: "Navigate to your account settings and look for the 'Responsible Gaming' section. Here you can set daily, weekly, or monthly deposit limits, as well as betting limits and session time reminders.",
    },
    {
      question: "What should I do if I forgot my password?",
      answer: "Click the 'Forgot Password' link on the sign-in page. Enter your email address and we'll send you instructions to reset your password securely.",
    },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
    // Reset form
    setTimeout(() => {
      setContactForm({ name: "", email: "", subject: "", message: "" });
      setFormSubmitted(false);
    }, 3000);
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
          <h1 className="text-5xl font-bold text-white mb-6 text-center">
            Support <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Center</span>
          </h1>
          <p className="text-xl text-white/70 text-center mb-12 max-w-3xl mx-auto">
            Need help? We're here for you 24/7. Browse our FAQs or contact us directly.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* FAQ Section */}
            <div>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h2 className="text-3xl font-bold text-white mb-6">Frequently Asked Questions</h2>
                <div className="space-y-4">
                  {faqs.map((faq, index) => (
                    <motion.div
                      key={index}
                      className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <button
                        className="w-full text-left p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
                        onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                      >
                        <span className="text-white font-bold">{faq.question}</span>
                        <span className="text-white text-2xl">
                          {expandedFaq === index ? "−" : "+"}
                        </span>
                      </button>
                      {expandedFaq === index && (
                        <motion.div
                          className="p-4 pt-0"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                        >
                          <p className="text-white/70 leading-relaxed">{faq.answer}</p>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* Contact Form */}
            <div>
              <motion.div
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <h2 className="text-3xl font-bold text-white mb-6">Contact Us</h2>
                {formSubmitted ? (
                  <motion.div
                    className="bg-green-500/20 border border-green-500/50 rounded-xl p-6 text-center"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <div className="text-4xl mb-3">✓</div>
                    <h3 className="text-xl font-bold text-white mb-2">Message Sent!</h3>
                    <p className="text-white/80">
                      We've received your message and will respond within 24 hours.
                    </p>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block text-white mb-2">Name</label>
                      <input
                        type="text"
                        value={contactForm.name}
                        onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-cyan-400 transition-colors"
                        placeholder="Your name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-white mb-2">Email</label>
                      <input
                        type="email"
                        value={contactForm.email}
                        onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-cyan-400 transition-colors"
                        placeholder="your@email.com"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-white mb-2">Subject</label>
                      <input
                        type="text"
                        value={contactForm.subject}
                        onChange={(e) => setContactForm({ ...contactForm, subject: e.target.value })}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-cyan-400 transition-colors"
                        placeholder="How can we help?"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-white mb-2">Message</label>
                      <textarea
                        value={contactForm.message}
                        onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-cyan-400 transition-colors h-32 resize-none"
                        placeholder="Tell us more..."
                        required
                      />
                    </div>
                    <button
                      type="submit"
                      className="w-full px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg text-white font-bold transition-all hover:brightness-110"
                    >
                      Send Message
                    </button>
                  </form>
                )}
              </motion.div>

              {/* Contact Methods */}
              <motion.div
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mt-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <h3 className="text-xl font-bold text-white mb-4">Other Ways to Reach Us</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                      <span className="text-xl">📧</span>
                    </div>
                    <div>
                      <p className="text-white font-bold">Email Support</p>
                      <p className="text-white/70 text-sm">support@alllotto.com</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-lg flex items-center justify-center">
                      <span className="text-xl">💬</span>
                    </div>
                    <div>
                      <p className="text-white font-bold">Live Chat</p>
                      <p className="text-white/70 text-sm">Available 24/7 (coming soon)</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-500 rounded-lg flex items-center justify-center">
                      <span className="text-xl">📱</span>
                    </div>
                    <div>
                      <p className="text-white font-bold">Social Media</p>
                      <p className="text-white/70 text-sm">@GalaxyCash on Twitter & Instagram</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>

          {/* Responsible Gaming Notice */}
          <motion.div
            className="bg-gradient-to-r from-yellow-500/10 to-orange-500/10 backdrop-blur-md border-2 border-yellow-500/30 rounded-2xl p-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="flex items-start space-x-4">
              <div className="text-4xl">⚠️</div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-3">Need Help with Problem Gambling?</h3>
                <p className="text-white/80 leading-relaxed mb-4">
                  If you or someone you know has a gambling problem, help is available. Please visit these resources:
                </p>
                <ul className="space-y-2 text-white/80">
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>National Council on Problem Gambling: 1-800-522-4700</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>Gamblers Anonymous: www.gamblersanonymous.org</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-yellow-400 mr-2">•</span>
                    <span>GamCare (UK): 0808 8020 133</span>
                  </li>
                </ul>
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
            <button onClick={() => onNavigate('support')} className="text-white hover:text-white transition-colors">
              Support
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}