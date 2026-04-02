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
      Sports Lotto brings together sports betting and lottery-style payouts, offering a fresh, high-reward experience for fans and casual players.

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

      Once you set your preferences, the system generates ticket options that match your criteria. You can review the suggested tickets, choose the ones you like, and simply click <span class="accept-text">Accept</span> or <span class="deny-text">Deny</span> to continue. <br>This approach combines automation with player choice, making Sports Lotto easy to use while still giving you control over how you play.

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
  <!-- Start Now -->
  <div class="col-12 col-md-6 d-flex justify-content-center">
    <button class="subcard-btn subcard-btn-green d-flex gap-2" id="startNowTrigger">
      <span class="play-icon">▶</span> Start Now
    </button>
  </div>

  <!-- Learn More -->
  <div class="col-12 col-md-6 d-flex justify-content-center">
    <button class="subcard-btn subcard-btn-orange d-flex gap-2" id="learnMoreBtn">
      Learn More
    </button>
  </div>
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
        <b> AI-selected picks based on your filters:</b><br><br>
        🎯<b>Choose</b> <b>4 events</b> to win ~ <b>20×</b> for <b>1 risked</b>.<br>
        🎟️ You’ll receive<b>five tickets options</b> You can delete any tickets you don’t want.<br>
        ✅ Once you're ready, click <b>Buy Tickets!</b>
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
    id: "infoCash",
    title: "Cash Rewards and Payouts",
    icon: `
  <span class="gradient-icon">
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
    <!-- Dollar sign -->
    <path
      d="M12 3v18
         M16 7.5c0-1.9-1.8-3-4-3s-4 1.1-4 3
         1.8 3 4 3 4 1.1 4 3
         -1.8 3-4 3-4-1.1-4-3"
      stroke="#fff"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</span>


    `,
    body: `
      This is what makes Sports Lotto VIP different. Deposit money and play with confidence. Win real cash sent directly to your account. Withdraw your winnings easily anytime. No points, no credits, no gimmicks—just pure sports excitement and real money rewards for the players who play smart.
    `
  },
  {
   id: "info4",
  title: "Why Play Sports Lotto VIP",
  icon: `
<span class="gradient-icon3" aria-label="VIP Diamond A Wide">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"
 width="56" height="56" fill="none" stroke="#fff"
 stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round">

  <!-- Outer diamond (wider) -->
  <polygon points="8 24 20 10 44 10 56 24 32 54"/>

  <!-- Facets -->
  <line x1="20" y1="10" x2="32" y2="54"/>
  <line x1="44" y1="10" x2="32" y2="54"/>
  <line x1="8" y1="24" x2="56" y2="24"/>

</svg>
</span>


  `,
  body: `
    <div class="accordion-subtitle mb-3">
Sports Lotto VIP isn’t just another game — it’s where strategy meets adrenaline. You’re in control of every move, playing for real cash with higher stakes and bigger potential payouts.    </div>

    <div class="d-flex justify-content-between flex-wrap gap-3 mb-4">

      <div class="card4-subcard">
  <div class="card4-icon-row">
    <div class="icon-bg icon-bg-green">

      <svg xmlns="http://www.w3.org/2000/svg"
           viewBox="0 0 24 24"
           width="40" height="40"
           fill="none"
           stroke="#FFFFFF"
           stroke-width="2"
           stroke-linecap="round"
           stroke-linejoin="round"
           aria-hidden="true">

        <!-- Single bill -->
        <rect x="3" y="6" width="18" height="12" rx="2"/>

        <!-- Dollar sign (clean, not cartoon) -->
        <path d="M12 8.5 V15.5"/>
        <path d="M14.5 9.8 C14.5 8.7 13.4 8 12 8 C10.6 8 9.5 8.7 9.5 9.8 C9.5 10.9 10.6 11.5 12 11.9 C13.4 12.3 14.5 12.9 14.5 14.2 C14.5 15.3 13.4 16 12 16 C10.6 16 9.5 15.3 9.5 14.2"/>

      </svg>

    </div>
  </div>


        <div class="card4-title mt-2">Win real money on every play</div>
      </div>
<div class="card4-subcard">
  <div class="card4-icon-row">
    <div class="icon-bg icon-bg-blue">
      <svg xmlns="http://www.w3.org/2000/svg"
 viewBox="0 0 24 24"
 width="40" height="40"
 fill="none" stroke="#FFFFFF"
 stroke-width="2"
 stroke-linecap="round"
 stroke-linejoin="round"
 aria-hidden="true">

  <line x1="4" y1="6" x2="20" y2="6"/>
  <circle cx="10" cy="6" r="2"/>

  <line x1="4" y1="12" x2="20" y2="12"/>
  <circle cx="15" cy="12" r="2"/>

  <line x1="4" y1="18" x2="20" y2="18"/>
  <circle cx="8" cy="18" r="2"/>

</svg>

    </div>
  </div>
  <div class="card4-title mt-2">Control your risk, payout, and strategy</div>
</div>

      <div class="card4-subcard">
        <div class="card4-icon-row">
          <div class="icon-bg icon-bg-orange">
         <svg xmlns="http://www.w3.org/2000/svg"
       viewBox="0 0 64 64"
       width="40" height="40"
       fill="none"
       stroke="#ffffff"
       stroke-width="3"
       stroke-linecap="round"
       stroke-linejoin="round"
       aria-hidden="true">

    <!-- Center dot -->
    <circle cx="32" cy="32" r="4" fill="#ffffff"/>

    <!-- Signal rings -->
    <path d="M20 32a12 12 0 0 1 24 0"/>
    <path d="M14 32a18 18 0 0 1 36 0"/>
    <path d="M8 32a24 24 0 0 1 48 0"/>

  </svg>
          </div>
        </div>
        <div class="card4-title mt-2">Follow the action with live scores and instant updates</div>
      </div>

      <div class="card4-subcard">
        <div class="card4-icon-row">
   <div class="icon-bg icon-bg-purple">
  <svg xmlns="http://www.w3.org/2000/svg"
       viewBox="0 0 64 64"
       width="40" height="40"
       fill="none"
       stroke="#ffffff"
       stroke-width="3"
       stroke-linecap="round"
       stroke-linejoin="round"
       aria-hidden="true">

    <!-- Main VIP star (center, untouched) -->
    <polygon points="
      32 12
      36 26
      50 26
      38 34
      42 48
      32 40
      22 48
      26 34
      14 26
      28 26
    "/>

    <!-- Left accent star (pulled outward + up) -->
    <polygon points="
      10 10
      12 15
      17 15
      13 18
      15 23
      10 20
      5 23
      7 18
      3 15
      8 15
    "/>

    <!-- Right accent star (pulled outward + up) -->
    <polygon points="
      54 10
      56 15
      61 15
      57 18
      59 23
      54 20
      49 23
      51 18
      47 15
      52 15
    "/>

  </svg>
</div>
        </div>
        <div class="card4-title mt-2">Unlock higher-stakes matchups </div>
                <div class="card4-desc"> and exclusive VIP opportunities</div>

      </div>

    </div>

    <div class="mt-3" >
Every pick matters. Every ticket has upside. This is where big wins start.    </div>
  `
}

];
export default accordionItems;