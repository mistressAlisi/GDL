import {AbstractDashboardApp} from "/static/minerve/js/dashboards/DashboardApp/AbstractDashboardApp.js";
/**
 * Base Form Class
 * Handles common form functionality like balance counter animations
 */
export class BaseForm extends AbstractDashboardApp {
    settings = {
        "balance_prefix":""
    }
    urls = {
        "_api_prefix": "/api/v1/",
        "balance":"get/curr_balance"
    }

    /**
     * Derive API prefix from current URL path
     * e.g., /solstic.gdl/play/custom -> /api/v1/solstic.gdl/
     */
    _getApiPrefix() {
        const pathParts = window.location.pathname.split('/').filter(p => p);
        if (pathParts.length > 0) {
            return `/api/v1/${pathParts[0]}/`;
        }
        return '/api/v1/';
    }

    constructor(formId,settings,urls) {
        super(settings,urls)
        // Set dynamic API prefix based on current URL
        this.urls["_api_prefix"] = this._getApiPrefix();
        this.form = $(`#${formId}`);
        this.animateBalanceCounters();
        this.addRippleEffects();
        this.addKeyboardShortcuts();
    }

    /**
     * Animate balance counters on page load
     */
    animateBalanceCounters() {
        this.generic_api_getreq(this.urls["balance"],false,this._initializeBalanceCounters.bind(this))
    }
    _initializeBalanceCounters(res) {
        console.log("Initializing balance counters:", res);
        const prefix = this.settings.balance_prefix || '';
        this.animateCounter('#balance-amount', res.balance*1, prefix);
        this.animateCounter('#pending-amount', res.pending*1, prefix);
        this.animateCounter('#available-amount', res.available*1, prefix);
        this.animateCounter('#available-bonus', res.bonus*1, prefix);
        // Store bonus balance for use in purchase modal

    }

    /**
     * Animate a counter from 0 to target value
     */
    animateCounter(selector, targetValue, prefix = '') {
        const $element = $(selector);
        let currentValue = 0;
        const increment = targetValue / 50;
        const duration = 30;

        const timer = setInterval(() => {
            currentValue += increment;

            if (currentValue >= targetValue) {
                $element.text(`${prefix}${targetValue.toFixed(2)}`);
                clearInterval(timer);
            } else {
                $element.text(`${prefix}${currentValue.toFixed(2)}`);
            }
        }, duration);
    }

    /**
     * Add ripple effect to buttons
     */
    addRippleEffects() {
        $('.btn-gradient, .btn-outline, .sport-checkbox').on('click', function(e) {
            const $button = $(this);
            const $ripple = $('<span class="ripple"></span>');

            const diameter = Math.max($button.outerWidth(), $button.outerHeight());
            const radius = diameter / 2;

            const offset = $button.offset();
            const x = e.pageX - offset.left - radius;
            const y = e.pageY - offset.top - radius;

            $ripple.css({
                width: diameter,
                height: diameter,
                left: x + 'px',
                top: y + 'px'
            });

            $button.append($ripple);

            setTimeout(() => {
                $ripple.remove();
            }, 600);
        });
    }

    addKeyboardShortcuts() {
        $(document).on('keydown', (e) => {
            // ESC to go back
            if (e.key === 'Escape') {
                const $backBtn = $('.back-btn');
                if ($backBtn.length) {
                    window.location.href = $backBtn.attr('href');
                }
            }

            // Enter to submit form (if not in textarea)
            if (e.key === 'Enter' && !$(e.target).is('textarea')) {
                if (this.form.length) {
                    e.preventDefault();
                    this.form.submit();
                }
            }
        });
    }


    validateForm() {
        return this.form[0].checkValidity();
    }


    showError(message) {
        // Create toast notification
        const $toast = $(`
            <div class="toast-notification error">
                <i class="fa-solid fa-circle-exclamation me-2"></i>
                ${message}
            </div>
        `);

        $('body').append($toast);

        setTimeout(() => {
            $toast.addClass('show');
        }, 10);

        setTimeout(() => {
            $toast.removeClass('show');
            setTimeout(() => $toast.remove(), 300);
        }, 3000);
    }


    showSuccess(message) {
        const $toast = $(`
            <div class="toast-notification success">
                <i class="fa-solid fa-circle-check me-2"></i>
                ${message}
            </div>
        `);

        $('body').append($toast);

        setTimeout(() => {
            $toast.addClass('show');
        }, 10);

        setTimeout(() => {
            $toast.removeClass('show');
            setTimeout(() => $toast.remove(), 300);
        }, 3000);
    }
}


