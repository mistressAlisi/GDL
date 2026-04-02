document.getElementById("drawFlow").beginElement();

// document.addEventListener("DOMContentLoaded", function () {
//
//   const SPORTS = [
//     {
//       key: "nfl",
//       icon: "#sport-football",
//       teams: ["DAL", "NYJ", "KC", "SF"]
//     },
//     {
//       key: "nba",
//       icon: "#sport-basketball",
//       teams: ["LAL", "BOS", "GSW", "NYK"]
//     },
//     {
//       key: "mlb",
//       icon: "#sport-baseball",
//       teams: ["NYY", "LAD", "ATL", "BOS"]
//     },
//     {
//       key: "nhl",
//       icon: "#sport-hockey",
//       teams: ["NYR", "TOR", "CHI", "VGK"]
//     },
//     {
//       key: "fifa",
//       icon: "#sport-soccer",
//       teams: ["BRA", "ARG", "ENG", "FRA"]
//     }
//   ];
//
//   const tubes = document.querySelectorAll(".tube");
//   const template = document.getElementById("arena-ball-template");
//
//   function clearTubes() {
//     tubes.forEach(t => t.innerHTML = "");
//   }
//
//   function spawnTicket() {
//     clearTubes();
//
//     let labelText = [];
//
//     for (let i = 0; i < 6; i++) {
//       const sport = SPORTS[Math.floor(Math.random() * SPORTS.length)];
//       const teamA = sport.teams[Math.floor(Math.random() * sport.teams.length)];
//       const teamB = sport.teams[Math.floor(Math.random() * sport.teams.length)];
//
//       labelText.push(`${teamA} vs ${teamB}`);
//
//       const topBall = template.content.cloneNode(true);
//       const bottomBall = template.content.cloneNode(true);
//
//       topBall.querySelector("use").setAttribute("href", sport.icon);
//       bottomBall.querySelector("use").setAttribute("href", sport.icon);
//
//       topBall.querySelector(".ball-label").textContent = teamA;
//       bottomBall.querySelector(".ball-label").textContent = teamB;
//
//       tubes[0].appendChild(topBall);
//       tubes[1].appendChild(bottomBall);
//     }
//
//     document.getElementById("matchup-text").textContent =
//       labelText.slice(0, 3).join(" • ");
//   }
//
//   spawnTicket();
//   setInterval(spawnTicket, 25000);
//   document.getElementById("reroll-ticket").onclick = spawnTicket;
//
// });
