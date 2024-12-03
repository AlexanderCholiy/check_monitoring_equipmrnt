document.addEventListener("DOMContentLoaded", () => {
    // Находим все элементы с подменю
    const submenuContainers = document.querySelectorAll(".has-submenu");

    submenuContainers.forEach((container) => {
        const trigger = container.querySelector(".menu-trigger");
        const submenu = container.querySelector(".submenu");

        if (!trigger || !submenu) return; // Пропустить, если элементов нет

        // Показать/скрыть подменю при клике
        trigger.addEventListener("click", (e) => {
            e.stopPropagation(); // Остановка распространения события
            submenu.classList.toggle("show");
        });
    });

    // Закрытие всех подменю при клике вне их
    document.addEventListener("click", () => {
        document.querySelectorAll(".submenu.show").forEach((submenu) => {
            submenu.classList.remove("show");
        });
    });
});
