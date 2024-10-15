let slug = document.querySelector('input').value
console.log(slug)

async function getMatches() {
    let response = await fetch(`/api/json/matches_in_season/${slug}`);
    let content = await response.json();

    let list = document.querySelector('.matches_table');

    let key;

    for (key in content) {
        // Умова для кольору тексту залежно від статусу
        let color = content[key].status === "Тех. поразка" ? "red" : "blue";

        list.innerHTML += `
            <tr class="row-default">
                <td style="width: 15%;"><strong>${content[key].event}</strong></td>
                <td style="width: 30%;">
                    <a href="/teams/${content[key].team1_slug}/application">
                        <h5><strong>${content[key].team1_name}</strong> (${content[key].team1_city})</h5>
                    </a>
                </td>
                <td style="text-align: center;">
                    <img src="/static/img/teams/${content[key].team1_logo}"
                         alt="${content[key].team1_name} logo" style="height: 60px">
                </td>
                <td style="width: 10%;" align="center">
                    <a href="/matches/${content[key].match_id}/review" target="_blank">
                        <strong style="color: ${color}; text-align: center;">
                            <h3>${content[key].team1_goals} : ${content[key].team2_goals}</h3>
                        </strong><br>

                        ${ (content[key].team1_penalty && content[key].team2_penalty) > 0 ? `
                            <p style="text-align: center;">
                                (п. ${content[key].team1_penalty} : ${content[key].team2_penalty})
                            </p>` : ''}
                </td>
                <td style="text-align: center;">
                    <img src="/static/img/teams/${content[key].team2_logo}"
                         alt="${content[key].team2_name} logo" style="height: 60px">
                </td>
                <td style="width: 30%;">
                    <a href="/teams/${content[key].team2_slug}/application">
                        <h5><strong>${content[key].team2_name}</strong> (${content[key].team2_city})</h5>
                    </a>
                </td>
            </tr>
        `;
    }
}
getMatches();
