document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('initForm');
    const passwordInput = document.getElementById('masterKey');

    // Password strength indicator
    passwordInput.addEventListener('input', function () {
        const strength = calculatePasswordStrength(this.value);
        updateStrengthMeter(strength);
    });

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const masterKey = passwordInput.value;

        try {
            const response = await fetch('/api/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ master_key: masterKey })
            });

            const data = await response.json();

            if (data.status === 'success') {
                window.location.href = data.redirect || '/';
            } else {
                alert(data.error || 'Initialization failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Initialization failed');
        }
    });

    function calculatePasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        return Math.min(strength, 5);
    }

    function updateStrengthMeter(strength) {
        const meter = document.getElementById('strengthMeter');
        const text = document.getElementById('strengthText');

        meter.value = strength;
        meter.className = `strength-${strength}`;

        const labels = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'];
        text.textContent = labels[strength - 1] || '';
    }
});