// This process for animations buttons is nav-block (Season and Region)

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".nav-buttons a").forEach(link => {
        let currentUrl = window.location.pathname; // Отримуємо поточний шлях без домену
        let linkUrl = new URL(link.href).pathname; // Отримуємо шлях із посилання

        if (currentUrl === linkUrl || currentUrl === linkUrl + "/") {
            link.classList.add("nav-block-active");
        }
    });
});