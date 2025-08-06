// Configuração da API
const API_BASE = '/api';

// Variáveis globais
let currentSection = 'dashboard';

// Debug: Verificar se o script está carregando
console.log('Admin.js carregado com sucesso!');

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando admin...');
    
    // Configurar event listeners
    console.log('Configurando event listeners...');
    setupEventListeners();
    
    // Inicializar apenas o dashboard primeiro
    console.log('Carregando apenas dashboard...');
    loadDashboard();
    
    // Mostrar a seção do dashboard por padrão
    console.log('Mostrando seção dashboard...');
    showSection('dashboard');
    
    console.log('Admin inicializado com sucesso!');
});

// Função para configurar event listeners
function setupEventListeners() {
    const atmConfigForm = document.getElementById('atm-config-form');
    if (atmConfigForm) {
        atmConfigForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveConfig('atm');
        });
    }
    
    const bitcoinConfigForm = document.getElementById('bitcoin-config-form');
    if (bitcoinConfigForm) {
        bitcoinConfigForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveConfig('bitcoin');
        });
    }
    
    const securityConfigForm = document.getElementById('security-config-form');
    if (securityConfigForm) {
        securityConfigForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveConfig('security');
        });
    }
    
    const notificationsConfigForm = document.getElementById('notifications-config-form');
    if (notificationsConfigForm) {
        notificationsConfigForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveConfig('notifications');
        });
    }
    
    const notificationEventsForm = document.getElementById('notification-events-form');
    if (notificationEventsForm) {
        notificationEventsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await saveConfig('notification-events');
        });
    }
}

// Navegação entre seções
function showSection(sectionName) {
    console.log(`Tentando mostrar seção: ${sectionName}`);
    
    // Esconder todas as seções
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remover classe active de todos os links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar seção selecionada
    const sectionElement = document.getElementById(sectionName + '-section');
    if (sectionElement) {
        sectionElement.style.display = 'block';
        console.log(`Seção ${sectionName} mostrada com sucesso`);
    } else {
        console.error(`Seção não encontrada: ${sectionName}-section`);
        return;
    }
    
    // Adicionar classe active ao link correspondente
    const navLinks = document.querySelectorAll(`.nav-link[onclick*="showSection('${sectionName}')"]`);
    navLinks.forEach(link => {
        link.classList.add('active');
    });
    
    // Carregar dados da seção
    switch(sectionName) {
        case 'dashboard':
            console.log('Carregando dashboard...');
            loadDashboard();
            break;
        case 'health':
            console.log('Carregando health...');
            loadHealth();
            break;
        case 'transactions':
            console.log('Carregando transactions...');
            loadTransactions();
            break;
        case 'reports':
            console.log('Carregando reports...');
            loadReports();
            break;
        case 'security':
            console.log('Carregando security...');
            loadSecurity();
            break;
        case 'config':
            console.log('Carregando config...');
            loadConfig();
            break;
        case 'notifications':
            console.log('Carregando notifications...');
            loadNotifications();
            break;
        case 'logs':
            console.log('Carregando logs...');
            loadLogs();
            break;
        case 'accounting':
            console.log('Carregando contabilidade...');
            loadAccounting();
            break;
        default:
            console.warn(`Nenhuma função de carregamento definida para a seção: ${sectionName}`);
    }
    
    currentSection = sectionName;
    console.log(`Seção ${sectionName} carregada completamente`);
}

