from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('learning_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    """首页"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # 获取用户信息
    user = conn.execute('SELECT * FROM utilisateurs WHERE id = ?', (session['user_id'],)).fetchone()
    
    # 获取今日会话统计
    today = datetime.now().date()
    sessions_today = conn.execute('''
        SELECT COUNT(*) FROM sessions 
        WHERE utilisateur_id = ? AND DATE(date_debut) = ? AND statut = "Terminé"
    ''', (session['user_id'], today)).fetchone()[0]
    
    # 获取待办事项
    todos = conn.execute('''
        SELECT * FROM agenda 
        WHERE utilisateur_id = ? AND date_echeance >= DATE('now') 
        ORDER BY priorite DESC, date_echeance ASC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('index.html', user=user, sessions_today=sessions_today, todos=todos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM utilisateurs WHERE email = ? AND mot_de_passe_hash = ?',
            (email, hash_password(password))
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = f"{user['prenom']} {user['nom']}"
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='邮箱或密码错误')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe_hash) VALUES (?, ?, ?, ?)',
                (nom, prenom, email, hash_password(password))
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='邮箱已存在')
    
    return render_template('register.html')

@app.route('/pomodoro')
def pomodoro():
    """番茄工作法页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    methodes = conn.execute('SELECT * FROM methodes_travail').fetchall()
    conn.close()
    
    return render_template('pomodoro.html', methodes=methodes)

@app.route('/start_session', methods=['POST'])
def start_session():
    """开始学习会话"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'})
    
    methode_id = request.json['methode_id']
    conn = get_db_connection()
    
    # 插入新会话
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (utilisateur_id, methode_id, date_debut, statut) 
        VALUES (?, ?, ?, ?)
    ''', (session['user_id'], methode_id, datetime.now(), 'En cours...'))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'session_id': session_id})

@app.route('/end_session', methods=['POST'])
def end_session():
    """结束学习会话"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'})
    
    session_id = request.json['session_id']
    conn = get_db_connection()
    
    # 更新会话状态
    conn.execute('''
        UPDATE sessions SET date_fin = ?, statut = 'Terminé' 
        WHERE id = ? AND utilisateur_id = ?
    ''', (datetime.now(), session_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/agenda')
def agenda():
    """日程管理页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT * FROM agenda 
        WHERE utilisateur_id = ? 
        ORDER BY date_echeance ASC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('agenda.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    """添加任务"""
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    titre = request.json['titre']
    description = request.json.get('description', '')
    date_echeance = request.json['date_echeance']
    priorite = request.json.get('priorite', 'moyenne')
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO agenda (utilisateur_id, titre, description, date_echeance, priorite)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], titre, description, date_echeance, priorite))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/stats')
def stats():
    """数据统计页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # 获取最近7天的会话数据
    seven_days_ago = (datetime.now() - timedelta(days=7)).date()
    sessions_data = conn.execute('''
        SELECT DATE(date_debut) as date, COUNT(*) as count, SUM(duree_reelle) as total_duration
        FROM sessions 
        WHERE utilisateur_id = ? AND date_debut >= ? AND statut = 'Terminé'
        GROUP BY DATE(date_debut)
        ORDER BY date
    ''', (session['user_id'], seven_days_ago)).fetchall()
    
    # 获取最常用的工作方法
    popular_methods = conn.execute('''
        SELECT m.nom, COUNT(*) as usage_count
        FROM sessions s
        JOIN methodes_travail m ON s.methode_id = m.id
        WHERE s.utilisateur_id = ?
        GROUP BY m.nom
        ORDER BY usage_count DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('stats.html', 
                         sessions_data=sessions_data,
                         popular_methods=popular_methods)

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # 初始化数据库
    from init_database import init_database
    init_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
