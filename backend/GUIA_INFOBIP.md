# 🚀 GUIA COMPLETO - CONFIGURAÇÃO INFOBIP PARA LIQUIDGOLD ATM

## 📋 **VISÃO GERAL**
Este guia te ajudará a configurar o Infobip para enviar SMS para Argentina e outros países no sistema LiquidGold ATM.

## 🌍 **POR QUE INFOBIP?**
- ✅ **Cobertura Global**: Suporte completo para Argentina (+54)
- ✅ **Preços Competitivos**: Tarifas acessíveis para SMS
- ✅ **API Robusta**: SDK oficial em Python
- ✅ **Suporte Técnico**: Atendimento em português
- ✅ **WhatsApp Business**: Suporte futuro para WhatsApp

## 🔑 **PASSO A PASSO - CONFIGURAÇÃO**

### **1. CRIAR CONTA NO INFOBIP**
1. Acesse: https://portal.infobip.com/
2. Clique em "Start for free" ou "Sign up"
3. Preencha seus dados:
   - Nome completo
   - Email corporativo
   - Nome da empresa: "LiquidGold ATM"
   - Telefone
4. Confirme seu email

### **2. VERIFICAR CONTA**
1. Faça login no portal
2. Complete a verificação de identidade (se solicitado)
3. Adicione método de pagamento (cartão de crédito)

### **3. OBTER API KEY**
1. No portal, vá em **"API Security"** → **"API Keys"**
2. Clique em **"Create API Key"**
3. Configure a chave:
   - **Name**: `LiquidGold ATM SMS`
   - **Description**: `API Key para envio de SMS do sistema ATM`
   - **Permissions**: Selecione **"SMS"**
4. Clique em **"Create"**
5. **IMPORTANTE**: Copie a API Key imediatamente (não será exibida novamente)

### **4. CONFIGURAR VARIÁVEIS DE AMBIENTE**
1. No diretório `backend/`, crie um arquivo `.env`:
```bash
# Credenciais do Infobip
INFOBIP_API_KEY=sua_api_key_aqui
INFOBIP_BASE_URL=https://api.infobip.com
INFOBIP_SENDER=LiquidGold

# Número de teste (seu próprio número)
TEST_PHONE_NUMBER=+5491112345678

# Configurações do sistema
DEBUG=true
ENVIRONMENT=development
```

### **5. TESTAR CONFIGURAÇÃO**
Execute o script de teste:
```bash
cd backend
python test_infobip.py
```

## 📱 **FUNCIONALIDADES IMPLEMENTADAS**

### **SMS de Verificação**
- Código de 6 dígitos para confirmar número
- Expira em 10 minutos
- Mensagem personalizada com branding

### **Confirmação de Transação**
- Notificação de compra/venda confirmada
- Valores formatados em ARS e crypto
- Status da transação

### **Solicitação de Carteira**
- Solicita endereço da wallet do usuário
- Formato específico para cada criptomoeda
- Expira em 30 minutos

### **Atualizações de Status**
- Notificações de mudança de status
- IDs de transação para rastreamento
- Mensagens personalizadas por status

## 🌍 **SUPORTE POR PAÍS**

### **Argentina (+54)**
- **Formato**: +54 9 11 1234 5678
- **Cobertura**: 100% do território
- **Custo**: ~$0.02-0.05 por SMS

### **Brasil (+55)**
- **Formato**: +55 11 99999 9999
- **Cobertura**: Nacional
- **Custo**: ~$0.03-0.06 por SMS

### **Outros Países**
- **EUA**: +1 234 567 8900
- **Espanha**: +34 612 345 678
- **México**: +52 1 55 1234 5678

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **Personalização de Mensagens**
```python
# Exemplo de mensagem personalizada
message = f"🔐 LiquidGold ATM - Código: {code}\n⏰ Expira em {minutes} min"
```

### **Validação de Números**
- Verificação automática de formato
- Suporte a números com/sem código do país
- Validação de comprimento mínimo

### **Rastreamento de SMS**
- Message ID único para cada SMS
- Status de entrega
- Custo por mensagem

## 📊 **MONITORAMENTO E RELATÓRIOS**

### **Dashboard Infobip**
- Relatórios de entrega em tempo real
- Estatísticas de envio
- Análise de custos
- Logs de erro

### **Integração com Sistema**
- Logs automáticos no sistema ATM
- Notificações de falha
- Métricas de performance

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Erro: "API Key inválida"**
- Verifique se a chave foi copiada corretamente
- Confirme se a chave tem permissão SMS
- Teste no portal Infobip

### **Erro: "Número inválido"**
- Verifique formato internacional (+54...)
- Confirme se o número existe
- Teste com números conhecidos

### **Erro: "Saldo insuficiente"**
- Adicione créditos na conta Infobip
- Verifique limite de crédito
- Entre em contato com suporte

### **SMS não entregue**
- Verifique status no dashboard
- Confirme se o número está ativo
- Teste com outro número

## 💰 **CUSTOS E PLANOS**

### **Plano Gratuito**
- 100 SMS gratuitos por mês
- Suporte por email
- API completa

### **Planos Pagos**
- **Starter**: $0.02-0.05 por SMS
- **Business**: $0.015-0.04 por SMS
- **Enterprise**: Preços personalizados

### **Dicas para Economizar**
- Use números de teste apenas para desenvolvimento
- Implemente rate limiting
- Monitore uso de créditos

## 🔮 **FUTURO - WHATSAPP BUSINESS**

### **Vantagens**
- Custo menor que SMS
- Melhor taxa de entrega
- Suporte a mídia (imagens, documentos)
- Chat interativo

### **Implementação**
- API WhatsApp Business disponível
- Mesma estrutura de código
- Migração gradual possível

## 📞 **SUPORTE INFOBIP**

### **Canais de Atendimento**
- **Email**: support@infobip.com
- **Chat**: Portal Infobip
- **Telefone**: +1 855 463 6247
- **Documentação**: https://www.infobip.com/docs

### **Comunidade**
- **Fórum**: https://community.infobip.com/
- **GitHub**: https://github.com/infobip
- **Blog**: https://www.infobip.com/blog

## ✅ **CHECKLIST DE CONFIGURAÇÃO**

- [ ] Conta Infobip criada
- [ ] Email verificado
- [ ] Método de pagamento adicionado
- [ ] API Key criada e copiada
- [ ] Arquivo .env configurado
- [ ] Script de teste executado
- [ ] SMS de teste enviado com sucesso
- [ ] Sistema integrado ao ATM

## 🎯 **PRÓXIMOS PASSOS**

1. **Configure sua conta Infobip**
2. **Execute o script de teste**
3. **Integre com o sistema ATM**
4. **Teste com números reais**
5. **Monitore performance**
6. **Implemente WhatsApp Business (opcional)**

---

## 🚀 **RESULTADO FINAL**
Com o Infobip configurado, seu LiquidGold ATM terá:
- ✅ SMS funcionando para Argentina e outros países
- ✅ Sistema de verificação robusto
- ✅ Notificações automáticas
- ✅ Rastreamento completo
- ✅ Custo otimizado
- ✅ Escalabilidade para crescimento

**🎉 Sistema de SMS pronto para produção!**
