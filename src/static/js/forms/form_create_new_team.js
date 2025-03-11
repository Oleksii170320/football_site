$(document).ready(function () {

    // Встановлення обробників подій для вводу
    $('#teamName, #cityName, #regionName').on('input change', updateFullNameAndSlug);

    function updateFullNameAndSlug() {
        let teamName = $('#teamName').val().trim();
        let cityName = $('#cityName').val().trim();
        let regionName = $('#regionName').find(':selected').text().trim();
        let regionSlug = $('#regionName').find(':selected').attr('data-slug');


        if (!teamName || !cityName || regionName === "Оберіть область") {
            $('#full-name-input').val('');
            $('#team_slug, #teamSlugInput').val('');
            $('#regionSlugInput').val('');
            return;
        }

        let fullName = `${teamName} (${cityName}, ${regionName} обл.)`;
        $('#full-name-input').val(fullName);

        let slug = convertToSlug(`${teamName}-${cityName}`);
        $('#team_slug, #teamSlugInput').val(slug);
        $('#regionSlugInput').val(regionSlug); // Оновлюємо слаг

    }

    // Додаємо обробник події для випадаючого списку областей


$('#regionName').change(function () {
    let selectedOption = $(this).find(':selected');
    console.log("Змінилось значення!");
    console.log("Область:", selectedOption.text());
    console.log("Slug області:", selectedOption.attr('data-slug'));
});



    function convertToSlug(text) {
        const cyrillicToLatinMap = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'є': 'ye', 'э': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ю': 'yu', 'я': 'ya', 'ь': '', 'ъ': '', ' ': '-',
            '"': '', ',': '', '.': '', '—': '-', '’': '', "'": ''
        };

        return text.toLowerCase()
            .split('')
            .map(char => cyrillicToLatinMap[char] || char)
            .join('')
            .replace(/[^a-z0-9-]/g, '')  // Видаляємо всі не-латинські символи, цифри та дефіси
            .replace(/-+/g, '-'); // Замінюємо кілька дефісів на один
    }

    // Динамічний пошук стадіонів
    $('#team-stadium-input').on('input', function () {
        const query = $(this).val();
        if (query.length >= 2) {
            $.getJSON(`/stadiums/search?query=${encodeURIComponent(query)}`, function (data) {
                const stadiumSuggestions = $('#stadiumSuggestions').empty();
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(stadium => {
                        $('<div>', {
                            class: 'list-group-item',
                            text: `${stadium.name} (${stadium.city})`
                        }).on('click', function () {
                            $('#team-stadium-input').val(stadium.name);
                            $('#stadiumId').val(stadium.id);
                            stadiumSuggestions.empty();
                        }).appendTo(stadiumSuggestions);
                    });
                } else {
                    stadiumSuggestions.html('<div class="list-group-item">Нічого не знайдено</div>');
                }
            });
        } else {
            $('#stadiumSuggestions').empty();
        }
    });

    // Оновлення слагу регіону
    $('#regionName').on('change', function () {
        const selectedSlug = $(this).find(':selected').data('slug');
        $('#regionSlugInput').val(selectedSlug);
        $('#selectedRegionSlug').text(selectedSlug);
        updateFullNameAndSlug(); // Додано виклик функції оновлення
    });

    // Обробка форми створення команди
    $('#teamCreateForm').on('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        formData.append('region', $('#regionSlugPage').val());
        formData.append('season', $('#seasonSlugPage').val());

        $.ajax({
            url: '/teams/new_team',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                $('#teamCreateForm')[0].reset();
                $('#successMessage').show().delay(5000).fadeOut();
                $('#uploadLogoModal').show();
                const team_id = data.id;

                $('#addLogo').on('click', function () {
                    $('#uploadLogoModal').hide();
                    $('#uploadFormModal').show();
                    $('<input>', { type: 'hidden', name: 'team_id', value: team_id }).appendTo('#logoForm');
                });

                $('#completeHere').on('click', function () {
                    $('#uploadLogoModal').hide();
                    window.location.href = `/region/${formData.get('region')}/${formData.get('season')}/clubs`;
                });
            }
        });
    });

    // Обробка форми логотипу
    $('#logoForm').on('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        formData.append('region_slug', $('#regionSlugInput').val());
        formData.append('team_slug', $('#teamSlugInput').val());
        formData.append('region', $('#regionSlugPage').val());
        formData.append('season', $('#seasonSlugPage').val());

        $.ajax({
            url: '/teams/upload_logo',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                alert(`Логотип ${data.filename} успішно завантажено!`);
                window.location.href = `/region/${formData.get('region')}/${formData.get('season')}/clubs`;
            },
            error: function () {
                alert('Виникла помилка при завантаженні логотипу. Спробуйте ще раз.');
            }
        });
    });

    // Закриття модальних вікон
    $('#closeLogoModal').on('click', function () {
        $('#uploadLogoModal').hide();
    });

    $('#closeUploadFormModal').on('click', function () {
        $('#uploadFormModal').hide();
    });
});

