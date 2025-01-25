document.addEventListener('DOMContentLoaded', function () {
    const regionLinks = document.querySelectorAll('.region-link');

    regionLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const regionSlug = this.getAttribute('data-region-slug');
            const regionId = this.closest('tr').getAttribute('data-region-id');
            FetchfetchSeasons(regionSlug, regionId);
        });
    });

    function fetchSeasons(regionSlug, regionId) {
        fetch(`/seasons/${regionSlug}`)
            .then(response => response.json())
            .then(data => {
                displaySeasons(data.seasons, regionId);
            })
            .catch(error => console.error('Error fetching seasons:', error));
    }

    function displaySeasons(seasons, regionId) {
        const seasonsContainer = document.getElementById('seasons-container');
        seasonsContainer.innerHTML = ''; // Clear previous content

        const regionsList = document.getElementById('regions-list');
        const regionRows = regionsList.querySelectorAll('tr');
        regionRows.forEach(row => row.classList.remove('selected-region')); // Remove previous selection

        const selectedRow = regionsList.querySelector(`tr[data-region-id="${regionId}"]`);
        if (selectedRow) {
            selectedRow.classList.add('selected-region');
        }

        if (seasons.length === 0) {
            seasonsContainer.innerHTML = '<p>No seasons available for this region.</p>';
            return;
        }

        const seasonsList = document.createElement('ul');
        seasons.forEach(season => {
            const seasonItem = document.createElement('li');
            seasonItem.textContent = season.name;
            seasonsList.appendChild(seasonItem);
        });

        seasonsContainer.appendChild(seasonsList);
    }
});

