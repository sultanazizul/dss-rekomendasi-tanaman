document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.step');
    const progressFill = document.getElementById('progressFill');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const wizardForm = document.getElementById('wizardForm');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const recommendationList = document.getElementById('recommendationList');
    const restartBtn = document.getElementById('restartBtn');

    let currentStep = 0;
    const totalSteps = steps.length;

    // Range Input Listeners to update values
    const ranges = ['ph', 'rain', 'temp'];
    ranges.forEach(id => {
        const input = document.getElementById(id);
        const display = document.getElementById(id + 'Value');
        input.addEventListener('input', (e) => {
            let val = e.target.value;
            if (id === 'rain') val += ' mm';
            if (id === 'temp') val += '°C';
            display.textContent = val;
        });
    });

    function updateWizard() {
        // Show/Hide Steps
        steps.forEach((step, index) => {
            if (index === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Update Progress Bar
        const progress = ((currentStep + 1) / totalSteps) * 100;
        progressFill.style.width = `${progress}%`;

        // Button States
        prevBtn.disabled = currentStep === 0;

        if (currentStep === totalSteps - 1) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }

    nextBtn.addEventListener('click', () => {
        if (currentStep < totalSteps - 1) {
            currentStep++;
            updateWizard();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            updateWizard();
        }
    });

    wizardForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading
        loadingDiv.classList.remove('hidden');

        // Collect Data
        const formData = new FormData(wizardForm);
        const data = {
            ph: parseFloat(formData.get('ph')),
            rain: parseFloat(formData.get('rain')),
            temp: parseFloat(formData.get('temp')),
            sun: parseFloat(formData.get('sun')),
            irrigation: parseFloat(formData.get('irrigation')),
            soil: formData.get('soil')
        };

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const result = await response.json();
            displayResults(result.recommendations);

            // Hide form, show results
            wizardForm.classList.add('hidden');
            resultsDiv.classList.remove('hidden');

        } catch (error) {
            console.error('Error:', error);
            alert('Terjadi kesalahan saat memproses data. Silakan coba lagi.');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });

    function displayResults(recommendations) {
        recommendationList.innerHTML = '';

        if (recommendations.length === 0) {
            recommendationList.innerHTML = '<p>Tidak ada tanaman yang cocok dengan kriteria ini.</p>';
            return;
        }

        recommendations.forEach(rec => {
            const percentage = (rec.score * 100).toFixed(1);
            const item = document.createElement('div');
            item.className = 'rec-item';
            item.innerHTML = `
                <div class="rec-info">
                    <h3>${rec.crop_name}</h3>
                    <p>Kecocokan: ${percentage}%</p>
                </div>
                <div class="rec-score">
                    ${rec.score.toFixed(3)}
                </div>
            `;
            recommendationList.appendChild(item);
        });
    }

    restartBtn.addEventListener('click', () => {
        resultsDiv.classList.add('hidden');
        wizardForm.classList.remove('hidden');
        currentStep = 0;
        updateWizard();
        wizardForm.reset();
        // Reset range displays
        document.getElementById('phValue').textContent = '7.0';
        document.getElementById('rainValue').textContent = '1500 mm';
        document.getElementById('tempValue').textContent = '28°C';
    });

    // Initialize
    updateWizard();
});
