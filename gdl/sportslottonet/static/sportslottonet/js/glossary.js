document.addEventListener("DOMContentLoaded", () => {
  const glossaryTerms = [
    {
  term: "Sports Lotto",
  definition: "Sports Lotto combines real sports with lottery-style gameplay. Players receive a ticket made up of real sporting events and use points to play for rewards based on how those events finish."
    },
    {
      term: "Free-to-Play",
      definition: "A game model that allows users to play without paying money or risking financial loss."
    },
    {
      term: "Non-Gambling Game",
      definition: "A game that does not involve betting, wagering, odds, or real-money prizes."
    },
    {
      term: "Prediction Game",
      definition: "A game where users guess or predict sports outcomes purely for entertainment."
    },
    {
      term: "No Purchase Required",
      definition: "Participation does not require any payment or financial commitment."
    },
        {
      term: "Minimum Payout",
      definition:
        "The lowest possible amount a winning ticket can return. Minimum payouts apply when odds, ticket size, or consolation discounts reduce the final payout to the lowest eligible value."
    },
      {
      term: "Maximum Payout",
      definition:
        "The highest amount a single ticket can return, regardless of odds, number of events, or wager size. Maximum payout limits are set to control risk and are displayed before a ticket is accepted."
    },
    {
      term: "Virtual Ticket",
      definition: "A free digital entry used to make sports predictions inside the game."
    },
    {
      term: "Entertainment-Based Play",
      definition: "Gameplay designed purely for fun, engagement, and community interaction."
    },
    {
      term: "Points System",
      definition: "A scoring method used for tracking progress, not monetary value."
    },
    {
      term: "Leaderboard",
      definition: "A ranking system showing top players based on points or performance."
    },
    {
      term: "Skill-Based Gameplay",
      definition: "Game outcomes influenced by player knowledge, not chance or wagering."
    },
    {
      term: "No Cash Prizes",
      definition: "The platform does not award money or items with monetary value."
    },
    {
      term: "Digital Rewards",
      definition: "Non-monetary achievements such as badges, ranks, or visual effects."
    },
    {
      term: "Game Session",
      definition: "A single round or playthrough of predictions."
    },
    {
      term: "Match Prediction",
      definition: "Selecting an expected sports outcome for fun."
    },
    {
      term: "Sports Simulation",
      definition: "A game experience inspired by real sports without financial risk."
    },
    {
      term: "Fan Engagement",
      definition: "Interactive features designed to enhance sports enjoyment."
    },
    {
      term: "Casual Gaming",
      definition: "Lightweight gameplay intended for relaxation and fun."
    },
    {
      term: "No Betting",
      definition: "Users do not place wagers or risk currency."
    },
    {
      term: "Game Mechanics",
      definition: "Rules and systems that define how the game operates."
    },
    {
      term: "Randomized Outcomes",
      definition: "Visual or gameplay elements that add excitement without monetary stakes."
    },
    {
      term: "Sports Fan Game",
      definition: "A game designed for sports fans to interact playfully."
    },
    {
      term: "Play Credits",
      definition: "Free in-game units used only for participation."
    },
    {
      term: "Community Play",
      definition: "Social interaction with other players without competition for money."
    },
    {
      term: "Seasonal Events",
      definition: "Time-based game modes aligned with sports seasons."
    },
    {
      term: "Fair Play",
      definition: "Gameplay rules ensuring equal opportunity for all players."
    },
    {
      term: "Risk",
      definition: "Risk is the amount of points you choose to play on a ticket. Higher risk can lead to bigger rewards, while lower risk keeps potential wins smaller."
    },
    {
      term: "Game Tokens",
      definition: "Virtual items with no cash value."
    },
    {
      term: "Sports Challenge",
      definition: "A themed gameplay task based on sports events."
    },
    {
      term: "Game Mode",
      definition: "A variation of gameplay rules for different experiences."
    },
    {
      term: "Pick System",
      definition: "A selection process used to choose tickets."
    },
    {
      term: "Live Scoring",
      definition: "Live Scoring links each Sports Lotto ticket to real, in-progress sporting events and updates results in real time as games are played. Ticket outcomes are determined by actual game performance and are reflected automatically as official scoring updates occur."
    },
    {
      term: "Progress Tracking",
      definition: "Monitoring game advancement through stats or points."
    },
    {
     term: "No Risk",
    definition: "Play for free and earn points—no payments required!"
    },
    {
      term: "User Rank",
      definition: "A non-monetary status indicator based on play."
    },
    {
      term: "Digital Badge",
      definition: "A visual achievement earned through gameplay."
    },
    {
      term: "Bonus Points",
      definition: "Free points awarded to players for completing actions such as registering, verifying an email, or verifying a phone number. Bonus points can be used to play games but have no cash value."
    },
      {
      term: "Verification Bonus",
      definition: "Extra points awarded for confirming account details such as email address or phone number. These bonuses help keep accounts secure."
    },
    {
      term: "Safe Play",
      definition: "Gameplay designed without financial or addictive risk."
    },
    {
      term: "Game UI",
      definition: "The visual interface players interact with."
    },
    {
      term: "Interactive Sports Game",
      definition: "A game combining sports themes and player interaction."
    },
    {
      term: "No Real Money",
      definition: "The platform does not use real currency."
    },
    {
      term: "Just for Fun",
      definition: "Gameplay created solely for enjoyment."
    },
    {
      term: "Digital Entertainment",
      definition: "Online content designed for recreational use."
    },

    {
      term: "Player Choice",
      definition: "User selections that influence game flow without risk."
    },
    {
      term: "Sports-Themed Game",
      definition: "A game inspired by sports culture and events."
    },
    {
      term: "Free Sports Game",
      definition: "A sports-based game that costs nothing to play."
    }
  ];

  const list = document.getElementById("glossaryList");
  const search = document.getElementById("glossarySearch");

  function render(filter = "") {
    list.innerHTML = "";
    glossaryTerms
      .filter(item =>
        item.term.toLowerCase().includes(filter) ||
        item.definition.toLowerCase().includes(filter)
      )
      .forEach(item => {
        const div = document.createElement("div");
        div.className = "glossary-item";
        div.innerHTML = `
          <h3>${item.term}</h3>
          <p>${item.definition}</p>
        `;
        list.appendChild(div);
      });
  }

  search.addEventListener("input", e => {
    render(e.target.value.toLowerCase());
  });

  render();
});
