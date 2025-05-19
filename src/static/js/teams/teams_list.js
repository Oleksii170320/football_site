const currentUrl = window.location.href;
const regionSlug = currentUrl.split('/').find((segment, index, arr) => arr[index - 1] === 'region');

const regionsTeamsUrl = `http://127.0.0.1:8000/region/api/${regionSlug}/teams_list`;


const regionsUrl = 'http://127.0.0.1:8000/region/api/region_list';


async function regionList() {
    try {
        const response = await fetch(regionsUrl);
        return await response.json(); // Повертає всі регіони
    } catch (e) {
        console.error("Помилка завантаження регіонів:", e);
        return [];
    }
}


async function regionTeamsList() {
    try {
        const regions = await regionList(); // Отримуємо список усіх регіонів
        const response = await fetch(regionsTeamsUrl);
        const data = await response.json();

        const container = document.getElementById('teams-container'); // Заміна на правильний ID контейнера



        container.innerHTML = '';

        data.forEach(team => {
            // Знаходимо назву регіону за region_id
            const region = regions.find(r => r.id === team.region_id);
            const regionName = region ? region.name : 'Невідомий регіон';

            const card_col = document.createElement('div');
            card_col.className = 'col';

            card_col.innerHTML = `
                <div class="card">
                    <img 
                        src="/static/img/teams/${team.logo}" 
                        class="card-img-top team-logo"
                        alt="${team.name}"
                    >
                    <div class="card-body">
                        <a href="/teams/${team.slug}">
                            <h5 class="card-title">${team.name} (${team.city})</h5>
                        </a>
                        <p class="card-text">${regionName} область</p>
                    </div>
                </div>
            `;


            container.appendChild(card_col);
        });

    } catch (e) {
        console.error("Помилка завантаження даних:", e);
    }

}

// todo: розібратися, чому так не можно...
regionTeamsList();

console.log("Hi")

