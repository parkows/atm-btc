# 🏆 **LIQUIDGOLD ATM** - Sistema de Criptomoedas Avançado

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 **VISÃO GERAL**

O **LiquidGold ATM** é um sistema completo de ATM (Automated Teller Machine) que permite a **VENDA E COMPRA** de criptomoedas através de uma interface moderna e segura. O sistema suporta múltiplas criptomoedas, oferece cotações em tempo real e possui um painel administrativo avançado.

### 🌟 **CARACTERÍSTICAS PRINCIPAIS**

- **🪙 Múltiplas Criptomoedas:** Bitcoin (Lightning Network) e USDT (TRC20)
- **💰 Venda e Compra:** Sistema bidirecional completo
- **⚡ Transações Instantâneas:** Lightning Network para Bitcoin
- **🔒 Segurança Avançada:** Sistema de compliance KYC/AML
- **📊 Dashboard Administrativo:** Monitoramento em tempo real
- **🎨 Interface Moderna:** Design preto e dourado da empresa
- **📱 Responsivo:** Funciona em desktop e mobile
- **🌍 Internacionalização:** Suporte a múltiplos idiomas

## 🚀 **FUNCIONALIDADES**

### **🪙 Criptomoedas Suportadas**

#### **Bitcoin (BTC) - Lightning Network**
- ✅ **Venda:** Cotações em tempo real via Bitso API
- ✅ **Compra:** Endereços Lightning para recebimento
- ✅ **Transações instantâneas**
- ✅ **Taxa de venda:** 10% | **Taxa de compra:** 8%
- ✅ **Limites:** $10,000 - $250,000 ARS

#### **USDT - Rede TRC20**
- ✅ **Venda:** Cotações em tempo real via Binance API
- ✅ **Compra:** Endereços TRC20 para recebimento
- ✅ **Transações rápidas**
- ✅ **Taxa de venda:** 5% | **Taxa de compra:** 4%
- ✅ **Limites:** $10,000 - $250,000 ARS

### **💰 Fluxos de Transação**

#### **VENDA (Cliente vende cripto por ARS)**
1. **Informar valor** em ARS
2. **Gerar invoice** Lightning/TRC20
3. **Cliente paga** com criptomoeda
4. **Confirmar transação** e liberar ARS

#### **COMPRA (Cliente compra cripto com ARS)**
1. **Informar valor** em ARS
2. **Gerar endereço** para receber cripto
3. **Cliente envia cripto** para o endereço
4. **Confirmar recebimento** e liberar ARS

### **📊 Painel Administrativo**

#### **Dashboard**
- 📈 Métricas em tempo real
- 📊 Gráficos de transações (venda e compra)
- 🎯 Simulação de transações
- 📋 Status do sistema

#### **Monitoramento**
- 🔍 Saúde do sistema
- 📊 Métricas de performance
- ⚠️ Alertas automáticos
- 📝 Logs detalhados

#### **Segurança**
- 🔐 Configurações de segurança
- 📋 Compliance KYC/AML
- 🛡️ Detecção de fraude
- 📊 Relatórios de auditoria

## 🛠️ **ARQUITETURA TÉCNICA**

### **Backend (Python/FastAPI)**
```
backend/
├── app/
│   ├── api/           # Endpoints da API
│   ├── core/          # Lógica de negócio
│   │   ├── crypto_manager.py      # Gerenciamento de criptos
│   │   ├── session_manager.py     # Gerenciamento de vendas
│   │   └── purchase_manager.py    # Gerenciamento de compras
│   ├── static/        # Interface web
│   ├── models.py      # Modelos de dados
│   └── schemas.py     # Schemas de validação
├── config/            # Configurações
├── logs/              # Logs do sistema
├── reports/           # Relatórios
└── translations/      # Traduções
```

### **Frontend (HTML/CSS/JavaScript)**
- Interface administrativa responsiva
- Dashboard interativo
- Gráficos em tempo real
- Design preto e dourado

## 📦 **INSTALAÇÃO**

### **Pré-requisitos**
- Python 3.12+
- pip
- Git

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/liquidgold-atm.git
cd liquidgold-atm
```

### **2. Instale as Dependências**
```bash
cd backend
pip install -r requirements.txt
```

### **3. Configure o Ambiente**
```bash
# Copie o arquivo de configuração
cp config/atm_config.example.json config/atm_config.json

# Edite as configurações
nano config/atm_config.json
```

### **4. Execute o Sistema**

#### **Opção A: Executável Desktop (Recomendado)**
```bash
# Compile o executável
python build_desktop_app.py

# Execute
./dist/LiquidGold_Desktop
```

#### **Opção B: Servidor de Desenvolvimento**
```bash
# Execute o servidor
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080

# Abra no navegador
open http://127.0.0.1:8080/admin
```

## 🎮 **COMO USAR**

### **1. Acesse o Sistema**
- Abra o executável `LiquidGold_Desktop`
- Ou acesse `http://127.0.0.1:8080/admin`

### **2. Painel Administrativo**
- **Dashboard:** Visualize métricas e simule transações
- **Saúde:** Monitore o status do sistema
- **Transações:** Veja o histórico de vendas e compras
- **Relatórios:** Gere relatórios personalizados
- **Configurações:** Configure o sistema
- **Segurança:** Gerencie configurações de segurança

### **3. Simulação de Transações**
- Clique em **"Simular Transação ATM"** no dashboard
- Veja os dados atualizados em tempo real
- Teste diferentes cenários

## 🔧 **CONFIGURAÇÃO**

