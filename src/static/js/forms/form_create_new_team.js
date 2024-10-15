// Встановлення обробників подій для вводу
    document.getElementById('teamName').addEventListener('input', updateFullNameAndSlug);
    document.getElementById('cityName').addEventListener('input', updateFullNameAndSlug);
    document.getElementById('regionName').addEventListener('change', updateFullNameAndSlug);


    function updateFullNameAndSlug() {
        const teamName = document.getElementById('teamName').value;
        const cityName = document.getElementById('cityName').value;
        const regionSelect = document.getElementById('regionName');
        const regionName = regionSelect.selectedOptions[0]?.text || ''; // Перевірка наявності вибору

        // Формуємо повну назву команди
        const fullName = `${teamName} (${cityName}, ${regionName})`;
        document.getElementById('full-name-input').value = fullName;

        // Формуємо slug без пробілів
        const slug = convertToSlug(`${teamName} (${cityName})`);

        // Оновлюємо значення поля team_slug
        document.getElementById('team_slug').value = slug;

        // Оновлюємо значення прихованого поля teamSlugInput
        document.getElementById('teamSlugInput').value = slug;
    }

    function convertToSlug(text) {
        const cyrillicToLatinMap = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'є': 'ye', 'э': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ы': 'y', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ю': 'yu', 'я': 'ya', 'ь': '.', 'ъ': '', ' ': '-', // Зміна пробілу на дефіс
            '"': '', ',': '', '.': '', '—': '-', '’': '',
        };
        return text.toLowerCase().split('').map(char => cyrillicToLatinMap[char] || char).join('');
    }

