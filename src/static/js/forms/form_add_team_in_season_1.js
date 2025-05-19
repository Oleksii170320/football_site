// Функція для пошуку команди (фільтр по значеннях)
    function filterTeams() {
        let nameFilter = document.getElementById('team-name-input').value.toLowerCase();
        let cityFilter = document.getElementById('team-city-input').value.toLowerCase();
        let regionFilter = document.getElementById('team-region-input').value.toLowerCase();
        let options = document.querySelectorAll('#team-select option');

        options.forEach(function (option) {
            let optionText = option.textContent;
            let teamName = optionText.split(' (')[0].toLowerCase();
            let cityAndRegion = optionText.split(' (')[1]?.split(')')[0].split(', ');
            let teamCity = cityAndRegion ? cityAndRegion[0].toLowerCase() : '';
            let teamRegion = cityAndRegion ? cityAndRegion[1].toLowerCase() : '';

            if (
                teamName.includes(nameFilter) &&
                teamCity.includes(cityFilter) &&
                teamRegion.includes(regionFilter)
            ) {
                option.style.display = '';  // Відобразити
            } else {
                option.style.display = 'none';  // Сховати
            }
        });
    }

    document.getElementById('team-name-input').addEventListener('input', filterTeams);
    document.getElementById('team-city-input').addEventListener('input', filterTeams);
    document.getElementById('team-region-input').addEventListener('input', filterTeams);

// Функція яка додає команду в розіграш
    async function submitForm() {
        const form = document.getElementById('add-teams-form');
        const formData = new FormData(form);

        try {
            const response = await fetch('/seasons/add_teams', {
                method: 'POST',
                body: formData,
            });
            if (response.ok) {
                form.reset(); // Очищення форми
                fetchTeams(); // Якщо запит успішний, оновлюємо список команд
                const successMessage_add_team = document.getElementById('successMessage_add_team');
                successMessage_add_team.style.display = 'block'; // Показати повідомлення

                setTimeout(() => {
                    successMessage_add_team.style.display = 'none'; // Приховати повідомлення через 5 секунд
                }, 5000);

            } else {
                console.error('Помилка при додаванні команди');
                const errorMessage_add_team = document.getElementById('errorMessage_add_team');
                errorMessage_add_team.style.display = 'block'; // Показати повідомлення

                setTimeout(() => {
                     errorMessage_add_team.style.display = 'none'; // Приховати повідомлення через 5 секунд
                }, 5000);
            }

        } catch (error) {
            console.error('Error:', error);
            alert('Сталася помилка при додаванні команди.');
        }
    }

// Додаємо обробник подій на кнопку
    document.querySelector('button[type="submit"]').addEventListener('click', function (event) {
        event.preventDefault();  // Запобігаємо стандартній відправці форми
        submitForm();
    });


