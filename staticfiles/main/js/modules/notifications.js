export function showNotification(message, options = {}) {
    const notification = document.getElementById('notification');
    notification.innerHTML = message;
    notification.className = 'notification';

    if (options.isError) {
        notification.classList.add('error');
    }

    if (options.isConfirm) {
        notification.innerHTML += '<br><button id="confirmYes">Yes</button><button id="confirmNo">No</button>';
    }

    notification.classList.add('show');

    if (options.isConfirm) {
        document.getElementById('confirmYes').addEventListener('click', function () {
            notification.classList.remove('show');
            if (options.confirmCallback) options.confirmCallback(true);
        });
        document.getElementById('confirmNo').addEventListener('click', function () {
            notification.classList.remove('show');
            if (options.confirmCallback) options.confirmCallback(false);
        });
    } else {
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}
