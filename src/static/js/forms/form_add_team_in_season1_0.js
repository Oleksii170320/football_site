$(document).ready(function () {

    // Вибір необхідного регіону при пошуку команди...
    $("#team-region-input").on("input", function() {
        let input = $(this).val().toLowerCase();
        let regionIdField = $("#regionId");
        let regionNameField = $("#regionName");
        let regionSlugField = $("#regionSlug");

        regionIdField.val("");
        regionSlugField.val("");

        $("#regionsList option").each(function() {
            if ($(this).val().toLowerCase() === input) {
                regionIdField.val($(this).data("id"));
                regionNameField.val($(this).data("name"));
                regionSlugField.val($(this).data("slug"));
            }
        });
    });

    // Словник, для формування slug
    function convertToSlug(text) {
        const cyrillicToLatinMap = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'є': 'ye', 'э': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ы': 'y', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ю': 'yu', 'я': 'ya', 'ь': '.', 'ъ': '', ' ': '-',
            '"': '', ',': '', '.': '', '—': '-', '’': ''
        };
        return text.toLowerCase().split('').map(char => cyrillicToLatinMap[char] || char).join('');
    }

    // Пошук або створення команди для заявлення її в розіграш
    function fetchTeamsAddToSeason() {
        let teamName = $('#team-name-input').val().trim();
        let cityName = $('#team-city-input').val().trim();
        // let region = $('#team-region-input').val().trim();
        let regionName = $('#regionName').val().trim();

        // Якщо всі поля порожні - очищуємо список та не виконуємо запит
        if (teamName === '' && cityName === '' && regionName === '') {
            $('.team-results').empty();
            return;
        }

        /* Якщо необхідну команди зі списку запропонованих не знайдено,
         дана функція створює нову команду */
        function updateList() {
            let teamName = $('#team-name-input').val().trim();
            let cityName = $('#team-city-input').val().trim();
            let regionName = $('#team-region-input').val().trim();

            let list = $('.rows-team-create');
            let registration = '';

            // Перетворюємо першу літеру на велику
            let cityUp = cityName  ? cityName.charAt(0).toUpperCase() + cityName.slice(1).toLowerCase() : '';
            let regionUp = regionName ? regionName.charAt(0).toUpperCase() + regionName.slice(1).toLowerCase() : '';

            // Формуємо текст для виводу
            if (cityUp && regionUp) {
                registration = `(${cityUp}, ${regionUp})`;
            } else if (cityUp) {
                registration = `(${cityUp})`;
            } else if (regionUp) {
                registration = `(${regionUp})`;
            }

            // Формуємо повну назву команди та slug без пробілів
            const fullName = `${teamName} (${cityUp}, ${regionUp})`;
            const slug = convertToSlug(`${teamName} (${cityUp})`);

            // Очищаємо список перед додаванням
            list.empty();

            // Додаємо новий елемент лише якщо є хоча б одне заповнене поле
            if (teamName || cityUp || regionUp) {
                list.append(`                    
                    <div class="t-team-add-num">${slug}</div>

                    <div class="t-team-add-logo">
                        <img src="/static/img/techical_image/icon_team.PNG" alt="logo" height="40px">
                    </div>
                    
                    <div class="t-new-add-team-name">
                        <span>${teamName}</span> ${registration}
                    </div>
                    
                    <div class="t-team-add_region create-team">
                        <span type="btn_create_new_team">Створити нову команду</span>
                    </div>
                  </form>  
                `);
            };
        };


        // Викликати функцію при введенні символів у будь-яке поле
        $('#team-name-input, #team-city-input, #team-region-input').on('input', updateList);

        $.ajax({
            url: "/api/teams/json/teams_list",
            method: "GET",
            data: {
                team_name: teamName.charAt(0).toUpperCase() + teamName.slice(1),
                team_city: cityName.charAt(0).toUpperCase() + cityName.slice(1),
                region_name: regionName.charAt(0).toUpperCase() + regionName.slice(1)
            },
            dataType: "json",
            success: function (response) {
                let list = $('.team-results');
                list.empty();

                if (response.length < 0) {
                    list.append('<div class="no-results">За вказаною назвою команду не знайдено</div>');
                    return;
                } else if (response.length >= 1) {
                    $.each(response, function (index, team) {
                        let teamLogo = team.logo ? `/static/img/teams/${team.logo}` : '/static/img/techical_image/icon_team.PNG';

                        list.append(`
                            <div class="archive-rows rows-team-list" data-id="${team.id}">
                                <div class="t-team-add-num"></div>
                                
                                <div class="t-team-add-logo">
                                    <img src="${teamLogo}" alt="${team.name} logo" height="40px">
                                </div>
                                <div class="t-new-add-team-name">
                                    <a class="nav-link" href="/teams/${team.slug}">
                                        <strong>${team.name}</strong> (${team.city}, ${team.region_name} обл.)
                                    </a>
                                </div>
                                <div class="t-team-add_region">
                                    <span class="declare-team">Заявити в турнір</span>
                                </div>
                            </div>
                        `);
                    });
                };
            },
            error: function () {
                $('.team-results')
                    .html('<div class="archive-rows add-team-error">' +
                        'За вказаною назвою команду не знайдено' +
                        '</div>');
            }
        });
    };


    // Виконувати пошук із затримкою при введенні тексту
    let typingTimer;
    let doneTypingInterval = 500; // Час затримки перед виконанням запиту

    $('#team-name-input, #team-city-input, #team-region-input').on('input', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(fetchTeamsAddToSeason, doneTypingInterval);
    });


    // Додавання команди в розіграш
    $(document).on('click', '.declare-team', function () {
        let teamId = $(this).closest('.rows-team-list').data('id');

        $.ajax({
            url: '/seasons/add_teams',
            method: 'POST',
            data: {
                team_id: teamId,
                season_id: $('input[name="season_id"]').val(),
                region_slug: $('input[name="region_slug"]').val(),
                season_slug: $('input[name="season_slug"]').val(),
            },
            success: function () {
                $('#successMessage_add_team').fadeIn().delay(5000).fadeOut();

                fetchTeamsAddToSeason(); // Оновлення списку команд у формі

                if (typeof window.fetchTeamsInSeason === 'function') {
                    window.fetchTeamsInSeason(); // Оновлення списку команд у сезоні
                }
            },
            error: function () {
                $('#errorMessage_add_team').fadeIn().delay(5000).fadeOut();
            }
        });


        // Очищення списку при натисканні на кнопку "Заявити в турнір"
        let blockBtnAdd = $('.btn-add-team');
        let blockInputAdd = $('.btn-input-team');

        $('.team-results').empty();// Очищаємо список
        $('#team-name-input').val('');
        $('#team-city-input').val('');
        $('#team-region-input').val('');

        if (blockInputAdd.is(":visible")) {
            blockBtnAdd.show();
            blockInputAdd.hide();
        }
    });

    // Відкрити форму створення нової команди
    $(document).on('click', '.rows-team-list .create-team', function () {
        let createTeam = $('#teamForm');

        createTeam.show();
    });

    // Створення нової команди та додавання її в розіграш
    $(document).on('click', '.btn_create_new_team', function () {

        $.ajax({
            url: '/teams/new_team',
            method: 'POST',
            data: {
                name: $('input[name="team.name"]').val(),
                city: $('input[name="cityUp"]').val(),
                region_id: $('input[name="season_slug"]').val(),
                full_name: `${fullName}`,
                slug: `${cityUp}`,
            },
            success: function () {
                $('#successMessage_add_team').fadeIn().delay(5000).fadeOut();

                fetchTeamsAddToSeason(); // Оновлення списку команд у формі

                if (typeof window.fetchTeamsInSeason === 'function') {
                    window.fetchTeamsInSeason(); // Оновлення списку команд у сезоні
                }
            },
            error: function () {
                $('#errorMessage_add_team').fadeIn().delay(5000).fadeOut();
            }
        });
    });
});
