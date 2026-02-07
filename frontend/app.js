// NutriScan AI - Frontend Controller

const API_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:5000' 
    : ''; // Relative path for production/Render

// --- DOM Elements ---
const tabs = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Input Elements
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const uploadPreview = document.getElementById('uploadPreview');
const previewImage = document.getElementById('previewImage');
const uploadBtn = document.getElementById('uploadBtn');
const removeImageBtn = document.getElementById('removeImageBtn');
const manualForm = document.getElementById('nutritionForm');
const resetBtn = document.getElementById('resetBtn');

// Result/State Elements
const emptyState = document.getElementById('emptyState');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// Result Data Elements
const productCard = document.getElementById('productCard');
const productNameText = document.getElementById('productNameText');
const scoreValue = document.getElementById('scoreValue');
const scoreCirclePath = document.getElementById('scoreCirclePath');
const classificationBadge = document.getElementById('classificationBadge');
const classificationText = document.getElementById('classificationText');
const classificationSummary = document.getElementById('classificationSummary');
const warningsCard = document.getElementById('warningsCard');
const warningsList = document.getElementById('warningsList');
const pointsList = document.getElementById('pointsList');
const recommendationsList = document.getElementById('recommendationsList');
const alternativesCard = document.getElementById('alternativesCard');
const alternativesList = document.getElementById('alternativesList');
const qualityScoreValue = document.getElementById('qualityScoreValue');
const qualityScoreBar = document.getElementById('qualityScoreBar');
const riskScoreValue = document.getElementById('riskScoreValue');
const riskScoreBar = document.getElementById('riskScoreBar');
const nutrientGrid = document.getElementById('nutrientGrid');

// --- Initialization ---
function init() {
    setupTabs();
    setupImageUpload();
    setupManualForm();
}

// --- Tab Logic ---
function setupTabs() {
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Deactivate all
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Activate current
            tab.classList.add('active');
            const targetId = 'content' + tab.dataset.tab.charAt(0).toUpperCase() + tab.dataset.tab.slice(1);
            document.getElementById(targetId).classList.add('active');
        });
    });
}

// --- Image Upload Logic ---
function setupImageUpload() {
    // Click to upload
    uploadArea.addEventListener('click', () => imageInput.click());

    // Drag & Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
        uploadArea.style.background = '#f0fdf4';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border-light)';
        uploadArea.style.background = '#f8fafc';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-light)';
        uploadArea.style.background = '#f8fafc';

        if (e.dataTransfer.files.length > 0) {
            handleImageSelect(e.dataTransfer.files[0]);
        }
    });

    // File Input Change
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageSelect(e.target.files[0]);
        }
    });

    // Remove Image
    removeImageBtn.addEventListener('click', resetImageUpload);

    // Upload Action
    uploadBtn.addEventListener('click', processImageOCR);
}

function handleImageSelect(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file (JPG, PNG).');
        return;
    }

    // Determine if file is too large (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('Image is too large. Max size is 16MB.');
        return;
    }

    window.selectedImage = file;

    // Show Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        uploadPreview.style.display = 'block';
        uploadBtn.disabled = false;
        hideError();
    };
    reader.readAsDataURL(file);
}

function resetImageUpload() {
    window.selectedImage = null;
    imageInput.value = '';
    previewImage.src = '';
    uploadArea.style.display = 'block';
    uploadPreview.style.display = 'none';
    uploadBtn.disabled = true;
    hideError();
}

// --- Manual Form Logic ---
function setupManualForm() {
    manualForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await analyzeFood();
    });

    resetBtn.addEventListener('click', () => {
        manualForm.reset();
        resetImageUpload();
        showEmptyState();
    });
}

// --- API Interactions ---