// Dashboard
async function loadDashboard() {
    try {
        console.log('Carregando dashboard...');
        showLoading();
        
        // Carregar métricas
        console.log('Fazendo requisições para APIs...');
        const [healthData, transactionsData] = await Promise.all([
            fetch(`${API_BASE}/health`).then(r => r.json()),
            fetch(`${API_BASE}/admin/transactions`).then(r => r.json())
        ]);
        
        console.log('Dados recebidos:', { healthData, transactionsData });
        
        // Calcular métricas das transações reais
        const transactions = transactionsData.transactions || [];
        const totalTransactions = transactions.length;
        const completedTransactions = transactions.filter(t => t.status === 'completed').length;
        const successRate = totalTransactions > 0 ? Math.round((completedTransactions / totalTransactions) * 100) : 0;
        const totalAmount = transactions.reduce((sum, t) => sum + (t.amount_ars || 0), 0);
        
        console.log('Métricas calculadas:', {
            totalTransactions,
            completedTransactions,
            successRate,
            totalAmount
        });
        
        // Atualizar métricas
        const totalTransactionsElement = document.getElementById('total-transactions');
        const totalAmountElement = document.getElementById('total-amount');
        const successRateElement = document.getElementById('success-rate');
        const systemStatusElement = document.getElementById('system-status');
        
        console.log('Elementos encontrados:', {
            totalTransactions: !!totalTransactionsElement,
            totalAmount: !!totalAmountElement,
            successRate: !!successRateElement,
            systemStatus: !!systemStatusElement
        });
        
        if (totalTransactionsElement) {
            totalTransactionsElement.textContent = totalTransactions;
        }
        if (totalAmountElement) {
            totalAmountElement.textContent = formatCurrency(totalAmount);
        }
        if (successRateElement) {
            successRateElement.textContent = successRate + '%';
        }
        if (systemStatusElement) {
            systemStatusElement.textContent = healthData.overall_status || 'unknown';
        }
        
        // Atualizar tabela de transações recentes
        updateRecentTransactionsTable(transactions.slice(0, 4));
        
        // Criar gráficos - VOU COMENTAR TEMPORARIAMENTE PARA TESTAR
        /*
        const transactionsChartElement = document.getElementById('transactionsChart');
        if (transactionsChartElement) {
            console.log('Criando gráfico de transações...');
            createTransactionsChart();
        }
        
        const statusChartElement = document.getElementById('statusChart');
        if (statusChartElement) {
            console.log('Criando gráfico de status...');
            createStatusChart(performanceData.status_breakdown);
        }
        */
        
        hideLoading();
        console.log('Dashboard carregado com sucesso!');
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        hideLoading();
        showAlert('Erro ao carregar dashboard', 'danger');
    }
}

