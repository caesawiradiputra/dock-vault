document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const masterKey = document.getElementById('masterKey').value;

        try {
            const response = await fetch('/api/login', {
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
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Login failed');
        }
    });
});