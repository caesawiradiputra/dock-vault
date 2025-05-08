
document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const modal = document.getElementById('credentialModal');
    const addBtn = document.getElementById('addCredBtn');
    const closeBtn = document.querySelector('.close');
    const form = document.getElementById('credentialForm');
    const exportBtn = document.getElementById('exportBtn');
    const importBtn = document.getElementById('importBtn');
    const importFile = document.getElementById('importFile');
    const credentialsTable = document.getElementById('credentialsTable');
    const typeSelect = document.getElementById('type');
    const detailsTextarea = document.getElementById('details');

    // Modal handling
    addBtn.addEventListener('click', () => {
        document.getElementById('modalTitle').textContent = 'Add Credential';
        form.reset();
        document.getElementById('credentialId').value = '';
        modal.style.display = 'block';
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Password toggle
    document.getElementById('toggleSecret').addEventListener('click', function () {
        const secretField = document.getElementById('secret');
        if (secretField.type === 'password') {
            secretField.type = 'text';
            this.textContent = 'Hide';
        } else {
            secretField.type = 'password';
            this.textContent = 'Show';
        }
    });

    // Password strength meter
    document.getElementById('secret').addEventListener('input', function () {
        updateStrengthMeter(calculatePasswordStrength(this.value));
    });

    // Form submission
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Validate JSON
        let detailsJson;
        try {
            detailsJson = document.getElementById('details').value
                ? JSON.parse(document.getElementById('details').value)
                : {};
        } catch (err) {
            alert('Invalid JSON format in details field');
            return;
        }

        const formData = {
            name: document.getElementById('name').value,
            type: document.getElementById('type').value,
            env: document.getElementById('env').value,
            username: document.getElementById('username').value,
            secret: document.getElementById('secret').value,
            details: detailsJson
        };
        if (formData.type === 'ssh') {
            const passphrase = document.getElementById('sshPassphrase').value;
            if (passphrase) {
                formData.ssh_passphrase = passphrase;
            }
        }

        if (!formData.env) {
            alert('Please select an environment');
            return;
        }

        const credentialId = document.getElementById('credentialId').value;
        const url = credentialId ? `/api/credentials/${credentialId}` : '/api/credentials';
        const method = credentialId ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    modal.style.display = 'none';
                    loadCredentials();
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(`Error: ${error.message}`);
            });
    });

    // Export functionality
    exportBtn.addEventListener('click', exportCredentials);

    function exportCredentials() {
        const passphrase = prompt("Enter encryption passphrase (remember this!):");
        if (!passphrase) return;

        fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ passphrase })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Create download
                    const blob = new Blob([data.data], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'credentials.enc';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } else {
                    throw new Error(data.error || 'Export failed');
                }
            })
            .catch(error => {
                console.error('Export error:', error);
                alert(`Export failed: ${error.message}`);
            });
    }

    // Import functionality
    importBtn.addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', handleImport);

    function handleImport(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Reset file input
        event.target.value = '';

        const tryImport = (attempt = 1) => {
            const passphrase = prompt(`Enter decryption passphrase (Attempt ${attempt}):`);
            if (!passphrase) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                fetch('/api/import', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        data: e.target.result,
                        passphrase: passphrase
                    })
                })
                    .then(response => {
                        if (!response.ok) throw new Error('Import failed');
                        return response.json();
                    })
                    .then(data => {
                        if (data.status === 'success') {
                            alert('Import successful!');
                            loadCredentials();
                        } else {
                            throw new Error(data.error || 'Invalid passphrase');
                        }
                    })
                    .catch(error => {
                        if (confirm(`${error.message}\n\nTry again with different passphrase?`)) {
                            tryImport(attempt + 1);
                        }
                    });
            };
            reader.readAsText(file);
        };

        tryImport();
    }

    importFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                fetch('/api/import', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ data })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            loadCredentials();
                        }
                    });
            } catch (error) {
                console.error('Error parsing file:', error);
            }
        };
        reader.readAsText(file);
    });

    // Load credentials on page load
    loadCredentials();

    function loadCredentials() {
        fetch('/api/credentials')
            .then(response => response.json())
            .then(data => {
                credentialsTable.innerHTML = '';
                data.forEach(cred => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${cred.name}</td>
                        <td>${cred.type}</td>
                        <td class="env-${cred.env}">${cred.env}</td>
                        <td>${cred.username}</td>
                        <td>
                            <button class="action-btn edit-btn" data-id="${cred.id}">Edit</button>
                            <button class="action-btn delete-btn" data-id="${cred.id}">Delete</button>
                            <button class="action-btn copy-btn" data-clipboard-text="${cred.secret}">Copy Secret</button>
                            ${cred.type === 'ssh' && cred.ssh_passphrase ?
                            `<button class="action-btn copy-passphrase-btn" data-clipboard-text="${cred.ssh_passphrase}">Copy Passphrase</button>` : ''}
                        </td>
                    `;
                    credentialsTable.appendChild(row);
                });

                // Add event listeners to action buttons
                document.querySelectorAll('.edit-btn').forEach(btn => {
                    btn.addEventListener('click', () => editCredential(btn.dataset.id));
                });

                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', () => deleteCredential(btn.dataset.id));
                });

                document.querySelectorAll('.copy-btn').forEach(btn => {
                    btn.addEventListener('click', function () {
                        const text = this.getAttribute('data-clipboard-text');
                        navigator.clipboard.writeText(text).then(() => {
                            const originalText = this.textContent;
                            this.textContent = 'Copied!';
                            setTimeout(() => {
                                this.textContent = originalText;
                            }, 2000);
                        });
                    });
                });
                document.querySelectorAll('.copy-passphrase-btn').forEach(btn => {
                    btn.addEventListener('click', function () {
                        const text = this.getAttribute('data-clipboard-text');
                        navigator.clipboard.writeText(text).then(() => {
                            const originalText = this.textContent;
                            this.textContent = 'Copied!';
                            setTimeout(() => {
                                this.textContent = originalText;
                            }, 2000);
                        });
                    });
                });
            });
    }

    function editCredential(id) {
        fetch(`/api/credential/${id}`)
            .then(response => response.json())
            .then(cred => {
                document.getElementById('modalTitle').textContent = 'Edit Credential';
                document.getElementById('credentialId').value = cred.id;
                document.getElementById('name').value = cred.name;
                document.getElementById('type').value = cred.type;
                document.getElementById('env').value = cred.env || 'prod';
                document.getElementById('username').value = cred.username;
                document.getElementById('secret').value = cred.secret;
                document.getElementById('details').value = JSON.stringify(cred.details, null, 2);
                if (cred.type === 'ssh') {
                    document.getElementById('sshPassphraseGroup').style.display = 'block';
                    document.getElementById('sshPassphrase').value = cred.ssh_passphrase || '';
                } else {
                    document.getElementById('sshPassphraseGroup').style.display = 'none';
                }
                modal.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching credential:', error);
                alert('Failed to load credential');
            });
    }

    function deleteCredential(id) {
        if (confirm('Are you sure you want to delete this credential?')) {
            fetch(`/api/credentials/${id}`, {
                method: 'DELETE'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        loadCredentials();
                    }
                });
        }
    }

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
        if (!meter) return;

        meter.value = strength;
        meter.className = `strength-${strength}`;

        const labels = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'];
        document.getElementById('strengthText').textContent = labels[strength - 1] || '';
    }
    // typeSelect.addEventListener('change', updateJsonPlaceholder);
    document.getElementById('type').addEventListener('change', function () {
        updateJsonPlaceholder();
        toggleSshPassphraseField();
    });
    document.getElementById('env').addEventListener('change', updateJsonPlaceholder);

    function updateJsonPlaceholder() {
        const type = document.getElementById('type').value;
        const env = document.getElementById('env').value;
        let placeholder = '';

        switch (type) {
            case 'database':
                placeholder = `{
      "host": "${env === 'prod' ? 'prod-db' : 'dev-db'}.example.com",
      "port": ${env === 'prod' ? 5432 : 5433},
      "database": "myapp_${env}",
      "ssl": true,
      "connection_timeout": 30
    }`;
                break;

            case 'ssh':
                placeholder = `{
      "host": "${env}-server.example.com",
      "port": 22,
      "key_path": "/path/to/${env}_key",
      "jump_host": ${env === 'prod' ? '"bastion.example.com"' : 'null'}
    }`;
                break;

            case 'application':
                placeholder = `{
      "url": "https://app.example.com",
      "api_key": "optional",
      "auth_type": "basic|oauth|api_key",
      "scopes": ["read", "write"]
    }`;
                break;

            default:
                placeholder = `{
      "custom_field": "value",
      "notes": "Additional information"
    }`;
        }

        const detailsTextarea = document.getElementById('details');
        detailsTextarea.placeholder = placeholder;

        // Only update value if it's empty or contains the old placeholder
        const currentValue = detailsTextarea.value.trim();
        if (!currentValue || currentValue === '{}' || currentValue === detailsTextarea.dataset.lastPlaceholder) {
            detailsTextarea.value = placeholder;
        }
        detailsTextarea.dataset.lastPlaceholder = placeholder;
    }

    detailsTextarea.addEventListener('blur', function () {
        try {
            const json = JSON.parse(this.value);
            this.value = JSON.stringify(json, null, 2);
        } catch (e) {
            // Don't reformat invalid JSON
        }
    });

    function toggleSshPassphraseField() {
        const type = document.getElementById('type').value;
        const sshGroup = document.getElementById('sshPassphraseGroup');
        sshGroup.style.display = type === 'ssh' ? 'block' : 'none';
    }

    document.getElementById('toggleSshPassphrase').addEventListener('click', function () {
        const passphraseField = document.getElementById('sshPassphrase');
        if (passphraseField.type === 'password') {
            passphraseField.type = 'text';
            this.textContent = 'Hide';
        } else {
            passphraseField.type = 'password';
            this.textContent = 'Show';
        }
    });

    updateJsonPlaceholder();
});