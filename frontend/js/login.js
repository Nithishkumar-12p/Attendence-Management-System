        const loginForm = document.getElementById('loginForm');
        const toggleAuth = document.getElementById('toggleAuth');
        const formTitle = document.getElementById('formTitle');
        const submitBtn = document.getElementById('submitBtn');
        const resetBtn = document.getElementById('resetBtn');
        const toggleText = document.getElementById('toggleText');
        const togglePrefix = toggleText.childNodes[0];
        const errorMsg = document.getElementById('errorMsg');
        const successMsg = document.getElementById('successMsg');
        const confirmPasswordGroup = document.getElementById('confirmPasswordGroup');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        const forgotPasswordLink = document.getElementById('forgotPasswordLink');
        const forgotBtn = document.getElementById('forgotBtn');
        
        let mode = 'login'; // 'login', 'register', 'reset'

        const API_URL = 'http://127.0.0.1:5000/api/auth';

        function updateUI() {
            errorMsg.style.display = 'none';
            successMsg.style.display = 'none';
            
            if (mode === 'login') {
                formTitle.textContent = 'Supervisor Login';
                submitBtn.textContent = 'Authenticate';
                confirmPasswordGroup.style.display = 'none';
                confirmPasswordInput.required = false;
                resetBtn.style.display = 'none';
                forgotPasswordLink.style.display = 'block';
                toggleText.style.display = 'block';
                togglePrefix.textContent = "Don't have an account? ";
                toggleAuth.textContent = "Register Now";
            } else if (mode === 'register') {
                formTitle.textContent = 'Supervisor Registration';
                submitBtn.textContent = 'Register Account';
                confirmPasswordGroup.style.display = 'block';
                confirmPasswordInput.required = true;
                resetBtn.style.display = 'block';
                forgotPasswordLink.style.display = 'none';
                toggleText.style.display = 'block';
                togglePrefix.textContent = "Already have an account? ";
                toggleAuth.textContent = "Login Instead";
            } else if (mode === 'reset') {
                formTitle.textContent = 'Reset Access Password';
                submitBtn.textContent = 'Update Password';
                confirmPasswordGroup.style.display = 'block';
                confirmPasswordInput.required = true;
                resetBtn.style.display = 'block';
                forgotPasswordLink.style.display = 'none';
                toggleText.style.display = 'block';
                togglePrefix.textContent = "Remembered password? ";
                toggleAuth.textContent = "Back to Login";
            }
        }

        toggleAuth.addEventListener('click', (e) => {
            e.preventDefault();
            if (mode === 'login') mode = 'register';
            else mode = 'login';
            updateUI();
        });

        forgotBtn.addEventListener('click', (e) => {
            e.preventDefault();
            mode = 'reset';
            updateUI();
        });

        resetBtn.addEventListener('click', () => {
            loginForm.reset();
            errorMsg.style.display = 'none';
            successMsg.style.display = 'none';
        });

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmPassword = confirmPasswordInput.value;
            
            errorMsg.style.display = 'none';
            successMsg.style.display = 'none';

            if ((mode === 'register' || mode === 'reset') && password !== confirmPassword) {
                errorMsg.style.display = 'block';
                errorMsg.textContent = 'Passwords do not match';
                return;
            }

            let endpoint = '';
            if (mode === 'login') endpoint = '/login';
            else if (mode === 'register') endpoint = '/register';
            else if (mode === 'reset') endpoint = '/reset-password';
            
            try {
                const response = await fetch(`${API_URL}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (data.success) {
                    if (mode === 'login') {
                        localStorage.setItem('user', JSON.stringify(data.user));
                        window.location.href = 'dashboard.html';
                    } else if (mode === 'register') {
                        successMsg.style.display = 'block';
                        successMsg.textContent = 'Registration successful! Please login.';
                        mode = 'login';
                        updateUI();
                    } else if (mode === 'reset') {
                        successMsg.style.display = 'block';
                        successMsg.textContent = 'Password reset successful! Please login.';
                        mode = 'login';
                        updateUI();
                    }
                } else {
                    errorMsg.style.display = 'block';
                    errorMsg.textContent = data.message || 'Action failed';
                }
            } catch (error) {
                console.error('Error:', error);
                errorMsg.style.display = 'block';
                errorMsg.textContent = 'Connection error. Is the backend running?';
            }
        });

        // ─── Background Slideshow Logic ───
        function startSlideshow() {
            const slides = document.querySelectorAll('.background-slide');
            let currentSlide = 0;

            if (slides.length <= 1) return;

            setInterval(() => {
                slides[currentSlide].classList.remove('active');
                currentSlide = (currentSlide + 1) % slides.length;
                slides[currentSlide].classList.add('active');
            }, 5000);
        }

        startSlideshow();
        updateUI();