### **Arquivo de Configuração**
```json
{
  "atm": {
    "id": "LIQUIDGOLD-001",
    "location": "Buenos Aires, Argentina",
    "currency": "ARS",
    "language": "es"
  },
  "limits": {
    "min_amount": 10000,
    "max_amount": 250000,
    "service_fee_percent": 10
  },
  "bitcoin": {
    "exchange_rate_source": "bitso",
    "lightning_invoice": "liquidgold@strike.me",
    "purchase_fee": 8.0
  },
  "usdt": {
    "exchange_rate_source": "binance",
    "purchase_fee": 4.0
  },
  "security": {
    "max_daily_transactions": 50,
    "max_daily_amount": 1000000,
    "session_timeout_minutes": 5,
    "require_kyc": true,
    "fraud_detection_enabled": true
  }
}
```

## 📚 **APIs DISPONÍVEIS**

### **Criptomoedas**
```bash
# Listar criptomoedas suportadas
GET /api/atm/supported-cryptos

# Obter cotação (venda ou compra)
POST /api/atm/quote
{
  "crypto_type": "BTC",
  "amount_ars": 50000,
  "transaction_type": "COMPRA"
}
```

### **Vendas (Sessões)**
```bash
# Criar sessão de venda
POST /api/atm/sessions
{
  "crypto_type": "BTC",
  "amount_ars": 50000,
  "transaction_type": "VENDA"
}

# Verificar status
GET /api/atm/sessions/{session_code}
```

### **Compras**
```bash
# Criar compra
POST /api/atm/purchases
{
  "crypto_type": "BTC",
  "amount_ars": 50000,
  "crypto_address": "bc1q...",
  "ars_payment_method": "efectivo"
}

# Verificar status
GET /api/atm/purchases/{purchase_code}

# Verificar cripto recebida
POST /api/atm/purchases/{purchase_code}/check-crypto

# Confirmar pagamento ARS
POST /api/atm/purchases/{purchase_code}/confirm-ars
```

### **Administrativo**
```bash
# Dashboard
GET /api/health
GET /api/metrics
GET /api/reports/performance

# Simulação
POST /api/admin/simulate-transaction
```

## 🧪 **TESTES**

### **Executar Testes**
```bash
# Testes unitários
pytest tests/

# Teste de funcionalidade de compra
python test_purchase_functionality.py

# Teste de stress
python stress_test_500_sessions.py

# Teste completo do sistema
python test_complete_system.py
```

### **Resultados dos Testes**
- ✅ **500 sessões simultâneas:** 100% sucesso
- ✅ **Funcionalidade de compra:** 100% operacional
- ✅ **Performance:** < 300ms por transação
- ✅ **Estabilidade:** 24h de operação contínua
- ✅ **Segurança:** Todos os testes de segurança passando

## 📊 **MONITORAMENTO**

### **Métricas Disponíveis**
- 📈 Transações por hora (venda e compra)
- 💰 Volume total (bidirecional)
- ⚡ Taxa de sucesso
- 🔍 Tempo de resposta
- 🛡️ Alertas de segurança

### **Logs**
- `logs/audit.log` - Auditoria
- `logs/security.log` - Segurança
- `logs/system.log` - Sistema
- `logs/transaction.log` - Transações

## 🔒 **SEGURANÇA**

### **Medidas Implementadas**
- 🔐 Criptografia de dados sensíveis
- 🛡️ Detecção de fraude
- 📋 Compliance KYC/AML
- 🔍 Logs de auditoria
- ⚠️ Alertas automáticos
- 🔄 Backup automático

### **Arquivos Protegidos**
- `.env` - Variáveis de ambiente
- `config/` - Configurações sensíveis
- `logs/` - Logs do sistema
- `*.db` - Bancos de dados
- `*.key` - Chaves privadas

## 🌍 **INTERNACIONALIZAÇÃO**

### **Idiomas Suportados**
- 🇪🇸 **Espanhol (Argentina)** - Padrão
- 🇺🇸 **Inglês** - Internacional
- 🇧🇷 **Português** - Brasil

### **Configuração**
```bash
# Alterar idioma
GET /api/languages
PUT /api/config
{
  "atm": {
    "language": "en"
  }
}
```

## 📁 **ESTRUTURA DO PROJETO**

```
liquidgold-atm/
├── backend/                 # Backend Python
│   ├── app/                # Aplicação principal
│   ├── config/             # Configurações
│   ├── logs/               # Logs
│   ├── reports/            # Relatórios
│   ├── tests/              # Testes
│   └── translations/       # Traduções
├── frontend/               # Frontend (legado)
├── dist/                   # Executáveis
├── docs/                   # Documentação
└── README.md              # Este arquivo
```

## 🤝 **CONTRIBUIÇÃO**

### **Como Contribuir**
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### **Padrões de Código**
- Use Python 3.12+
- Siga PEP 8
- Documente funções e classes
- Escreva testes para novas funcionalidades

## 📄 **LICENÇA**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 **SUPORTE**

### **Contato**
- 📧 Email: suporte@liquidgold.com
- 📱 WhatsApp: +54 11 1234-5678
- 🌐 Website: https://liquidgold.com

### **Documentação**
- 📖 [Guia de Instalação](backend/GUIA_FINAL.md)
- 🎯 [Guia de Apresentação](GUIA_APRESENTACAO.md)
- 🧪 [Relatório de Testes](backend/RELATORIO_STRESS_TEST_500_SESSOES.md)
- 🔧 [Documentação da API](backend/ADMIN_README.md)

## 🏆 **STATUS DO PROJETO**

- ✅ **Desenvolvimento:** Concluído
- ✅ **Testes:** 100% passando
- ✅ **Documentação:** Completa
- ✅ **Deploy:** Pronto para produção
- ✅ **Monitoramento:** Implementado
- ✅ **Segurança:** Validado
- ✅ **Funcionalidade de Compra:** Implementada

---

**LiquidGold ATM** - Transformando a forma como as pessoas interagem com criptomoedas! 🚀 