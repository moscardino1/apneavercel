document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add search on enter key
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchSong();
        }
    });

    function showLoading() {
        console.log('Loading started'); // Debugging log
        document.getElementById('loadingOverlay').style.display = 'block';
        document.getElementById('loadingIndicator').style.display = 'block';
    }
    
    function hideLoading() {
        console.log('Loading ended'); // Debugging log
        document.getElementById('loadingOverlay').style.display = 'none';
        document.getElementById('loadingIndicator').style.display = 'none';
    }
    

    // Add this code to handle mobile menu
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    mobileMenuBtn.addEventListener('click', function() {
        navLinks.classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.mobile-menu-btn') && !event.target.closest('.nav-links')) {
            navLinks.classList.remove('active');
        }
    });

    
}); 