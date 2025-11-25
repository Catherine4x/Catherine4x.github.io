import sqlite3
import hashlib
from datetime import datetime

def init_database():
    """初始化数据库和表结构"""
    conn = sqlite3.connect('learning_management.db')
    cursor = conn.cursor()
    
    # 你的表结构
    tables_sql = [
        '''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            mot_de_passe_hash VARCHAR(255) NOT NULL
        )''',
        
        '''CREATE TABLE IF NOT EXISTS methodes_travail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom VARCHAR(50) NOT NULL,
            duree_session INTEGER NOT NULL,
            duree_pause INTEGER NOT NULL,
            description TEXT
        )''',
        
        '''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            methode_id INTEGER NOT NULL,
            date_debut DATETIME,
            date_fin DATETIME,
            duree_reelle INTEGER,
            statut TEXT DEFAULT 'En cours...',
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (methode_id) REFERENCES methodes_travail(id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS mesures_environnement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp DATETIME,
            luminosite INTEGER,
            qualite_air INTEGER,
            bruit INTEGER,
            presence BOOLEAN,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS pauses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            date_debut DATETIME,
            date_fin DATETIME,
            duree_reelle INTEGER,
            type TEXT DEFAULT 'programmee',
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            titre VARCHAR(255) NOT NULL,
            description TEXT,
            date_echeance DATETIME NOT NULL,
            type TEXT,
            priorite TEXT DEFAULT 'moyenne',
            notifie BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS recompenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            date DATE NOT NULL,
            sessions_completees INTEGER DEFAULT 0,
            jours_consecutifs INTEGER DEFAULT 0,
            objectif_atteint BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )'''
    ]
    
    # 创建所有表
    for sql in tables_sql:
        cursor.execute(sql)
    
    # 插入默认的工作方法
    cursor.execute('''SELECT COUNT(*) FROM methodes_travail''')
    if cursor.fetchone()[0] == 0:
        methodes = [
            ('Pomodoro Classique', 25, 5, 'Méthode traditionnelle 25/5'),
            ('Pomodoro Long', 50, 10, 'Sessions plus longues pour concentration intense'),
            ('Focus Intense', 90, 15, 'Session longue pour travail profond'),
            ('Rapide', 15, 3, 'Sessions courtes pour tâches rapides')
        ]
        cursor.executemany('''INSERT INTO methodes_travail (nom, duree_session, duree_pause, description) 
                              VALUES (?, ?, ?, ?)''', methodes)
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成！")

def hash_password(password):
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    init_database()
