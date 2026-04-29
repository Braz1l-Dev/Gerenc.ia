// ================================
// MOSTRAR / OCULTAR SENHA
// ================================
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}

// ================================
// INDICADOR DE FORÇA DA SENHA
// ================================
const passwordInput = document.getElementById('password');
const strengthBar = document.getElementById('strengthBar');

if (passwordInput && strengthBar) {
    passwordInput.addEventListener('input', () => {
        const value = passwordInput.value;
        let strength = 0;

        if (value.length >= 6) strength++;
        if (value.length >= 10) strength++;
        if (/[A-Z]/.test(value)) strength++;
        if (/[0-9]/.test(value)) strength++;
        if (/[^A-Za-z0-9]/.test(value)) strength++;

        // Remover classes anteriores
        strengthBar.classList.remove('weak', 'medium', 'strong');

        if (value.length === 0) {
            strengthBar.style.width = '0%';
        } else if (strength <= 2) {
            strengthBar.classList.add('weak');
        } else if (strength <= 3) {
            strengthBar.classList.add('medium');
        } else {
            strengthBar.classList.add('strong');
        }
    });
}

// ================================
// VERIFICAÇÃO DE MATCH DAS SENHAS
// ================================
const confirmInput = document.getElementById('confirm_password');
const passwordMatch = document.getElementById('passwordMatch');

if (confirmInput && passwordMatch && passwordInput) {
    confirmInput.addEventListener('input', checkPasswordMatch);
    passwordInput.addEventListener('input', () => {
        if (confirmInput.value.length > 0) {
            checkPasswordMatch();
        }
    });
}

function checkPasswordMatch() {
    if (!confirmInput || !passwordMatch || !passwordInput) return;

    const password = passwordInput.value;
    const confirm = confirmInput.value;

    if (confirm.length === 0) {
        passwordMatch.textContent = '';
        passwordMatch.className = 'password-match';
        return;
    }

    if (password === confirm) {
        passwordMatch.textContent = '✓ Senhas coincidem';
        passwordMatch.className = 'password-match match';
    } else {
        passwordMatch.textContent = '✗ Senhas não coincidem';
        passwordMatch.className = 'password-match no-match';
    }
}

// ================================
// TEMA — APLICAR SALVO NO AUTH
// ================================
const savedTheme = localStorage.getItem('pedro-theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
