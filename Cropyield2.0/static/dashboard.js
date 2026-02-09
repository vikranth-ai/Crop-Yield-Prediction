let modelsTrained = false;
let currentPredictions = null;
let modelResults = null;

// Tab switching
function switchTab(tabName) {
    const panes = document.querySelectorAll('.tab-pane');
    const buttons = document.querySelectorAll('.tab-btn');
    
    panes.forEach(p => p.classList.remove('active'));
    buttons.forEach(b => b.classList.remove('active'));
    
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
    
    // Load content when switching tabs
    if (tabName === 'dataset') loadDataset();
    if (tabName === 'eda') loadEDACharts();
    if (tabName === 'history') loadHistory();
    if (tabName === 'evaluation' && modelsTrained) loadActualVsPredictedCharts();
}

// Logout
async function logout() {
    await fetch('/logout');
    window.location.href = '/';
}

// Update range slider values
document.addEventListener('DOMContentLoaded', () => {
    const sliders = ['test-size', 'farm-area', 'fertilizer', 'pesticide', 'water'];
    
    sliders.forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            const valueSpan = document.getElementById(`${id}-value`);
            slider.addEventListener('input', (e) => {
                let value = e.target.value;
                if (id === 'test-size') value += '%';
                valueSpan.textContent = value;
            });
        }
    });
    
    loadDataset();
});

// Train Models
async function trainModels() {
    const testSize = document.getElementById('test-size').value / 100;
    const statusBox = document.getElementById('training-status');
    
    statusBox.className = 'status-box loading';
    statusBox.textContent = '⏳ Training models... This may take a moment.';
    
    try {
        const response = await fetch('/train-models', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ test_size: testSize })
        });
        
        const data = await response.json();
        
        if (data.success) {
            modelsTrained = true;
            modelResults = data.results;
            statusBox.className = 'status-box success';
            statusBox.textContent = '✅ Models trained successfully!';
            document.getElementById('predict-warning').style.display = 'none';
            updateEvaluationTab(data.results);
        } else {
            statusBox.className = 'status-box error';
            statusBox.textContent = '❌ Training failed: ' + data.message;
        }
    } catch (error) {
        statusBox.className = 'status-box error';
        statusBox.textContent = '❌ Network error';
    }
}

// Load Dataset
async function loadDataset() {
    try {
        const response = await fetch('/get-dataset');
        const data = await response.json();
        
        if (data.success) {
            const table = createTable(data.data);
            document.getElementById('dataset-table').innerHTML = table;
        }
    } catch (error) {
        console.error('Error loading dataset:', error);
    }
}

// Create HTML table
function createTable(data) {
    if (!data || data.length === 0) return '<p>No data available</p>';
    
    const headers = Object.keys(data[0]);
    let html = '<table><thead><tr>';
    
    headers.forEach(h => {
        html += `<th>${h}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(h => {
            const val = typeof row[h] === 'number' ? row[h].toFixed(2) : row[h];
            html += `<td>${val}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}

// Download Dataset
function downloadDataset() {
    window.location.href = '/download-dataset';
}

// Make Prediction
document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!modelsTrained) {
        alert('Please train models first!');
        return;
    }
    
    const formData = {
        farm_area: document.getElementById('farm-area').value,
        fertilizer: document.getElementById('fertilizer').value,
        pesticide: document.getElementById('pesticide').value,
        water: document.getElementById('water').value,
        crop: document.getElementById('crop').value,
        irrigation: document.getElementById('irrigation').value,
        soil: document.getElementById('soil').value,
        season: document.getElementById('season').value,
        save: false
    };
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPredictions = data.predictions;
            const avg = data.predictions.average;
            
            const resultBox = document.getElementById('prediction-result');
            resultBox.innerHTML = `🌾 Predicted Yield: <strong>${avg.toFixed(2)}</strong> tons`;
            resultBox.className = 'result-box show';
            
            document.getElementById('save-btn').disabled = false;
            updateComparisonTab(data.predictions);
        }
    } catch (error) {
        alert('Prediction failed: ' + error.message);
    }
});

