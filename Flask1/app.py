from flask import Flask
from flask import request, jsonify, g, abort
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
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
   rating = db.Column(db.Integer, unique=False, default=1)

   def __init__(self, author, text, rating = 1):
       self.author = author
       self.text  = text
       self.rating = rating
      
   def __repr__(self):
      return f"Quote({self.author}, {self.text}, {self.rating})"

   def to_dict(self):
      return {
         "id": self.id,
         "author": self.author,
         "text": self.text,
         "rating": self.rating
      }

   @staticmethod
   def validate_rating(rating):
      if rating in range(1,6): 
         return True
      return False

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

@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
   quote = QuoteModel.query.get(quote_id)
   if quote:
      return jsonify(quote.to_dict()), 200
   abort(404)

@app.post("/quotes")
def create_quote():
   data = request.json
   author = data.get("author")
   text = data.get("text")
   rating = data.get("rating")
   if not rating or not QuoteModel.validate_rating(rating):
      rating = 1
   quote = QuoteModel(author=author, text=text, rating=rating)
   db.session.add(quote)
   try:
      db.session.commit()
      return jsonify(quote.to_dict()), 200
   except:
      abort(500)

@app.put("/quotes/<int:quote_id>")
def edit_quote(quote_id):
   new_data = request.json
   quote = QuoteModel.query.get(quote_id)
   if not quote:
      abort(404)
   quote.author = new_data.get("author") if new_data.get("author") else quote.author
   quote.text = new_data.get("text") if new_data.get("text") else quote.text
   rating = new_data.get("rating")
   if rating and quote.validate_rating(rating):
      quote.rating = rating
   try:
      db.session.commit()
      return jsonify(quote.to_dict()), 200
   except:
      abort(500)

@app.delete("/quotes/<int:quote_id>")
def delete_quote(quote_id):
   quote = QuoteModel.query.get(quote_id)
   if not quote:
      abort(404)
   db.session.delete(quote)
   try:
      db.session.commit()
      return jsonify(message=f"Quote with id = {quote_id} deleted successfully"), 200
   except:
      abort(500)

@app.get("/quotes/random")
def get_random_quote():
   quote = QuoteModel.query.order_by(func.random()).limit(1)
   if quote:
      return jsonify(quote[0].to_dict()), 200
   abort(404)

@app.get("/quotes/count")
def get_quotes_count():
   count = QuoteModel.query.count()
   if count:
      return jsonify(count=count), 200
   abort(404)

@app.get("/quotes/filter")
def get_filtered_quotes():
   args = request.args
   author = args.get("author", default="", type=str)
   rating = args.get("rating", default=0, type=int)
   query = QuoteModel.query
   if author:
      query = query.filter(QuoteModel.author.contains(author))
   if rating:
      query = query.filter_by(rating=rating)
   
   quotes_db = query.all()
   if quotes_db:
      quotes = []
      for quote in quotes_db:
         quotes.append(quote.to_dict())      
      return jsonify(quotes), 200
   abort(404)

if __name__ == "__main__":
   app.run(debug=True)

