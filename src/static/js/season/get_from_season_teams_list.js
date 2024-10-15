let slug = document.querySelector('input').value
console.log(slug)


    async function fetchTeams() {
        let response = await fetch(`/api/json/teams_in_season/${slug}`,{
            method: 'GET',
        });
        let content = await response.json()
        let list = document.querySelector('.posts')

        list.innerHTML = '';  // Очищаємо список перед оновленням

        content.forEach((team, index) => {
            let num = index + 1;
            list.innerHTML += `
                <tr class="row-default">
                    <th scope="row" style="width: 5%;">${num}</th>
                    <td>
                        <img src="/static/img/teams/${team.logo}" alt="${team.name} logo" height="40px">
                    </td>
                    <td align="center" style="width: 60%;">
                        <a class="nav-link" href="/teams/${team.slug}">
                            <strong>${team.name}</strong> (${team.city}, ${team.region_name})
                        </a>    
                    </td>
                    <td align="center" style="width: 15%;">заявлено в турнір</td>
                    <td align="center" style="width: 10%;">
                        <button type="button" class="btn btn-outline-danger"
                                data-season-id="${team.season_id}" data-team-id="${team.id}"
                                onclick="deleteTeamFromSeason(this)">
                            Відзаявити
                        </button>
                    </td>
                </tr>
            `;
        });

        console.log(content);
    }
    fetchTeams();



// Функція яка видаляє команду зі розіграшу (кнопка "Видалити")
    async function deleteTeamFromSeason(button) {
        const seasonId = button.getAttribute('data-season-id');
        const teamId = button.getAttribute('data-team-id');

        if (confirm("Ви впевнені, що хочете відзаявити команду?")) {
            try {
                const response = await fetch(`/seasons/del_teams/${seasonId}/${teamId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();

                // Оновлюємо список команд після успішного видалення
                fetchTeams();

            } catch (error) {
                console.error('Error:', error);
                alert('Сталася помилка при видаленні команди');
            }
        }
    }



