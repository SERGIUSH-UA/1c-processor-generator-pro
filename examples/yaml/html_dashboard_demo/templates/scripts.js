// Counter functionality
let counter = 0;

function changeCounter(delta) {
    counter += delta;
    updateCounterDisplay();
}

function resetCounter() {
    counter = 0;
    updateCounterDisplay();
}

function updateCounterDisplay() {
    const el = document.getElementById('counterValue');
    if (el) {
        el.textContent = counter;
        el.style.color = counter > 0 ? '#4caf50' : counter < 0 ? '#f44336' : '#667eea';
    }
}

// Update time every second
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('ru-RU');
    const el = document.getElementById('serverTime');
    if (el) {
        el.textContent = timeStr;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Start time updates
    setInterval(updateTime, 1000);

    // Add animation to cards on load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
