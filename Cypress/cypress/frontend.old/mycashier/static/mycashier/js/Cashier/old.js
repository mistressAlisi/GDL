  {#function getCSRFToken() {#}
        {#    return document.querySelector('[name=csrfmiddlewaretoken]').value;#}
        {#}#}
        {##}
        {#function updateBellBadge() {#}
        {#    const unread = document.querySelectorAll(".alert-item.unread").length;#}
        {#    const badge = document.getElementById('alertBadge');#}
        {##}
        {#    if (unread === 0 && badge) {#}
        {#        badge.remove();#}
        {#    }#}
        {#}#}

        document.querySelectorAll(".mark-read-btn").forEach(btn => {
            btn.addEventListener("click", async (e) => {
                const alertId = btn.dataset.alertId;

                const response = await fetch("{% url 'read_message' %}", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": "{{ csrf_token }}",
                    },
                    body: new URLSearchParams({alert_id: alertId}),
                });

                const result = await response.json();

                if (result.success) {
                    // Remove unread styling
                    const alertItem = btn.closest(".alert-item");
                    alertItem.classList.remove("unread");

                    // Remove button
                    btn.remove();

                    // Update bell badge if needed
                    updateBellBadge();
                }
            });
        });

        const bonusAlreadyClaimed = {{ bonusEngine.is_user_claimed|yesno:"true,false" }};

        const backBtn = document.getElementById('backButton');
        if (backBtn) {
            backBtn.addEventListener('click', () => window.history.back());
        }

        const helpButton = document.getElementById('helpButton');

        if (helpButton) {
            helpButton.addEventListener('click', () => {
                window.open('https://sportslotto.vip/slv/faq', '_blank', 'noopener,noreferrer');
            });
        }

        const CRYPTO_DEPOSIT_URL = "{% url 'deposit_start' 'cashier.providers.ionBlock' %}";
        const APPLE_WALLET_DEPOSIT_URL = "{% url 'deposit_start' 'apl' %}";
        const PAYPAL_WALLET_DEPOSIT_URL = "{% url 'deposit_start' 'pyl' %}";
        const CARD_WALLET_DEPOSIT_URL = "{% url 'deposit_start' 'crd' %}";

        // Bonus state
        let bonusAvailable = false;  // becomes true when user clicks "Claim Bonus"
        let bonusUsed = false;       // prevents re-use after deposit

        const claimBonusBtn = document.getElementById("claimBonusButton");

        // Initialize state from Django
        const bonusIsActive = {{ bonusEngine.active|yesno:"true,false" }};

        if (!bonusIsActive) {
            // INACTIVE ALWAYS WINS
            claimBonusBtn.disabled = true;
            claimBonusBtn.setAttribute("aria-disabled", "true");
            claimBonusBtn.classList.add("bonus-claimed");
            claimBonusBtn.innerHTML = "🎁 Bonus Unavailable";
            bonusUsed = true;

        } else if (bonusAlreadyClaimed) {
            claimBonusBtn.classList.add("bonus-claimed");
            claimBonusBtn.disabled = true;
            claimBonusBtn.setAttribute("aria-disabled", "true");
            claimBonusBtn.innerHTML = "🎁 Bonus Applied";
            bonusUsed = true;
        }

        claimBonusBtn.addEventListener("click", async () => {
            if (!bonusIsActive || bonusUsed) return;

            try {
                const response = await fetch("{% url 'claim_bonus' %}", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json"
                    }
                });

                const data = await response.json();

                if (data.success) {
                    bonusAvailable = true;
                    bonusUsed = true;

                    claimBonusBtn.classList.add("bonus-claimed");
                    claimBonusBtn.disabled = true;
                    claimBonusBtn.innerHTML = "🎁 Bonus Applied";
                } else {
                    alert(data.message || "Unable to claim bonus.");
                }

            } catch (err) {
                console.error("Bonus claim failed:", err);
                alert("Network error. Please try again.");
            }
        });

        let selectedAmount = 50;
        let quickDepositAmount = 100;

        function selectAmount(amount) {
            selectedAmount = amount;
            document.getElementById('selectedAmountDisplay').innerText = selectedAmount.toLocaleString();
            quickDepositAmount = amount;
            document.getElementById('quickDepositDisplay').innerText = `$${quickDepositAmount.toLocaleString()}`;
            document.getElementById('quickDepositBtn').innerText = `➕ Deposit $${quickDepositAmount.toLocaleString()} →`;

            // Update active button
            document.querySelectorAll('#quickAmountButtons button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('#quickAmountButtons button').forEach(btn => {
                if (parseInt(btn.innerText.replace('$', '')) === amount) btn.classList.add('quick-deposit-btn', 'active');
            });

            // update deposit enabled state
            updateDepositButtonState();
        }

        document.getElementById('customAmountInput').addEventListener('input', function (e) {
            let val = e.target.value.replace(/[^0-9]/g, '');
            e.target.value = val;
            if (val) {
                quickDepositAmount = parseInt(val);
                document.getElementById('quickDepositDisplay').innerText = `$${quickDepositAmount.toLocaleString()}`;
                document.getElementById('quickDepositBtn').innerText = `➕ Deposit $${quickDepositAmount.toLocaleString()} →`;
            } else {
                quickDepositAmount = 0;
                document.getElementById('quickDepositDisplay').innerText = `$0`;
                document.getElementById('quickDepositBtn').innerText = `➕ Deposit $0 →`;
            }

            // update deposit buttons whenever amount changes
            updateDepositButtonState();
        });

        // Quick amount buttons click
        document.querySelectorAll('#quickAmountButtons button').forEach(btn => {
            btn.addEventListener('click', function () {
                selectAmount(parseInt(btn.innerText.replace('$', '')));
            });
        });

        // ---------- Begin: Recent Activity wiring ----------

        const MAX_RECENT_ACTIVITY_ITEMS = 5;

        function enforceRecentActivityLimit() {
            const list = document.getElementById('recentActivityList');
            if (!list) return;

            const items = Array.from(list.children);

            items.forEach((item, index) => {
                if (index < MAX_RECENT_ACTIVITY_ITEMS) {
                    item.classList.remove('d-none');
                } else {
                    item.classList.add('d-none'); // hide overflow
                }
            });
        }


        // friendly names for payment method ids
        const PAYMENT_METHOD_NAMES = {
            card: 'Credit/Debit Card',
            crypto: 'Cryptocurrency',
            ewallet: 'E-Wallet',
            bank: 'Bank Transfer'
        };

        // state
        let selectedPaymentMethod = null; // { id: 'card', name: 'Credit/Debit Card' }
        let selectedCryptoSymbol = null;  // optional, if you implement cryptoOptions UI

        // helper: format "time ago" (simple)
        function formatTimeNow() {
            const d = new Date();
            // simple timestamp; you can replace with relative time logic
            return d.toLocaleString();
        }

        // helper: create badge element HTML
        function statusBadgeHtml(status) {
            if (status === 'completed') {
                return `<span class="badge bg-success text-dark small">✔ ${status}</span>`;
            } else {
                return `<span class="badge bg-warning text-dark small">⌛ ${status}</span>`;
            }
        }

        // function to actually render/prepend a transaction into the Recent Activity list
        function addTransactionToRecentActivity(tx) {
            const list = document.getElementById('recentActivityList');
            if (!list) return;

            // Decide color class and arrow for deposit/withdrawal
            const isDeposit = tx.type === 'deposit';
            const arrow = isDeposit ? '⬇' : '⬆';
            const colorText = isDeposit ? 'text-emerald-400' : 'text-orange-400';
            const bgColorClass = isDeposit ? 'bg-emerald-500 bg-opacity-10' : 'bg-orange-500 bg-opacity-10';

            // Build DOM element
            const item = document.createElement('div');
            item.className = `list-group-item d-flex justify-content-between align-items-center p-2 mb-2 rounded ${bgColorClass}`;
            item.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <div class="p-2 rounded-lg" style="min-width:40px; text-align:center; font-weight:bold; border-radius:0.5rem;">
        <div style="font-size:1rem;">${arrow}</div>
      </div>
      <div>
        <div class="d-flex align-items-center gap-2">
          <span class="fw-bold">${tx.method}</span>
          ${statusBadgeHtml(tx.status)}
        </div>
        <small class="text-muted">${tx.time}</small>
      </div>
    </div>
    <div class="text-end">
      <div class="fw-bold ${colorText}">${isDeposit ? '+' : '-'}$${Number(tx.amount).toLocaleString()}</div>
    </div>
  `;

            // Prepend newest to top
            if (list.firstChild) {
                list.insertBefore(item, list.firstChild);
            } else {
                list.appendChild(item);
            }

            // Optionally keep the recent-activity container's scroll at top (if you prefer)
            // list.scrollTop = 0;
            // Enforce display limit after adding new transaction
            enforceRecentActivityLimit();
        }

        // ===== Wallet options predefined list =====
        const walletOptions = ["PayPal", "Apple Pay"];
        let selectedWalletProvider = null; // NEW

        // ===== Helper function to render E-Wallet submenu =====
        function showEwalletOptions() {
            const container = document.getElementById("ewalletOptions");
            container.innerHTML = "";

            walletOptions.forEach(wallet => {
                const btn = document.createElement("button");
                btn.className = "crypto-btn wallet-btn w-100 text-start p-2 rounded mb-2";
                btn.dataset.wallet = wallet.toLowerCase();
                btn.innerHTML = `
      <div style="font-weight:700">${wallet}</div>
      <small class="d-block text-purple">E-Wallet</small>
    `;

                btn.addEventListener("click", (ev) => {
                    ev.stopPropagation();

                    // remove previous active
                    container.querySelectorAll(".wallet-btn").forEach(x => x.classList.remove("active"));

                    // activate this one
                    btn.classList.add("active");

                    // store selection
                    selectedWalletProvider = wallet;

                    // ensure correct parent selection
                    selectedPaymentMethod = {id: "ewallet", name: "E-Wallet"};

                    // enable deposit using same logic as crypto
                    updateDepositButtonState();
                });

                container.appendChild(btn);
            });

            // UI show/hide
            document.getElementById("cryptoOptions").classList.add("d-none");
            container.classList.remove("d-none");
        }

        // ===== Helper function to render Crypto submenu =====
        function showCryptoOptions() {
            const cryptoBox = document.getElementById('cryptoOptions');
            if (!cryptoBox) return;

            // crypto token data
            const cryptos = [
                {symbol: 'BTC', label: 'Bitcoin'},
                {symbol: 'ETH', label: 'Ethereum'},
                {symbol: 'USDT', label: 'Tether'},
                {symbol: 'LTC', label: 'Litecoin'}
            ];

            // Clear & rebuild container
            cryptoBox.innerHTML = `
    <div class="d-flex flex-wrap gap-2" id="cryptoOptionsButtons"></div>
    <div class="mt-2 text-purple small">Select a cryptocurrency to use for this deposit</div>
  `;

            const btnContainer = document.getElementById('cryptoOptionsButtons');

            cryptos.forEach(c => {
                const b = document.createElement('button');
                b.type = 'button';
                b.className = 'crypto-btn';
                b.dataset.symbol = c.symbol;
                b.innerHTML = `
      <div style="font-weight:700">${c.symbol}</div>
      <small class="d-block text-purple">${c.label}</small>
    `;

                btnContainer.appendChild(b);

                // submenu click handler
                b.addEventListener('click', (ev) => {
                    ev.stopPropagation();

                    // update selection
                    selectedCryptoSymbol = c.symbol;

                    // toggle active styles
                    btnContainer.querySelectorAll('.crypto-btn').forEach(x => x.classList.remove('active'));
                    b.classList.add('active');

                    // make sure parent 'crypto' is selected
                    selectedPaymentMethod = {id: "crypto", name: "Cryptocurrency"};
                    document.querySelectorAll('.payment-method-btn').forEach(p => {
                        p.classList.toggle('active', p.dataset.id === "crypto");
                    });

                    updateDepositButtonState();
                });
            });

            // show UI
            cryptoBox.classList.remove("d-none");
            document.getElementById("ewalletOptions").classList.add("d-none");
        }

        // Payment method selection wiring
        document.querySelectorAll('.payment-method-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                selectedPaymentMethod = {id, name: PAYMENT_METHOD_NAMES[id]};

                // reset submenu selection state
                selectedCryptoSymbol = null;
                selectedWalletProvider = null;

                // active visual state
                document.querySelectorAll('.payment-method-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // hide both submenu containers
                const cryptoBox = document.getElementById('cryptoOptions');
                const ewalletBox = document.getElementById('ewalletOptions');
                cryptoBox?.classList.add("d-none");
                ewalletBox?.classList.add("d-none");

                // === CRYPTO ===
                if (id === "crypto") {
                    showCryptoOptions();
                }

                // === E-WALLET ===
                if (id === "ewallet") {
                    showEwalletOptions();
                }

                updateDepositButtonState();
            });
        });

        // ---------- Deposit enable/disable logic ----------

        // Ensure the buttons start disabled
        const quickAmountButtons = document.querySelectorAll(
            '#quickAmountButtons button'
        );
        const customAmountInput = document.getElementById('customAmountInput');
        const depositDisplay = document.getElementById('quickDepositDisplay');
        const desktopDepositBtn = document.getElementById('quickDepositBtn');
        const mobileDepositBtn = document.getElementById('depositBtn');

        /* -----------------------------
           Helpers
        -------------------------------- */
        function clearQuickAmountSelection() {
            quickAmountButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.classList.add('btn-outline-light');
            });
        }

        function normalizeAmount(value) {
            const cleaned = value.replace(/[^\d]/g, '');
            return cleaned ? Number(cleaned) : 0;
        }

        function updateDepositUI(amount) {
            const value = Number(amount);

            // 🔑 SINGLE SOURCE OF TRUTH
            quickDepositAmount = (!value || isNaN(value) || value <= 0) ? 0 : value;

            const formatted = `$${quickDepositAmount.toLocaleString()}`;

            depositDisplay.textContent = formatted;

            if (desktopDepositBtn) {
                desktopDepositBtn.textContent = `➕ Deposit ${formatted} →`;
            }

            if (mobileDepositBtn) {
                mobileDepositBtn.textContent = `➕ Deposit ${formatted} →`;
            }

            // 🔑 ensure enable/disable is recalculated
            updateDepositButtonState();
        }

        /* -----------------------------
           Custom input interactions
        -------------------------------- */
        function handleCustomAmountInteraction() {
            clearQuickAmountSelection();

            const value = normalizeAmount(customAmountInput.value);
            updateDepositUI(value);
        }

        customAmountInput.addEventListener('focus', handleCustomAmountInteraction);
        customAmountInput.addEventListener('click', handleCustomAmountInteraction);

        customAmountInput.addEventListener('input', handleCustomAmountInteraction);

        /* -----------------------------
           Preset amount buttons
        -------------------------------- */
        quickAmountButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                clearQuickAmountSelection();

                btn.classList.add('active');
                btn.classList.remove('btn-outline-light');

                const amount = normalizeAmount(btn.textContent);
                customAmountInput.value = '';
                updateDepositUI(amount);
            });
        });

        // Helper: returns true if amount is valid (>0)
        function isAmountValid() {
            // quickDepositAmount already maintained by your code
            const a = Number(quickDepositAmount);
            return !isNaN(a) && a > 0;
        }

        // Centralized updater
        function updateDepositButtonState() {
            const canDeposit =
                isAmountValid() &&
                selectedPaymentMethod &&
                (
                    (selectedPaymentMethod.id === 'card') ||
                    (selectedPaymentMethod.id === 'bank') ||
                    (selectedPaymentMethod.id === 'crypto' && selectedCryptoSymbol) ||
                    (selectedPaymentMethod.id === 'ewallet' && selectedWalletProvider)
                );

            if (desktopDepositBtn) {
                desktopDepositBtn.disabled = !canDeposit;
                desktopDepositBtn.setAttribute('aria-disabled', (!canDeposit).toString());
            }

            if (mobileDepositBtn) {
                mobileDepositBtn.disabled = !canDeposit;
                mobileDepositBtn.setAttribute('aria-disabled', (!canDeposit).toString());
            }
        }


        // Call once on page load to set initial state
        updateDepositButtonState();
        // Apply limit to transactions loaded from Django template
        enforceRecentActivityLimit();

        let depositInProgress = false;

        // Deposit button handlers (desktop Quick Deposit and mobile bottom)
        function handleDepositClick() {
            if (depositInProgress) {
                //e.preventDefault();
                return;
            }

            depositInProgress = true;
            qBtn.disabled = true;
            qBtn.classList.add("disabled");
            qBtn.style.cursor = "not-allowed";
            qBtn.innerHTML = "⏳ Processing Deposit…";
            mobileDepositBtn.disabled = true;
            mobileDepositBtn.classList.add("disabled");
            mobileDepositBtn.style.cursor = "not-allowed";
            mobileDepositBtn.innerHTML = "⏳ Processing Deposit…";

            // Auto-reset after 5 seconds
            resetTimer = setTimeout(() => {
                depositInProgress = false;
                qBtn.disabled = false;
                qBtn.classList.remove("disabled");
                qBtn.style.cursor = "";
                qBtn.innerHTML = `➕ Deposit $${quickDepositAmount.toLocaleString()} →`;
                mobileDepositBtn.disabled = false;
                mobileDepositBtn.classList.remove("disabled");
                mobileDepositBtn.style.cursor = "";
                mobileDepositBtn.innerHTML = `➕ Deposit $${quickDepositAmount.toLocaleString()} →`;
            }, 5000);

            // Use quickDepositAmount (kept up-to-date by existing code) as amount
            const amount = Number(quickDepositAmount);
            if (!amount || isNaN(amount) || amount <= 0) {
                alert('Please enter a valid deposit amount.');
                return;
            }

            if (!selectedPaymentMethod) {
                alert('Please select a payment method before depositing.');
                return;
            }

            // determine status: bank -> pending, others -> completed
            const status = selectedPaymentMethod.id === 'bank' ? 'pending' : 'completed';

            // construct friendly method name — if crypto and coin chosen, include coin
            let methodName = selectedPaymentMethod.name;
            if (selectedPaymentMethod.id === 'crypto' && selectedCryptoSymbol) {
                methodName = `${selectedCryptoSymbol} (Crypto)`;
            }

            // 🚀 REDIRECT FOR CRYPTO DEPOSITS
            if (selectedPaymentMethod.id === 'crypto' && selectedCryptoSymbol) {
                // Optional: persist amount + coin if needed later
                //sessionStorage.setItem('depositAmount', amount);
                //sessionStorage.setItem('depositCrypto', selectedCryptoSymbol);

                window.location.href = `${CRYPTO_DEPOSIT_URL}?amount=${amount}&currency=${selectedCryptoSymbol}`;
                //window.open(`${CRYPTO_DEPOSIT_URL}?amount=${amount}&currency=${selectedCryptoSymbol}`, '_blank', 'noopener,noreferrer');
                return; // IMPORTANT: stop normal flow
            }

            if (selectedPaymentMethod.id === 'ewallet' && selectedWalletProvider) {
                methodName = `${selectedWalletProvider} (E-Wallet)`;

                if (selectedWalletProvider === 'Apple Pay') {
                    //window.location.href = `${APPLE_WALLET_DEPOSIT_URL}?amount=${amount}`;
                    window.open(`${APPLE_WALLET_DEPOSIT_URL}?amount=${amount}`, '_blank', 'noopener,noreferrer');
                }
                else if (selectedWalletProvider === 'PayPal') {
                    //window.location.href = `${PAYPAL_WALLET_DEPOSIT_URL}?amount=${amount}`;
                    window.open(`${PAYPAL_WALLET_DEPOSIT_URL}?amount=${amount}`, '_blank', 'noopener,noreferrer');
                }
                return; // IMPORTANT: stop normal flow
            }

            if (selectedPaymentMethod.id === 'card') {
                //window.location.href = `${CARD_WALLET_DEPOSIT_URL}?amount=${amount}`;
                window.open(`${CARD_WALLET_DEPOSIT_URL}?amount=${amount}`, '_blank', 'noopener,noreferrer');
                return;
            }

            let finalAmount = amount;

            if (bonusAvailable && !bonusUsed) {
                // apply matching bonus up to max of $500
                const bonusAmount = Math.min(amount, 500);
                finalAmount = amount + bonusAmount;

                // lock out future use
                bonusAvailable = false;
                bonusUsed = true;

                // disable button visually
                claimBonusBtn.disabled = true;
                claimBonusBtn.style.opacity = "0.6";
                claimBonusBtn.style.cursor = "not-allowed";
                claimBonusBtn.title = "Bonus used";

                if (bonusAmount > 0) {
                    bonusName = "Bonus Match"
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
                amount: amount,
                status: status,
                time: formatTimeNow()
            };

            // add to Recent Activity
            addTransactionToRecentActivity(tx);

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

        // Attach to desktop quick deposit button
        const qBtn = document.getElementById('quickDepositBtn');
        if (qBtn) qBtn.addEventListener('click', handleDepositClick);

        // Attach to mobile deposit button
        if (mobileDepositBtn) mobileDepositBtn.addEventListener('click', handleDepositClick);

        // If you have a "View Full History" button, you can hook it here
        const viewFullBtn = document.getElementById('viewFullHistoryBtn');
        const recentActivityList = document.getElementById('recentActivityList');
        const fullHistoryContent = document.getElementById('fullHistoryContent');
        if (viewFullBtn && recentActivityList) {
            viewFullBtn.addEventListener('click', () => {
                // Clear previous modal content
                fullHistoryContent.innerHTML = '';

                // Clone all existing activity items
                const items = recentActivityList.children;

                if (!items.length) {
                    fullHistoryContent.innerHTML =
                        '<p class="text-muted text-center">No transactions available.</p>';
                } else {
                    [...items].forEach(item => {
                        const clone = item.cloneNode(true);

                        // 🔑 IMPORTANT: ensure modal shows ALL items
                        clone.classList.remove('d-none');

                        clone.classList.add('mb-2');
                        fullHistoryContent.appendChild(clone);
                    });
                }

                // Show modal
                const modal = new bootstrap.Modal(
                    document.getElementById('fullHistoryModal')
                );
                modal.show();
            });
        }

        // ---------- End: Recent Activity wiring ----------

        const alertBellBtn = document.getElementById('alertBellBtn');
        const alertsModalEl = document.getElementById('alertsModal');
        const alertBadge = document.getElementById('alertBadge');

        if (alertBellBtn && alertsModalEl) {
            alertBellBtn.addEventListener('click', () => {
                const modal = new bootstrap.Modal(alertsModalEl);
                modal.show();
            });
        }