async function processImageOCR() {
    if (!window.selectedImage) return;

    setLoading(true);
    hideError();

    // Check Backend Health first
    const isOnline = await checkBackendHealth();

    if (!isOnline) {
        setLoading(false);
        showError('Backend offline. Is the server running?');
        return;
    }

    // Warn if taking too long
    window.slowRequestTimer = setTimeout(() => {
        if (document.getElementById('loadingIndicator').style.display !== 'none') {
            const msg = document.createElement('div');
            msg.id = 'slowRequestMsg';
            msg.textContent = 'Analysis is taking longer than usual (optimizing image)...';
            msg.style.color = '#666';
            msg.style.marginTop = '10px';
            msg.style.fontSize = '0.9rem';
            document.getElementById('loadingIndicator').appendChild(msg);
        }
    }, 8000);

    try {
        const formData = new FormData();
        formData.append('image', window.selectedImage);

        // timeout after 30s
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch(`${API_URL}/api/upload-image`, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            const error = await response.json();
            // Handle "Product Found but need label" case if backend sends specific code
            if (error.code === 'PRODUCT_NOT_FOUND_NEED_LABEL') {
                showError(error.suggestion);
                return;
            }
            throw new Error(error.error || 'Failed to process image');
        }

        const result = await response.json();

        // Populate inputs if extracted
        if (result.extracted_values) {
            populateManualForm(result.extracted_values);
        }

        // We might want to switch to manual tab if extraction was partial, but for now just show results
        displayResults(result);

    } catch (err) {
        console.error('OCR Error:', err);
        showError(err.message || 'Error processing image. Is the server running?');
    } finally {
        setLoading(false);
        if (window.slowRequestTimer) clearTimeout(window.slowRequestTimer);
        const slowMsg = document.getElementById('slowRequestMsg');
        if (slowMsg) slowMsg.remove();
    }
}

