#!/usr/bin/env python3
"""
Servidor HTTP simples para teste
"""

import http.server
import socketserver
import os

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/app/static/admin.html'
        elif self.path == '/admin':
            self.path = '/app/static/admin.html'
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            return
        
        return super().do_GET()

def main():
    PORT = 8080
    
    # Mudar para o diretório backend
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"🚀 Iniciando servidor HTTP simples na porta {PORT}")
    print(f"📊 Acesse: http://localhost:{PORT}/admin")
    print(f"🔧 Health: http://localhost:{PORT}/health")
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Servidor rodando em http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main() 