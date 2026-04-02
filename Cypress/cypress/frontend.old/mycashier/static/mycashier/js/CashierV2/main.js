import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
import {ElementH} from "/static/minerve/js/dashboards/DashboardApp/Elements/H.js";
import {ElementP} from "/static/minerve/js/dashboards/DashboardApp/Elements/P.js";
import {ElementA} from "/static/minerve/js/dashboards/DashboardApp/Elements/A.js";
import {ElementImg} from "/static/minerve/js/dashboards/DashboardApp/Elements/Img.js";
import {ElementDiv} from "/static/minerve/js/dashboards/DashboardApp/Elements/Div.js";

import {ElementSpan} from "/static/minerve/js/dashboards/DashboardApp/Elements/Span.js";
import {ElementInput} from "/static/minerve/js/dashboards/DashboardApp/Elements/Input.js";
import {Modal} from "/static/minerve/js/dashboards/DashboardApp/Elements/Modal.js";

export class CashierApp extends AbstractDashboardApp {
    urls = {
        "claim_bonus":"/change/me",
        "read_message":"read/message",
        "crypto_deposit_url":"crypto/deposit/url",
        "apple_wallet":"apple/wallet",
        "paypal_wallet":"apple/wallet",
        "card_wallet":"apple/wallet"
    }
    settings = {
        "max_recent_activity_items":5,
        "selAmnDis":"#selectedAmountDisplay",
        "qckDepDis":"#quickDepositDisplay",
        "qckDepBtn":"#quickDepositBtn",
        "qckAmnBtns":"#quickAmountButtons button",
        "recActList":"#recentActivityList",
        "payMtdBttns":".payment-method-btn",
        "mrkRedBttn":".mark-read-btn",
        "alertBell":".alert-item.unread",
        "alertBellBtn":"#alertBellBtn",
        "alertBdg":"#alertBadge",
        "alertsModal":"#alertsModal",
        "claimBonusButton":"#claimBonusButton",
        "customAmountInput":"#customAmountInput",
        "depositDisplay":"#quickDepositDisplay",
        "withdrawDisplay":"#withdrawDisplay",
        "desktopDepositBtn":"#quickDepositBtn",
        "mobileDepositBtn":"#depositBtn",
        "desktopWithdrawBtn":"#desktopWithdrawBtn",
        "mobileWithdrawBtn":"#withdrawBtn",
        "cryptoOptions":"#cryptoOptions",
        "eWallet":"#ewalletOptions",
        "recentActivityList":"#recentActivityList",
        "fullHistoryContent":"#fullHistoryContent",
        "fullHistoryModal":"#fullHistoryModal",
        "cryptoOptionsButtons":"#cryptoOptionsButtons",
        "viewFullHistoryBtn":"#viewFullHistoryBtn",
        "text-emerald":"text-emerald-400",
        "text-orange":"text-orange-400",
        "walletOptions":["PayPal", "Apple Pay"],
        "bonusActive":false,
        "bonusClaimed":false,
         "cryptos":[
                {symbol: 'BTC', label: 'Bitcoin'},
                {symbol: 'ETH', label: 'Ethereum'},
                {symbol: 'USDT', label: 'Tether'},
                {symbol: 'LTC', label: 'Litecoin'}
                ],
        "csrf_token": "",
        "isWithdraw":false,
    }
    texts = {
        card: 'Credit/Debit Card',
        crypto: 'Cryptocurrency',
        ewallet: 'E-Wallet',
        bank: 'Bank Transfer',
        processing_deposit:"⏳ Processing Deposit…",
        PAYMENT_METHOD_NAMES: {
            card: 'Credit/Debit Card',
            crypto: 'Cryptocurrency',
            ewallet: 'E-Wallet',
            bank: 'Bank Transfer'
        }
    }
    elements = {

    }
    selectedAmount = 0
    quickDepAmount = 0
    selectedPaymentMethod = false
    selectedWalletProvider = false
    depositInProgress = false
    withdrawInProgress = false
    resetTimer = false
    selectedCryptoSymbol = false
    bonusAvailable = false
    bonusUsed = false
    formatTimeNow() {
        const d = new Date();
        // simple timestamp; you can replace with relative time logic
        return d.toLocaleString();
    }

    statusBadgeHtml(status) {
            if (status === 'completed') {
                return `<span class="badge bg-success text-dark small">✔ ${status}</span>`;
            } else {
                return `<span class="badge bg-warning text-dark small">⌛ ${status}</span>`;
            }
        }

