window.onload = function() {
    // Get username from sessionStorage
    const username = sessionStorage.getItem('authenticatedUser');
    if (username) {
        document.getElementById('username').textContent = username;
    }

    // Trigger confetti animation
    triggerConfetti();
};

/**
 * Triggers confetti animation
 */
function triggerConfetti() {
    // Main confetti burst
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
    });

    // Additional confetti bursts
    setTimeout(() => {
        confetti({
            particleCount: 50,
            angle: 60,
            spread: 55,
            origin: { x: 0 }
        });
        confetti({
            particleCount: 50,
            angle: 120,
            spread: 55,
            origin: { x: 1 }
        });
    }, 250);
}

/**
 * Handles user logout
 */
function logout() {
    sessionStorage.removeItem('authenticatedUser');
    window.location.href = '/frontend/login.html';
}
