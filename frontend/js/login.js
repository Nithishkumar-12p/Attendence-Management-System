        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            // Simple mock authentication for prototype
            const user = document.getElementById('username').value;
            const pass = document.getElementById('password').value;
            
            if (user === 'admin' && pass === 'admin123') {
                window.location.href = 'dashboard.html';
            } else {
                document.getElementById('errorMsg').style.display = 'block';
            }
        });

        // ─── Background Slideshow Logic ───
        function startSlideshow() {
            const slides = document.querySelectorAll('.background-slide');
            let currentSlide = 0;

            if (slides.length <= 1) return;

            setInterval(() => {
                // Remove active class from current slide
                slides[currentSlide].classList.remove('active');
                
                // Increment slide index
                currentSlide = (currentSlide + 1) % slides.length;
                
                // Add active class to next slide
                slides[currentSlide].classList.add('active');
            }, 5000); // 5 seconds per slide for a more dynamic feel
        }

        // Start the transition
        startSlideshow();
