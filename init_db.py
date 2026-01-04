#!/usr/bin/env python3
"""
Script de inicialização do banco de dados
Executa migrations automaticamente no Railway
"""
import os
import sys
from flask_migrate import upgrade, init, migrate as create_migration
from app import create_app, db

def init_database():
    """Inicializa o banco de dados e executa migrations"""
    app = create_app()

    with app.app_context():
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

        # Verifica se o diretório migrations existe
        if not os.path.exists(migrations_dir):
            print("📦 Criando diretório de migrations...")
            try:
                init()
                print("✅ Diretório de migrations criado")
            except Exception as e:
                print(f"⚠️  Erro ao criar migrations: {e}")
                print("Tentando criar tabelas diretamente...")
                db.create_all()
                return

        # Executa migrations
        try:
            print("🔄 Executando migrations...")
            upgrade()
            print("✅ Migrations executadas com sucesso")
        except Exception as e:
            print(f"⚠️  Erro ao executar migrations: {e}")
            print("Tentando criar tabelas diretamente...")
            db.create_all()

if __name__ == '__main__':
    init_database()
