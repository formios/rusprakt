from flask import Flask, request, jsonify
from models import db, Note, Category

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/api/notes', methods=['GET'])
    def get_notes():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        category_id = request.args.get('category_id', type=int)

        query = Note.query
        if category_id:
            query = query.filter_by(category_id=category_id)

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        notes_list = [{
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'category_id': note.category_id
        } for note in paginated.items]

        return jsonify({
            'notes': notes_list,
            'total': paginated.total,
            'page': page,
            'pages': paginated.pages
        }), 200

    @app.route('/api/notes', methods=['POST'])
    def create_note():
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Обязательные поля: title и content'}), 400

        new_note = Note(
            title=data['title'],
            content=data['content'],
            category_id=data.get('category_id')
        )
        db.session.add(new_note)
        db.session.commit()

        return jsonify({'message': 'Заметка успешно создана', 'id': new_note.id}), 201

    @app.route('/api/notes/<int:note_id>', methods=['DELETE'])
    def delete_note(note_id):
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return jsonify({'message': 'Заметка удалена'}), 200

    @app.route('/api/categories', methods=['POST'])
    def create_category():
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Поле name обязательно'}), 400

        new_cat = Category(name=data['name'])
        db.session.add(new_cat)
        db.session.commit()

        return jsonify({'message': 'Категория создана', 'id': new_cat.id}), 201

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.route('/api/categories', methods=['GET', 'POST'])
def handle_categories():
    if request.method == 'POST':
        data = request.get_json()
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({"id": new_category.id, "message": "Категория создана"}), 201
    
    # Если метод GET (например, при открытии в браузере):
    categories = Category.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in categories]), 200