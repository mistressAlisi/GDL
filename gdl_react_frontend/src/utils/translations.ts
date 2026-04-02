export type Language = 'en' | 'es';

export const translations = {
  en: {
    // Header & Navigation
    home: 'Home',
    about: 'About',
    games: 'Games',
    learnMore: 'Learn More',
    howItWorks: 'How It Works',
    glossary: 'Glossary',
    faq: 'FAQ',
    signIn: 'Sign In',
    register: 'Register',
    logout: 'Logout',
    profile: 'Profile',
    mainMenu: 'Main Menu',
    
    // Hero Section
    welcomeTitle: 'BETANY LOTTO',
    heroTagline: 'The Future of Lottery Betting is Here',
    heroDescription: 'Experience the thrill of lottery betting with our premium platform. Place bets on official lottery draws from multiple states with instant results and guaranteed payouts.',
    startPlaying: 'Start Playing Now',
    learnMoreBtn: 'Learn More',
    
    // Features
    featuresTitle: 'Why Choose Betany Lotto?',
    feature1Title: 'Place Your Bet',
    feature1Desc: 'Bet on the outcome of the official lottery draw. Your numbers are matched against the real results.',
    feature2Title: 'Real-Time Results',
    feature2Desc: 'Get instant notifications when draws happen. No waiting - know your results immediately.',
    feature3Title: 'Multiple States',
    feature3Desc: 'Access lottery betting from NY, CA, TX, FL and more states. All in one premium platform.',
    feature4Title: 'Guaranteed Payouts',
    feature4Desc: 'Fixed odds mean you know exactly what you can win. Instant credit to your account when you win.',
    
    // How It Works
    howItWorksTitle: 'How It Works',
    step1Title: 'Choose Your Game',
    step1Desc: 'Select from Pick 2, Pick 3, Pick 4, or Pick 5 lottery games across multiple states.',
    step2Title: 'Pick Your Numbers',
    step2Desc: 'Choose your lucky numbers or use our Quick Pick feature for random selections.',
    step3Title: 'Select Bet Type',
    step3Desc: 'Choose between Straight (exact order) or Boxed (any order) betting options.',
    step4Title: 'Place Your Bet & Win',
    step4Desc: 'Confirm your bet and wait for the draw. Match the numbers to win based on the official lottery results.',
    
    // Lottery Machine / Game Selection
    pickYourGame: 'Pick Your Game',
    selectState: 'Select State',
    selectLottery: 'Select Lottery Type',
    pickType: 'Pick Type',
    stateFirst: 'State First',
    lotteryFirst: 'Lottery First',
    chooseHowToStart: 'Choose how you want to start',
    chooseYourPlay: 'Choose Your Play',
    selectHowManyNumbers: 'Select how many numbers you want to bet on',
    nextDraws: 'Next Draws',
    quickPlay: 'Quick Play',
    quickPlaySubtitle: 'Fast & Easy - All Your Favorites in One Place',
    playByState: 'Play by State',
    playByStateSubtitle: 'Browse all 52 states & territories',
    
    // Quick Play Screen
    lotterySelection: 'Lottery Selection',
    saveFavorite: 'Save Favorite',
    favoriteLotteries: 'Favorite Lotteries',
    selectLotteries: 'Select Lotteries',
    tutorial: 'Tutorial',
    numberSelection: 'Number Selection',
    pickNumbers: 'Pick Numbers',
    luckyPick: 'Lucky Pick',
    saveNumbers: 'Save Numbers',
    loadFavorite: 'Load Favorite',
    betConfiguration: 'Bet Configuration',
    selectBonusPacks: 'Select Bonus Packs',
    optional: 'Optional',
    calendarSchedule: 'Calendar & Schedule',
    daysToRun: 'Days to Run',
    selectDates: 'Select Dates',
    startDate: 'Start Date',
    numberOfDays: 'Number of Days',
    days: 'days',
    selectDrawDates: 'Select Draw Dates',
    summary: 'Summary',
    totalTickets: 'Total Tickets',
    totalCombinations: 'Total Combinations',
    currentTicket: 'Current Ticket',
    allTickets: 'All Tickets',
    addToCart: 'Add to Cart',
    quickBuyNow: 'Quick Buy Now',
    changeSelection: 'Change Selection',
    noLotteriesSelected: 'No lotteries selected',
    selectAtLeastOne: 'Select at least one lottery to continue',
    favoriteNumbers: 'Favorite Numbers',
    noFavoritesYet: 'No favorites yet',
    startSavingFavorites: 'Start saving your favorite numbers and lotteries',
    
    // Months
    january: 'January',
    february: 'February',
    march: 'March',
    april: 'April',
    may: 'May',
    june: 'June',
    july: 'July',
    august: 'August',
    september: 'September',
    october: 'October',
    november: 'November',
    december: 'December',
    
    // Day names
    sunday: 'Sun',
    monday: 'Mon',
    tuesday: 'Tue',
    wednesday: 'Wed',
    thursday: 'Thu',
    friday: 'Fri',
    saturday: 'Sat',
    
    // Bet Amount & Schedule
    betAmountAndSchedule: 'Bet Amount & Schedule',
    betAmountPerTicket: 'Bet Amount Per Ticket',
    enterCustomAmount: 'Enter custom amount...',
    currentBetAmount: 'Current Bet Amount',
    day: 'day',
    
    // States
    newYork: 'New York',
    california: 'California',
    texas: 'Texas',
    florida: 'Florida',
    
    // Lottery Types
    pick2: 'Pick 2',
    pick3: 'Pick 3',
    pick4: 'Pick 4',
    pick5: 'Pick 5',
    pick2Desc: '2-digit lottery game',
    pick3Desc: '3-digit lottery game',
    pick4Desc: '4-digit lottery game',
    pick5Desc: '5-digit lottery game',
    
    // Number Selection
    selectYourNumbers: 'Select Your Numbers',
    chooseNumbers: 'Choose {{count}} numbers',
    quickPick: 'Quick Pick',
    clearAll: 'Clear All',
    selectedNumbers: 'Selected Numbers',
    numbersSelected: '{{count}}/{{total}} numbers selected',
    
    // Bet Types
    betType: 'Bet Type',
    straight: 'Straight',
    boxed: 'Boxed',
    straightDesc: 'Exact order - Higher payout',
    boxedDesc: 'Any order - More ways to win',
    
    // Bet Amount
    betAmount: 'Bet Amount',
    enterAmount: 'Enter bet amount',
    minimumBet: 'Minimum bet: ${{amount}}',
    maximumBet: 'Maximum bet: ${{amount}}',
    
    // Bonus Bets
    bonusBets: 'Bonus Bets',
    addBonusBets: 'Add Bonus Bets',
    bonusBetsOptional: 'Bonus Bets (Optional)',
    skipBonusBets: 'Skip Bonus Bets',
    firstBall: 'First Ball',
    lastBall: 'Last Ball',
    firstTwo: 'First Two',
    lastTwo: 'Last Two',
    middleThree: 'Middle Three',
    anyBall: 'Any Ball',
    ballPosition: 'Ball {{position}}',
    
    // Bet Calculator / Sidebar
    betCalculator: 'Bet Calculator',
    yourBet: 'Your Bet',
    totalCost: 'Total Cost',
    potentialPayout: 'Potential Payout',
    odds: 'Odds',
    mainBet: 'Main Bet',
    baseBet: 'Base Bet',
    bonusBet: 'Bonus Bet',
    
    // Cart
    cart: 'Cart',
    cartEmpty: 'Your cart is empty',
    addBetsToStart: 'Add bets to get started',
    removeFromCart: 'Remove from cart',
    checkout: 'Checkout',
    continueShopping: 'Continue Shopping',
    itemsInCart: '{{count}} item(s) in cart',
    
    // Quick Buy
    quickBuy: 'Quick Buy',
    quickBuyTitle: 'Quick Buy Options',
    quickBuyDesc: 'Fast bet placement with pre-configured options',
    
    // Review & Confirm
    reviewYourBet: 'Review Your Bet',
    confirmBet: 'Confirm Bet',
    placeBet: 'Place Bet',
    betPlaced: 'Bet Placed Successfully!',
    viewTicket: 'View Ticket',
    placeAnotherBet: 'Place Another Bet',
    
    // Draw Information
    nextDraw: 'Next Draw',
    drawTime: 'Draw Time',
    timeUntilDraw: 'Time Until Draw',
    drawDate: 'Draw Date',
    
    // Buttons & Actions
    continue: 'Continue',
    back: 'Back',
    cancel: 'Cancel',
    confirm: 'Confirm',
    save: 'Save',
    edit: 'Edit',
    delete: 'Delete',
    close: 'Close',
    next: 'Next',
    previous: 'Previous',
    submit: 'Submit',
    apply: 'Apply',
    reset: 'Reset',
    
    // Profile Page
    profileSettings: 'Profile Settings',
    personalInformation: 'Personal Information',
    updateProfile: 'Update Profile',
    resetForm: 'Reset Form',
    profilePicture: 'Profile Picture',
    uploadImage: 'Upload Image',
    changeImage: 'Change Image',
    fullName: 'Full Name',
    pronouns: 'Pronouns',
    pronounsPlaceholder: 'e.g., he/him, she/her, they/them',
    email: 'Email',
    phone: 'Phone / SMS',
    phonePlaceholder: '+1 (555) 123-4567',
    recoveryEmail: 'Recovery Email (Optional)',
    recoveryEmailPlaceholder: 'Optional backup email',
    language: 'Language',
    timezone: 'Timezone',
    selectLanguage: 'Select Language',
    selectTimezone: 'Select Timezone',
    profileUpdated: 'Profile updated successfully!',
    formReset: 'Form reset to saved values',
    
    // Common
    balance: 'Current Balance',
    activeBets: 'Active Bets',
    totalWins: 'Total Wins',
    loggedInAs: 'Logged in as',
    
    // Menu Items
    openTickets: 'Open Tickets',
    gradedTickets: 'Graded Tickets',
    deposit: 'Deposit',
    withdraw: 'Withdraw',
    regionTimezone: 'Region & Timezone',
    security: 'Security Settings',
    manageLimits: 'Manage Loss Limits',
    accountLockout: 'Account Lockout',
    
    // Sections
    tickets: 'Tickets',
    cashier: 'Cashier',
    settings: 'Settings',
    
    // Ticket Details
    ticketNumber: 'Ticket Number',
    lottery: 'Lottery',
    state: 'State',
    numbers: 'Numbers',
    status: 'Status',
    outcome: 'Outcome',
    winnings: 'Winnings',
    open: 'Open',
    graded: 'Graded',
    win: 'Win',
    loss: 'Loss',
    pending: 'Pending',
    
    // Messages
    noTicketsYet: 'No tickets yet',
    startPlayingToSeeBets: 'Start playing to see your bets here',
    insufficientBalance: 'Insufficient balance',
    betTooLow: 'Bet amount too low',
    betTooHigh: 'Bet amount too high',
    selectAllNumbers: 'Please select all numbers',
    
    // Footer
    termsOfService: 'Terms of Service',
    privacyPolicy: 'Privacy Policy',
    responsibleGaming: 'Responsible Gaming',
    support: 'Support',
    allRightsReserved: 'All rights reserved',
  },
  es: {
    // Header & Navigation
    home: 'Inicio',
    about: 'Acerca de',
    games: 'Juegos',
    learnMore: 'Aprende Más',
    howItWorks: 'Cómo Funciona',
    glossary: 'Glosario',
    faq: 'Preguntas Frecuentes',
    signIn: 'Iniciar Sesión',
    register: 'Registrarse',
    logout: 'Cerrar Sesión',
    profile: 'Perfil',
    mainMenu: 'Menú Principal',
    
    // Hero Section
    welcomeTitle: 'BETANY LOTTO',
    heroTagline: 'El Futuro de las Apuestas de Lotería Está Aquí',
    heroDescription: 'Experimenta la emoción de las apuestas de lotería con nuestra plataforma premium. Apuesta en sorteos oficiales de lotería de múltiples estados con resultados instantáneos y pagos garantizados.',
    startPlaying: 'Comenzar a Jugar',
    learnMoreBtn: 'Aprende Más',
    
    // Features
    featuresTitle: '¿Por Qué Elegir Betany Lotto?',
    feature1Title: 'Haz Tu Apuesta',
    feature1Desc: 'Apuesta en el resultado del sorteo oficial de lotería. Tus números se comparan con los resultados reales.',
    feature2Title: 'Resultados en Tiempo Real',
    feature2Desc: 'Recibe notificaciones instantáneas cuando ocurran los sorteos. Sin esperas - conoce tus resultados inmediatamente.',
    feature3Title: 'Múltiples Estados',
    feature3Desc: 'Accede a apuestas de lotería de NY, CA, TX, FL y más estados. Todo en una plataforma premium.',
    feature4Title: 'Pagos Garantizados',
    feature4Desc: 'Las probabilidades fijas significan que sabes exactamente cuánto puedes ganar. Crédito instantáneo a tu cuenta cuando ganas.',
    
    // How It Works
    howItWorksTitle: 'Cómo Funciona',
    step1Title: 'Elige Tu Juego',
    step1Desc: 'Selecciona entre juegos de lotería Pick 2, Pick 3, Pick 4 o Pick 5 en múltiples estados.',
    step2Title: 'Elige Tus Números',
    step2Desc: 'Elige tus números de la suerte o usa nuestra función de Selección Rápida para selecciones aleatorias.',
    step3Title: 'Selecciona Tipo de Apuesta',
    step3Desc: 'Elige entre opciones de apuesta Directa (orden exacto) o en Caja (cualquier orden).',
    step4Title: 'Haz Tu Apuesta y Gana',
    step4Desc: 'Confirma tu apuesta y espera el sorteo. Coincide con los números para ganar según los resultados oficiales de la lotería.',
    
    // Lottery Machine / Game Selection
    pickYourGame: 'Elige Tu Juego',
    selectState: 'Selecciona Estado',
    selectLottery: 'Selecciona Tipo de Lotería',
    pickType: 'Tipo de Pick',
    stateFirst: 'Estado Primero',
    lotteryFirst: 'Lotería Primero',
    chooseHowToStart: 'Elige cómo quieres comenzar',
    chooseYourPlay: 'Elige Tu Juego',
    selectHowManyNumbers: 'Selecciona cuántos números quieres apostar',
    nextDraws: 'Próximos Sorteos',
    quickPlay: 'Juego Rápido',
    quickPlaySubtitle: 'Rápido y Fácil - Todos tus Favoritos en un Lugar',
    playByState: 'Jugar por Estado',
    playByStateSubtitle: 'Explora todos los 52 estados y territorios',
    
    // Quick Play Screen
    lotterySelection: 'Selección de Lotería',
    saveFavorite: 'Guardar Favorito',
    favoriteLotteries: 'Loterías Favoritas',
    selectLotteries: 'Seleccionar Loterías',
    tutorial: 'Tutorial',
    numberSelection: 'Selección de Números',
    pickNumbers: 'Elegir Números',
    luckyPick: 'Selección Afortunada',
    saveNumbers: 'Guardar Números',
    loadFavorite: 'Cargar Favorito',
    betConfiguration: 'Configuración de Apuesta',
    selectBonusPacks: 'Seleccionar Paquetes Bonus',
    optional: 'Opcional',
    calendarSchedule: 'Calendario y Horario',
    daysToRun: 'Días para Ejecutar',
    selectDates: 'Seleccionar Fechas',
    startDate: 'Fecha de Inicio',
    numberOfDays: 'Número de Días',
    days: 'días',
    selectDrawDates: 'Seleccionar Fechas de Sorteo',
    summary: 'Resumen',
    totalTickets: 'Total de Tickets',
    totalCombinations: 'Total de Combinaciones',
    currentTicket: 'Ticket Actual',
    allTickets: 'Todos los Tickets',
    addToCart: 'Agregar al Carrito',
    quickBuyNow: 'Comprar Rápido Ahora',
    changeSelection: 'Cambiar Selección',
    noLotteriesSelected: 'No se han seleccionado loterías',
    selectAtLeastOne: 'Selecciona al menos una lotería para continuar',
    favoriteNumbers: 'Números Favoritos',
    noFavoritesYet: 'No hay favoritos aún',
    startSavingFavorites: 'Comienza a guardar tus números y loterías favoritas',
    
    // Months
    january: 'Enero',
    february: 'Febrero',
    march: 'Marzo',
    april: 'Abril',
    may: 'Mayo',
    june: 'Junio',
    july: 'Julio',
    august: 'Agosto',
    september: 'Septiembre',
    october: 'Octubre',
    november: 'Noviembre',
    december: 'Diciembre',
    
    // Day names
    sunday: 'Dom',
    monday: 'Lun',
    tuesday: 'Mar',
    wednesday: 'Mié',
    thursday: 'Jue',
    friday: 'Vie',
    saturday: 'Sáb',
    
    // Bet Amount & Schedule
    betAmountAndSchedule: 'Monto de Apuesta & Horario',
    betAmountPerTicket: 'Monto de Apuesta por Ticket',
    enterCustomAmount: 'Ingresa monto personalizado...',
    currentBetAmount: 'Monto de Apuesta Actual',
    day: 'día',
    
    // States
    newYork: 'Nueva York',
    california: 'California',
    texas: 'Texas',
    florida: 'Florida',
    
    // Lottery Types
    pick2: 'Pick 2',
    pick3: 'Pick 3',
    pick4: 'Pick 4',
    pick5: 'Pick 5',
    pick2Desc: 'Juego de lotería de 2 dígitos',
    pick3Desc: 'Juego de lotería de 3 dígitos',
    pick4Desc: 'Juego de lotería de 4 dígitos',
    pick5Desc: 'Juego de lotería de 5 dígitos',
    
    // Number Selection
    selectYourNumbers: 'Selecciona Tus Números',
    chooseNumbers: 'Elige {{count}} números',
    quickPick: 'Selección Rápida',
    clearAll: 'Borrar Todo',
    selectedNumbers: 'Números Seleccionados',
    numbersSelected: '{{count}}/{{total}} números seleccionados',
    
    // Bet Types
    betType: 'Tipo de Apuesta',
    straight: 'Directa',
    boxed: 'En Caja',
    straightDesc: 'Orden exacto - Mayor pago',
    boxedDesc: 'Cualquier orden - Más formas de ganar',
    
    // Bet Amount
    betAmount: 'Monto de Apuesta',
    enterAmount: 'Ingresa el monto de apuesta',
    minimumBet: 'Apuesta mínima: ${{amount}}',
    maximumBet: 'Apuesta máxima: ${{amount}}',
    
    // Bonus Bets
    bonusBets: 'Apuestas Bonus',
    addBonusBets: 'Agregar Apuestas Bonus',
    bonusBetsOptional: 'Apuestas Bonus (Opcional)',
    skipBonusBets: 'Omitir Apuestas Bonus',
    firstBall: 'Primera Bola',
    lastBall: 'Última Bola',
    firstTwo: 'Primeras Dos',
    lastTwo: 'Últimas Dos',
    middleThree: 'Tres del Medio',
    anyBall: 'Cualquier Bola',
    ballPosition: 'Bola {{position}}',
    
    // Bet Calculator / Sidebar
    betCalculator: 'Calculadora de Apuestas',
    yourBet: 'Tu Apuesta',
    totalCost: 'Costo Total',
    potentialPayout: 'Pago Potencial',
    odds: 'Probabilidades',
    mainBet: 'Apuesta Principal',
    baseBet: 'Apuesta Base',
    bonusBet: 'Apuesta Bonus',
    
    // Cart
    cart: 'Carrito',
    cartEmpty: 'Tu carrito está vacío',
    addBetsToStart: 'Agrega apuestas para comenzar',
    removeFromCart: 'Eliminar del carrito',
    checkout: 'Finalizar Compra',
    continueShopping: 'Continuar Comprando',
    itemsInCart: '{{count}} artículo(s) en el carrito',
    
    // Quick Buy
    quickBuy: 'Compra Rápida',
    quickBuyTitle: 'Opciones de Compra Rápida',
    quickBuyDesc: 'Colocación rápida de apuestas con opciones preconfiguradas',
    
    // Review & Confirm
    reviewYourBet: 'Revisa Tu Apuesta',
    confirmBet: 'Confirmar Apuesta',
    placeBet: 'Realizar Apuesta',
    betPlaced: '¡Apuesta Realizada con Éxito!',
    viewTicket: 'Ver Ticket',
    placeAnotherBet: 'Realizar Otra Apuesta',
    
    // Draw Information
    nextDraw: 'Próximo Sorteo',
    drawTime: 'Hora del Sorteo',
    timeUntilDraw: 'Tiempo Hasta el Sorteo',
    drawDate: 'Fecha del Sorteo',
    
    // Buttons & Actions
    continue: 'Continuar',
    back: 'Atrás',
    cancel: 'Cancelar',
    confirm: 'Confirmar',
    save: 'Guardar',
    edit: 'Editar',
    delete: 'Eliminar',
    close: 'Cerrar',
    next: 'Siguiente',
    previous: 'Anterior',
    submit: 'Enviar',
    apply: 'Aplicar',
    reset: 'Restablecer',
    
    // Profile Page
    profileSettings: 'Configuración de Perfil',
    personalInformation: 'Información Personal',
    updateProfile: 'Actualizar Perfil',
    resetForm: 'Restablecer Formulario',
    profilePicture: 'Foto de Perfil',
    uploadImage: 'Subir Imagen',
    changeImage: 'Cambiar Imagen',
    fullName: 'Nombre Completo',
    pronouns: 'Pronombres',
    pronounsPlaceholder: 'ej., él, ella, elle',
    email: 'Correo Electrónico',
    phone: 'Teléfono / SMS',
    phonePlaceholder: '+1 (555) 123-4567',
    recoveryEmail: 'Correo de Recuperación (Opcional)',
    recoveryEmailPlaceholder: 'Correo alternativo opcional',
    language: 'Idioma',
    timezone: 'Zona Horaria',
    selectLanguage: 'Seleccionar Idioma',
    selectTimezone: 'Seleccionar Zona Horaria',
    profileUpdated: '¡Perfil actualizado exitosamente!',
    formReset: 'Formulario restablecido a valores guardados',
    
    // Common
    balance: 'Balance Actual',
    activeBets: 'Apuestas Activas',
    totalWins: 'Ganancias Totales',
    loggedInAs: 'Conectado como',
    
    // Menu Items
    openTickets: 'Tickets Abiertos',
    gradedTickets: 'Tickets Calificados',
    deposit: 'Depositar',
    withdraw: 'Retirar',
    regionTimezone: 'Región y Zona Horaria',
    security: 'Configuración de Seguridad',
    manageLimits: 'Gestionar Límites de Pérdida',
    accountLockout: 'Bloqueo de Cuenta',
    
    // Sections
    tickets: 'Tickets',
    cashier: 'Caja',
    settings: 'Configuración',
    
    // Ticket Details
    ticketNumber: 'Número de Ticket',
    lottery: 'Lotería',
    state: 'Estado',
    numbers: 'Números',
    status: 'Estado',
    outcome: 'Resultado',
    winnings: 'Ganancias',
    open: 'Abierto',
    graded: 'Calificado',
    win: 'Ganado',
    loss: 'Perdido',
    pending: 'Pendiente',
    
    // Messages
    noTicketsYet: 'No hay tickets aún',
    startPlayingToSeeBets: 'Comienza a jugar para ver tus apuestas aquí',
    insufficientBalance: 'Balance insuficiente',
    betTooLow: 'Monto de apuesta demasiado bajo',
    betTooHigh: 'Monto de apuesta demasiado alto',
    selectAllNumbers: 'Por favor selecciona todos los números',
    
    // Footer
    termsOfService: 'Términos de Servicio',
    privacyPolicy: 'Política de Privacidad',
    responsibleGaming: 'Juego Responsable',
    support: 'Soporte',
    allRightsReserved: 'Todos los derechos reservados',
  }
};

export const useTranslation = (language: Language) => {
  return (key: keyof typeof translations.en, params?: Record<string, string | number>): string => {
    let text = translations[language][key] || translations.en[key];
    
    // Handle interpolation like {{count}}
    if (params) {
      Object.keys(params).forEach(param => {
        text = text.replace(new RegExp(`{{${param}}}`, 'g'), String(params[param]));
      });
    }
    
    return text;
  };
};

export const getMonthNames = (language: Language): string[] => {
  const t = useTranslation(language);
  return [
    t('january'),
    t('february'),
    t('march'),
    t('april'),
    t('may'),
    t('june'),
    t('july'),
    t('august'),
    t('september'),
    t('october'),
    t('november'),
    t('december')
  ];
};

export const getDayNames = (language: Language): string[] => {
  const t = useTranslation(language);
  return [
    t('sunday'),
    t('monday'),
    t('tuesday'),
    t('wednesday'),
    t('thursday'),
    t('friday'),
    t('saturday')
  ];
};