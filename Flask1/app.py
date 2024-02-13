from flask import Flask
from flask import request
from random import choice

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
         return quote, 200
   return {"error": f"Цитата c {id=} не найдена"}, 404

@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
   for quote in quotes:
      if quote["id"] == id:
         quotes.remove(quote)
         return {"error": f"Quote with id {id} is deleted."}, 200
   return {"error": f"Цитата c {id=} не найдена"}, 404
   
@app.route("/quotes/count")
def get_quotes_count():
   return {"count": len(quotes)}, 200

@app.route("/quotes/random")
def get_random_quote():
   return choice(quotes), 200

if __name__ == "__main__":
   app.run(debug=True)

