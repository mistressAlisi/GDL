import { AbstractApp } from "/static/minerve/js/core/AbstractApp.js";

export class ThemeSwitcherApp extends AbstractApp {
    settings = {
        themeBtn: "#theme-btn",
        themeModal: "#theme-modal",
        themeOption: ".theme-option",
        icon: "#site-logo", // header logo
        defaultTheme: "purple",
        defaultVariant: 0,
        logoDir: "/get/logo/", // updated folder
        applyThemeClassSelector: ".navbar, .nav-link, a, table, .modal-content, input, select, textarea, .form-control, .form-select, .form-check-input, .form-check-label, .input-group, .input-group-text, label, fieldset, legend",
        gameCardClass: ".gdl-ticket-card",
    };

    elements = {};
    currentTheme = false;
    currentVariant = false;

    applyTheme(theme, variant = 0) {
        this.currentTheme = theme;
        this.currentVariant = variant;

        // Update tickets
        $(this.settings.gameCardClass).each((i, item) => {
            this._set_ticket_theme($(item), theme, variant);
        });

        // Set data attributes for Bootstrap/JS logic
        document.documentElement.setAttribute("data-bs-theme", theme);
        document.documentElement.setAttribute("data-bs-variant", variant);
        this.elements.body.attr("data-bs-theme", theme);
        this.elements.body.attr("data-bs-variant", variant);

        // Clear old theme classes
        Array.from(document.documentElement.classList)
            .filter(cls => cls.startsWith("theme-"))
            .forEach(cls => document.documentElement.classList.remove(cls));
        document.documentElement.classList.add(`theme-${theme}`);

        // Determine logo filename
        const logoFile = `${theme}.png`;

        // Update header logo smoothly
        const $logo = $(this.settings.icon);
        const $regLogo = $(".register-page-logo");

        const updateLogo = (logoElement, file) => {
            logoElement.css({ opacity: 0 });
            setTimeout(() => {
                logoElement.attr("src", this.settings.logoDir + file).animate({ opacity: 1 }, 350);
            }, 50);
        };

        if (window.location.pathname.includes("register")) {
            updateLogo($logo, logoFile);
            $regLogo.attr("src", this.settings.logoDir + "transparent.png");
        } else {
            updateLogo($logo, logoFile);
            $regLogo.attr("src", this.settings.logoDir + logoFile);
        }

        // Save theme
        localStorage.setItem("theme", theme);
        localStorage.setItem("theme-variant", variant);
    }

    onClickBtnHandler(event) {
        const theme = $(event.currentTarget).data("theme");
        this.applyTheme(theme, 0); // always variant 0
    }

    constructor(settings) {
        super(settings);

        this.elements.themeBtn = $(this.settings.themeBtn);
        this.elements.themeModal = $(this.settings.themeModal);
        this.elements.themeOption = $(this.settings.themeOption);
        this.elements.body = $("body");

        // Toggle modal
        this.elements.themeBtn.on("click", this.elements.themeModal.toggle.bind(this.elements.themeModal));

        // Theme option clicks
        this.elements.themeOption.on("click", this.onClickBtnHandler.bind(this));

        // Load saved theme
        this.currentTheme = localStorage.getItem("theme") || this.settings.defaultTheme;
        this.currentVariant = parseInt(localStorage.getItem("theme-variant")) || this.settings.defaultVariant;

        // Apply theme on load
        this.applyTheme(this.currentTheme, this.currentVariant);

        console.log("ThemeSwitcherApp started");
    }
}

export default ThemeSwitcherApp;
