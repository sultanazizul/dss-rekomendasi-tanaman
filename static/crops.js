document.addEventListener('DOMContentLoaded', async () => {
    const cropsGrid = document.getElementById('cropsGrid');
    const loading = document.getElementById('loading');

    try {
        const response = await fetch('/api/crops');
        if (!response.ok) throw new Error('Gagal mengambil data tanaman');

        const crops = await response.json();

        loading.classList.add('hidden');
        cropsGrid.classList.remove('hidden');

        displayCrops(crops);
    } catch (error) {
        console.error('Error:', error);
        loading.innerHTML = '<p style="color: red;">Terjadi kesalahan saat memuat data.</p>';
    }

    function displayCrops(crops) {
        cropsGrid.innerHTML = '';

        crops.forEach(crop => {
            const card = document.createElement('div');
            card.className = 'crop-card';

            card.innerHTML = `
                <div class="crop-header">
                    <h3>${crop.name}</h3>
                    <span class="badge">${crop.soil_type}</span>
                </div>
                <p class="crop-desc">${crop.description || 'Tidak ada deskripsi.'}</p>
                
                <div class="crop-details">
                    <div class="detail-item">
                        <i class="fa-solid fa-flask"></i>
                        <span>pH: ${crop.ph_min} - ${crop.ph_max}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fa-solid fa-temperature-half"></i>
                        <span>Suhu: ${crop.temp_min}°C - ${crop.temp_max}°C</span>
                    </div>
                    <div class="detail-item">
                        <i class="fa-solid fa-cloud-rain"></i>
                        <span>Hujan: ${crop.rain_min} - ${crop.rain_max} mm</span>
                    </div>
                    <div class="detail-item">
                        <i class="fa-solid fa-sun"></i>
                        <span>Matahari: ${crop.sun_requirement}</span>
                    </div>
                    <div class="detail-item">
                        <i class="fa-solid fa-droplet"></i>
                        <span>Irigasi: ${crop.irrigation_need}</span>
                    </div>
                </div>
            `;

            cropsGrid.appendChild(card);
        });
    }
});
