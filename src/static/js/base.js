// buttons in the block menu
$(function () {
    $('.logIn-logout a').click(function(e) {
        alert("Autorisation");
    });
});

$(function () {
    let currentUrl = window.location.pathname; // Отримуємо поточний шлях без домену

    $('.selected-reg .region-season a').each(function () {
        let linkUrl = new URL(this.href).pathname; // Отримуємо шлях із посилання
        let seasonSlug = $(this).data('season-slug'); // Отримуємо slug турніру з data-атрибута

        // Якщо URL містить slug сезону або повністю збігається
        if (currentUrl.includes(seasonSlug) || currentUrl === linkUrl) {
            $(this).removeClass('tournament').addClass('tournament-active'); // Додаємо CSS-клас
        }
    });
});

$(document).ready(function () {
    let button = $("#toggleRegions");
    let hiddenRegions = $(".hidden-region");

    // Переконуємось, що при завантаженні вони приховані
    hiddenRegions.hide();

    button.click(function () {
        if (hiddenRegions.is(":visible")) {
            hiddenRegions.slideUp();
            button.text("Показати всі регіони ↓");
        } else {
            hiddenRegions.slideDown();
            button.text("Приховати ↑");
        }
    });
});



