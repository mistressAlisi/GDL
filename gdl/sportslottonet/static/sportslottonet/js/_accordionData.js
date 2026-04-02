export const accordionItems = [  {
    id: "info1",
    title: "A New Way to Play",
    icon: `
      <span class="gradient-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="56" height="56">
          <g transform="translate(-10,100) scale(1,-1)">
            <path fill="#ffffff" d="M20 50 C20 40, 28 32, 38 32 C46 32, 52 36, 60 36 C68 36, 74 32, 82 32 C92 32, 100 40, 100 50 C100 58, 94 66, 84 68 C76 69.8, 72 66, 60 66 C48 66, 44 69.8, 36 68 C26 66, 20 58, 20 50 Z"></path>
            <rect x="34" y="46" width="6" height="14" rx="1" fill="#a95cff"></rect>
            <rect x="30" y="51" width="14" height="6" rx="1" fill="#a95cff"></rect>
            <circle cx="68" cy="46" r="3" fill="#ffffff" stroke="#b10554" stroke-width="1"></circle>
            <circle cx="75" cy="52" r="3" fill="#ffffff" stroke="#b10554" stroke-width="1"></circle>
            <circle cx="68" cy="58" r="3" fill="#ffffff" stroke="#b10554" stroke-width="1"></circle>
            <circle cx="61" cy="52" r="3" fill="#ffffff" stroke="#b10554" stroke-width="1"></circle>
          </g>
        </svg>
      </span>
    `,
    body: `
      Win and earn rewards. Sports Lotto combines the thrill of sporting events
      with the strategy of choosing wagers — a fresh approach for fans and casual gamers alike.

      <div class="mt-3">
        <button class="start-btn" id="loginTrigger">Start Playing →</button>
      </div>
    `
  },

  {
    id: "info2",
    title: "Smart Ticket Generation",
    icon: `
      <span class="gradient-icon2">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 100 100">
          <polygon points="50,12 61,42 88,50 61,58 50,88 39,58 12,50 39,42"
            fill="transparent" stroke="#ffffff" stroke-width="6" stroke-linejoin="round">
          </polygon>
        </svg>
      </span>
    `,
    body: `
      <div class="accordion-subhead">Automation Meets Strategy</div>

      Once preferences are entered, an algorithm generates every possible combination
      of games that match your criteria. Review potential tickets, decide which to
      purchase, and click <span class="accept-text">Accept</span> or <span class="deny-text">Deny</span>.

      <p class="sub-note">Strategic and accessible — play your own way.</p>
    `
  },

  {
    id: "info3",
    title: "How It Works",
    icon: `
      <span class="gradient-icon3">
        <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 56 56">
          <circle cx="28" cy="28" r="20" fill="none" stroke="#ffffff" stroke-width="4"></circle>
          <circle cx="28" cy="28" r="12" fill="none" stroke="#ffffff" stroke-width="4"></circle>
          <circle cx="28" cy="28" r="4" fill="none" stroke="#ffffff" stroke-width="4"></circle>
        </svg>
      </span>
    `,
    body: `
      <div class="row g-3">

        <div class="col-12 col-md-4">
          <div class="subcard">
            <div class="subcard-number">1</div>
            <div class="subcard-title">Select Tickets</div>
            <div class="subcard-desc">Choose number of games to include</div>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <div class="subcard">
            <div class="subcard-number">2</div>
            <div class="subcard-title">Set Risk</div>
            <div class="subcard-desc">Wager points based on desired returns</div>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <div class="subcard">
            <div class="subcard-number">3</div>
            <div class="subcard-title">Win Big</div>
            <div class="subcard-desc">Track picks in real time & redeem points</div>
          </div>
        </div>

      </div>

      <div class="row mt-4 g-3">
        <div class="col-6 col-md-6 d-flex justify-content-center">
          <button class="subcard-btn subcard-btn-green d-flex gap-2" id="startNowTrigger">
            <span class="play-icon">▶</span> Start Now
          </button>
        </div>

      <div class="col-6 col-md-6 d-flex justify-content-center">
  <button class="subcard-btn subcard-btn-orange d-flex gap-2" id="learnMoreBtn">
    Learn More
  </button>
</div>

      </div>
    `
  },

  {
    id: "infoQuickPicks",
    title: "Quick Picks",
    icon: `<span class="gradient-icon">⚡</span>`,
    body: `
      <p>
        <b>A.</b> Picks where your events are chosen by <b>AI</b> with filters:<br>
        🎯 <b>4 events</b> to win ~ <b>20×</b> for <b>1 risked</b>.<br>
        🎟️ You get <b>five tickets</b> and can delete any you don’t want.<br>
        ✅ Once satisfied, click <b>Buy Tickets!</b>
      </p>
    `
  },

  {
    id: "infoTracking",
    title: "Real-Time Tracking & Results",
    icon: `
      <span class="gradient-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
          <path d="M7 4h10v3a5 5 0 0 1-10 0V4Z" fill="#fff"></path>
          <path d="M7 4H4v3c0 2.2 1.8 4 4 4" stroke="#fff" stroke-width="1.5"></path>
          <path d="M17 4h3v3c0 2.2-1.8 4-4 4" stroke="#fff" stroke-width="1.5"></path>
          <path d="M12 12v4" stroke="#fff" stroke-width="1.5"></path>
          <path d="M8 20h8" stroke="#fff" stroke-width="1.5"></path>
          <path d="M9.5 20v-2h5v2" stroke="#fff" stroke-width="1.5"></path>
        </svg>
      </span>
    `,
    body: `
      Pending tickets update live as games unfold, letting players follow the action
      in real time — turning lotto into a sports-driven adventure instead of waiting
      for a number draw.
    `
  },

  {
   id: "info4",
  title: "🎁 Free Rewards & Points",
  icon: `
    <span class="gradient-icon3" role="img" aria-label="Target icon" title="Target">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="56" height="56" fill="none" stroke="#ffffff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="10" y="16" width="44" height="10" rx="2" ry="2"></rect>
        <rect x="10" y="26" width="44" height="30" rx="3" ry="3"></rect>
        <line x1="32" y1="16" x2="32" y2="56"></line>
        <line x1="10" y1="21" x2="54" y2="21"></line>
        <circle cx="32" cy="10" r="3" fill="#ffffff" stroke="none"></circle>
        <path d="M32 10 C26 4, 18 6, 20 12 C22 18, 28 16, 32 12" fill="none"></path>
        <path d="M32 10 C38 4, 46 6, 44 12 C42 18, 36 16, 32 12" fill="none"></path>
        <path d="M30 12 C28 18, 26 22, 26 26" fill="none"></path>
        <path d="M34 12 C36 18, 38 22, 38 26" fill="none"></path>
      </svg>
    </span>
  `,
  body: `
    <div class="accordion-subtitle mb-3">
      Earn points by completing actions:
    </div>

    <div class="d-flex justify-content-between flex-wrap gap-3 mb-4">

      <div class="card4-subcard">
        <div class="card4-icon-row">
          <div class="icon-bg icon-bg-blue">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="5" width="18" height="14" rx="2" ry="2"></rect>
              <polyline points="3,5 12,13 21,5"></polyline>
            </svg>
          </div>
        </div>
        <div class="card4-title mt-2">Register Email</div>
        <div class="card4-desc">1,500 pts</div>
      </div>
<div class="card4-subcard">
  <div class="card4-icon-row">
    <div class="icon-bg icon-bg-green">
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.72 19.72 0 0 1-8.63-3.07 19.36 19.36 0 0 1-6-6 19.72 19.72 0 0 1-3.07-8.63A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.81.37 1.61.73 2.37a2 2 0 0 1-.45 2.11L9.21 8.79a16.05 16.05 0 0 0 6 6l.57-.57a2 2 0 0 1 2.11-.45c.76.36 1.56.61 2.37.73a2 2 0 0 1 1.72 2z"></path>
      </svg>
    </div>
  </div>
  <div class="card4-title mt-2">Verify Phone</div>
  <div class="card4-desc">2,500 pts</div>
</div>

      <div class="card4-subcard">
        <div class="card4-icon-row">
          <div class="icon-bg icon-bg-orange">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg"
                 alt="Telegram"
                 style="width:30px; height:30px;"
                 loading="lazy">
          </div>
        </div>
        <div class="card4-title mt-2">Telegram</div>
        <div class="card4-desc">1,000 pts</div>
      </div>

      <div class="card4-subcard">
        <div class="card4-icon-row">
          <div class="icon-bg icon-bg-purple">👥</div>
        </div>
        <div class="card4-title mt-2">Refer Friend</div>
        <div class="card4-desc">2,500 pts</div>
      </div>

    </div>

    <div class="mt-3" >
      💳 Redeem for Amazon gift cards at 100 points = $1 USD
    </div>
  `
}

];
export default accordionItems;