    handleDepositClick(event) {
        if (this.depositInProgress) {
            event.preventDefault()
            return false;
        }
        let amount = Number(this.quickDepAmount)
        if (!amount || isNaN(amount) || amount <= 0) {
                alert('Please enter a valid deposit amount.');
                return false;
        }

        if (!this.selectedPaymentMethod) {
                alert('Please select a payment method before depositing.');
                return false;
        }
        this.depositInProgress = true
        if (this.elements["desktopDepositBtn"] !== undefined) {
            this.elements["desktopDepositBtn"].attr('disabled','disabled')
            this.elements["desktopDepositBtn"].addClass("disabled");
            this.elements["desktopDepositBtn"].css("cursor", "not-allowed")
            this.elements["desktopDepositBtn"].html(this.texts.processing_deposit)
        }
        if (this.elements["mobileDepositBtn"] !== undefined) {
            this.elements["mobileDepositBtn"].attr('disabled','disabled')
            this.elements["mobileDepositBtn"].addClass("disabled");
            this.elements["mobileDepositBtn"].css("cursor", "not-allowed")
            this.elements["mobileDepositBtn"].html(this.texts.processing_deposit)
        }
        this.resetTimer = setTimeout(() => {
                this.depositInProgress = false;
                if (this.elements["desktopDepositBtn"] !== undefined) {
                    this.elements["desktopDepositBtn"].attr('disabled')
                    this.elements["desktopDepositBtn"].removeClass("disabled");
                    this.elements["desktopDepositBtn"].css("cursor", "")
                    this.elements["desktopDepositBtn"].html(`➕ Deposit $${this.quickDepAmount.toLocaleString()} →`)
                }
                if (this.elements["mobileDepositBtn"] !== undefined) {
                    this.elements["mobileDepositBtn"].attr('disabled')
                    this.elements["mobileDepositBtn"].addClass("disabled");
                    this.elements["mobileDepositBtn"].css("cursor", "")
                    this.elements["mobileDepositBtn"].html(`➕ Deposit $${this.quickDepAmount.toLocaleString()} →`)
                }
            }, 5000);
        // determine status: bank -> pending, others -> completed
        const status = this.selectedPaymentMethod.id === 'bank' ? 'pending' : 'completed';
        let methodName = this.selectedPaymentMethod.name;
            if (this.selectedPaymentMethod.id === 'crypto' && this.selectedCryptoSymbol) {
                methodName = `${this.selectedCryptoSymbol} (Crypto)`;
            }
        if (this.selectedPaymentMethod.id === 'crypto' && this.selectedCryptoSymbol) {
            // Optional: persist amount + coin if needed later
            //sessionStorage.setItem('depositAmount', amount);
            //sessionStorage.setItem('depositCrypto', selectedCryptoSymbol);

            window.location.href = this.urls["crypto_deposit_url"]+`?amount=${amount}&currency=${this.selectedCryptoSymbol}`;
            //window.open(this.urls["crypto_deposit_url"]+`?amount=${amount}&currency=${this.selectedCryptoSymbol}`, '_blank', 'noopener,noreferrer');
            return; // IMPORTANT: stop normal flow
        }
        if (this.selectedPaymentMethod.id === 'ewallet' && this.selectedWalletProvider) {
                methodName = `${this.selectedWalletProvider} (E-Wallet)`;

                if (this.selectedWalletProvider === 'Apple Pay') {
                    window.open(this.urls["apple_wallet"]+`?amount=${amount}`, '_blank', 'noopener,noreferrer');
                }
                else if (this.selectedWalletProvider === 'PayPal') {
                    window.open(this.urls["paypal_wallet"]+`?amount=${amount}`, '_blank', 'noopener,noreferrer');
                }
                return; // IMPORTANT: stop normal flow
            }

            if (this.selectedPaymentMethod.id === 'card') {
                window.open(this.urls["card_wallet"]+`?amount=${amount}`, '_blank', 'noopener,noreferrer');
                return;
            }
           let finalAmount = amount;
           if (this.bonusAvailable && this.bonusUsed) {
               const bonusAmount = Math.min(amount * 0.2, 500);
               finalAmount = amount + bonusAmount;
               this.bonusAvailable = false
               this.bonusUsed = true
               this.elements["claimBonusButton"].attr('disabled', true)
               this.elements["claimBonusButton"].css("opacity", 0.6)
               this.elements["claimBonusButton"].css("cursor", "not-allowed")
               this.elements["claimBonusButton"].title = "Bonus used"
               if (bonusAmount > 0) {
                   let bonusName = "Bonus 20% Match"
                   const bonusTx = {
                       id: Date.now(),                // simple unique id
                       type: 'deposit',
                       method: bonusName,
                       amount: bonusAmount,
                       status: status,
                       time: formatTimeNow()
                   };
                   addTransactionToRecentActivity(bonusTx);
               }
           }
           const tx = {
                id: Date.now(),                // simple unique id
                type: 'deposit',
                method: methodName,
                amount: finalAmount,
                status: status,
                time: formatTimeNow()
           }
           this.addTransactionToRecentActivity(tx);
           try {
                if (status === 'pending') {
                    const pendingEl = document.getElementById('balancePending');
                    if (pendingEl) {
                        const curr = Number(pendingEl.innerText.replace(/[^0-9.-]/g, '')) || 0;
                        pendingEl.innerText = `$${(curr + amount).toLocaleString()}`;
                    }
                } else {
                    const totalEl = document.getElementById('balanceTotal');
                    if (totalEl) {
                        const curr = Number(totalEl.innerText.replace(/[^0-9.-]/g, '')) || 0;
                        totalEl.innerText = `$${(curr + amount).toLocaleString()}`;
                    }
                    const availEl = document.getElementById('balanceAvailable');
                    if (availEl) {
                        const currA = Number(availEl.innerText.replace(/[^0-9.-]/g, '')) || 0;
                        availEl.innerText = `$${(currA + amount).toLocaleString()}`;
                    }
                }
            } catch (err) {
                // non-fatal if balance elements not present
                console.warn('Balance update skipped', err);
            }
            const customInput = this.elements["customAmountInput"];
            if (customInput) {
                customInput.val('');
            }
        }

