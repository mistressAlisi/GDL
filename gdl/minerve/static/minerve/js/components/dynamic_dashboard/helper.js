 // Open second sidebar and show correct submenu
  function toggleSecondSidebar(index) {
    const $sidebar = $('#secondSidebar');
    $sidebar.addClass('open');

    $('.second-sidebar-section').addClass('d-none');
    $('#second-sidebar-' + index).removeClass('d-none');
  }

  // Toggle main sidebar (mobile)
  $('#toggleSidebarBtn').on('click', function () {
    $('#mainSidebar').toggleClass('show');
  });

  // Collapse Bootstrap top navbar on link click (mobile only)
  $('.navbar-collapse .nav-link').on('click', function () {
    if ($(window).width() < 768) {
      $('.navbar-collapse').collapse('hide');
    }
  });
  // ✅ Collapse mainSidebar on link click (mobile only)
  $('#mainSidebar .nav-link').on('click', function () {
    if ($(window).width() < 768) {
      $('#mainSidebar').removeClass('show');
    }
  });
  // Click-outside handler to close both sidebars on mobile
  $(document).on('click', function (e) {
    const $target = $(e.target);

    // Close mainSidebar if clicked outside
    if (
      $('#mainSidebar').hasClass('show') &&
      !$target.closest('#mainSidebar').length &&
      !$target.closest('#toggleSidebarBtn').length
    ) {
      $('#mainSidebar').removeClass('show');
    }

    // Close secondSidebar if clicked outside
    if (
      $('#secondSidebar').hasClass('open') &&
      !$target.closest('#secondSidebar').length &&
      !$target.closest('.sidebar').length
    ) {
      $('#secondSidebar').removeClass('open');
    }
  });