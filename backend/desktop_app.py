#!/usr/bin/env python3
"""
LiquidGold - Aplicativo Desktop
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import time
import sys
import os
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.append(str(Path(__file__).parent))

class LiquidGoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LiquidGold - Interface Administrativa")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variáveis
        self.server_running = False
        self.server_thread = None
        
        # Configurar interface
        self.setup_ui()
        
        # Iniciar servidor automaticamente
        self.root.after(1000, self.start_server)
        
    def setup_ui(self):
        """Configurar interface gráfica"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="🎛️ LiquidGold - Interface Administrativa",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status do servidor
        self.status_label = ttk.Label(
            main_frame,
            text="Status: Parado",
            font=("Arial", 12)
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="🚀 Iniciar Servidor",
            command=self.start_server,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Parar Servidor",
            command=self.stop_server,
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_button = ttk.Button(
            button_frame,
            text="🌐 Abrir Interface",
            command=self.open_interface,
            state="disabled"
        )
        self.open_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # URLs
        urls_frame = ttk.LabelFrame(main_frame, text="URLs Disponíveis", padding="10")
        urls_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        urls = [
            ("📊 Dashboard", "http://127.0.0.1:8080/admin"),
            ("🔧 API Docs", "http://127.0.0.1:8080/docs"),
            ("📋 Health Check", "http://127.0.0.1:8080/api/health")
        ]
        
        for i, (name, url) in enumerate(urls):
            ttk.Label(urls_frame, text=f"{name}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            url_label = ttk.Label(urls_frame, text=url, foreground="blue", cursor="hand2")
            url_label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
            url_label.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        
        self.log_text = tk.Text(log_frame, height=8, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configurar grid weights
        main_frame.rowconfigure(4, weight=1)
        
    def log(self, message):
        """Adicionar mensagem ao log"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\\n")
        self.log_text.see(tk.END)
        
    def start_server(self):
        """Iniciar servidor"""
        if self.server_running:
            return
            
        self.log("🚀 Iniciando servidor LiquidGold...")
        self.status_label.config(text="Status: Iniciando...")
        self.start_button.config(state="disabled")
        
        # Iniciar servidor em thread separada
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
    def _run_server(self):
        """Executar servidor"""
        try:
            import uvicorn
            from app.main import app
            
            self.log("✅ Servidor iniciado com sucesso!")
            self.server_running = True
            
            # Atualizar UI na thread principal
            self.root.after(0, self._update_ui_running)
            
            # Executar servidor
            uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
            
        except Exception as e:
            self.log(f"❌ Erro ao iniciar servidor: {e}")
            self.root.after(0, self._update_ui_stopped)
            
    def _update_ui_running(self):
        """Atualizar UI quando servidor estiver rodando"""
        self.status_label.config(text="Status: Rodando")
        self.stop_button.config(state="normal")
        self.open_button.config(state="normal")
        
    def _update_ui_stopped(self):
        """Atualizar UI quando servidor parar"""
        self.status_label.config(text="Status: Parado")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.open_button.config(state="disabled")
        self.server_running = False
        
    def stop_server(self):
        """Parar servidor"""
        if not self.server_running:
            return
            
        self.log("⏹️ Parando servidor...")
        self.server_running = False
        self._update_ui_stopped()
        
    def open_interface(self):
        """Abrir interface no navegador"""
        try:
            self.log("🌐 Abrindo interface no navegador...")
            webbrowser.open("http://127.0.0.1:8080/admin")
            self.log("✅ Interface aberta!")
        except Exception as e:
            self.log(f"❌ Erro ao abrir navegador: {e}")
            messagebox.showerror("Erro", f"Não foi possível abrir o navegador: {e}")

def main():
    """Função principal"""
    root = tk.Tk()
    app = LiquidGoldApp(root)
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar ícone (se disponível)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Centralizar janela
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Iniciar aplicação
    root.mainloop()

if __name__ == "__main__":
    main() 