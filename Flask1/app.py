from flask import Flask
from flask import request, jsonify, g, abort
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from pathlib import Path
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
   __tablename__ = "authors"
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(302), unique=True, nullable=False)
   quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

   def __init__(self, name):
       self.name = name

   def __repr__(self):
      return f"Author({self.name})"
   
   def to_dict(self):
      return {
         "id": self.id,
         "name": self.name
      }

class QuoteModel(db.Model):
   __tablename__ = "quotes"
   id = db.Column(db.Integer, primary_key=True)
   author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id), nullable=False)
   text = db.Column(db.String(255), unique=False, nullable=False)
   rating = db.Column(db.Integer, unique=False, nullable=False, default=1, server_default="1")

   def __init__(self, author: AuthorModel, text, rating):
       self.author_id = author.id
       self.text  = text
       self.rating = rating
      
   def __repr__(self):
      return f"Quote({self.author}, {self.text}, {self.rating})"

   def to_dict(self):
      return {
         "id": self.id,
         "author_id": self.author_id,
         "text": self.text,
         "rating": self.rating
      }


def validate(in_data: dict, method="POST") -> dict:
   rating = in_data.setdefault("rating", 1)
   if rating not in range(1,6):
      if method == "POST":
         in_data["rating"] = 1
      if method == "PUT":
         in_data.pop("rating")
   text = in_data.setdefault("text", "text")

   if text == "text" and method == "PUT":
      in_data.pop("text")

   return in_data
   
# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/authors", methods=["GET", "POST"])
def handle_authors():
      if request.method == "GET":
         authors = AuthorModel.query.all()
         authors_dict = []
         for author in authors:
            authors_dict.append(author.to_dict())
         return jsonify(authors_dict), 200       
      if request.method == "POST":
         author_data = request.json
         author = AuthorModel(author_data.get("name", "Ivan"))
         db.session.add(author)
         try:
            db.session.commit()
            return author.to_dict(), 201
         except:
            abort(400, "UNIQUE constraint failed")   

@app.route("/authors/<int:author_id>", methods=["GET", "PUT", "DELETE"])
def handle_author(author_id):
      author = AuthorModel.query.get(author_id)
      if not author:
         abort(404, f"Author with id = {author_id} not found")
      
      if request.method == "GET":
         return jsonify(author.to_dict()), 200

      message = {}
      if request.method == "PUT":
         new_data = request.json
         # Универсальный случай
         for key, value in new_data.items():
            setattr(author, key, value)
         message = author.to_dict()

      if request.method == "DELETE":
         quotes_db = QuoteModel.query.filter_by(author_id=author_id).all()
         for quote in quotes_db:
            db.session.delete(quote)
         db.session.delete(author)
         message = {"message": f"Author with id={author_id} deleted successfully"}
    
      try:
         db.session.commit()
         return jsonify(message), 200
      except:
         abort(400, f"Database commit operation failed.") 

@app.route("/authors/<int:author_id>/quotes", methods=["GET", "POST"])
def handle_quotes_by_author(author_id):
   author = AuthorModel.query.get(author_id)
   if not author:
      abort(404, f"Author with id = {author_id} not found")

   if request.method == "GET":
      quotes_db = QuoteModel.query.filter_by(author_id=author_id).all()
      quotes_dict = []
      for quote in quotes_db:
         quotes_dict.append(quote.to_dict())
      return jsonify(quotes_dict), 200      

   if request.method == "POST":
      data = request.json
      data = validate(data, "POST")
      new_quote = QuoteModel(author=author, **data)
      db.session.add(new_quote)
      try:
         db.session.commit()
         return jsonify(new_quote.to_dict()), 200
      except:       
         abort(400, "NOT NULL constraint failed")

@app.route("/quotes/<int:quote_id>", methods=["GET", "PUT", "DELETE"])
def handle_quote_by_id(quote_id):
      quote = QuoteModel.query.get(quote_id)
      if not quote:
         abort(404, f"Quote with id={quote_id} not found")
      
      if request.method == "GET":
         return jsonify(quote.to_dict()), 200

      message = {}
      if request.method == "PUT":
         new_data = request.json
         new_data = validate(new_data, "PUT")         
         # Универсальный случай
         for key, value in new_data.items():
            setattr(quote, key, value) 
         message = quote.to_dict()                  

      if request.method == "DELETE":
         db.session.delete(quote)
         message = {"message": f"Quote with id={quote_id} deleted successfully"}
      
      try:
         db.session.commit()
         return jsonify(message), 200
      except:
         abort(400, f"Database commit operation failed.") 
         
@app.route("/quotes")
def get_quotes():
   """Сериализация: list[quotes] -> list[dict] -> str(JSON)"""
   quotes_db = QuoteModel.query
   quotes = []
   for quote in quotes_db:
      quotes.append(quote.to_dict())
   
   return jsonify(quotes), 200

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
   
   # Частный случай
   # author = args.get("author", default="", type=str)
   # rating = args.get("rating", default=0, type=int)
     
   # query = QuoteModel.query
   # if author:
   #    query = query.filter(QuoteModel.author.contains(author))
   # if rating:
   #    query = query.filter_by(rating=rating)
   # quotes_db = query.all()

   # Универсальное решение  
   quotes_db = QuoteModel.query.filter_by(**args).all()
   
   if quotes_db:
      quotes = []
      for quote in quotes_db:
         quotes.append(quote.to_dict())      
      return jsonify(quotes), 200
   abort(404)

if __name__ == "__main__":
   app.run(debug=True)