    // Withdraw button handlers (desktop Withdraw and mobile bottom)
    handleWithdrawClick(event) {
        if (this.withdrawInProgress) {
            event.preventDefault()
            return false;
        }
        let amount = Number(this.withdrawAmount)
        if (!amount || isNaN(amount) || amount <= 0) {
            alert('Please enter a valid withdraw amount.');
            return false;
        }

        if (!this.selectedPaymentMethod) {
            alert('Please select a payment method before withdrawing.');
            return false;
        }
        this.withdrawInProgress = true
        if (this.elements["desktopWithdrawBtn"] !== undefined) {
            this.elements["desktopWithdrawBtn"].attr('disabled', 'disabled')
            this.elements["desktopWithdrawBtn"].addClass("disabled");
            this.elements["desktopWithdrawBtn"].css("cursor", "not-allowed")
            this.elements["desktopWithdrawBtn"].html(this.texts.processing_deposit)
        }
        if (this.elements["mobileWithdrawBtn"] !== undefined) {
            this.elements["mobileWithdrawBtn"].attr('disabled', 'disabled')
            this.elements["mobileWithdrawBtn"].addClass("disabled");
            this.elements["mobileWithdrawBtn"].css("cursor", "not-allowed")
            this.elements["mobileWithdrawBtn"].html(this.texts.processing_deposit)
        }
        this.resetTimer = setTimeout(() => {
            this.withdrawInProgress = false;
            if (this.elements["desktopWithdrawBtn"] !== undefined) {
                this.elements["desktopWithdrawBtn"].attr('disabled')
                this.elements["desktopWithdrawBtn"].removeClass("disabled");
                this.elements["desktopWithdrawBtn"].css("cursor", "")
                this.elements["desktopWithdrawBtn"].html(`▬ Withdraw $${this.withdrawAmount.toLocaleString()} →`)
            }
            if (this.elements["mobileWithdrawBtn"] !== undefined) {
                this.elements["mobileWithdrawBtn"].attr('disabled')
                this.elements["mobileWithdrawBtn"].addClass("disabled");
                this.elements["mobileWithdrawBtn"].css("cursor", "")
                this.elements["mobileWithdrawBtn"].html(`▬ Withdraw $${this.withdrawAmount.toLocaleString()} →`)
            }
        }, 5000);
            // determine status: bank -> pending, others -> completed
            const status = this.selectedPaymentMethod.id === 'bank' ? 'pending' : 'completed';

            // construct friendly method name — if crypto and coin chosen, include coin
            let methodName = this.selectedPaymentMethod.name;
            if (this.selectedPaymentMethod.id === 'crypto' && this.selectedCryptoSymbol) {
                methodName = `${this.selectedCryptoSymbol} (Crypto)`;
            }

            // 🚀 REDIRECT FOR CRYPTO WITHDRAWS
            if (this.selectedPaymentMethod.id === 'crypto' && this.selectedCryptoSymbol) {
                // Optional: persist amount + coin if needed later
                //sessionStorage.setItem('depositAmount', amount);
                //sessionStorage.setItem('depositCrypto', selectedCryptoSymbol);

                //window.location.href = `${CRYPTO_WITHDRAW_URL}?amount=${amount}&currency=${selectedCryptoSymbol}`;
                window.location.href = this.urls["crypto_withdraw_url"]+`?amount=${amount}&currency=${this.selectedCryptoSymbol}`;
                //window.open(`${CRYPTO_WITHDRAW_URL}?amount=${amount}&currency=${selectedCryptoSymbol}`, '_blank', 'noopener,noreferrer');
                return; // IMPORTANT: stop normal flow
            }

            if (this.selectedPaymentMethod.id === 'bank') {
                methodName = `Bank Transfer (SEPA)`;

                // Need to open a new withdraw form for player to initiate SEPA transfer
                window.location.href = this.urls["sepa_withdraw_url"]+`?amount=${amount}`;
                //window.open(`${SEPA_WITHDRAW_URL}?amount=${amount}`, '_blank', 'noopener,noreferrer');
                return; // IMPORTANT: stop normal flow
            }

            let finalAmount = amount;

            const tx = {
                id: Date.now(),                // simple unique id
                type: 'withdraw',
                method: methodName,
                amount: amount,
                status: status,
                time: formatTimeNow()
            };

            // add to Recent Activity
            this.addTransactionToRecentActivity(tx);

            // Optional: update balances UI (increment Pending or Total depending on status)
            try {
                if (status === 'pending') {
                    const pendingEl = document.getElementById('balancePending');
                    if (pendingEl) {
                        const curr = Number(pendingEl.innerText.replace(/[^0-9.-]/g, '')) || 0;
                        pendingEl.innerText = `$${(curr + amount).toLocaleString()}`;
                    }
                } else {
                    const totalEl = document.getElementById('balanceTotal');
                    if (totalEl) {
                        const curr = Number(totalEl.innerText.replace(/[^0-9.-]/g, '')) || 0;
                        totalEl.innerText = `$${(curr + amount).toLocaleString()}`;
                    }
                    const availEl = document.getElementById('balanceAvailable');
                    if (availEl) {
                        const currA = Number(availEl.innerText.replace(/[^0-9.-]/g, '')) || 0;
                        availEl.innerText = `$${(currA + amount).toLocaleString()}`;
                    }
                }
            } catch (err) {
                // non-fatal if balance elements not present
                console.warn('Balance update skipped', err);
            }

            // UX: Briefly flash success or reset custom input if used
            const customInput = document.getElementById('customAmountInput');
            if (customInput) {
                customInput.value = '';
            }
        }

