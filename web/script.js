let autoscrollEnabled = false;
let autoscrollInterval = null;
let autoscrollSpeed = 2;

function restartAutoscroll() {
    if (autoscrollEnabled && autoscrollInterval) {
        clearInterval(autoscrollInterval);
        autoscrollInterval = setInterval(() => {
            window.scrollBy(0, 1);
        }, 100 / autoscrollSpeed);
    }
}

function increaseAutoscrollSpeed() {
    autoscrollSpeed = Math.min(autoscrollSpeed + 0.5, 10);
    restartAutoscroll();
    const speedIndicator = document.getElementById('autoscroll-speed');
    if (speedIndicator) {
        speedIndicator.textContent = autoscrollSpeed.toFixed(1);
    }
    return autoscrollSpeed;
}

function decreaseAutoscrollSpeed() {
    autoscrollSpeed = Math.max(autoscrollSpeed - 0.5, 0.5);
    restartAutoscroll();
    const speedIndicator = document.getElementById('autoscroll-speed');
    if (speedIndicator) {
        speedIndicator.textContent = autoscrollSpeed.toFixed(1);
    }
    return autoscrollSpeed;
}

function toggleAutoscroll() {
    autoscrollEnabled = !autoscrollEnabled;

    const autoscrollBtn = document.getElementById('autoscroll-btn');
    const speedIndicator = document.getElementById('autoscroll-speed');

    if (autoscrollEnabled) {
        if (autoscrollBtn) {
            autoscrollBtn.classList.add('enabled');
        }
        if (speedIndicator) {
            speedIndicator.textContent = autoscrollSpeed.toFixed(1);
        }
        autoscrollInterval = setInterval(() => {
            window.scrollBy(0, 1);
        }, 100 / autoscrollSpeed);
    } else {
        if (autoscrollBtn) {
            autoscrollBtn.classList.remove('enabled');
        }
        if (autoscrollInterval) {
            clearInterval(autoscrollInterval);
            autoscrollInterval = null;
        }
    }

    return autoscrollEnabled;
}
