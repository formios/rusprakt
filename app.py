import os
from flask import Flask, request, jsonify, render_template_string
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
# HTML-интерфейс (Простой визуальный сайт)
# ------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сервис заметок</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f7f6; }
        h1, h2 { color: #333; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        form { display: flex; flex-direction: column; gap: 10px; }
        input, textarea, select, button { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #0056b3; }
        .note-item { border-left: 4px solid #007bff; padding: 10px; margin-bottom: 10px; background: #fafafa; display: flex; justify-content: space-between; align-items: center; }
        .delete-btn { background-color: #dc3545; padding: 5px 10px; font-size: 12px; }
        .delete-btn:hover { background-color: #bd2130; }
        .badge { background: #e2e8f0; padding: 3px 8px; border-radius: 12px; font-size: 12px; color: #4a5568; }
    </style>
</head>
<body>

    <h1>📝 Сервис заметок (`rusprakt`)</h1>

    <!-- Форма создания категории -->
    <div class="card">
        <h2>Создать категорию</h2>
        <form id="categoryForm">
            <input type="text" id="catName" placeholder="Название категории (например, Учёба)" required>
            <button type="submit">Добавить категорию</button>
        </form>
    </div>

    <!-- Форма создания заметки -->
    <div class="card">
        <h2>Добавить заметку</h2>
        <form id="noteForm">
            <input type="text" id="noteTitle" placeholder="Заголовок заметки" required>
            <textarea id="noteContent" placeholder="Текст заметки..." rows="3" required></textarea>
            <select id="noteCategory">
                <option value="">Без категории</option>
            </select>
            <button type="submit">Сохранить заметку</button>
        </form>
    </div>

    <!-- Список заметок -->
    <div class="card">
        <h2>Все заметки</h2>
        <div id="notesList">Загрузка заметок...</div>
    </div>

    <script>
        // Функция загрузки категорий в список формы
        async function loadCategories() {
            const res = await fetch('/api/categories');
            const categories = await res.json();
            const select = document.getElementById('noteCategory');
            select.innerHTML = '<option value="">Без категории</option>';
            categories.forEach(c => {
                select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }

        // Функция загрузки заметок
        async function loadNotes() {
            const res = await fetch('/api/notes');
            const notes = await res.json();
            const catRes = await fetch('/api/categories');
            const categories = await catRes.json();
            const catMap = Object.fromEntries(categories.map(c => [c.id, c.name]));

            const list = document.getElementById('notesList');
            if (notes.length === 0) {
                list.innerHTML = '<p style="color: #777;">Заметок пока нет. Создайте первую!</p>';
                return;
            }

            list.innerHTML = '';
            notes.forEach(n => {
                const catName = n.category_id ? catMap[n.category_id] || 'Категория' : 'Без категории';
                list.innerHTML += `
                    <div class="note-item">
                        <div>
                            <strong>${n.title}</strong> <span class="badge">${catName}</span>
                            <p style="margin: 5px 0 0 0; color: #555;">${n.content}</p>
                        </div>
                        <button class="delete-btn" onclick="deleteNote(${n.id})">Удалить</button>
                    </div>
                `;
            });
        }

        // Создание категории
        document.getElementById('categoryForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('catName').value;
            await fetch('/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            document.getElementById('catName').value = '';
            loadCategories();
        });

        // Создание заметки
        document.getElementById('noteForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('noteTitle').value;
            const content = document.getElementById('noteContent').value;
            const category_id = document.getElementById('noteCategory').value || null;

            await fetch('/api/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content, category_id: category_id ? parseInt(category_id) : null })
            });
            document.getElementById('noteTitle').value = '';
            document.getElementById('noteContent').value = '';
            loadNotes();
        });

        // Удаление заметки
        async function deleteNote(id) {
            await fetch(`/api/notes/${id}`, { method: 'DELETE' });
            loadNotes();
        }

        // Первоначальная загрузка
        loadCategories();
        loadNotes();
    </script>
</body>
</html>
"""

# ------------------------------------------------------------------
# Маршруты (Endpoints)
# ------------------------------------------------------------------

# Главная страница с визуальным интерфейсом
@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

# API Категорий
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

    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories]), 200

# API Заметок
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

    notes = Note.query.all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'category_id': n.category_id
    } for n in notes]), 200

# Удаление заметки
@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Заметка не найдена'}), 404
    
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': f'Заметка с id {note_id} удалена'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)