    updateDepositButtonState() {
        const canDeposit =
                this.isAmountValid() &&
                this.selectedPaymentMethod &&
                (
                    (this.selectedPaymentMethod.id === 'card') ||
                    (this.selectedPaymentMethod.id === 'bank') ||
                    (this.selectedPaymentMethod.id === 'crypto' && this.selectedCryptoSymbol) ||
                    (this.selectedPaymentMethod.id === 'ewallet' && this.selectedWalletProvider)
                );

            this.elements["desktopDepositBtn"].prop("disabled", !canDeposit);
            this.elements["mobileDepositBtn"].prop("disabled", !canDeposit);

    }

    updateWithdrawButtonState() {
            const canWithdraw =
                this.isWithdrawAmountValid() &&
                this.selectedPaymentMethod &&
                (
                    (this.selectedPaymentMethod.id === 'bank') ||
                    (this.selectedPaymentMethod.id === 'crypto' && this.selectedCryptoSymbol)
                );

            this.elements["desktopWithdrawBtn"].prop("disabled", !canWithdraw);
            this.elements["mobileWithdrawBtn"].prop("disabled", !canWithdraw);
        }

    enforceRecentActivityLimit() {
            const list = this.elements["recActList"];
            if (!list) return;

            const items = Array.from(list.children);

            items.forEach((item, index) => {
                if (index < this.settings["max_recent_activity_items"]) {
                    item.classList.remove('d-none');
                } else {
                    item.classList.add('d-none'); // hide overflow
                }
            });
    }