// Save Prediction
async function savePrediction() {
    if (!currentPredictions) return;
    
    const formData = {
        farm_area: document.getElementById('farm-area').value,
        fertilizer: document.getElementById('fertilizer').value,
        pesticide: document.getElementById('pesticide').value,
        water: document.getElementById('water').value,
        crop: document.getElementById('crop').value,
        irrigation: document.getElementById('irrigation').value,
        soil: document.getElementById('soil').value,
        season: document.getElementById('season').value,
        save: true
    };
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Prediction saved successfully!');
            loadHistory();
        }
    } catch (error) {
        alert('Failed to save prediction');
    }
}

// Load EDA Charts
async function loadEDACharts() {
    try {
        const response = await fetch('/get-charts');
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('eda-charts');
            container.innerHTML = `
                <img src="${data.charts.crop_yield}" alt="Crop Yield">
                <img src="${data.charts.soil_yield}" alt="Soil Yield">
                <img src="${data.charts.correlation}" alt="Correlation">
            `;
        }
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}
// Update Evaluation Tab
function updateEvaluationTab(results) {
    const models = Object.keys(results);
    const tableData = models.map(name => ({
        Model: name,
        'R² Score': results[name].r2.toFixed(3),
        'MAE': results[name].mae.toFixed(3),
        'RMSE': results[name].rmse.toFixed(3)
    }));
    
    document.getElementById('eval-table').innerHTML = createTable(tableData);
    
    // R² Chart
    const r2Chart = new Chart(document.getElementById('r2-chart'), {
        type: 'bar',
        data: {
            labels: models,
            datasets: [{
                label: 'R² Score',
                data: models.map(m => results[m].r2),
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'R² Score Comparison' }
            }
        }
    });
    
    // RMSE Chart
    const rmseChart = new Chart(document.getElementById('rmse-chart'), {
        type: 'bar',
        data: {
            labels: models,
            datasets: [{
                label: 'RMSE',
                data: models.map(m => results[m].rmse),
                backgroundColor: 'rgba(239, 68, 68, 0.6)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'RMSE Comparison' }
            }
        }
    });
    
    // Load Actual vs Predicted charts
    loadActualVsPredictedCharts();
}

// Load Actual vs Predicted Charts
async function loadActualVsPredictedCharts() {
    try {
        const response = await fetch('/get-evaluation-charts');
        const data = await response.json();
        
        if (data.success) {
            const container = document.getElementById('actual-vs-predicted-charts');
            container.innerHTML = '';
            
            Object.entries(data.charts).forEach(([modelName, chartData]) => {
                const div = document.createElement('div');
                div.className = 'comparison-chart-item';
                div.innerHTML = `<img src="${chartData}" alt="${modelName}">`;
                container.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error loading actual vs predicted charts:', error);
    }
}

// Update Comparison Tab
function updateComparisonTab(predictions) {
    const models = Object.keys(predictions).filter(k => k !== 'average');
    
    const tableData = models.map(name => ({
        Model: name,
        'Predicted Yield': predictions[name].toFixed(3)
    }));
    
    document.getElementById('comparison-content').innerHTML = createTable(tableData);
    
    const canvas = document.getElementById('comparison-chart');
    if (window.comparisonChart) {
        window.comparisonChart.destroy();
    }
    
    window.comparisonChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: models,
            datasets: [{
                label: 'Predicted Yield',
                data: models.map(m => predictions[m]),
                backgroundColor: 'rgba(59, 130, 246, 0.6)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Model-wise Prediction Comparison' }
            }
        }
    });
}

// Load History
async function loadHistory() {
    try {
        const response = await fetch('/get-predictions');
        const data = await response.json();
        
        if (data.success && data.predictions.length > 0) {
            document.getElementById('history-table').innerHTML = createTable(data.predictions);
        } else {
            document.getElementById('history-table').innerHTML = '<p class="info">No predictions yet</p>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Download History
function downloadHistory() {
    window.location.href = '/download-predictions';
}