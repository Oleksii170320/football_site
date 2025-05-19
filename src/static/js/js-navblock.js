// This process for animations buttons is nav-block (Season and Region)

document.addEventListener("DOMContentLoaded", function () {
    let currentUrl = window.location.pathname; // Отримуємо поточний шлях без домену

    document.querySelectorAll(".region-season a").forEach(link => {
        let linkUrl = new URL(link.href).pathname; // Отримуємо шлях із посилання
        let seasonSlug = link.getAttribute("data-season-slug"); // Отримуємо slug турніру з data-атрибута

        // Перевіряємо, чи збігається URL або slug сезону
        if (currentUrl.includes(seasonSlug) || currentUrl === linkUrl) {
            link.classList.add("tournament-active");
        }
    });
});



console.log('Hi')