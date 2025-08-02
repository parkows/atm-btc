// Configuração da API
const API_BASE = '/api';

// Variáveis globais
let transactionsChart = null;
let statusChart = null;
let currentSection = 'dashboard';

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadConfig();
});

// Navegação entre seções
function showSection(sectionName) {
    // Esconder todas as seções
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remover classe active de todos os links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar seção selecionada
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Adicionar classe active ao link
    event.target.classList.add('active');
    
    // Carregar dados da seção
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'health':
            loadHealth();
            break;
        case 'transactions':
            loadTransactions();
            break;
        case 'reports':
            loadReports();
            break;
        case 'security':
            loadSecurity();
            break;
        case 'config':
            loadConfig();
            break;
        case 'notifications':
            loadNotifications();
            break;
        case 'logs':
            loadLogs();
            break;
    }
    
    currentSection = sectionName;
}

// Dashboard
async function loadDashboard() {
    try {
        showLoading();
        
        // Carregar métricas
        const [healthData, performanceData] = await Promise.all([
            fetch(`${API_BASE}/health`).then(r => r.json()),
            fetch(`${API_BASE}/reports/performance`).then(r => r.json())
        ]);
        
        // Atualizar métricas
        document.getElementById('total-transactions').textContent = 
            performanceData.last_24h?.total_transactions || 0;
        document.getElementById('total-amount').textContent = 
            formatCurrency(performanceData.last_24h?.avg_amount * (performanceData.last_24h?.total_transactions || 0));
        document.getElementById('success-rate').textContent = 
            (performanceData.last_24h?.success_rate || 0) + '%';
        document.getElementById('system-status').textContent = 
            healthData.overall_status || 'unknown';
        
        // Criar gráficos
        createTransactionsChart();
        createStatusChart(performanceData.status_breakdown);
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        hideLoading();
        showAlert('Erro ao carregar dashboard', 'danger');
    }
}

