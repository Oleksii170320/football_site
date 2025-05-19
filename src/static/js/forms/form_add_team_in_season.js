$(document).ready(function () {
    let teamFullName = $('#team-name-input, #team-city-input, #team-region-input')

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

    // Пошук команди заявлення в розіграш
    function fetchTeamsAddToSeason() {
        let teamName = $('#team-name-input').val().trim();
        let cityName = $('#team-city-input').val().trim();
        let regionName = $('#regionName').val().trim();


        // Якщо всі поля порожні - очищуємо список та не виконуємо запит
        if (teamName === '' && cityName === '' && regionName === '') {
            $('.team-results').empty();
            return;
        }

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
                let found_list = $('.team-results');
                found_list.empty();

                if (response.length < 0) {
                    found_list.append('<div class="no-results">За вказаною назвою команду не знайдено' +
                        `<strong id="btn_create_new_team_in_season">Створити нову команду</strong>` +
                        '</div>');
                    return;
                } else if (response.length >= 1) {
                    $.each(response, function (index, team) {
                        let teamLogo = team.logo ? `/static/img/teams/${team.logo}` : '/static/img/techical_image/icon_team.PNG';

                        found_list.append(`
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
                        '<div class="">За вказаною назвою команду не знайдено... </div> ' +
                        '</div>');
            }
        });
    };


    // Виконувати пошук із затримкою при введенні тексту
    let typingTimer;
    let doneTypingInterval = 500; // Час затримки перед виконанням запиту

    teamFullName.on('input', function () {
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

    // Відкрити кнопку для створення нової команди
    $(document).on('click', '.static-entry', function () {
        let createTeam = $('.rows-team-create');

        createTeam.show();
    });


    // Відкрити кнопку для створення нової команди
    $(document).on('click', '#btn-season-create-new-team', function () {
        alert('Hi')
    });

});
