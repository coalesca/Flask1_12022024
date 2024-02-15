from flask import Flask
from flask import request, jsonify, g, abort
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class QuoteModel(db.Model):
   __tablename__ = "quotes"
   id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(32), unique=False)
   text = db.Column(db.String(255), unique=False)

   def __init__(self, author, text):
       self.author = author
       self.text  = text
      
   def __repr__(self):
      return f"Quote({self.author}, {self.text})"

   def to_dict(self):
      return {
         "id": self.id,
         "author": self.author,
         "text": self.text
      }

# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/quotes")
def get_quotes():
   """Сериализация: list[quotes] -> list[dict] -> str(JSON)"""
   quotes_db = QuoteModel.query
   quotes = []
   for quote in quotes_db:
      quotes.append(quote.to_dict())
   
   return jsonify(quotes), 200


if __name__ == "__main__":
   app.run(debug=True)

