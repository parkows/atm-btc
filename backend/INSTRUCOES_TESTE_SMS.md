# 📱 INSTRUÇÕES PARA TESTE DE SMS REAL - LIQUIDGOLD ATM

## 🎯 **OBJETIVO**
Testar o sistema de SMS real com Infobip implementando as duas funcionalidades principais:
1. **🔐 Envio de código de verificação** - Para confirmar número do cliente
2. **📱 Solicitação de carteira** - Para receber endereço da wallet

## ✅ **PRÉ-REQUISITOS CONCLUÍDOS**
- [x] Backup no GitHub realizado
- [x] Credenciais Infobip configuradas
- [x] Sistema de SMS implementado
- [x] Endpoints da API criados
- [x] Script de teste preparado

## 🔑 **CREDENCIAIS CONFIGURADAS**
- **API Key**: `79bec273e41a23ad3b8faa773e443ab8-deb0d324-2fb7-484e-9133-03c2a215c1d6`
- **Base URL**: `https://9kegvy.api.infobip.com`
- **Sender**: `LiquidGold`

## 🚀 **COMO TESTAR**

### **Opção 1: Script de Teste Interativo**
```bash
cd backend
python test_sms_real.py
```

### **Opção 2: Teste via API Endpoints**
```bash
# 1. Testar envio de código de verificação
curl -X POST "http://127.0.0.1:8080/api/sms/send-verification" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+5491112345678",
    "atm_id": "ATM001"
  }'

# 2. Testar solicitação de carteira
curl -X POST "http://127.0.0.1:8080/api/sms/wallet-request" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+5491112345678",
    "crypto_type": "BTC",
    "amount_ars": 50000
  }'
```

### **Opção 3: Interface Web**
- **Admin Dashboard**: http://127.0.0.1:8080/admin
- **ATM Interface**: http://127.0.0.1:8080/atm
- **API Docs**: http://127.0.0.1:8080/docs

## 📋 **CHECKLIST DE TESTE**

### **Teste 1: Código de Verificação**
- [ ] Executar script de teste
- [ ] Escolher opção 1 (Código de verificação)
- [ ] Inserir número de telefone real
- [ ] Verificar se SMS foi recebido
- [ ] Confirmar código de 6 dígitos
- [ ] Verificar logs do sistema

### **Teste 2: Solicitação de Carteira**
- [ ] Escolher opção 2 (Solicitação de carteira)
- [ ] Inserir número de telefone real
- [ ] Escolher tipo de criptomoeda (BTC/USDT)
- [ ] Inserir valor em ARS
- [ ] Verificar se SMS foi recebido
- [ ] Confirmar mensagem solicitando carteira
- [ ] Verificar logs do sistema

### **Teste 3: Verificação de Saúde**
- [ ] Escolher opção 3 (Saúde do sistema)
- [ ] Verificar se todas as configurações estão corretas
- [ ] Confirmar que Infobip está conectado
- [ ] Verificar validação de números de telefone

## 🔍 **O QUE VERIFICAR**

### **SMS Recebido**
- ✅ Mensagem com branding "LiquidGold ATM"
- ✅ Código de verificação de 6 dígitos (Teste 1)
- ✅ Solicitação de carteira com valores corretos (Teste 2)
- ✅ Formatação adequada da mensagem
- ✅ Emissor correto no telefone

### **Logs do Sistema**
- ✅ Mensagens de sucesso no console
- ✅ Message ID retornado pela Infobip
- ✅ Status de entrega
- ✅ Custo por SMS (se disponível)

### **API Response**
- ✅ Status 200 OK
- ✅ Campo "success": true
- ✅ Message ID retornado
- ✅ Status da mensagem

## 🚨 **POSSÍVEIS PROBLEMAS E SOLUÇÕES**

### **Erro: "Module not found"**
```bash
pip install infobip-api-python-sdk python-dotenv
```

### **Erro: "API Key inválida"**
- Verificar se a chave foi copiada corretamente
- Confirmar se a chave tem permissão SMS
- Verificar se a URL base está correta

### **Erro: "Número inválido"**
- Usar formato internacional: +5491112345678
- Verificar se o número existe e está ativo
- Testar com números conhecidos

### **SMS não entregue**
- Verificar saldo da conta Infobip
- Confirmar se o número está ativo
- Verificar logs de erro da API

## 📊 **MÉTRICAS DE SUCESSO**

### **Taxa de Entrega**
- ✅ 100% dos SMS devem ser entregues
- ✅ Tempo de entrega < 30 segundos
- ✅ Confirmação de leitura (se disponível)

### **Qualidade da Mensagem**
- ✅ Formatação correta
- ✅ Informações completas
- ✅ Branding consistente
- ✅ Instruções claras

### **Performance do Sistema**
- ✅ Resposta da API < 2 segundos
- ✅ Logs em tempo real
- ✅ Tratamento de erros adequado

## 🎯 **PRÓXIMOS PASSOS APÓS TESTE**

1. **Validar Funcionalidades**
   - Confirmar que ambos os SMS funcionam
   - Verificar qualidade das mensagens
   - Testar com diferentes números

2. **Integração com ATM**
   - Implementar no fluxo de compra
   - Implementar no fluxo de venda
   - Adicionar validação de códigos

3. **Produção**
   - Configurar variáveis de ambiente
   - Monitorar custos
   - Implementar rate limiting

## 📞 **SUPORTE**

### **Logs do Sistema**
- Console do servidor
- Arquivo de logs (se configurado)
- Dashboard Infobip

### **Contato Infobip**
- **Email**: support@infobip.com
- **Portal**: https://portal.infobip.com/
- **Documentação**: https://www.infobip.com/docs

---

## 🚀 **RESULTADO ESPERADO**
Após os testes, você deve ter:
- ✅ Sistema de SMS funcionando perfeitamente
- ✅ Códigos de verificação sendo enviados
- ✅ Solicitações de carteira funcionando
- ✅ Integração completa com o ATM
- ✅ Sistema pronto para produção

**🎉 LiquidGold ATM com SMS profissional funcionando!**
