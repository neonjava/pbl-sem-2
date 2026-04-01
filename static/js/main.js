/**
 * BloodBridge Main JavaScript
 * Handles basic UI interactions and dynamic elements.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('BloodBridge: Initialized Architecture.');

    // Auto-dismiss Flash Alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Handle SOS Pulses (if added dynamically)
    setInterval(() => {
        const pulses = document.querySelectorAll('.pulse');
        pulses.forEach(pulse => {
            pulse.classList.toggle('pulse-active');
        });
    }, 1000);
});

/**
 * Handle form double submissions
 */
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', () => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        }
    });
});

/**
 * Utility function to format dates in local time
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}
