document.addEventListener('DOMContentLoaded', () => {
    const questionContainer = document.getElementById('questionContainer');
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
    let questions = [];
    let userAnswers = {}; // Map question_id -> selected_option (A, B, C)
    let steps = []; // Array of arrays, chunking questions into steps

    // Grouping configuration: How many questions per page?
    // Let's group by category or just constant number.
    // Grouping by category is better UX.

    async function init() {
        try {
            const response = await fetch('/api/questions');
            if (!response.ok) throw new Error('Failed to fetch questions');
            const data = await response.json();
            questions = data;

            // Organize questions into steps based on category
            const grouped = {};
            questions.forEach(q => {
                if (!grouped[q.category]) grouped[q.category] = [];
                grouped[q.category].push(q);
            });

            // Convert grouped object to array of steps
            steps = Object.values(grouped);

            // Render first step
            renderStep();
            updateNavigation();
        } catch (error) {
            console.error(error);
            questionContainer.innerHTML = '<p class="error">Gagal memuat pertanyaan. Silakan refresh halaman.</p>';
        }
    }

    function renderStep() {
        questionContainer.innerHTML = '';
        const currentQuestions = steps[currentStep];

        // Add Title based on category of first question in step
        const categoryMap = {
            'ph': 'Kondisi Tanah (pH)',
            'rain': 'Curah Hujan',
            'temp': 'Suhu Udara',
            'sun': 'Sinar Matahari',
            'irrigation': 'Ketersediaan Air',
            'soil': 'Tekstur Tanah'
        };
        const cat = currentQuestions[0].category;
        const title = document.createElement('h2');
        title.textContent = categoryMap[cat] || 'Pertanyaan';
        questionContainer.appendChild(title);

        const desc = document.createElement('p');
        desc.className = 'step-desc';
        desc.textContent = 'Jawab pertanyaan berikut sesuai kondisi lahan Anda:';
        questionContainer.appendChild(desc);

        currentQuestions.forEach(q => {
            const qDiv = document.createElement('div');
            qDiv.className = 'input-group';
            qDiv.innerHTML = `<label>${q.text}</label>`;

            const optionsGrid = document.createElement('div');
            optionsGrid.className = 'options-grid';

            q.options.forEach(opt => {
                const isChecked = userAnswers[q.id] === opt.value_code;
                const label = document.createElement('label');
                label.className = `option-card ${isChecked ? 'selected' : ''}`;
                label.style.cursor = 'pointer';

                label.innerHTML = `
                    <input type="radio" name="${q.id}" value="${opt.value_code}" ${isChecked ? 'checked' : ''} class="hidden-radio">
                    <div class="card-content">
                        <span class="opt-label">${opt.label}</span>
                        <small class="opt-desc">${opt.description}</small>
                    </div>
                `;

                // Click handler
                label.addEventListener('click', () => {
                    // Remove selected class from siblings
                    optionsGrid.querySelectorAll('.option-card').forEach(el => el.classList.remove('selected'));
                    label.classList.add('selected');
                    label.querySelector('input').checked = true;
                    userAnswers[q.id] = opt.value_code;
                    updateNavigation(); // Enable next button if all answered
                });

                optionsGrid.appendChild(label);
            });

            qDiv.appendChild(optionsGrid);
            questionContainer.appendChild(qDiv);
        });

        // Update Progress
        const progress = ((currentStep + 1) / steps.length) * 100;
        progressFill.style.width = `${progress}%`;
    }

    function updateNavigation() {
        // Check if all questions in current step are answered
        const currentQuestions = steps[currentStep];
        const allAnswered = currentQuestions.every(q => userAnswers[q.id]);

        nextBtn.disabled = !allAnswered;
        submitBtn.disabled = !allAnswered;

        prevBtn.disabled = currentStep === 0;

        if (currentStep === steps.length - 1) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }

    nextBtn.addEventListener('click', () => {
        if (currentStep < steps.length - 1) {
            currentStep++;
            renderStep();
            updateNavigation();
            window.scrollTo(0, 0);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            renderStep();
            updateNavigation();
            window.scrollTo(0, 0);
        }
    });

    wizardForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loadingDiv.classList.remove('hidden');

        // Prepare payload: List of {question_id: "...", selected_option: "..."}
        const answersList = Object.keys(userAnswers).map(qid => ({
            question_id: qid,
            selected_option: userAnswers[qid]
        }));

        const payload = { answers: answersList };

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const result = await response.json();
            displayResults(result.recommendations);

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

        recommendations.forEach((rec, index) => {
            const percentage = (rec.score * 100).toFixed(1);
            const item = document.createElement('div');
            item.className = 'rec-item';
            // Add slight delay for animation effect
            item.style.animationDelay = `${index * 0.1}s`;

            item.innerHTML = `
                <div class="rec-info">
                    <h3>${rec.crop_name}</h3>
                    <p>Kecocokan: <strong>${percentage}%</strong></p>
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
        userAnswers = {}; // Reset answers
        renderStep();
        updateNavigation();
        window.scrollTo(0, 0);
    });

    // Start
    init();
});
