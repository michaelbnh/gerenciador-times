import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self):
        # Detecta se está no Render
        if os.path.exists('/data'):
            self.db_path = '/data/gerenciador.db'
        else:
            self.db_path = os.path.join(os.path.dirname(__file__), 'gerenciador.db')
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Inicializa as tabelas do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela para jogadores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jogadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem INTEGER UNIQUE,
                nome TEXT NOT NULL,
                localizacao TEXT DEFAULT 'fila',  -- 'fila', 'time1', 'time2', 'historico'
                time_destino INTEGER,  -- 1 ou 2 para times, NULL para fila
                partida_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para controle de estado
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estado (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                contador_ordem INTEGER DEFAULT 1,
                contador_partidas INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para histórico de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_numero INTEGER,
                vencedor TEXT,  -- JSON
                perdedor TEXT,  -- JSON
                entrou TEXT,    -- JSON
                time1 TEXT,     -- JSON (para sorteios)
                time2 TEXT,     -- JSON (para sorteios)
                sorteio BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inicializa o estado se não existir
        cursor.execute('INSERT OR IGNORE INTO estado (id, contador_ordem, contador_partidas) VALUES (1, 1, 1)')
        
        conn.commit()
        conn.close()
    
    def salvar_jogadores(self, fila, times):
        """Salva todos os jogadores no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Limpa jogadores antigos (exceto do histórico)
        cursor.execute("DELETE FROM jogadores WHERE localizacao != 'historico'")
        
        # Salva jogadores da fila
        for j in fila:
            cursor.execute('''
                INSERT INTO jogadores (ordem, nome, localizacao)
                VALUES (?, ?, 'fila')
            ''', (j['ordem'], j['nome']))
        
        # Salva jogadores do time 1
        for j in times[1]:
            cursor.execute('''
                INSERT INTO jogadores (ordem, nome, localizacao, time_destino)
                VALUES (?, ?, 'time1', 1)
            ''', (j['ordem'], j['nome']))
        
        # Salva jogadores do time 2
        for j in times[2]:
            cursor.execute('''
                INSERT INTO jogadores (ordem, nome, localizacao, time_destino)
                VALUES (?, ?, 'time2', 2)
            ''', (j['ordem'], j['nome']))
        
        conn.commit()
        conn.close()
    
    def carregar_jogadores(self):
        """Carrega todos os jogadores do banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT ordem, nome, localizacao, time_destino FROM jogadores ORDER BY ordem')
        rows = cursor.fetchall()
        
        fila = []
        times = {1: [], 2: []}
        
        for ordem, nome, localizacao, time_destino in rows:
            jogador = {'ordem': ordem, 'nome': nome}
            
            if localizacao == 'fila':
                fila.append(jogador)
            elif localizacao == 'time1' or (localizacao == 'time' and time_destino == 1):
                times[1].append(jogador)
            elif localizacao == 'time2' or (localizacao == 'time' and time_destino == 2):
                times[2].append(jogador)
        
        conn.close()
        return fila, times
    
    def salvar_estado(self, contador_ordem, contador_partidas):
        """Salva os contadores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE estado 
            SET contador_ordem = ?, contador_partidas = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (contador_ordem, contador_partidas))
        
        conn.commit()
        conn.close()
    
    def carregar_estado(self):
        """Carrega os contadores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT contador_ordem, contador_partidas FROM estado WHERE id = 1')
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return row[0], row[1]
        return 1, 1
    
    def salvar_historico(self, historico):
        """Salva o histórico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Limpa histórico antigo
        cursor.execute("DELETE FROM historico")
        
        for h in historico:
            # Converte listas de jogadores para JSON
            vencedor_json = json.dumps([{'nome': j['nome']} for j in h.get('vencedor', [])])
            perdedor_json = json.dumps([{'nome': j['nome']} for j in h.get('perdedor', [])])
            entrou_json = json.dumps([{'nome': j['nome']} for j in h.get('entrou', [])])
            time1_json = json.dumps([{'nome': j['nome']} for j in h.get('time1', [])])
            time2_json = json.dumps([{'nome': j['nome']} for j in h.get('time2', [])])
            
            cursor.execute('''
                INSERT INTO historico 
                (partida_numero, vencedor, perdedor, entrou, time1, time2, sorteio)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                h['partida'],
                vencedor_json,
                perdedor_json,
                entrou_json,
                time1_json,
                time2_json,
                1 if h.get('sorteio') else 0
            ))
        
        conn.commit()
        conn.close()
    
    def carregar_historico(self):
        """Carrega o histórico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT partida_numero, vencedor, perdedor, entrou, time1, time2, sorteio 
            FROM historico 
            ORDER BY partida_numero DESC
        ''')
        rows = cursor.fetchall()
        
        historico = []
        for row in rows:
            h = {
                'partida': row[0],
                'vencedor': [{'nome': j['nome']} for j in json.loads(row[1])],
                'perdedor': [{'nome': j['nome']} for j in json.loads(row[2])],
                'entrou': [{'nome': j['nome']} for j in json.loads(row[3])],
                'time1': [{'nome': j['nome']} for j in json.loads(row[4])],
                'time2': [{'nome': j['nome']} for j in json.loads(row[5])],
                'sorteio': bool(row[6])
            }
            historico.append(h)
        
        conn.close()
        return historico