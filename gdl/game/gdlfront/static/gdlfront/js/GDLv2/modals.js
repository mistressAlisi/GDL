/**
 * SPORTSLOTTO Modals
 * Handles all modal open/close animations and interactions
 */

(function($) {
    'use strict';

    // ===== NOT ENOUGH EVENTS MODAL =====

    // Show Not Enough Events modal
    function showNotEnoughEventsModal() {
        const $modal = $('#notEnoughEventsModal');

        // Show modal with animation
        $modal.css('display', 'block');

        // Trigger animation on next frame
        setTimeout(function() {
            $modal.addClass('show');
            lucide.createIcons(); // Re-initialize icons
        }, 10);

        // Prevent body scroll
        $('body').css('overflow', 'hidden');
    }

    // Hide Not Enough Events modal
    function hideNotEnoughEventsModal() {
        const $modal = $('#notEnoughEventsModal');

        // Remove show class to trigger exit animation
        $modal.removeClass('show');

        // Wait for animation to complete before hiding
        setTimeout(function() {
            $modal.css('display', 'none');
        }, 300);

        // Restore body scroll
        $('body').css('overflow', '');
    }

    // ===== LOADING MODAL =====

    // Show Loading modal
    function showLoadingModal(title, message) {
        const $modal = $('#loadingModal');

        // Update text if provided
        if (title) {
            $('#loadingModalTitle').text(title);
        }
        if (message) {
            $('#loadingModalMessage').text(message);
        }

        // Show modal with animation
        $modal.css('display', 'block');

        // Trigger animation on next frame
        setTimeout(function() {
            $modal.addClass('show');
            lucide.createIcons(); // Re-initialize icons
        }, 10);

        // Prevent body scroll
        $('body').css('overflow', 'hidden');
    }

    // Hide Loading modal
    function hideLoadingModal() {
        const $modal = $('#loadingModal');

        // Remove show class to trigger exit animation
        $modal.removeClass('show');

        // Wait for animation to complete before hiding
        setTimeout(function() {
            $modal.css('display', 'none');
            // Reset to default text
            $('#loadingModalTitle').text('Processing...');
            $('#loadingModalMessage').text('Please wait while we process your request');
        }, 300);

        // Restore body scroll
        $('body').css('overflow', '');
    }

    // ===== INITIALIZATION =====

    // Initialize modal handlers
    function initModals() {
        // Not Enough Events Modal handlers
        $('#closeModalBtn').on('click', function() {
            hideNotEnoughEventsModal();
        });

        $('#modalActionBtn').on('click', function() {
            hideNotEnoughEventsModal();
        });

        // Click backdrop to close (only for dismissable modals)
        $('.modal-backdrop').on('click', function() {
            hideNotEnoughEventsModal();
        });

        // Prevent closing when clicking modal content
        $('.modal-content').on('click', function(e) {
            e.stopPropagation();
        });

        // Escape key to close (only for dismissable modals)
        $(document).on('keydown', function(e) {
            if (e.key === 'Escape' && $('#notEnoughEventsModal').hasClass('show')) {
                hideNotEnoughEventsModal();
            }
            // Note: Loading modal cannot be dismissed by user
        });
    }

    // Initialize on document ready
    $(document).ready(function() {
        initModals();
        console.log('SPORTSLOTTO Modals initialized');
    });

    // ===== EXPORT =====

    // Export Not Enough Events Modal functions
    window.NotEnoughEventsModal = {
        show: showNotEnoughEventsModal,
        hide: hideNotEnoughEventsModal
    };

    // Export Loading Modal functions
    window.LoadingModal = {
        show: showLoadingModal,
        hide: hideLoadingModal
    };

})(jQuery);
