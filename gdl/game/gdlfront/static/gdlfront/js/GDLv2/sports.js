import {BaseForm} from "./main.js";
export class SportForm extends BaseForm {
    constructor(formId) {
        super(formId);
        this.riskInput = $('#sport-risk-amount');
        this.ticketCountInput = $('#sport-ticket-count');
        this.possibleReturnDisplay = $('#sport-possible-return');

        this.bindEvents();
        this.calculateReturn();
    }

    bindEvents() {
        // Real-time calculation on risk amount change
        this.riskInput.on('input', () => {
            this.calculateReturn();
        });

        // Add smooth transition on focus
        this.riskInput.on('focus', function() {
            $(this).parent('.input-container').addClass('focused');
        }).on('blur', function() {
            $(this).parent('.input-container').removeClass('focused');
        });

        this.ticketCountInput.on('focus', function() {
            $(this).parent('.input-container').addClass('focused');
        }).on('blur', function() {
            $(this).parent('.input-container').removeClass('focused');
        });

        // Form submission
        this.form.on('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showError('Please fill in all required fields correctly.');
            }
        });
    }

    calculateReturn() {
        const risk = parseFloat(this.riskInput.val()) || 0;
        const possibleReturn = risk * 20; // 20 to 1 odds (consistent across all sports)

        this.possibleReturnDisplay.text(`$${possibleReturn.toFixed(2)}`);

        // Add animation effect
        this.possibleReturnDisplay.addClass('pulse-animation');
        setTimeout(() => {
            this.possibleReturnDisplay.removeClass('pulse-animation');
        }, 300);
    }
}