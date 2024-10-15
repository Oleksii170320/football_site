// Функція яка видаляє команду зі розіграшу (кнопка "Видалити")
async function deleteTeamFromSeason(button) {
    const seasonId = button.getAttribute('data-season-id');
    const teamId = button.getAttribute('data-team-id');
    if (confirm("Ви впевнені, що хочете віздаявити команду?")) {
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
            if (data.status === 'success') {
                alert('Команду успішно віздаялено!');
                window.location.reload(); // Перезавантаження сторінки
            } else {
                console.error('Error:', data.message);
                alert('Помилка: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Сталася помилка при видаленні команди');
        }
    }
}


export function deleteTeamFromSeason() {
    console.log("This is MyFunc from index.js");
}