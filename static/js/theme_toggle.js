document.addEventListener("DOMContentLoaded", () => {
    const themeToggleButton = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    const body = document.body;

    // Чтение куки
    const savedTheme = getCookie("theme");
    if (savedTheme) {
        body.classList.add(savedTheme);
        updateButton(savedTheme === "dark");
    }

    themeToggleButton.addEventListener("click", () => {
        // Переключение темы
        const isDark = body.classList.toggle("dark");
        const theme = isDark ? "dark" : "light";

        // Установка куки с длительностью
        setCookie("theme", theme, 7); // Срок действия куки: 7 дней

        // Обновляем кнопку
        updateButton(isDark);
    });

    // Функция для обновления кнопки
    function updateButton(isDark) {
        if (isDark) {
            themeIcon.classList.replace("bxs-sun", "bxs-moon");
            themeToggleButton.setAttribute("title", "Переключить на светлую тему");
        } else {
            themeIcon.classList.replace("bxs-moon", "bxs-sun");
            themeToggleButton.setAttribute("title", "Переключить на темную тему");
        }
    }

    // Утилиты для работы с куки
    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000); // В миллисекундах
        document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/`;
    }

    function getCookie(name) {
        const cookies = document.cookie.split("; ");
        for (const cookie of cookies) {
            const [key, value] = cookie.split("=");
            if (key === name) return value;
        }
        return null;
    }
});
