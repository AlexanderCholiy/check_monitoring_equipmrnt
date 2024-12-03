document.addEventListener("DOMContentLoaded", () => {
    // Убираем спиннер после "загрузки" страницы с задержкой
    const spinnerOverlay = document.getElementById("spinner-overlay");

    // Искусственная задержка для проверки работы спиннера
    setTimeout(() => {
        spinnerOverlay.classList.add("hidden");
    }, 250); // n милисекунды задержки
});