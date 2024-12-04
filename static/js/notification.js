function showNotification(message, isGood) {
    const notification = document.getElementById('notification');
    notification.textContent = message;

    // Удаляем предыдущие классы стиля
    notification.classList.remove('hidden', 'show', 'notification-good', 'notification-bad');

    // Добавляем нужный класс в зависимости от isGood
    if (isGood) {
        notification.classList.add('notification-good');
    } else {
        notification.classList.add('notification-bad');
    }

    // Показываем уведомление
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
        notification.classList.add('hidden');
    }, 7000); // Уведомление исчезнет через 7 секунды
}