// Функція для динамічного пошуку стадіонів
    document.getElementById('team-stadium-input').addEventListener('input', function () {
        const query = this.value;

        if (query.length >= 2) { // Пошук починається після введення 2 або більше літер
            fetch(`/stadiums/search?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const stadiumSuggestions = document.getElementById('stadiumSuggestions');
                    stadiumSuggestions.innerHTML = ''; // Очищення попередніх результатів

                    if (Array.isArray(data) && data.length > 0) {  // Переконання, що data - масив
                        data.forEach(stadium => {
                            const suggestionItem = document.createElement('div');
                            suggestionItem.classList.add('list-group-item');
                            suggestionItem.textContent = `${stadium.name} (${stadium.city})`;

                            suggestionItem.addEventListener('click', function () {
                                document.getElementById('team-stadium-input').value = stadium.name;
                                document.getElementById('stadiumId').value = stadium.id;
                                stadiumSuggestions.innerHTML = ''; // Очищення списку після вибору
                            });

                            stadiumSuggestions.appendChild(suggestionItem);
                        });
                    } else {
                        stadiumSuggestions.innerHTML = '<div class="list-group-item">Нічого не знайдено</div>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching stadiums:', error);
                });
        } else {
            document.getElementById('stadiumSuggestions').innerHTML = ''; // Очищення результатів при короткому запиті
        }
    });

// Підставляємо слаг регіону команди в модальне вікно, для правильне розміщення лого.
        function updateRegionSlug() {
        const selectElement = document.getElementById("regionName");
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const selectedSlug = selectedOption.getAttribute("data-slug");

        // Оновлення значення в прихованому input
        document.getElementById("regionSlugInput").value = selectedSlug;

        // Оновлення тексту в заголовку
        document.getElementById("selectedRegionSlug").innerText = selectedSlug;
    }


// Обробка події при відправці форми команди
    document.getElementById('teamForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Зупиняє стандартну поведінку форми

        const regionSlugPage = document.getElementById('regionSlugPage').value;// slug регіону для оновлення сторінки
        const seasonSlugPage = document.getElementById('seasonSlugPage').value;// slug розіграшу для оновлення сторінки

        const formData = new FormData(this);
        formData.append('region', regionSlugPage);
        formData.append('season', seasonSlugPage);

        fetch('/teams/new_team', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                if (data) {
                    this.reset(); // Очищення форми
                    const successMessage = document.getElementById('successMessage');
                    successMessage.style.display = 'block'; // Показати повідомлення

                    setTimeout(() => {
                        successMessage.style.display = 'none'; // Приховати повідомлення через 5 секунд
                    }, 5000);

                    // Відкриваємо модальне вікно з питанням про завантаження логотипу
                    document.getElementById('uploadLogoModal').style.display = 'block';

                    // Зберігаємо team_id для можливого використання в завантаженні логотипу
                    const team_id = data.id; // Виправлено на data.id
                    const team_slug = data.slug; // Виправлено на data.slug

                    document.getElementById('addLogo').addEventListener('click', function () {
                        document.getElementById('uploadLogoModal').style.display = 'none';
                        document.getElementById('uploadFormModal').style.display = 'block';

                        // Додаємо прихований input для team_id у форму логотипу
                        const logoForm = document.getElementById('logoForm');
                        let hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = 'team_id';
                        hiddenInput.value = team_id; // Виправлено на team_id
                        logoForm.appendChild(hiddenInput);
                    });

                    document.getElementById('completeHere').addEventListener('click', function () {
                        document.getElementById('uploadLogoModal').style.display = 'none';
                        window.location.href = `/region/${formData.get('region')}/${formData.get('season')}/clubs`;
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });


// Обробка події при відправці форми логотипу
    document.getElementById('logoForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Зупиняє стандартну поведінку форми


        const logoInput = document.getElementById('logoInput').files[0]; // Отримуємо файл логотипу
        const regionSlug = document.getElementById('regionSlugInput').value; // Отримуємо slug регіону
        const teamSlug = document.getElementById('teamSlugInput').value; // Отримуємо slug команди
        const regionSlugPage = document.getElementById('regionSlugPage').value;// slug регіону для оновлення сторінки
        const seasonSlugPage = document.getElementById('seasonSlugPage').value;// slug розіграшу для оновлення сторінки

        if (!logoInput) {
            alert('Будь ласка, оберіть файл для завантаження'); // Перевірка наявності файлу
            return;
        }

        // Перевірка типу файлу (можна додати інші формати при необхідності)
        const allowedExtensions = ['image/jpeg', 'image/png', 'image/jpg', 'image/jfif'];
        if (!allowedExtensions.includes(logoInput.type)) {
            alert('Будь ласка, оберіть файл у форматі JPEG, JPG, PNG, JFIF.');
            return;
        }

        const formData = new FormData();
        formData.append('file', logoInput); // Додаємо файл до форми
        formData.append('region_slug', regionSlug); // Додаємо slug регіону
        formData.append('team_slug', teamSlug); // Додаємо slug команди
        formData.append('region', regionSlugPage);
        formData.append('season', seasonSlugPage);


    // Відправка запиту на сервер для завантаження логотипу
        fetch('/teams/upload_logo', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Помилка завантаження логотипу'); // Обробка помилок
            }
            return response.json(); // Парсимо відповідь у форматі JSON
        })
        .then(data => {
            console.log('Логотип завантажено успішно:', data);

            // Закриваємо модальне вікно
            document.getElementById('uploadFormModal').style.display = 'none';

            // Показуємо повідомлення про успішне завантаження
            alert(`Логотип ${data.filename} успішно завантажено!`);

            // Оновлення сторінки або виконання додаткових дій
            window.location.href = `/region/${formData.get('region')}/${formData.get('season')}/clubs`;
            // location.reload(); // Можна перезавантажити сторінку або оновити частину контенту
        })
        .catch(error => {
            console.error('Помилка завантаження логотипу:', error);
            alert('Виникла помилка при завантаженні логотипу. Спробуйте ще раз.'); // Показати повідомлення про помилку
        });
    });

    // Закриття модальних вікон
    document.getElementById('closeLogoModal').addEventListener('click', function () {
        document.getElementById('uploadLogoModal').style.display = 'none';
    });

    document.getElementById('closeUploadFormModal').addEventListener('click', function () {
        document.getElementById('uploadFormModal').style.display = 'none';
    });

