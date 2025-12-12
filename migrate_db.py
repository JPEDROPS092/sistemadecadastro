#!/usr/bin/env python3
"""
Script de migração do banco de dados antigo para a nova estrutura
"""
import sqlite3
import os
import shutil
from datetime import datetime

# Caminho do banco de dados
db_path = 'estoque.db'
backup_path = f'estoque_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

print(f"Iniciando migração do banco de dados...")

# Fazer backup do banco antigo
if os.path.exists(db_path):
    print(f"Criando backup: {backup_path}")
    shutil.copy2(db_path, backup_path)

    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Adicionar colunas faltantes na tabela produto
        print("Adicionando coluna 'estoque_minimo' à tabela 'produto'...")
        try:
            cursor.execute("ALTER TABLE produto ADD COLUMN estoque_minimo INTEGER DEFAULT 5")
            conn.commit()
            print("✓ Coluna 'estoque_minimo' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("✓ Coluna 'estoque_minimo' já existe")
            else:
                raise

        print("Adicionando coluna 'ativo' à tabela 'produto'...")
        try:
            cursor.execute("ALTER TABLE produto ADD COLUMN ativo BOOLEAN DEFAULT 1")
            conn.commit()
            print("✓ Coluna 'ativo' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("✓ Coluna 'ativo' já existe")
            else:
                raise

        # Adicionar coluna observacao na tabela movimento
        print("Adicionando coluna 'observacao' à tabela 'movimento'...")
        try:
            cursor.execute("ALTER TABLE movimento ADD COLUMN observacao VARCHAR(200)")
            conn.commit()
            print("✓ Coluna 'observacao' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("✓ Coluna 'observacao' já existe")
            else:
                raise

        # Criar tabelas novas (caixa e movimento_caixa)
        print("Criando tabela 'caixa'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caixa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_fechamento DATETIME,
                saldo_inicial FLOAT DEFAULT 0.0,
                saldo_final FLOAT DEFAULT 0.0,
                status VARCHAR(20) DEFAULT 'aberto',
                observacao VARCHAR(200)
            )
        """)
        conn.commit()
        print("✓ Tabela 'caixa' criada/verificada")

        print("Criando tabela 'movimento_caixa'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimento_caixa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caixa_id INTEGER NOT NULL,
                tipo VARCHAR(10) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                descricao VARCHAR(200) NOT NULL,
                valor FLOAT NOT NULL,
                data DATETIME DEFAULT CURRENT_TIMESTAMP,
                forma_pagamento VARCHAR(50),
                FOREIGN KEY (caixa_id) REFERENCES caixa(id)
            )
        """)
        conn.commit()
        print("✓ Tabela 'movimento_caixa' criada/verificada")

        print("\n✅ Migração concluída com sucesso!")
        print(f"Backup salvo em: {backup_path}")

    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
else:
    print("Banco de dados não encontrado. Um novo será criado ao iniciar a aplicação.")

print("\nVocê pode agora iniciar a aplicação com: python run.py")
