from flask import Flask
from flask import request, jsonify
from random import choice
from pathlib import Path
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"

about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
       "rating": 1
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
       "rating": 2
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
       "rating": 4
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так.",
       "rating": 5
   },

]

@app.route("/")
def hello_world():
   return "Hello, World!"

@app.route("/about")
def about():
   return about_me

@app.route("/quotes")
def get_quotes():
   # Получение данных из БД
   select_quotes = "SELECT * from quotes"
   connection = sqlite3.connect("test.db")
   cursor = connection.cursor()
   cursor.execute(select_quotes)
   quotes_db = cursor.fetchall() # list[tuple]
   cursor.close()
   connection.close()   
   # Подготовка данных для возврата
   # Необходимо выполнит преобразование:
   # list[tuple] -> list[dict]
   keys = ["id", "author", "text"]
   quotes = []
   for quote_db in quotes_db:
      quote = dict(zip(keys, quote_db))
      quotes.append(quote)

   return jsonify(quotes), 200

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   print("data = ", data)
   new_quote = {
                  "id": get_new_quote_id(),
                  "author": data["author"],
                  "text": data["text"],
                  "rating": new_rating if "rating" in data.keys() and (new_rating := data["rating"]) >= 1 and new_rating <= 5 else 1
               }
   quotes.append(new_quote)
   return new_quote, 201

def get_new_quote_id():
   return quotes[-1]["id"] + 1

@app.route("/quotes/<int:id>", methods=['GET'])
def get_quote(id):
   print("GET id = ", id)
   for quote in quotes:
      if quote["id"] == id:
         return quote, 200
   return {"error": f"Цитата c {id=} не найдена"}, 404

@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
   new_data = request.json
   for quote in quotes:
      if quote["id"] == id:
         if "text" in new_data.keys():
            quote["text"] = new_data["text"]
         if "author" in new_data.keys():
            quote["author"] = new_data["author"]
         if "rating" in new_data.keys():
            # Валидируем новое значение рейтинга, в случае успеха обновляем
            if (new_rating := new_data["rating"]) >= 1 and new_rating <= 5:
               quote["rating"] = new_rating            
         return quote, 200
   return {"error": f"Цитата c {id=} не найдена"}, 404

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id):
   for quote in quotes:
      if quote["id"] == id:
         quotes.remove(quote)
         return jsonify({"message": f"Quote with id {id} is deleted."}), 200
   return {"error": f"Цитата c {id=} не найдена"}, 404
   
@app.route("/quotes/count")
def get_quotes_count():
   return {"count": len(quotes)}, 200

@app.route("/quotes/random")
def get_random_quote():
   return choice(quotes), 200

@app.route("/quotes/filter")
def get_filtered_quotes():
   args = request.args
   result = []
   author = args.get("author", default="", type=str)
   rating = args.get("rating", default=0, type=int)
   for quote in quotes:
      # Поиск по автору по части строки регистронезависимый
      if author:
         if author.lower() not in quote["author"].lower():
            continue
      # Поиск по рейтингу
      if rating:
         if quote["rating"] != rating:
            continue         
      result.append(quote)
   if result:
      return result, 200
   return {"error": f"Цитаты c указанными фильтрами не найдены"}, 404
   

if __name__ == "__main__":
   app.run(debug=True)

