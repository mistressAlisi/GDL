import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
/**
 * Base Form Class
 * Handles common form functionality like balance counter animations
 */
export class WinnerBoard extends AbstractDashboardApp {
    settings = {
        "currentWinnerName":"#currentWinnerName",
        "winTime":"#winTime",
        "progressBar":"#progressBar",
        "remainingWinnersSection":"#remainingWinnersSection",
        "topWinnersList":"#topWinnersList",
        "remainingWinnersList":"#remainingWinnersList",
        "avatarColors":['avatar-blue', 'avatar-purple', 'avatar-pink', 'avatar-green', 'avatar-orange', 'avatar-red', 'avatar-teal', 'avatar-indigo']

    }
    urls = {
        "_api_prefix": "/api/v1/game/",
        "winners":"get/winners"
    }
    elements = {}
    // Recent Winners Ticker
    currentWinIndex = 0
    tickerInterval = undefined
    winnersData = {}
    recentWins = {}

    // Helper Functions:
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getAvatarColor(id) {
        return this.settings["avatarColors"][parseInt(id) % this.settings["avatarColors"].length];
    }

    getInitials(name) {
        return name.split(' ').map(function(n) { return n[0]; }).join('').toUpperCase();
    }

    renderAvatar(winner) {
        const initials = this.getInitials(winner.name);
        const colorClass = this.getAvatarColor(winner.id);
        const escapedName = this.escapeHtml(winner.name);

        if (winner.avatar) {
            return '<div class="winner-avatar ' + colorClass + '"><img src="/media/' + this.escapeHtml(winner.avatar) + '" alt="' + escapedName + '" style="width:100%;height:100%;border-radius:50%;object-fit:cover;"></div>';
        }
        return '<div class="winner-avatar ' + colorClass + '">' + initials + '</div>';
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    createWinnerHTML(winner, rank, isTopTen) {
        const rankDisplay = isTopTen
            ? '<div class="rank-badge"><span class="rank-number">' + rank + '</span></div>'
            : '<div class="rank-text"><span>' + rank + '</span></div>';
        // console.log("CreateWinnerHTML",winner);
        const escapedName = this.escapeHtml(winner.name);
        const formattedWins = this.formatNumber(winner.total_win);

        return '<div class="winner-item">' +
            (isTopTen ? rankDisplay : '') +
            '<div class="winner-content">' +
                (!isTopTen ? rankDisplay : '') +
                this.renderAvatar(winner) +
                '<div class="winner-name-container">' +
                    '<div class="winner-name-text">' + escapedName + '</div>' +
                '</div>' +
                '<div class="wins-badge">' +
                    '<i class="fas fa-award"></i>' +
                    '<span class="wins-number">' + formattedWins + '</span>' +
                    '<span class="wins-label">total won</span>' +
                '</div>' +
            '</div>' +
        '</div>';
    }

    // Render winners
    renderTopWinners() {
        const topWinners = this.winnersData.slice(0, 10);
        // console.log("TopWinners",topWinners);
        const html = topWinners.map(function(winner, index) {
            return this.createWinnerHTML(winner, index + 1, true);
        }.bind(this)).join('');
        this.elements["topWinnersList"].html(html);
    }

     renderRemainingWinners() {
        const remaining = this.winnersData.slice(10);
        if (remaining.length === 0) return;

        const html = remaining.map(function(winner, index) {
            return this.createWinnerHTML(winner, index + 11, false);
        }.bind(this)).join('');
        this.elements["remainingWinnersSection"].show().find(this.elements["remainingWinnersList"]).html(html);
    }


    getTimeAgo(timestamp) {
        const seconds = Math.floor((Date.now() - timestamp.getTime()) / 1000);
        if (seconds < 60) return seconds + 's ago';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return minutes + 'm ago';
        return Math.floor(minutes / 60) + 'h ago';
    }

    updateTicker() {
        if (this.recentWins.length === 0) return;

        const currentWin = this.recentWins[this.currentWinIndex];


        this.elements["currentWinnerName"].addClass('fade-out');
        this.elements["progressBar"].css('width', '0%');

        setTimeout(function() {
            this.elements["currentWinnerName"].text(currentWin.name).removeClass('fade-out');
            // this.elements["winTime"].text(this.getTimeAgo(currentWin.timestamp));
            setTimeout(function() {
                this.elements["progressBar"].css('width', '100%');
            }.bind(this), 50);
            this.currentWinIndex = (this.currentWinIndex + 1) % this.recentWins.length;
        }.bind(this), 500);
    }

    startTicker() {
        if (this.recentWins.length === 0) {
            this.elements["currentWinnerName"].text('No recent wins');
            this.elements["winTime"].text('');
            return;
        }

        const firstWin = this.recentWins[0];
        this.elements["currentWinnerName"].text(firstWin.name);
        // this.elements["winTime"].text(this.getTimeAgo(firstWin.timestamp));

        setTimeout(function() {
            this.elements["progressBar"].css('width', '100%');
        }.bind(this), 100);

        if (this.recentWins.length > 1) {
            this.currentWinIndex = 1;
            this.tickerInterval = setInterval(this.updateTicker.bind(this), 5000);
        }
    }
    _handle_data(res) {
        window.resultdata = res["data"];
        this.winnersData = res["data"]["top_winners"]
           this.recentWins = res.data.winning_tickets.map(w => ({
        ...w,
        // timestamp: new Date(w.graded_at),
        name: w.account?.name ?? w.account?.acctnum
        }));
        // console.log("Got this data:",window.resultdata);
        this.renderTopWinners();
        this.renderRemainingWinners()
        // this.startTicker();
    }

    constructor(settings,urls) {
        super(settings,urls);
        $.extend(this.settings,settings)
        $.extend(this.urls,urls)
        this.elements["currentWinnerName"]=$(this.settings["currentWinnerName"])
        this.elements["winTime"]=$(this.settings["winTime"])
        this.elements["progressBar"]=$(this.settings["progressBar"])
        this.elements["remainingWinnersSection"]=$(this.settings["remainingWinnersSection"])
        this.elements["topWinnersList"]=$(this.settings["topWinnersList"])
        this.elements["remainingWinnersList"]=$(this.settings["remainingWinnersList"])
        $(window).on('unload', function() {
            if (this.tickerInterval) clearInterval(this.tickerInterval);
        }.bind(this));
        console.log("WinnerBoard Loaded")

        this.generic_api_getreq(this.urls["winners"],false,this._handle_data.bind(this))
        // console.log("Firing Winnerboard")
    }
}
