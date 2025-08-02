# 🎛️ RedATM - Painel Administrativo

Interface web completa para gerenciar todas as funcionalidades do RedATM baseadas no LiquidGold Bitcoin Machine.

## 🚀 Como Iniciar

### Opção 1: Script Python
```bash
cd backend
python start_admin.py
```

### Opção 2: Uvicorn Direto
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Acessos

- **Dashboard Administrativo**: http://localhost:8000/admin
- **Documentação da API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📊 Funcionalidades Disponíveis

### 🎯 Dashboard
- **Métricas em tempo real**: Transações, valores, taxa de sucesso
- **Gráficos interativos**: Transações por hora, status das transações
- **Status do sistema**: Indicadores visuais de saúde

### 💓 Saúde do Sistema
- **Monitoramento de componentes**: CPU, memória, disco, rede
- **Status de hardware**: Impressora, câmera, touchscreen
- **Limites diários**: Controle de transações e valores
- **Alertas automáticos**: Notificações de problemas

### 💰 Transações
- **Histórico completo**: Todas as transações com filtros
- **Detalhes por sessão**: Código, valor, status, timestamp
- **Ações em lote**: Visualização e auditoria

### 📈 Relatórios
- **Relatório diário**: Métricas do dia atual
- **Relatório semanal**: Análise de 7 dias
- **Relatório mensal**: Visão macro do período
- **Métricas de performance**: Taxa de sucesso, tempo médio
- **Exportação**: Download em JSON

### 🔐 Segurança
- **Configurações de segurança**: Limites, timeouts, KYC
- **Compliance**: Verificação de requisitos legais
- **Detecção de fraude**: Configuração de alertas
- **Auditoria**: Trilha completa de eventos

### ⚙️ Configurações
- **ATM**: ID, localização, moeda, idioma
- **Bitcoin**: Limites, taxas, fonte de cotação
- **Segurança**: Limites diários, timeouts, KYC
- **Notificações**: Email, webhook, alertas

### 🔔 Notificações
- **Teste de notificações**: Verificar webhook e email
- **Modo de manutenção**: Habilitar/desabilitar
- **Histórico**: Log de notificações enviadas

### 📋 Logs
- **Logs recentes**: Visualização em tempo real
- **Filtros**: Por tipo, data, componente
- **Exportação**: Download de logs

## 🛠️ APIs Disponíveis

### Dashboard
- `GET /api/health` - Status do sistema
- `GET /api/metrics` - Métricas em tempo real
- `GET /api/reports/performance` - Métricas de performance

### Configurações
- `GET /api/config` - Obter configurações
- `PUT /api/config/{key}` - Atualizar configuração

### Relatórios
- `GET /api/reports/daily` - Relatório diário
- `GET /api/reports/weekly` - Relatório semanal
- `GET /api/reports/monthly/{year}/{month}` - Relatório mensal
- `GET /api/reports/history` - Histórico de transações

### Administrativo
- `GET /api/admin/health` - Health check administrativo
- `GET /api/admin/config` - Configurações administrativas
- `POST /api/admin/maintenance/enable` - Habilitar manutenção
- `POST /api/admin/maintenance/disable` - Desabilitar manutenção
- `POST /api/admin/notifications/test` - Testar notificações

### Segurança
- `GET /api/admin/security/audit/{session_code}` - Trilha de auditoria
- `GET /api/admin/security/compliance/{amount}` - Verificar compliance

### Internacionalização
- `GET /api/i18n/languages` - Idiomas disponíveis
- `GET /api/i18n/translations/{language}` - Traduções
- `PUT /api/i18n/language/{language}` - Definir idioma

## 🎨 Interface

### Design Responsivo
- **Desktop**: Layout completo com sidebar
- **Tablet**: Layout adaptativo
- **Mobile**: Interface otimizada para touch

### Tema
- **Cores**: Azul corporativo (#1e3c72) e laranja Bitcoin (#f7931a)
- **Tipografia**: Segoe UI para melhor legibilidade
- **Ícones**: Font Awesome para consistência

### Componentes
- **Cards**: Métricas e informações
- **Gráficos**: Chart.js para visualizações
- **Tabelas**: Dados organizados
- **Formulários**: Configurações intuitivas
- **Alertas**: Feedback visual

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# Configurações do servidor
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Configurações do ATM
ATM_ID=ATM001
ATM_LOCATION="Buenos Aires, Argentina"
ATM_CURRENCY=ARS
ATM_LANGUAGE=es
```

### Arquivos de Configuração
- `config/atm_config.json` - Configurações principais
- `logs/` - Arquivos de log
- `reports/` - Relatórios exportados
- `translations/` - Arquivos de tradução

## 🚨 Troubleshooting

### Problemas Comuns

#### Interface não carrega
```bash
# Verificar se os arquivos estáticos existem
ls -la app/static/

# Verificar permissões
chmod 644 app/static/admin.html
chmod 644 app/static/admin.js
```

#### APIs não respondem
```bash
# Verificar se o servidor está rodando
curl http://localhost:8000/api/health

# Verificar logs
tail -f logs/system.log
```

#### Gráficos não aparecem
```bash
# Verificar console do navegador (F12)
# Verificar se Chart.js está carregando
```

### Logs
- **Sistema**: `logs/system.log`
- **Transações**: `logs/transaction.log`
- **Auditoria**: `logs/audit.log`
- **Segurança**: `logs/security.log`

## 📱 Compatibilidade

### Navegadores Suportados
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Dispositivos
- ✅ Desktop (1920x1080+)
- ✅ Laptop (1366x768+)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

## 🔒 Segurança

### Autenticação
- **Desenvolvimento**: Sem autenticação (para facilitar testes)
- **Produção**: Implementar autenticação JWT

### Autorização
- **Admin**: Acesso completo
- **Operador**: Acesso limitado
- **Auditor**: Apenas visualização

### Logs de Segurança
- **Login/Logout**: Registro de acesso
- **Configurações**: Mudanças de configuração
- **Transações**: Todas as operações
- **Erros**: Tentativas de acesso inválido

## 🚀 Próximos Passos

### Melhorias Planejadas
1. **Autenticação**: Sistema de login seguro
2. **Notificações push**: Alertas em tempo real
3. **Exportação**: PDF, Excel, CSV
4. **Backup**: Configurações automáticas
5. **Monitoramento**: Integração com Prometheus/Grafana

### Integrações
1. **Telegram**: Notificações via bot
2. **Slack**: Alertas de sistema
3. **Email**: Relatórios automáticos
4. **SMS**: Alertas críticos

---

**🎉 Interface administrativa completa e funcional!**

Acesse http://localhost:8000/admin para começar a usar todas as funcionalidades do RedATM. 