    addTransactionToRecentActivity(tx) {
        const list = this.elements["recActList"];
        if (!list) return;
        const isDeposit = tx.type === 'deposit';
        const arrow = isDeposit ? '⬇' : '⬆';
        const colorText = isDeposit ? this.settings["text-emerald"] : this.settings["text-orange"];
        const bgColorClass = isDeposit ? this.settings["text-emerald"]+' bg-opacity-10' : this.settings["text-orange"]+' bg-opacity-10';
        const item = $('<div></div>');
        item.addClass(`list-group-item d-flex justify-content-between align-items-center p-2 mb-2 rounded ${bgColorClass}`);
        item.html(`<div class="d-flex align-items-center gap-2"><div class="p-2 rounded-lg" style="min-width:40px; text-align:center; font-weight:bold; border-radius:0.5rem;">
                          <div style="font-size:1rem;">${arrow}</div></div><div><div class="d-flex align-items-center gap-2"><span class="fw-bold">${tx.method}</span>
                          ${statusBadgeHtml(tx.status)}</div><small class="text-muted">${tx.time}</small></div></div>
                          <div class="text-end"><div class="fw-bold ${colorText}">${isDeposit ? '+' : '-'}$${Number(tx.amount).toLocaleString()}</div></div>`);
        list.prepend(item);
        this.enforceRecentActivityLimit();
    }

    showEwalletOptions() {
        const box = this.elements["eWallet"];
        if (box.data("initialized")) {
            box.removeClass("d-none");
            this.elements["cryptoOptions"].addClass("d-none");
            return;
        }

        box.data("initialized", true);
        box.empty();
            this.settings.walletOptions.forEach(wallet => {
                const btn = $('<button></button>')
                // identity classes
                btn.addClass("payment-sub-option wallet-option-btn btn btn-outline-light");
                // style classes
                btn.addClass("w-100 text-start p-2 rounded mb-2");

                btn.data("wallet",wallet.toLowerCase())
                btn.html(`<div style="font-weight:700">${wallet}</div><small class="d-block text-purple">E-Wallet</small>`)
                btn.on("click", (ev) => {
                    ev.preventDefault();
                    ev.stopPropagation();
                    box.find('.payment-sub-option')
                    .removeClass('active')
                    .addClass('btn-outline-light');
                    btn.removeClass('btn-outline-light').addClass('active');
                    this.selectedWalletProvider = wallet;
                    //this.selectedPaymentMethod = {id: "ewallet", name: "E-Wallet"};
                    if(!this.settings.isWithdraw) {
                        this.updateDepositButtonState();
                    } else {
                        this.updateWithdrawButtonState();
                    }
                });
                box.append(btn);
                this.elements["eWallet"].append(btn);
            });
            // UI show/hide
            // document.getElementById("cryptoOptions").classList.add("d-none");
            // container.classList.remove("d-none");
            box.removeClass("d-none");
            this.elements["cryptoOptions"].addClass("d-none")
    }

    showCryptoOptions() {
            const cryptoBox = this.elements["cryptoOptions"]
            if (!cryptoBox || cryptoBox.data("initialized")) {
                cryptoBox.removeClass("d-none");
                this.elements["eWallet"].addClass("d-none");
                return;
            }

            cryptoBox.data("initialized", true);

            // Clear & rebuild container
            const inner = this.elements.cryptoOptions.find('.crypto-inner');
            //cryptoBox.innerHTML = `<div class="d-flex flex-wrap gap-2" id="cryptoOptions"></div><div class="mt-2 text-purple small">Select a cryptocurrency to use for this deposit</div>`
            const btnContainer = $('<div class="d-flex flex-wrap gap-2"></div>');
            inner.append(btnContainer);

            this.settings["cryptos"].forEach(c => {
                const b = $('<button></button>')
                b.type = 'button'
                b.addClass('payment-sub-option crypto-option-btn btn btn-outline-light p-2')
                b.data('symbol',c.symbol)
                b.html(`<div style="font-weight:700">${c.symbol}</div><small class="d-block text-purple">${c.label}</small>`);
                // submenu click handler
                b.on('click', (ev) => {
                    ev.preventDefault();
                    ev.stopPropagation();
                    // update selection
                    this.selectedCryptoSymbol = c.symbol;
                    // toggle active styles
                    btnContainer.find('.payment-sub-option')
                    .removeClass('active')
                    .addClass('btn-outline-light');
                    b.removeClass('btn-outline-light').addClass('active');

                    // make sure parent 'crypto' is selected
                    //this.selectedPaymentMethod = {id: "crypto", name: "Cryptocurrency"};
                    $('.payment-method-btn').removeClass('active')
                    $(`.payment-method-btn[data-id="crypto"]`).addClass('active')

                    if(!this.settings.isWithdraw) {
                        this.updateDepositButtonState();
                    } else {
                        this.updateWithdrawButtonState();
                    }
                });
                btnContainer.append(b);
            });

            // show UI
            cryptoBox.removeClass("d-none");
            this.elements["eWallet"].addClass("d-none")
        }