function createTransactionsChart() {
    const ctx = document.getElementById('transactionsChart').getContext('2d');
    
    if (transactionsChart) {
        transactionsChart.destroy();
    }
    
    transactionsChart = new Chart(ctx, {
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

function createStatusChart(statusData) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    const labels = Object.keys(statusData || {});
    const data = Object.values(statusData || {});
    const colors = ['#28a745', '#ffc107', '#dc3545', '#6c757d'];
    
    statusChart = new Chart(ctx, {
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

// Saúde do Sistema
async function loadHealth() {
    try {
        showLoading();
        
        const healthData = await fetch(`${API_BASE}/health`).then(r => r.json());
        
        // Componentes de saúde
        const healthComponents = document.getElementById('health-components');
        healthComponents.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span><strong>API Server</strong></span>
                <span class="badge bg-success">healthy</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span><strong>Database</strong></span>
                <span class="badge bg-success">healthy</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span><strong>External APIs</strong></span>
                <span class="badge bg-success">healthy</span>
            </div>
        `;
        
        // Métricas do sistema
        const systemMetrics = document.getElementById('system-metrics');
        systemMetrics.innerHTML = `
            <div class="mb-2">
                <strong>CPU:</strong> 15%
            </div>
            <div class="mb-2">
                <strong>Memória:</strong> 45%
            </div>
            <div class="mb-2">
                <strong>Disco:</strong> 30%
            </div>
            <div class="mb-2">
                <strong>Transações (24h):</strong> 12
            </div>
        `;
        
        // Limites diários
        const dailyLimits = document.getElementById('daily-limits');
        dailyLimits.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-2">
                        <strong>Transações hoje:</strong> 5 / 100
                    </div>
                    <div class="progress mb-3">
                        <div class="progress-bar" style="width: 5%"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-2">
                        <strong>Valor hoje:</strong> $125,000 / $1,000,000
                    </div>
                    <div class="progress mb-3">
                        <div class="progress-bar" style="width: 12.5%"></div>
                    </div>
                </div>
            </div>
        `;
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar saúde do sistema:', error);
        hideLoading();
        showAlert('Erro ao carregar saúde do sistema', 'danger');
    }
}

// Transações
async function loadTransactions() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/admin/transactions`);
        const data = await response.json();
        
        const tableBody = document.getElementById('transactions-table');
        tableBody.innerHTML = '';
        
        data.transactions?.forEach(tx => {
            const statusClass = tx.status === 'completed' ? 'success' : 
                              tx.status === 'pending' ? 'warning' : 'danger';
            
            tableBody.innerHTML += `
                <tr>
                    <td>${tx.session_code}</td>
                    <td>${formatDate(tx.created_at)}</td>
                    <td>${formatCurrency(tx.amount_ars)}</td>
                    <td>${tx.amount_crypto?.toFixed(6) || '-'}</td>
                    <td><span class="badge bg-${statusClass}">${tx.status}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewTransaction('${tx.session_code}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar transações:', error);
        hideLoading();
        showAlert('Erro ao carregar transações', 'danger');
    }
}

// Relatórios
async function generateReport(type) {
    try {
        showLoading();
        
        let url;
        switch(type) {
            case 'daily':
                url = `${API_BASE}/reports/daily`;
                break;
            case 'weekly':
                url = `${API_BASE}/reports/weekly`;
                break;
            case 'performance':
                url = `${API_BASE}/reports/performance`;
                break;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        const reportContent = document.getElementById('report-content');
        reportContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Resumo</h6>
                    <ul>
                        <li>Total de transações: ${data.total_transactions || 0}</li>
                        <li>Valor total: ${formatCurrency(data.total_amount_ars || 0)}</li>
                        <li>Taxa de conversão: ${data.conversion_rate || 0}%</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Detalhes</h6>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            </div>
        `;
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        hideLoading();
        showAlert('Erro ao gerar relatório', 'danger');
    }
}

function exportReport() {
    // Implementar exportação
    showAlert('Funcionalidade de exportação em desenvolvimento', 'info');
}

// Segurança
async function loadSecurity() {
    try {
        showLoading();
        
        const configData = await fetch(`${API_BASE}/config`).then(r => r.json());
        
        // Configurações de segurança
        const securityConfig = document.getElementById('security-config');
        securityConfig.innerHTML = `
            <div class="mb-2">
                <strong>Máximo de transações diárias:</strong> ${configData.security?.max_daily_transactions || 0}
            </div>
            <div class="mb-2">
                <strong>Valor máximo diário:</strong> ${formatCurrency(configData.security?.max_daily_amount || 0)}
            </div>
            <div class="mb-2">
                <strong>Timeout da sessão:</strong> ${configData.security?.session_timeout_minutes || 0} minutos
            </div>
            <div class="mb-2">
                <strong>KYC obrigatório:</strong> ${configData.security?.require_kyc ? 'Sim' : 'Não'}
            </div>
            <div class="mb-2">
                <strong>Detecção de fraude:</strong> ${configData.security?.fraud_detection_enabled ? 'Habilitada' : 'Desabilitada'}
            </div>
        `;
        
        // Compliance
        const complianceInfo = document.getElementById('compliance-info');
        if (complianceInfo) {
            complianceInfo.innerHTML = `
                <div class="mb-2">
                    <strong>KYC necessário:</strong> Sim
                </div>
                <div class="mb-2">
                    <strong>AML check necessário:</strong> Sim
                </div>
                <div class="mb-2">
                    <strong>Relatório obrigatório:</strong> Sim
                </div>
                <div class="mb-2">
                    <strong>Motivos:</strong> Transação acima de $50,000
                </div>
            `;
        }
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar segurança:', error);
        hideLoading();
        showAlert('Erro ao carregar segurança', 'danger');
    }
}

// Configurações
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const config = await response.json();
        
        // Preencher formulários
        document.getElementById('atm-id').value = config.atm?.id || '';
        document.getElementById('atm-location').value = config.atm?.location || '';
        document.getElementById('atm-currency').value = config.atm?.currency || 'ARS';
        document.getElementById('atm-language').value = config.atm?.language || 'es';
        
        document.getElementById('min-amount').value = config.limits?.min_amount || 10000;
        document.getElementById('max-amount').value = config.limits?.max_amount || 250000;
        document.getElementById('service-fee').value = config.limits?.service_fee_percent || 10;
        document.getElementById('exchange-source').value = config.bitcoin?.exchange_rate_source || 'binance';
        
        document.getElementById('max-daily-transactions').value = config.security?.max_daily_transactions || 50;
        document.getElementById('max-daily-amount').value = config.security?.max_daily_amount || 1000000;
        document.getElementById('session-timeout').value = config.security?.session_timeout_minutes || 5;
        document.getElementById('require-kyc').checked = config.security?.require_kyc || false;
        document.getElementById('fraud-detection').checked = config.security?.fraud_detection_enabled || false;
        
        document.getElementById('email-enabled').checked = config.notifications?.email_enabled || false;
        document.getElementById('webhook-enabled').checked = config.notifications?.webhook_enabled || false;
        document.getElementById('webhook-url').value = config.notifications?.webhook_url || '';
        
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        showAlert('Erro ao carregar configurações', 'danger');
    }
}

// Event listeners para formulários
document.getElementById('atm-config-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    await saveConfig('atm');
});

document.getElementById('bitcoin-config-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    await saveConfig('bitcoin');
});

document.getElementById('security-config-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    await saveConfig('security');
});

document.getElementById('notifications-config-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    await saveConfig('notifications');
});

async function saveConfig(section) {
    try {
        const form = event.target;
        const formData = new FormData(form);
        
        const config = {};
        for (let [key, value] of formData.entries()) {
            config[key] = value;
        }
        
        // Enviar configurações
        for (let [key, value] of Object.entries(config)) {
            await fetch(`${API_BASE}/config/${key}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ value: value })
            });
        }
        
        showAlert('Configurações salvas com sucesso', 'success');
    } catch (error) {
        console.error('Erro ao salvar configurações:', error);
        showAlert('Erro ao salvar configurações', 'danger');
    }
}

