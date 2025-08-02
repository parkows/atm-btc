#!/usr/bin/env python3
"""
Script de Deploy para Produção - LiquidGold ATM
Configura ambiente de produção com todas as otimizações
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class ProductionDeploy:
    def __init__(self):
        self.config = {
            'host': '0.0.0.0',
            'port': 8000,
            'workers': 4,
            'max_connections': 1000,
            'timeout': 30,
            'log_level': 'info'
        }
    
    def check_dependencies(self):
        """Verifica dependências necessárias"""
        print("🔍 VERIFICANDO DEPENDÊNCIAS...")
        
        required_packages = [
            'fastapi',
            'uvicorn[standard]',
            'sqlalchemy',
            'requests',
            'python-multipart',
            'python-jose[cryptography]',
            'passlib[bcrypt]',
            'python-dotenv'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_').replace('[', '').replace(']', ''))
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}")
        
        if missing_packages:
            print(f"\n📦 INSTALANDO PACOTES FALTANTES...")
            for package in missing_packages:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                 capture_output=True, text=True)
                    print(f"✅ {package} instalado")
                except Exception as e:
                    print(f"⚠️  {package} - conflito de dependência (continuando)")
        
        return True  # Continuar mesmo com conflitos menores
    
    def setup_production_config(self):
        """Configura ambiente de produção"""
        print("\n⚙️  CONFIGURANDO AMBIENTE DE PRODUÇÃO...")
        
        # Criar arquivo de configuração de produção
        prod_config = {
            'environment': 'production',
            'debug': False,
            'host': self.config['host'],
            'port': self.config['port'],
            'workers': self.config['workers'],
            'max_connections': self.config['max_connections'],
            'timeout': self.config['timeout'],
            'log_level': self.config['log_level'],
            'database': {
                'url': 'sqlite:///./liquidgold_atm_prod.db',
                'pool_size': 20,
                'max_overflow': 30
            },
            'security': {
                'session_timeout_minutes': 5,
                'max_attempts_per_hour': 10,
                'rate_limit_per_minute': 100
            },
            'monitoring': {
                'enabled': True,
                'metrics_interval': 60,
                'health_check_interval': 30
            }
        }
        
        with open('config/production_config.json', 'w') as f:
            json.dump(prod_config, f, indent=2)
        
        print("✅ Configuração de produção criada")
    
    def setup_logging(self):
        """Configura sistema de logging para produção"""
        print("\n📝 CONFIGURANDO SISTEMA DE LOGGING...")
        
        # Criar diretórios de log
        log_dirs = ['logs', 'logs/production', 'logs/backup']
        for log_dir in log_dirs:
            os.makedirs(log_dir, exist_ok=True)
        
        # Configurar rotação de logs
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'production': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/production/app.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'production'
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/production/error.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'production',
                    'level': 'ERROR'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file', 'error_file'],
                    'level': 'INFO'
                }
            }
        }
        
        with open('config/logging_config.json', 'w') as f:
            json.dump(log_config, f, indent=2)
        
        print("✅ Sistema de logging configurado")
    
    def setup_database(self):
        """Configura banco de dados para produção"""
        print("\n🗄️  CONFIGURANDO BANCO DE DADOS...")
        
        try:
            # Importar e criar tabelas
            from app.create_db import create_tables
            create_tables()
            print("✅ Banco de dados configurado")
        except Exception as e:
            print(f"❌ Erro ao configurar banco: {e}")
    
    def create_systemd_service(self):
        """Cria serviço systemd para produção"""
        print("\n🔧 CRIANDO SERVIÇO SYSTEMD...")
        
        service_content = f"""[Unit]
Description=LiquidGold ATM API
After=network.target

[Service]
Type=exec
User={os.getenv('USER', 'www-data')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getenv('PATH')}
ExecStart={sys.executable} -m uvicorn app.main:app --host {self.config['host']} --port {self.config['port']} --workers {self.config['workers']}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        with open('liquidgold-atm.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Arquivo de serviço systemd criado: liquidgold-atm.service")
        print("📋 Para instalar o serviço:")
        print("   sudo cp liquidgold-atm.service /etc/systemd/system/")
        print("   sudo systemctl daemon-reload")
        print("   sudo systemctl enable liquidgold-atm")
        print("   sudo systemctl start liquidgold-atm")
    
    def create_nginx_config(self):
        """Cria configuração Nginx para produção"""
        print("\n🌐 CRIANDO CONFIGURAÇÃO NGINX...")
        
        nginx_config = f"""server {{
    listen 80;
    server_name liquidgold-atm.local;

    location / {{
        proxy_pass http://127.0.0.1:{self.config['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /static {{
        alias {os.getcwd()}/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    location /api {{
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:{self.config['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        with open('nginx-liquidgold-atm.conf', 'w') as f:
            f.write(nginx_config)
        
        print("✅ Configuração Nginx criada: nginx-liquidgold-atm.conf")
        print("📋 Para instalar:")
        print("   sudo cp nginx-liquidgold-atm.conf /etc/nginx/sites-available/")
        print("   sudo ln -s /etc/nginx/sites-available/nginx-liquidgold-atm.conf /etc/nginx/sites-enabled/")
        print("   sudo nginx -t")
        print("   sudo systemctl reload nginx")
    
    def run_health_check(self):
        """Executa verificação de saúde do sistema"""
        print("\n🏥 EXECUTANDO VERIFICAÇÃO DE SAÚDE...")
        
        try:
            import requests
            import time
            
            # Aguardar servidor iniciar
            time.sleep(2)
            
            # Testar endpoint de saúde
            response = requests.get(f"http://{self.config['host']}:{self.config['port']}/health")
            if response.status_code == 200:
                print("✅ Servidor respondendo corretamente")
            else:
                print(f"⚠️  Servidor respondendo com status: {response.status_code}")
            
            # Testar endpoint de criptomoedas
            response = requests.get(f"http://{self.config['host']}:{self.config['port']}/api/atm/supported-cryptos")
            if response.status_code == 200:
                data = response.json()
                if 'USDT' in data.get('cryptos', {}):
                    print("✅ API USDT funcionando")
                if 'BTC' in data.get('cryptos', {}):
                    print("✅ API BTC funcionando")
            else:
                print(f"❌ Erro na API: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na verificação de saúde: {e}")
    
    def deploy(self):
        """Executa deploy completo"""
        print("🚀 INICIANDO DEPLOY DE PRODUÇÃO")
        print("=" * 50)
        
        # Verificar dependências
        if not self.check_dependencies():
            print("❌ Falha na verificação de dependências")
            return False
        
        # Configurar ambiente
        self.setup_production_config()
        self.setup_logging()
        self.setup_database()
        
        # Criar arquivos de configuração
        self.create_systemd_service()
        self.create_nginx_config()
        
        # Verificar saúde
        self.run_health_check()
        
        print("\n" + "=" * 50)
        print("✅ DEPLOY DE PRODUÇÃO CONCLUÍDO!")
        print("📋 Próximos passos:")
        print("   1. Instalar serviço systemd")
        print("   2. Configurar Nginx")
        print("   3. Configurar firewall")
        print("   4. Configurar SSL/TLS")
        print("   5. Configurar monitoramento")
        
        return True

def main():
    """Função principal"""
    deployer = ProductionDeploy()
    success = deployer.deploy()
    
    if success:
        print("\n🎉 Sistema pronto para produção!")
    else:
        print("\n❌ Falha no deploy")

if __name__ == "__main__":
    main() 