    selectAmount(amount) {
        this.selectedAmount = amount;
        this.elements["selAmnDis"].text(this.selectedAmount.toLocaleString())
        if (this.settings.isWithdraw === true) {
            this.withdrawAmount = amount;
            this.elements["withdrawDisplay"].text(`$${this.withdrawAmount.toLocaleString()}`);
            this.elements["desktopWithdrawBtn"].text(`▬ Withdraw $${this.withdrawAmount.toLocaleString()} →`);
        } else {
            this.quickDepAmount = amount;
            this.elements["qckDepDis"].text(`$${this.quickDepAmount.toLocaleString()}`)
            this.elements["qckDepBtn"].text(`➕ Deposit $${this.quickDepAmount.toLocaleString()} →`);
        }
        // Update active button
        // document.querySelectorAll('#quickAmountButtons button').forEach(btn => btn.classList.remove('active'));
        this.elements["qckAmnBtns"].removeClass("active")
        this.elements["qckAmnBtns"].each(function () {
            const btn = this;
            if (parseInt(btn.innerText.replace('$', '')) === amount) $(btn).addClass('quick-deposit-btn', 'active');
        });

        if (!this.settings.isWithdraw) {
            // update deposit enabled state
            this.updateDepositButtonState();
        } else {
            this.updateWithdrawButtonState();
        }
    }

    bind_events() {
        $('.payment-method-btn').on('click', (event) => {
                // 🔑 IGNORE submenu button clicks entirely
            if (
                $(event.target).closest('.crypto-option-btn').length ||
                $(event.target).closest('.wallet-option-btn').length
            ) {
                return;
            }
            const $btn = $(event.currentTarget)
            const id = $btn.data("id");
            const prev_payment_method_selected = this.selectedPaymentMethod?.id
            this.selectedPaymentMethod = {id, name: this.texts["PAYMENT_METHOD_NAMES"][id]};

            if (prev_payment_method_selected !== id) {
                // reset submenu selection state
                this.selectedCryptoSymbol = null;
                this.selectedWalletProvider = null;

                this.clearCryptoSelectionUI();
                this.clearEwalletSelectionUI();
            }

            // active visual state
            $('.payment-method-btn[data-id]').removeClass('active');
            $btn.addClass('active');

            // ALWAYS reset submenus first
            this.elements.cryptoOptions.addClass('d-none');
            this.elements.eWallet.addClass('d-none');

            // === CRYPTO ===
            if (id === "crypto") {
                this.elements.eWallet.addClass('d-none')
                this.showCryptoOptions();
            }

            // === E-WALLET ===
            if (id === "ewallet") {
                this.elements.cryptoOptions.addClass('d-none')
                this.showEwalletOptions();
            }
            // console.log("Button",btn)
            if (!this.settings.isWithdraw) {
                this.updateDepositButtonState();
            } else {
                this.updateWithdrawButtonState();
            }
        });
        this.elements["customAmountInput"].on('focus',this.handleCustomAmountInteraction.bind(this))
        this.elements["customAmountInput"].on('click',this.handleCustomAmountInteraction.bind(this))
        this.elements["customAmountInput"].on('input',this.handleCustomAmountInteraction.bind(this))
        this.elements["qckAmnBtns"].on('click',(event)=>{
            const btn = $(event.currentTarget);

            this.clearQuickAmountSelection();

            btn.addClass('active').removeClass('btn-outline-light');

            const amount = this.normalizeAmount(btn.text());
            this.selectAmount(amount);
        });
        this.elements["qckDepBtn"].on("click",this.handleDepositClick.bind(this))
        this.elements["mobileDepositBtn"].on("click",this.handleDepositClick.bind(this))
        this.elements["desktopWithdrawBtn"].on("click",this.handleWithdrawClick.bind(this))
        this.elements["mobileWithdrawBtn"].on("click",this.handleWithdrawClick.bind(this))
        if (this.elements["viewFullHistoryBtn"] && this.elements["recentActivityList"]) {
                this.elements["viewFullHistoryBtn"].on('click', () => {
                // Clear previous modal content
                this.elements["fullHistoryContent"].empty();

                // Clone all existing activity items
                const items = this.elements["recentActivityList"].children();

                if (!items.length) {
                     this.elements["fullHistoryContent"].html(
                        '<p class="text-muted text-center">No transactions available.</p>');
                } else {
                    [...items].forEach(item => {
                        const clone = item.cloneNode(true);

                        // 🔑 IMPORTANT: ensure modal shows ALL items
                        clone.classList.remove('d-none');

                        clone.classList.add('mb-2');
                        this.elements["fullHistoryContent"].append(clone);
                    });
                }

                // Show modal
                const modal = new bootstrap.Modal(
                    this.elements['fullHistoryModal'][0]
                );
                modal.show();
                });
        }
        if (this.elements["alertBellBtn"] && this.elements["alertsModal"]) {

            this.elements["alertBellBtn"].on('click', () => {
                const modal = new bootstrap.Modal(this.elements["alertsModal"][0]);
                modal.show();
            });
        }
        $('#helpButton').on('click', function () {
            window.open('/slv/faq', '_blank', 'noopener,noreferrer');
        });
        $('#backButton').on('click', function () {
            window.location.href = '/game/play';
        });
    }