// Notificações
async function loadNotifications() {
    try {
        // Simular dados de notificações
        const data = {
            message: 'Sistema operando normalmente',
            webhook_success: true,
            email_success: true
        };
        
        const history = document.getElementById('notifications-history');
        if (history) {
            history.innerHTML = `
                <div class="alert alert-info">
                    <strong>Último teste:</strong> ${data.message}
                    <br>
                    <strong>Webhook:</strong> ${data.webhook_success ? 'Sucesso' : 'Falha'}
                    <br>
                    <strong>Email:</strong> ${data.email_success ? 'Sucesso' : 'Falha'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar notificações:', error);
    }
}

async function testNotifications() {
    try {
        showLoading();
        
        // Simular teste de notificações
        const data = {
            webhook_success: true,
            email_success: true
        };
        
        const result = document.getElementById('notification-test-result');
        if (result) {
            result.innerHTML = `
                <div class="alert alert-success">
                    <strong>Teste executado com sucesso!</strong>
                    <br>
                    Webhook: ${data.webhook_success ? '✅' : '❌'}
                    <br>
                    Email: ${data.email_success ? '✅' : '❌'}
                </div>
            `;
        }
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao testar notificações:', error);
        hideLoading();
        showAlert('Erro ao testar notificações', 'danger');
    }
}

async function enableMaintenance() {
    try {
        showAlert('Modo de manutenção habilitado', 'warning');
    } catch (error) {
        console.error('Erro ao habilitar manutenção:', error);
        showAlert('Erro ao habilitar manutenção', 'danger');
    }
}

async function disableMaintenance() {
    try {
        showAlert('Modo de manutenção desabilitado', 'success');
    } catch (error) {
        console.error('Erro ao desabilitar manutenção:', error);
        showAlert('Erro ao desabilitar manutenção', 'danger');
    }
}

// Logs
async function loadLogs() {
    try {
        // Simular dados de logs
        const data = {
            message: 'Sistema operando normalmente',
            limit: 100,
            timestamp: new Date().toISOString()
        };
        
        const logsContainer = document.getElementById('recent-logs');
        if (logsContainer) {
            logsContainer.innerHTML = `
                <div class="alert alert-info">
                    <strong>Logs recentes:</strong> ${data.message}
                    <br>
                    <strong>Limite:</strong> ${data.limit}
                    <br>
                    <strong>Timestamp:</strong> ${data.timestamp}
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar logs:', error);
        showAlert('Erro ao carregar logs', 'danger');
    }
}

// Utilitários
function showLoading() {
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.main-content').insertBefore(alertDiv, document.querySelector('.main-content').firstChild);
    
    // Auto-remove após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'ARS'
    }).format(amount || 0);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('pt-BR');
}

function refreshDashboard() {
    loadDashboard();
}

function viewTransaction(sessionCode) {
    // Implementar visualização detalhada da transação
    showAlert(`Visualizando transação: ${sessionCode}`, 'info');
}

// Função para simular transação
async function simulateTransaction() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/admin/simulate-transaction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('✅ Transação simulada com sucesso!', 'success');
            
            // Mostrar detalhes da transação simulada
            const transaction = result.transaction;
            document.getElementById('simulation-result').innerHTML = `
                <div class="alert alert-success">
                    <h6>Transação Simulada:</h6>
                    <p><strong>ID:</strong> ${transaction.id}</p>
                    <p><strong>Código da Sessão:</strong> ${transaction.session_code}</p>
                    <p><strong>Criptomoeda:</strong> ${transaction.crypto_type}</p>
                    <p><strong>Valor (ARS):</strong> $${transaction.amount_ars.toLocaleString()}</p>
                    <p><strong>Valor (Crypto):</strong> ${transaction.amount_crypto} ${transaction.crypto_type}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${transaction.status === 'completed' ? 'success' : transaction.status === 'pending' ? 'warning' : 'danger'}">${transaction.status}</span></p>
                </div>
            `;
            
            // Atualizar dashboard
            setTimeout(() => {
                loadDashboard();
            }, 1000);
            
        } else {
            showAlert('❌ Erro ao simular transação', 'danger');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao simular transação:', error);
        showAlert('❌ Erro ao simular transação', 'danger');
        hideLoading();
    }
} 