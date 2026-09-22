import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------------------------------------------
# Модели базы данных
# ------------------------------------------------------------------
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    notes = db.relationship('Note', backref='category', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

# Инициализация таблиц
with app.app_context():
    db.create_all()

# ------------------------------------------------------------------
# Маршруты (Endpoints)
# ------------------------------------------------------------------

# 1. Главная страница (чтобы не было 404 на корневом URL)
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "REST API Сервис заметок успешно работает!",
        "endpoints": {
            "categories": "/api/categories",
            "notes": "/api/notes"
        }
    }), 200

# 2. Категории (GET - просмотреть все, POST - создать новую)
@app.route('/api/categories', methods=['GET', 'POST'])
def handle_categories():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Имя категории обязательно'}), 400
        
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'id': new_category.id, 'message': 'Категория создана'}), 201

    # Если запрос GET (например, при открытии в браузере)
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories]), 200

# 3. Заметки (GET - просмотреть все, POST - создать новую)
@app.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Поля title и content обязательны'}), 400
        
        new_note = Note(
            title=data['title'],
            content=data['content'],
            category_id=data.get('category_id')
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'id': new_note.id, 'message': 'Заметка создана'}), 201

    # Если запрос GET
    notes = Note.query.all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'category_id': n.category_id
    } for n in notes]), 200

# 4. Удаление заметки по ID
@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Заметка не найдена'}), 404
    
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': f'Заметка с id {note_id} удалена'}), 200

# ------------------------------------------------------------------
# Запуск сервера
# ------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)