    isAmountValid() {
        // quickDepositAmount already maintained by your code
        const a = Number(this.quickDepAmount);
        return !isNaN(a) && a > 0;
    }

    isWithdrawAmountValid() {
        const a = Number(this.withdrawAmount);
        return !isNaN(a) && a > 0;
    }

    normalizeAmount(value) {
            const cleaned = value.replace(/[^\d]/g, '');
            return cleaned ? Number(cleaned) : 0;
    }

    updateDepositUI(amount) {
            const value = Number(amount);

            // 🔑 SINGLE SOURCE OF TRUTH
            this.quickDepAmount = (!value || isNaN(value) || value <= 0) ? 0 : value;
            const formatted = `$${this.quickDepAmount.toLocaleString()}`;

            this.elements["depositDisplay"][0].innerHTML = `➕ Deposit ${formatted} →`;
            this.elements["qckDepDis"][0].innerHTML = formatted
            if (this.elements["desktopDepositBtn"]) {
                this.elements["desktopDepositBtn"][0].innerHTML = `➕ Deposit ${formatted} →`;
            }

            if (this.elements["mobileDepositBtn"]) {
                this.elements["mobileDepositBtn"][0].innerHTML = `➕ Deposit ${formatted} →`;
            }

            // 🔑 ensure enable/disable is recalculated
            this.updateDepositButtonState();
    }

    updateWithdrawUI(amount) {
            const value = Number(amount);

            // 🔑 SINGLE SOURCE OF TRUTH
            this.withdrawAmount = (!value || isNaN(value) || value <= 0) ? 0 : value;

            const formatted = `$${this.withdrawAmount.toLocaleString()}`;

            this.elements["withdrawDisplay"].text(formatted);

            if (this.elements["desktopWithdrawBtn"]) {
                this.elements["desktopWithdrawBtn"].text(`▬ Withdraw ${formatted} →`);
            }

            if (this.elements["mobileWithdrawBtn"]) {
                this.elements["mobileWithdrawBtn"].text(`▬ Withdraw ${formatted} →`);
            }

            // 🔑 ensure enable/disable is recalculated
            this.updateWithdrawButtonState();
        }

    clearQuickAmountSelection() {
            this.elements["qckAmnBtns"].removeClass('active')
            this.elements["qckAmnBtns"].addClass('btn-outline-light')

    }

    handleCustomAmountInteraction() {
            this.clearQuickAmountSelection();

            const value = this.normalizeAmount(this.elements["customAmountInput"].val());
            if(!this.settings.isWithdraw) {
                this.updateDepositUI(value);
            } else {
                this.updateWithdrawUI(value);
            }
    }

    clearCryptoSelectionUI() {
        this.elements.cryptoOptions
            .find('.payment-sub-option')
            .removeClass('active')
            .addClass('btn-outline-light');
    }

    clearEwalletSelectionUI() {
        this.elements.eWallet
            .find('.payment-sub-option')
            .removeClass('active')
            .addClass('btn-outline-light');
    }

    updateBellBadge() {
        this.elements["alertBell"] = $(this.settings["alertBell"])
        const unread = this.elements["alertBell"].length;
        this.elements["alertBdg"] = $(this.settings["alertBdg"])
        if (unread === 0 && this.elements["alertBdg"].length) {
            this.elements["alertBdg"].remove();
        }
    }

