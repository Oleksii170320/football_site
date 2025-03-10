$(document).ready(function () {
    let slug = $('input').val();

    async function fetchTeamsInSeason() {
        try {
            let response = await $.ajax({
                url: `/api/seasons/json/teams_in_season/${slug}`,
                method: 'GET',
                dataType: 'json'
            });

            let list = $('.btn-team-list');
            list.empty(); // Очищаємо список перед оновленням

            $.each(response, function (index, team) {
                let num = index + 1;
                let teamLogo = team.logo ? `/static/img/teams/${team.logo}` : '/static/img/techical_image/icon_team.PNG';

                list.append(`
                    <div class="archive-rows">
                        <div class="t-team-num">${num}</div>
                        <div class="t-team-logo">
                            <img src="${teamLogo}" alt="${team.name} logo" height="40px">
                        </div>
                        <div class="t-team-name">
                            <a class="nav-link" href="/teams/${team.slug}"> 
                                <strong>${team.name}</strong> (${team.city}, ${team.region_name} обл.)
                            </a>    
                        </div>
                        <div class="t-team-status">заявлено в турнір</div>
                        <div class="t-team-btn">
                            <span class="delete-team-btn" data-season-id="${team.season_id}" data-team-id="${team.id}">
                                Відзаявити
                            </span>
                        </div>
                    </div>
                `);
            });

        } catch (error) {
            console.error('Помилка отримання даних:', error);
        }
    }

    // Робимо функцію глобальною
    window.fetchTeamsInSeason = fetchTeamsInSeason;

    $(document).ready(function () {
        fetchTeamsInSeason();
    });

    // Видалення команди (делегування події)
    $(document).on('click', '.delete-team-btn', async function () {
        let button = $(this);
        let seasonId = button.data('season-id');
        let teamId = button.data('team-id');

        if (confirm("Ви впевнені, що хочете відзаявити команду?")) {
            try {
                let response = await $.ajax({
                    url: `/seasons/del_teams/${seasonId}/${teamId}`,
                    method: 'DELETE',
                    contentType: 'application/json'
                });

                // Оновлення списку після видалення
                fetchTeamsInSeason();
            } catch (error) {
                console.error('Помилка при видаленні:', error);
                alert('Сталася помилка при видаленні команди');
            }
        }
    });
});

$(function () {
    $('.btn-add-team').click(function(e) {
        let blockBtnAdd = $('.btn-add-team');
        let blockInputAdd = $('.btn-input-team');

        if (blockBtnAdd.is(":visible")) {
            blockBtnAdd.hide();
            blockInputAdd.show();
        }
    });
});
