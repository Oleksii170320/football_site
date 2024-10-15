    document.getElementById('matchForm').addEventListener('submit', async function (event) {
        event.preventDefault();  // Зупиняємо стандартну відправку форми

        const stageId = document.getElementById('round_id').value;
        const standingField = document.getElementById('standing');

        // Перевіряємо, чи обраний round_id більше за 50
        if (stageId > 50) {
            standingField.value = "false";  // Якщо більше 50, передаємо false
        } else {
            standingField.value = "true";   // Інакше передаємо true
        }

        const date = document.getElementById('startDate').value;
        let time = document.getElementById('startTime').value;
        if (!time) {
            time = "04:00";
        }

        const team1Id = document.getElementById('team1_id').value;
        const team2Id = document.getElementById('team2_id').value;
        const status = document.getElementById('status').value;
        const roundId = document.getElementById('round_id').value;

        if (!team1Id || !team2Id || !status || !roundId) {
            console.error("Всі обов'язкові поля повинні бути заповнені!");
            return;
        }

        const datetime = date && time ? new Date(`${date}T${time}`) : null;
        const epochTime = datetime ? Math.floor(datetime.getTime() / 1000) : null;
        document.getElementById('event_epoch').value = epochTime;

        const formData = new FormData(this);

        // Відправляємо запит через Fetch API
        try {
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (result.success) {
                // Показуємо модальне вікно після успішного створення матчу
                $('#successModal').modal('show');

                // Перезавантаження сторінки після закриття модального вікна
                $('#successModal').on('hidden.bs.modal', function () {
                    const regionSlug = result.region_slug;
                    const seasonSlug = result.season_slug;
                    window.location.href = `/region/${regionSlug}/${seasonSlug}/schedule`;
                });
            } else {
                console.error(result.error || "Сталася помилка");
                }
        } catch (error) {
            console.error("Помилка під час створення матчу:", error);
        }
    });