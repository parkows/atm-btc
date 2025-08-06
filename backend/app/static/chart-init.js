// Inicialização do Chart.js

// Função para criar o gráfico de transações
function createTransactionsChart(transactionData) {
    const ctx = document.getElementById('transactionsChart').getContext('2d');
    
    if (window.transactionsChart) {
        window.transactionsChart.destroy();
    }
    
    window.transactionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            datasets: [{
                label: 'Transações',
                data: [12, 19, 3, 5, 2, 3],
                borderColor: '#1e3c72',
                backgroundColor: 'rgba(30, 60, 114, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

// Função para criar o gráfico de status
function createStatusChart(statusData) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    if (window.statusChart) {
        window.statusChart.destroy();
    }
    
    const labels = Object.keys(statusData || {});
    const data = Object.values(statusData || {});
    const colors = ['#28a745', '#ffc107', '#dc3545', '#6c757d'];
    
    window.statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

// Exportar funções para o escopo global
window.createTransactionsChart = createTransactionsChart;
window.createStatusChart = createStatusChart;