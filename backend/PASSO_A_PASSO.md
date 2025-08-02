# 🔧 Guia Passo a Passo - Resolver Problema do Servidor

## ❌ **Problema Identificado**

O servidor não está iniciando corretamente devido a conflitos de porta e processos.

## ✅ **Solução Passo a Passo**

### 1. **Parar todos os processos Python**
```bash
# Verificar processos Python
ps aux | grep python | grep -v grep

# Matar todos os processos Python relacionados ao servidor
pkill -f uvicorn
pkill -f python.*server
```

### 2. **Limpar portas**
```bash
# Verificar portas em uso
lsof -i :3000
lsof -i :5000
lsof -i :8000
lsof -i :8080

# Matar processos nas portas
kill -9 $(lsof -t -i:3000)
kill -9 $(lsof -t -i:5000)
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:8080)
```

### 3. **Verificar se está no diretório correto**
```bash
# Deve estar em: /Users/ravrok/atm-btc/backend
pwd

# Se não estiver, navegar para o diretório
cd /Users/ravrok/atm-btc/backend
```

### 4. **Testar servidor simples**
```bash
# Criar servidor de teste
python -c "
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
def root():
    return {'status': 'ok'}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)
"
```

### 5. **Iniciar servidor principal**
```bash
# Opção 1: Uvicorn direto
uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload

# Opção 2: Script Python
python final_server.py

# Opção 3: Script shell
./start.sh
```

### 6. **Testar acesso**
```bash
# Testar health check
curl http://127.0.0.1:5000/api/health

# Testar dashboard
curl http://127.0.0.1:5000/admin
```

### 7. **Acessar no navegador**
- Abrir navegador
- Acessar: **http://127.0.0.1:5000/admin**
- Se não funcionar, tentar: **http://localhost:5000/admin**

## 🔍 **Se Ainda Não Funcionar**

### Verificar logs
```bash
# Verificar se há erros
python -c "from app.main import app; print('App OK')"
```

### Testar porta diferente
```bash
# Tentar porta 9000
uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload
```

### Verificar firewall
```bash
# Verificar se o firewall está bloqueando
sudo pfctl -s all
```

## 🎯 **URLs Finais**

- **Dashboard**: http://127.0.0.1:5000/admin
- **API Docs**: http://127.0.0.1:5000/docs
- **Health**: http://127.0.0.1:5000/api/health

## 📋 **Comandos Rápidos**

```bash
# Limpar tudo e iniciar
pkill -f uvicorn
cd /Users/ravrok/atm-btc/backend
python final_server.py
```

## ✅ **Resultado Esperado**

Após executar os comandos, você deve ver:
- Servidor iniciando sem erros
- Mensagem "Uvicorn running on http://127.0.0.1:5000"
- Interface acessível no navegador

---

**🚀 Execute os comandos passo a passo e a interface deve funcionar!** 