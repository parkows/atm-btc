// Variáveis globais
let currentStep = 1;
let selectedCommunication = null;
let selectedCrypto = null;
let selectedSaleCrypto = null;
let currentPhone = null;
let currentMethod = null;

// API Base URL
const API_BASE = 'http://localhost:8000';

// Funções de navegação
function showPurchaseForm() {
    document.getElementById('mainScreen').style.display = 'none';
    document.getElementById('purchaseForm').style.display = 'block';
    document.getElementById('backButton').style.display = 'flex';
    currentStep = 1;
    resetPurchaseForm();
}

function showSaleForm() {
    document.getElementById('mainScreen').style.display = 'none';
    document.getElementById('saleForm').style.display = 'block';
    document.getElementById('backButton').style.display = 'flex';
    resetSaleForm();
}

function goBack() {
    if (currentStep > 1) {
        currentStep--;
        showPurchaseStep(currentStep);
    } else {
        document.getElementById('purchaseForm').style.display = 'none';
        document.getElementById('saleForm').style.display = 'none';
        document.getElementById('mainScreen').style.display = 'block';
        document.getElementById('backButton').style.display = 'none';
    }
}

// Funções de compra
function selectCommunication(method) {
    selectedCommunication = method;
    currentMethod = method;
    
    // Remover seleção anterior
    document.querySelectorAll('.comm-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Selecionar nova opção
    event.target.closest('.comm-option').classList.add('selected');
    
    // Habilitar botão continuar
    document.getElementById('startPurchaseBtn').disabled = false;
}

function startPurchase() {
    if (!selectedCommunication) {
        showStatus('purchaseStatus', 'Por favor, selecione um método de comunicação', 'error');
        return;
    }
    
    currentStep = 2;
    showPurchaseStep(2);
}

function sendVerificationCode() {
    const phone = document.getElementById('purchasePhone').value.trim();
    
    if (!phone) {
        showStatus('purchaseStatus', 'Por favor, digite seu número de telefone', 'error');
        return;
    }
    
    currentPhone = phone;
    
    // Simular envio de código (em produção, chamar API)
    showStatus('purchaseStatus', `Código enviado para ${phone} via ${selectedCommunication}`, 'success');
    
    setTimeout(() => {
        currentStep = 3;
        showPurchaseStep(3);
    }, 1000);
}

function verifyCode() {
    const code = document.getElementById('verificationCode').value.trim();
    
    if (!code) {
        showStatus('purchaseStatus', 'Por favor, digite o código de verificação', 'error');
        return;
    }
    
    // Para testes, aceitar código 123456
    if (code === '123456') {
        showStatus('purchaseStatus', 'Código verificado com sucesso!', 'success');
        
        setTimeout(() => {
            currentStep = 4;
            showPurchaseStep(4);
        }, 1000);
    } else {
        showStatus('purchaseStatus', 'Código incorreto. Para testes, use: 123456', 'error');
    }
}

function selectCrypto(crypto) {
    selectedCrypto = crypto;
    
    showStatus('purchaseStatus', `${crypto} selecionado`, 'success');
    
    setTimeout(() => {
        currentStep = 5;
        showPurchaseStep(5);
    }, 1000);
}

function requestWalletAddress() {
    const amount = document.getElementById('purchaseAmount').value;
    
    if (!amount || amount < 10000 || amount > 250000) {
        showStatus('purchaseStatus', 'Por favor, digite um valor entre $10,000 e $250,000 ARS', 'error');
        return;
    }
    
    // Simular solicitação de endereço
    showStatus('purchaseStatus', `Solicitando endereço da wallet ${selectedCrypto}...`, 'info');
    
    // Simular resposta do usuário
    setTimeout(() => {
        showStatus('purchaseStatus', `Endereço recebido! Compra de ${selectedCrypto} por $${amount} ARS criada com sucesso!`, 'success');
        
        // Simular criação da compra
        setTimeout(() => {
            showStatus('purchaseStatus', 'Compra finalizada! Verifique seu telefone para mais detalhes.', 'success');
        }, 2000);
    }, 2000);
}

// Funções de venda
function selectSaleCrypto(crypto) {
    selectedSaleCrypto = crypto;
    
    showStatus('saleStatus', `${crypto} selecionado para venda`, 'success');
    
    setTimeout(() => {
        document.getElementById('saleStep1').classList.add('hidden');
        document.getElementById('saleStep2').classList.remove('hidden');
    }, 1000);
}

function createSaleSession() {
    const amount = document.getElementById('saleAmount').value;
    
    if (!amount || amount < 10000 || amount > 250000) {
        showStatus('saleStatus', 'Por favor, digite um valor entre $10,000 e $250,000 ARS', 'error');
        return;
    }
    
    // Simular criação de sessão de venda
    showStatus('saleStatus', `Criando sessão de venda de ${selectedSaleCrypto}...`, 'info');
    
    setTimeout(() => {
        showStatus('saleStatus', `Sessão de venda criada! QR Code gerado para ${selectedSaleCrypto} por $${amount} ARS`, 'success');
        
        // Simular QR Code
        setTimeout(() => {
            showStatus('saleStatus', 'Aguardando pagamento... Verifique o QR Code no ATM', 'info');
        }, 1000);
    }, 2000);
}

// Funções auxiliares
function showPurchaseStep(step) {
    // Esconder todos os passos
    for (let i = 1; i <= 5; i++) {
        const stepElement = document.getElementById(`purchaseStep${i}`);
        if (stepElement) {
            stepElement.classList.add('hidden');
        }
    }
    
    // Mostrar passo atual
    const currentStepElement = document.getElementById(`purchaseStep${step}`);
    if (currentStepElement) {
        currentStepElement.classList.remove('hidden');
    }
}

function resetPurchaseForm() {
    currentStep = 1;
    selectedCommunication = null;
    selectedCrypto = null;
    currentPhone = null;
    currentMethod = null;
    
    // Limpar campos
    document.getElementById('purchasePhone').value = '';
    document.getElementById('verificationCode').value = '';
    document.getElementById('purchaseAmount').value = '';
    
    // Remover seleções
    document.querySelectorAll('.comm-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Desabilitar botão
    document.getElementById('startPurchaseBtn').disabled = true;
    
    // Limpar status
    document.getElementById('purchaseStatus').innerHTML = '';
    
    // Mostrar primeiro passo
    showPurchaseStep(1);
}

function resetSaleForm() {
    selectedSaleCrypto = null;
    
    // Limpar campos
    document.getElementById('saleAmount').value = '';
    
    // Limpar status
    document.getElementById('saleStatus').innerHTML = '';
    
    // Mostrar primeiro passo
    document.getElementById('saleStep1').classList.remove('hidden');
    document.getElementById('saleStep2').classList.add('hidden');
}

function showStatus(elementId, message, type) {
    const statusElement = document.getElementById(elementId);
    const statusClass = `status-${type}`;
    
    statusElement.innerHTML = `
        <div class="status-message ${statusClass}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
        </div>
    `;
}

// Teste de API
async function testAPI() {
    try {
        const response = await fetch(`${API_BASE}/cryptos/supported`);
        const data = await response.json();
        console.log('API Test:', data);
    } catch (error) {
        console.error('API Error:', error);
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('LiquidGold ATM Interface carregada');
    
    // Testar API
    testAPI();
    
    // Adicionar listeners para Enter
    document.getElementById('purchasePhone').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendVerificationCode();
        }
    });
    
    document.getElementById('verificationCode').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            verifyCode();
        }
    });
    
    document.getElementById('purchaseAmount').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            requestWalletAddress();
        }
    });
    
    document.getElementById('saleAmount').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            createSaleSession();
        }
    });
}); 