    constructor(settings,urls) {
        super(settings, urls)
        $.extend(this.settings, settings);
        $.extend(this.urls, urls);
        console.log("Starting Cashier V2 App");
        this.elements["selAmnDis"] = $(this.settings["selAmnDis"])
        this.elements["qckDepDis"] = $(this.settings["qckDepDis"])
        this.elements["qckDepBtn"] = $(this.settings["qckDepBtn"])
        this.elements["qckAmnBtns"] = $(this.settings["qckAmnBtns"])
        this.elements["recActList"] = $(this.settings["recActList"])
        this.elements["payMtdBttns"] = $(this.settings["payMtdBttns"])
        this.elements["mrkRedBttn"] = $(this.settings["mrkRedBttn"])
        this.elements["claimBonusBtn"] = $(this.settings["claimBonusButton"])
        // this.elements["alertBell"] = $(this.settings["alertBell"])
        this.elements["alertBellBtn"] = $(this.settings["alertBellBtn"])
        this.elements["customAmountInput"] = $(this.settings["customAmountInput"])
        this.elements["depositDisplay"] = $(this.settings["depositDisplay"])
        this.elements["desktopDepositBtn"] =   $(this.settings["desktopDepositBtn"])
        this.elements["mobileDepositBtn"] =  $(this.settings["mobileDepositBtn"])
        this.elements["eWallet"] = $(this.settings["eWallet"])
        this.elements["cryptoOptions"] = $(this.settings["cryptoOptions"])
        this.elements["cryptoOptionsButtons"] = $(this.settings["cryptoOptionsButtons"])
        this.elements["viewFullHistoryBtn"] = $(this.settings["viewFullHistoryBtn"])
        this.elements["recentActivityList"] = $(this.settings["recentActivityList"])
        this.elements["fullHistoryContent"] = $(this.settings["fullHistoryContent"])
        this.elements["fullHistoryModal"] = $(this.settings["fullHistoryModal"])
        this.elements["alertsModal"] = $(this.settings["alertsModal"])
        this.elements["desktopWithdrawBtn"] = $(this.settings["desktopWithdrawBtn"])
        this.elements["mobileWithdrawBtn"] = $(this.settings["mobileWithdrawBtn"])
        this.elements["withdrawDisplay"] = $(this.settings["withdrawDisplay"])
        this.elements["mrkRedBttn"].on("click", async function (event) {
            event.preventDefault();
            event.stopPropagation();
            const btn = event.currentTarget;
            const alertId = btn.dataset.alertId;
            try {
                const response = await fetch(this.urls["read_message"], {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": this.settings["csrf_token"],
                    },
                    body: new URLSearchParams({ alert_id: alertId }),
                });
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const result = await response.json();
                if (result.success) {
                    // Remove unread styling
                    const alertItem = btn.closest(".alert-item");
                    if (alertItem) {
                        alertItem.classList.remove("unread");
                    }
                    // Remove button
                    btn.remove();
                    // Update bell badge if needed
                    this.updateBellBadge();
                }
            } catch (err) {
                console.error("Failed to mark alert as read:", err);
            }
        }.bind(this));

        let bonusUsed = false;
        let bonusAvailable = false
        if (!this.settings.bonusActive) {
            // INACTIVE ALWAYS WINS
            this.elements["claimBonusBtn"].disabled = true;
            this.elements["claimBonusBtn"].attr("aria-disabled", "true");
            this.elements["claimBonusBtn"].addClass("bonus-claimed");
            this.elements["claimBonusBtn"].html("🎁 Bonus Unavailable");
            bonusUsed = true;

        } else if (this.settings.bonusClaimed) {
            this.elements["claimBonusBtn"].addClass("bonus-claimed");
            this.elements["claimBonusBtn"].disabled = true;
            this.elements["claimBonusBtn"].attr("aria-disabled", "true");
            this.elements["claimBonusBtn"].html("🎁 Bonus Applied");
            bonusUsed = true;
        } else if (this.settings.bonusActive) {
            bonusAvailable = true;
        }
        this.elements["claimBonusBtn"].on("click", async function(){
            if (!bonusAvailable || bonusUsed) return;

                try {
                    const response = await fetch(this.urls["claim_bonus"], {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": this.settings["csrf_token"]
                        },
                        credentials: "same-origin"
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    const contentType = response.headers.get("content-type") || "";
                    if (!contentType.includes("application/json")) {
                        throw new Error("Non-JSON response received");
                    }

                    const data = await response.json();

                    if (data.success) {
                        bonusAvailable = true;
                        bonusUsed = true;

                        this.elements["claimBonusBtn"].addClass("bonus-claimed");
                        this.elements["claimBonusBtn"].prop("disabled", true).attr("aria-disabled", "true")
                        this.elements["claimBonusBtn"].html("🎁 Bonus Applied");
                    } else {
                        alert(data.message || "Unable to claim bonus.");
                    }

                } catch (err) {
                    console.error("Bonus claim failed:", err);
                    alert("Network error. Please try again.");
                }
        }.bind(this));
        this.bind_events()
    }

}