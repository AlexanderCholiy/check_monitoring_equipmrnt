// JavaScript для изменения видимости пароля и иконки
document.getElementById('hide-password').addEventListener('click', function() {
    var passwordField = document.getElementById('password');
    var icon = this;

    if (passwordField.type === 'password') {
        passwordField.type = 'text'; // Показать пароль
        icon.className = 'bx bx-lock-open-alt'; // Поменять иконку на открытую
    } else {
        passwordField.type = 'password'; // Скрыть пароль
        icon.className = 'bx bxs-lock-alt'; // Поменять иконку на закрытую
    }
});

