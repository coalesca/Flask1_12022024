from flask import Flask
from flask import request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
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
   return quotes

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   print("data = ", data)
   new_quote = {
                  "id": get_new_quote_id(),
                  "author": data["author"],
                  "text": data["text"]
               }
   quotes.append(new_quote)
   return new_quote, 201

def get_new_quote_id():
   return quotes[-1]["id"] + 1

@app.route("/quotes/<int:id>", methods=['GET'])
def get_quote(id):
   print("GET id = ", id)
   quote = list(filter(lambda x: x["id"] == id, quotes))
   if not quote:
      return {"error": f"Цитата c {id=} не найдена"}, 404
   if len(quote) > 1:
      return {"error": "Найдено несколько соответствий"}, 500
   return quote[0], 200

if __name__ == "__main__":
   app.run(debug=True)