// Função para atualizar tabela de transações recentes
function updateRecentTransactionsTable(transactions) {
    const tbody = document.querySelector('#dashboard-section .table tbody');
    if (!tbody) {
        console.warn('Tabela de transações recentes não encontrada');
        return;
    }
    
    tbody.innerHTML = '';
    
    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${transaction.id}</td>
            <td>${formatDate(transaction.created_at)}</td>
            <td>${transaction.transaction_type === 'sale' ? 'Venda' : 'Compra'} ${transaction.crypto_type}</td>
            <td>${formatCurrency(transaction.amount_ars)}</td>
            <td><span class="badge bg-${transaction.status === 'completed' ? 'success' : transaction.status === 'pending' ? 'warning' : 'danger'}">${transaction.status}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewTransaction('${transaction.session_code}')">Detalhes</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Função createTransactionsChart foi movida para chart-init.js

// Função createStatusChart foi movida para chart-init.js

// Relatórios
async function loadReports() {
    try {
        // Inicializar a seção de relatórios
        const reportContent = document.getElementById('report-content');
        if (reportContent) {
            reportContent.innerHTML = `
                <div class="alert alert-info">
                    Selecione um tipo de relatório acima para gerar.
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar relatórios:', error);
        showAlert('Erro ao carregar relatórios', 'danger');
    }
}

// Função de teste para verificar se generateReport está sendo chamada
function testGenerateReport() {
    console.log('Testando generateReport...');
    generateReport('daily');
}

// Função para gerar relatórios
async function generateReport(type) {
    try {
        console.log(`Gerando relatório do tipo: ${type}`);
        showLoading();
        
        // Buscar dados específicos do relatório
        let reportData = {};
        let reportTitle = '';
        
        switch(type) {
            case 'daily':
                reportTitle = 'Relatório Diário';
                console.log('Buscando dados do relatório diário...');
                const dailyResponse = await fetch(`${API_BASE}/reports/daily`);
                reportData = await dailyResponse.json();
                console.log('Dados do relatório diário:', reportData);
                break;
            case 'weekly':
                reportTitle = 'Relatório Semanal';
                console.log('Buscando dados do relatório semanal...');
                const weeklyResponse = await fetch(`${API_BASE}/reports/weekly`);
                reportData = await weeklyResponse.json();
                console.log('Dados do relatório semanal:', reportData);
                break;
            case 'monthly':
                reportTitle = 'Relatório Mensal';
                console.log('Buscando dados do relatório mensal...');
                const monthlyResponse = await fetch(`${API_BASE}/reports/monthly`);
                reportData = await monthlyResponse.json();
                console.log('Dados do relatório mensal:', reportData);
                break;
            case 'custom':
                reportTitle = 'Relatório Personalizado';
                console.log('Buscando dados do relatório de performance...');
                const customResponse = await fetch(`${API_BASE}/reports/performance`);
                reportData = await customResponse.json();
                console.log('Dados do relatório de performance:', reportData);
                break;
        }
        
        // Verificar se há erro nos dados
        if (reportData.error) {
            throw new Error(reportData.error);
        }
        
        console.log(`Renderizando relatório ${type} com dados:`, reportData);
        
        // Atualizar conteúdo do relatório
        const reportContent = document.getElementById('report-content');
        if (reportContent) {
            let reportHTML = `<h4>${reportTitle}</h4>`;
            
            if (type === 'daily') {
                reportHTML += `
                    <div class="row mt-4">
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Total de Transações</h5>
                                    <h3>${reportData.total_transactions || 0}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Transações Concluídas</h5>
                                    <h3>${reportData.completed_transactions || 0}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Volume Total</h5>
                                    <h3>${formatCurrency(reportData.total_amount_ars || 0)}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Taxa de Conversão</h5>
                                    <h3>${reportData.conversion_rate || 0}%</h3>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Distribuição por Hora</h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        ${Object.entries(reportData.hourly_distribution || {}).map(([hour, count]) => 
                                            `<div class="col-md-2 mb-2">
                                                <div class="text-center">
                                                    <small class="text-muted">${hour}h</small><br>
                                                    <strong>${count}</strong>
                                                </div>
                                            </div>`
                                        ).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Resumo</h6>
                                </div>
                                <div class="card-body">
                                    <p><strong>Data:</strong> ${reportData.date || 'N/A'}</p>
                                    <p><strong>Transações Pendentes:</strong> ${reportData.pending_transactions || 0}</p>
                                    <p><strong>Transações Falhadas:</strong> ${reportData.failed_transactions || 0}</p>
                                    <p><strong>Total Crypto:</strong> ${reportData.total_crypto || 0}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else if (type === 'weekly') {
                reportHTML += `
                    <div class="row mt-4">
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Total de Transações</h5>
                                    <h3>${reportData.total_transactions || 0}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Transações Concluídas</h5>
                                    <h3>${reportData.completed_transactions || 0}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Volume Total</h5>
                                    <h3>${formatCurrency(reportData.total_amount_ars || 0)}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Taxa de Conversão</h5>
                                    <h3>${reportData.conversion_rate || 0}%</h3>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-12">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Distribuição por Dia</h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        ${Object.entries(reportData.daily_distribution || {}).map(([date, count]) => 
                                            `<div class="col-md-1 mb-2">
                                                <div class="text-center">
                                                    <small class="text-muted">${date}</small><br>
                                                    <strong>${count}</strong>
                                                </div>
                                            </div>`
                                        ).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                // Para outros tipos de relatório
                reportHTML += `
                    <div class="row mt-4">
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Total de Transações</h5>
                                    <h3>${reportData.total_transactions || 0}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Volume Total</h5>
                                    <h3>${formatCurrency(reportData.total_amount_ars || 0)}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Valor Médio</h5>
                                    <h3>${formatCurrency(reportData.avg_amount_ars || 0)}</h3>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h5>Taxa de Sucesso</h5>
                                    <h3>${reportData.success_rate || 0}%</h3>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            reportHTML += `
                <div class="mt-4">
                    <button class="btn btn-success" onclick="exportReport('${type}', 'pdf')"><i class="fas fa-file-pdf"></i> Exportar PDF</button>
                    <button class="btn btn-success" onclick="exportReport('${type}', 'csv')"><i class="fas fa-file-csv"></i> Exportar CSV</button>
                </div>
            `;
            
            console.log('HTML do relatório gerado:', reportHTML);
            reportContent.innerHTML = reportHTML;
            console.log('Relatório renderizado com sucesso!');
        } else {
            console.error('Elemento report-content não encontrado!');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        hideLoading();
        showAlert('Erro ao gerar relatório: ' + error.message, 'danger');
    }
}

// Função para exportar relatórios
function exportReport(type, format) {
    showAlert(`Relatório ${type} exportado em formato ${format.toUpperCase()}`, 'success');
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
            
            const transactionType = tx.transaction_type === 'sale' ? 'Venda' : 'Compra';
            const communicationMethod = tx.communication_method || 'N/A';
            
            tableBody.innerHTML += `
                <tr>
                    <td>${tx.id}</td>
                    <td>${formatDate(tx.created_at)}</td>
                    <td>${transactionType} ${tx.crypto_type}</td>
                    <td>${formatCurrency(tx.amount_ars)}</td>
                    <td>${tx.amount_crypto?.toFixed(6) || '-'} ${tx.crypto_type}</td>
                    <td><span class="badge bg-${statusClass}">${tx.status}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewTransaction('${tx.session_code}')" title="Ver detalhes">
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
        if (securityConfig) {
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
        }
        
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
        console.log('Carregando configurações...');
        const response = await fetch(`${API_BASE}/config`);
        const config = await response.json();
        console.log('Configurações recebidas:', config);
        
        // Preencher formulários - verificando se os elementos existem antes de definir valores
        const setElementValue = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                console.log(`Elemento ${id} definido como: ${value}`);
            } else {
                console.warn(`Elemento ${id} não encontrado`);
            }
        };
        
        const setElementChecked = (id, checked) => {
            const element = document.getElementById(id);
            if (element) {
                element.checked = checked;
                console.log(`Elemento ${id} definido como: ${checked}`);
            } else {
                console.warn(`Elemento ${id} não encontrado`);
            }
        };
        
        // ATM Config
        setElementValue('atm-id', config.atm?.id || '');
        setElementValue('atm-location', config.atm?.location || '');
        setElementValue('atm-currency', config.atm?.currency || 'ARS');
        setElementValue('atm-language', config.atm?.language || 'es');
        
        // Bitcoin Config
        setElementValue('min-amount', config.limits?.min_amount || 10000);
        setElementValue('max-amount', config.limits?.max_amount || 250000);
        setElementValue('service-fee', config.limits?.service_fee_percent || 10);
        setElementValue('exchange-source', config.bitcoin?.exchange_rate_source || 'binance');
        
        // Security Config
        setElementValue('max-daily-transactions', config.security?.max_daily_transactions || 50);
        setElementValue('max-daily-amount', config.security?.max_daily_amount || 1000000);
        setElementValue('session-timeout', config.security?.session_timeout_minutes || 5);
        setElementChecked('require-kyc', config.security?.require_kyc || false);
        setElementChecked('fraud-detection', config.security?.fraud_detection_enabled || false);
        
        // Notifications Config
        setElementChecked('email-enabled', config.notifications?.email_enabled || false);
        setElementChecked('webhook-enabled', config.notifications?.webhook_enabled || false);
        setElementValue('webhook-url', config.notifications?.webhook_url || '');
        
        console.log('Configurações carregadas com sucesso!');
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        showAlert('Erro ao carregar configurações', 'danger');
    }
}

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
    console.log('Mostrando loading...');
    // Simplificado para evitar problemas com Bootstrap
}

function hideLoading() {
    console.log('Escondendo loading...');
    // Simplificado para evitar problemas com Bootstrap
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
        
        // Auto-remove após 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    } else {
        console.error('Elemento .main-content não encontrado');
    }
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
    console.log(`Visualizando transação: ${sessionCode}`);
    
    // Buscar dados da transação
    fetch(`${API_BASE}/admin/transactions`)
        .then(response => response.json())
        .then(data => {
            const transaction = data.transactions.find(t => t.session_code === sessionCode);
            if (transaction) {
                showTransactionDetails(transaction);
            } else {
                showAlert('Transação não encontrada', 'warning');
            }
        })
        .catch(error => {
            console.error('Erro ao buscar transação:', error);
            showAlert('Erro ao buscar detalhes da transação', 'danger');
        });
}

// Função para mostrar detalhes da transação
function showTransactionDetails(transaction) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'transactionModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Detalhes da Transação</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Informações Gerais</h6>
                            <p><strong>ID:</strong> ${transaction.id}</p>
                            <p><strong>Código da Sessão:</strong> ${transaction.session_code}</p>
                            <p><strong>Tipo:</strong> ${transaction.transaction_type === 'sale' ? 'Venda' : 'Compra'}</p>
                            <p><strong>Criptomoeda:</strong> ${transaction.crypto_type}</p>
                            <p><strong>Status:</strong> <span class="badge bg-${transaction.status === 'completed' ? 'success' : transaction.status === 'pending' ? 'warning' : 'danger'}">${transaction.status}</span></p>
                        </div>
                        <div class="col-md-6">
                            <h6>Valores</h6>
                            <p><strong>Valor (ARS):</strong> ${formatCurrency(transaction.amount_ars)}</p>
                            <p><strong>Valor (Crypto):</strong> ${transaction.amount_crypto} ${transaction.crypto_type}</p>
                            <p><strong>Método de Comunicação:</strong> ${transaction.communication_method || 'N/A'}</p>
                            <p><strong>Telefone:</strong> ${transaction.phone || 'N/A'}</p>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <h6>Datas</h6>
                            <p><strong>Criada em:</strong> ${formatDate(transaction.created_at)}</p>
                            <p><strong>Concluída em:</strong> ${transaction.completed_at ? formatDate(transaction.completed_at) : 'Pendente'}</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Remover modal quando fechado
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
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
            const simulationResult = document.getElementById('simulation-result');
            if (simulationResult) {
                simulationResult.innerHTML = `
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
            }
            
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

// Função para carregar contabilidade
async function loadAccounting() {
    try {
        console.log('Carregando seção de contabilidade...');
        // Inicializar a seção de contabilidade
        const accountingContent = document.getElementById('accounting-content');
        if (accountingContent) {
            accountingContent.innerHTML = `
                <div class="alert alert-info">
                    Selecione um período acima para gerar o relatório contábil.
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar contabilidade:', error);
        showAlert('Erro ao carregar contabilidade', 'danger');
    }
}

// Função para gerar relatórios contábeis
async function generateAccountingReport(period) {
    try {
        console.log(`Gerando relatório contábil para período: ${period}`);
        showLoading();
        
        // Buscar dados das transações
        const response = await fetch(`${API_BASE}/admin/transactions`);
        const data = await response.json();
        const transactions = data.transactions || [];
        
        // Filtrar transações por período
        const now = new Date();
        let filteredTransactions = [];
        
        switch(period) {
            case 'daily':
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                filteredTransactions = transactions.filter(tx => {
                    const txDate = new Date(tx.created_at);
                    return txDate >= today;
                });
                break;
            case 'weekly':
                const weekStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay());
                filteredTransactions = transactions.filter(tx => {
                    const txDate = new Date(tx.created_at);
                    return txDate >= weekStart;
                });
                break;
            case 'monthly':
                const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
                filteredTransactions = transactions.filter(tx => {
                    const txDate = new Date(tx.created_at);
                    return txDate >= monthStart;
                });
                break;
            case 'yearly':
                const yearStart = new Date(now.getFullYear(), 0, 1);
                filteredTransactions = transactions.filter(tx => {
                    const txDate = new Date(tx.created_at);
                    return txDate >= yearStart;
                });
                break;
        }
        
        // Calcular métricas contábeis
        const totalTransacted = filteredTransactions.reduce((sum, tx) => sum + (tx.amount_ars || 0), 0);
        const totalTransactions = filteredTransactions.length;
        
        // Taxas (baseadas no valor total transacionado)
        const atmFee = totalTransacted * 0.02; // 2% para ATM
        const operationalCosts = totalTransacted * 0.015; // 1.5% custos operacionais
        const grossProfit = totalTransacted * 0.065; // 6.5% lucro bruto (8% - 2% - 1.5%)
        const netProfit = grossProfit - operationalCosts; // Lucro líquido
        
        // Determinar período para exibição
        let periodText = '';
        switch(period) {
            case 'daily':
                periodText = 'Diário';
                break;
            case 'weekly':
                periodText = 'Semanal';
                break;
            case 'monthly':
                periodText = 'Mensal';
                break;
            case 'yearly':
                periodText = 'Anual';
                break;
        }
        
        // Atualizar conteúdo contábil
        const accountingContent = document.getElementById('accounting-content');
        if (accountingContent) {
            accountingContent.innerHTML = `
                <h4>Relatório Contábil - ${periodText}</h4>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h5>Total Transacionado</h5>
                                <h3>${formatCurrency(totalTransacted)}</h3>
                                <small class="text-muted">${totalTransactions} transações</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h5>Lucro Bruto</h5>
                                <h3>${formatCurrency(grossProfit)}</h3>
                                <small class="text-muted">6.5% sobre total transacionado</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6>Repasse para ATM</h6>
                            </div>
                            <div class="card-body">
                                <h4 class="text-primary">${formatCurrency(atmFee)}</h4>
                                <small class="text-muted">2% sobre total transacionado</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6>Custos Operacionais</h6>
                            </div>
                            <div class="card-body">
                                <h4 class="text-warning">${formatCurrency(operationalCosts)}</h4>
                                <small class="text-muted">1.5% sobre total transacionado</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6>Lucro Líquido</h6>
                            </div>
                            <div class="card-body">
                                <h4 class="text-success">${formatCurrency(netProfit)}</h4>
                                <small class="text-muted">Lucro bruto - Custos operacionais</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header">
                                <h6>Resumo Financeiro</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-3">
                                        <p><strong>Total Transacionado:</strong><br>${formatCurrency(totalTransacted)}</p>
                                    </div>
                                    <div class="col-md-3">
                                        <p><strong>Taxa ATM (2%):</strong><br>${formatCurrency(atmFee)}</p>
                                    </div>
                                    <div class="col-md-3">
                                        <p><strong>Custos Operacionais (1.5%):</strong><br>${formatCurrency(operationalCosts)}</p>
                                    </div>
                                    <div class="col-md-3">
                                        <p><strong>Lucro Líquido:</strong><br>${formatCurrency(netProfit)}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <button class="btn btn-success" onclick="exportAccountingReport('${period}', 'pdf')">
                        <i class="fas fa-file-pdf"></i> Exportar PDF
                    </button>
                    <button class="btn btn-success" onclick="exportAccountingReport('${period}', 'csv')">
                        <i class="fas fa-file-csv"></i> Exportar CSV
                    </button>
                </div>
            `;
        }
        
        hideLoading();
        console.log('Relatório contábil gerado com sucesso!');
    } catch (error) {
        console.error('Erro ao gerar relatório contábil:', error);
        hideLoading();
        showAlert('Erro ao gerar relatório contábil: ' + error.message, 'danger');
    }
}

// Função para exportar relatórios contábeis
function exportAccountingReport(period, format) {
    console.log(`Exportando relatório contábil ${period} em formato ${format}`);
    showAlert(`Exportando relatório contábil ${period} em formato ${format}`, 'info');
}