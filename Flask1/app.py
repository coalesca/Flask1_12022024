from flask import Flask
from flask import request, jsonify, g, abort
from pathlib import Path
import sqlite3
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"


def get_db():
   db = getattr(g, '_database', None)
   if db is None:
      db = g._database = sqlite3.connect(DATABASE)
   
   def make_dicts(cursor, row):
      return dict((cursor.description[idx][0], value)
                  for idx, value in enumerate(row))
   db.row_factory = make_dicts        
   return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code

@app.route("/")
def hello_world():
   return "Hello, World!"

@app.route("/about")
def about():
   about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
   }
   return about_me

@app.route("/quotes")
def get_quotes():
   # Получение данных из БД
   select_quotes = "SELECT * from quotes"
   cursor = get_db().cursor()
   cursor.execute(select_quotes)
   quotes_db = cursor.fetchall() # list[tuple]
   if quotes_db:
      return jsonify(quotes_db), 200
   abort(404)

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   attribute_list = ["author", "text"]
   insert_quotes = f"INSERT INTO quotes({', '.join(attribute_list)}) VALUES ({', '.join(list('?' for _ in range(len(attribute_list))))})"
   params = tuple(data.get(attr) for attr in attribute_list)
   # print(insert_quotes, params)
   connection = get_db()
   cursor = connection.cursor()
   cursor.execute(insert_quotes, params)
   new_id = cursor.lastrowid
   connection.commit() # Фиксируем транзакцию
   cursor.close()
   # Возвращаем созданную цитату по new_id, переиспользуем функцию для get
   response, code = get_quote_by_id(new_id)
   if code == 200:
      return response, code
   abort(507)

@app.route("/quotes/<int:quote_id>", methods=['GET'])
def get_quote_by_id(quote_id):
   # Получение данных из БД
   select_quotes = "SELECT * from quotes WHERE id = ?"
   cursor = get_db().cursor()
   cursor.execute(select_quotes, (quote_id,))
   quotes_db = cursor.fetchone() # tuple
   if quotes_db:
      return jsonify(quotes_db), 200
   abort(404)

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
   new_data = request.json
   attribute_list = ["author", "text"]
   if "rating" in new_data and "rating" in attribute_list and new_data["rating"] not in range(1, 6):
   # Валидируем новое значение рейтинга, в случае успеха обновляем
      attribute_list.remove("rating")
   update_quotes = f"UPDATE quotes SET {', '.join(list(attr + '=?' for attr in attribute_list))} WHERE id = ?"
   params = (*list(new_data.get(attr) for attr in attribute_list), quote_id)
   # print(update_quotes, params)
   connection = get_db()
   cursor = connection.cursor()
   cursor.execute(update_quotes, params)  
   rows = cursor.rowcount
   if rows:
      connection.commit()
      cursor.close()         
      # Возвращаем обновлённую цитату по quote_id, переиспользуем функцию для get
      response, code = get_quote_by_id(quote_id)
      if code == 200:
         return response, code
   connection.rollback()
   abort(404)

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
   delete_quotes = f"DELETE FROM quotes WHERE id = ?"
   params = (quote_id,)
   # print(delete_quotes, params)
   connection = get_db()
   cursor = connection.cursor()
   cursor.execute(delete_quotes, params)  
   rows = cursor.rowcount
   if rows:
      connection.commit()
      cursor.close()         
      return jsonify({"message": f"Quote with id {quote_id} is deleted."}), 200
   connection.rollback()
   abort(404)
   
@app.route("/quotes/count")
def get_quotes_count():
   # Получение данных из БД
   select_quote = "SELECT count(*) as count from quotes"
   cursor = get_db().cursor()
   cursor.execute(select_quote)
   quote_db = cursor.fetchone()
   if quote_db:
      return jsonify(quote_db), 200
   abort(404)

@app.route("/quotes/random")
def get_random_quote():
   # Получение данных из БД
   select_quote = "SELECT * from quotes ORDER BY RANDOM() LIMIT 1"
   cursor = get_db().cursor()
   cursor.execute(select_quote)
   quote_db = cursor.fetchone()
   if quote_db:
      return jsonify(quote_db), 200
   abort(404)

@app.route("/quotes/filter")
def get_filtered_quotes():
   args = request.args
   author = args.get("author", default="", type=str)
   rating = args.get("rating", default=0, type=int)

   attribute_list = ["author", "text"]
   select_quotes = f"SELECT * FROM quotes \n WHERE 1 = 1"
   params = []

   if author and "author" in attribute_list:
      select_quotes += f"\n AND author like ?"
      params.append(f"%{author}%")
   if rating and "rating" in attribute_list:
      select_quotes += f"\n AND rating = ?"
      params.append(rating)

   # print(select_quotes, tuple(params))
   cursor = get_db().cursor()
   cursor.execute(select_quotes, tuple(params))
   quotes_db = cursor.fetchall() # list[tuple]
   if quotes_db:
      return jsonify(quotes_db), 200
   abort(404)

if __name__ == "__main__":
   app.run(debug=True)

