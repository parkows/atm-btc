// Variáveis globais
let currentStep = 1;
let selectedCommunication = null;
let selectedCrypto = null;
let selectedSaleCrypto = null;
let currentPhone = null;
let currentMethod = null;
let detectedAmount = 0;

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

function goToMain() {
    document.getElementById('purchaseForm').style.display = 'none';
    document.getElementById('saleForm').style.display = 'none';
    document.getElementById('mainScreen').style.display = 'block';
    document.getElementById('backButton').style.display = 'none';
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
    
    // Atualizar informações da rede
    const networkInfo = document.getElementById('walletNetworkInfo');
    const methodInfo = document.getElementById('walletMethodInfo');
    
    if (crypto === 'BTC') {
        networkInfo.textContent = 'Rede Lightning Network';
    } else {
        networkInfo.textContent = 'Rede TRC20';
    }
    
    methodInfo.textContent = selectedCommunication === 'whatsapp' ? 'WhatsApp' : 'SMS';
    
    showStatus('purchaseStatus', `${crypto} selecionado`, 'success');
    
    setTimeout(() => {
        currentStep = 5;
        showPurchaseStep(5);
    }, 1000);
}

function confirmWalletAddress() {
    const walletAddress = document.getElementById('walletAddress').value.trim();
    
    if (!walletAddress) {
        showStatus('purchaseStatus', 'Por favor, digite qualquer texto para continuar', 'error');
        return;
    }
    
    showStatus('purchaseStatus', 'Carteira confirmada!', 'success');
    
    setTimeout(() => {
        currentStep = 6;
        showPurchaseStep(6);
    }, 1000);
}

function confirmCashInsertion() {
    // Simular detecção de valor
    detectedAmount = Math.floor(Math.random() * 90000) + 10000; // $10,000 - $100,000
    
    document.getElementById('detectedAmount').textContent = `$${detectedAmount.toLocaleString()}`;
    
    showStatus('purchaseStatus', 'Valor detectado!', 'success');
    
    setTimeout(() => {
        currentStep = 7;
        showPurchaseStep(7);
    }, 1000);
}

function confirmAmount() {
    showStatus('purchaseStatus', 'Valor confirmado! Processando...', 'success');
    
    setTimeout(() => {
        currentStep = 8;
        showPurchaseStep(8);
        
        // Simular processamento por 5 segundos
        setTimeout(() => {
            currentStep = 9;
            showPurchaseStep(9);
        }, 5000);
    }, 1000);
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

function showSaleInfo() {
    const amount = document.getElementById('saleAmount').value;
    
    if (!amount || amount < 10000 || amount > 250000) {
        showStatus('saleStatus', 'Por favor, digite um valor entre $10,000 e $250,000 ARS', 'error');
        return;
    }
    
    // Simular dados da operação
    const cryptoAmount = (amount * 0.92 / 50000).toFixed(6); // Simular cotação
    const quote = 50000; // Simular cotação BTC
    const fee = selectedSaleCrypto === 'BTC' ? '8%' : '6%';
    
    // Atualizar informações
    document.getElementById('saleAmountInfo').textContent = `$${parseInt(amount).toLocaleString()} ARS`;
    document.getElementById('saleCryptoInfo').textContent = selectedSaleCrypto;
    document.getElementById('saleCryptoAmount').textContent = `${cryptoAmount} ${selectedSaleCrypto}`;
    document.getElementById('saleQuoteInfo').textContent = `$${quote.toLocaleString()}`;
    document.getElementById('saleFeeInfo').textContent = fee;
    
    showStatus('saleStatus', 'Informações calculadas!', 'success');
    
    setTimeout(() => {
        document.getElementById('saleStep2').classList.add('hidden');
        document.getElementById('saleStep3').classList.remove('hidden');
    }, 1000);
}

function goBackToSaleAmount() {
    document.getElementById('saleStep3').classList.add('hidden');
    document.getElementById('saleStep2').classList.remove('hidden');
}

function showQRCode() {
    showStatus('saleStatus', 'QR Code gerado!', 'success');
    
    setTimeout(() => {
        document.getElementById('saleStep3').classList.add('hidden');
        document.getElementById('saleStep4').classList.remove('hidden');
    }, 1000);
}

function confirmPayment() {
    showStatus('saleStatus', 'Pagamento confirmado!', 'success');
    
    setTimeout(() => {
        document.getElementById('saleStep4').classList.add('hidden');
        document.getElementById('saleStep5').classList.remove('hidden');
    }, 1000);
}

// Funções auxiliares
function showPurchaseStep(step) {
    // Esconder todos os passos
    for (let i = 1; i <= 9; i++) {
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
    detectedAmount = 0;
    
    // Limpar campos
    document.getElementById('purchasePhone').value = '';
    document.getElementById('verificationCode').value = '';
    document.getElementById('walletAddress').value = '';
    
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
    document.getElementById('saleStep3').classList.add('hidden');
    document.getElementById('saleStep4').classList.add('hidden');
    document.getElementById('saleStep5').classList.add('hidden');
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
    
    document.getElementById('walletAddress').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            confirmWalletAddress();
        }
    });
    
    document.getElementById('saleAmount').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            showSaleInfo();
        }
    });
}); 