async function analyzeFood() {
    setLoading(true);
    hideError();

    try {
        const formData = new FormData(manualForm);
        const data = Object.fromEntries(formData.entries());

        // Convert Strings to Numbers
        const nutritionData = {
            calories: parseFloat(data.calories) || 0,
            protein: parseFloat(data.protein) || 0,
            carbs: parseFloat(data.carbs) || 0,
            fat: parseFloat(data.fat) || 0,
            sugar: parseFloat(data.sugar) || 0,
            fiber: parseFloat(data.fiber) || 0,
            sodium: parseFloat(data.sodium) || 0,
            saturated_fat: parseFloat(data.saturated_fat) || 0,
            product_name: data.product_name || '' // Not in new form but good for compat
        };

        const response = await fetch(`${API_URL}/api/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nutritionData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }

        const result = await response.json();
        displayResults(result);

    } catch (err) {
        console.error('Analysis Error:', err);
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

function populateManualForm(values) {
    // Switch to manual tab to show values? Maybe.
    // Let's just fill the inputs.
    for (const [key, value] of Object.entries(values)) {
        const input = document.getElementById(key);
        if (input) input.value = value;
    }
}

// --- UI Updates ---

function displayResults(data) {
    const {
        classification,
        nutrition_score,
        detailed_score,
        traffic_lights,
        alternatives,
        warnings,
        explanation,
        product_name
    } = data;

    // Hide Empty State
    emptyState.style.display = 'none';
    resultsSection.style.display = 'block';

    // 1. Product Name
    productNameText.textContent = product_name || 'Analyzed Product';

    // 2. Score
    // Animate the circle
    const score = Math.round(nutrition_score);
    scoreValue.textContent = score;
    // Stroke Dasharray: first value is length of stroke, second is gap. 
    // Circumference is 100 (approx 2*PI*15.9155). So score is the length.
    scoreCirclePath.setAttribute('stroke-dasharray', `${score}, 100`);

    // Colorize circle based on score/verdict
    updateVerdictColors(classification);

    // 3. Classification
    classificationText.textContent = classification;
    classificationSummary.textContent = explanation.summary;

    // 4. Warnings
    displayWarnings(warnings);

    // 5. Lists
    displayList(pointsList, explanation.key_points);
    displayList(pointsList, explanation.key_points);
    displayList(recommendationsList, explanation.recommendations);

    // 6. Detailed Scores
    if (detailed_score) {
        qualityScoreValue.textContent = `${Math.round(detailed_score.quality)}/50`; // Actually max is ~100 in calc? logic says max 50+50=100
        // Wait, logic says quality_score = prot(50) + fiber(50) = 100 max.
        qualityScoreBar.style.width = `${Math.min(100, detailed_score.quality)}%`;

        riskScoreValue.textContent = `${Math.round(detailed_score.risk)}/100`;
        riskScoreBar.style.width = `${Math.min(100, detailed_score.risk)}%`;
    }

    // 7. Traffic Lights
    displayTrafficLights(traffic_lights, data.input_values);

    // 8. Alternatives
    displayAlternatives(alternatives);
}

function displayTrafficLights(lights, values) {
    if (!nutrientGrid) return;
    nutrientGrid.innerHTML = '';

    if (!lights) return; // Should be object

    // Filter explicit nutrients we care about
    const order = ['calories', 'protein', 'fiber', 'sugar', 'sodium', 'saturated_fat'];
    const labels = {
        'calories': 'Calories',
        'protein': 'Protein',
        'fiber': 'Fiber',
        'sugar': 'Sugar',
        'sodium': 'Sodium',
        'saturated_fat': 'Sat. Fat'
    };

    order.forEach(key => {
        const val = values[key];
        const color = lights[key] || 'neutral'; // green, yellow, red, neutral
        if (val !== undefined) {
            const div = document.createElement('div');
            div.className = `nutrient-item ${color}`;
            div.innerHTML = `
                <span class="nutrient-label">${labels[key]}</span>
                <span class="nutrient-value">${val}</span>
                <span class="traffic-dot"></span>
             `;
            nutrientGrid.appendChild(div);
        }
    });
}

function displayAlternatives(alts) {
    if (!alternativesCard) return;

    if (!alts || alts.length === 0) {
        alternativesCard.style.display = 'none';
        return;
    }

    alternativesCard.style.display = 'block'; // Ensure parent row is visible
    alternativesList.innerHTML = '';

    alts.forEach(alt => {
        const div = document.createElement('div');
        div.className = 'alt-item';
        div.textContent = `🥗 ${alt}`;
        alternativesList.appendChild(div);
    });
}

function updateVerdictColors(verdict) {
    const root = document.documentElement;
    // The CSS handles colors via data-verdict attribute on the container or badge
    // We added data-verdict to the .classification-card or similar wrapper in styles?
    // Let's rely on the badge specific logic or add a data attribute to the parent

    // In CSS we used: [data-verdict="Healthy"] .circle 
    // So let's add it to the resultsSection or a common parent
    const dashboardRow = document.querySelector('.dashboard-row.primary');
    if (dashboardRow) {
        dashboardRow.setAttribute('data-verdict', verdict);
    }
}

function displayWarnings(warnings) {
    if (!warnings || warnings.length === 0) {
        warningsCard.style.display = 'none';
        return;
    }

    warningsCard.style.display = 'grid'; // it's a grid item in row
    warningsList.innerHTML = '';

    warnings.forEach(w => {
        const tag = document.createElement('span');
        tag.className = 'warning-tag';
        tag.textContent = `⚠️ ${w.message}`; // Simplified for new UI
        warningsList.appendChild(tag);
    });
}

function displayList(element, items) {
    element.innerHTML = '';
    if (!items || items.length === 0) {
        element.innerHTML = '<li>No specific data available.</li>';
        return;
    }
    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        element.appendChild(li);
    });
}

function setLoading(isLoading) {
    if (isLoading) {
        emptyState.style.display = 'none';
        resultsSection.style.display = 'none';
        loadingIndicator.style.display = 'flex';
    } else {
        loadingIndicator.style.display = 'none';
    }
}

function showEmptyState() {
    emptyState.style.display = 'flex';
    resultsSection.style.display = 'none';
    loadingIndicator.style.display = 'none';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showError(msg) {
    errorText.textContent = msg;
    errorMessage.style.display = 'flex';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function showToast(msg, type = 'error') {
    errorText.textContent = msg;
    errorMessage.style.display = 'flex';
    errorMessage.style.backgroundColor = type === 'info' ? '#3b82f6' : '#ef4444';
    // Don't auto-hide info messages immediately
    if (type !== 'info') {
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
}


async function checkBackendHealth() {
    try {
        const res = await fetch(`${API_URL}/api/health`, { method: 'GET', mode: 'cors' });
        return res.ok;
    } catch (e) {
        return false;
    }
}

// --- Start ---
init();

