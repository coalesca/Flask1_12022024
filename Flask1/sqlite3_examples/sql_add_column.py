import sqlite3

add_rating = """
ALTER TABLE quotes ADD COLUMN rating INTEGER DEFAULT 1;
"""
add_constraint = """
ALTER TABLE quotes ADD CONSTRAINT rating_constraint CHECK ((rating >= 1) and (rating <=5));
"""
# Подключение в БД
connection = sqlite3.connect("main.db")
# Создаем cursor, он позволяет делать SQL-запросы
cursor = connection.cursor()
# Выполняем запрос:
cursor.execute(add_rating)
# cursor.execute(add_constraint)  # Не работает
# Фиксируем выполнение(транзакцию)
connection.commit()
# Закрыть курсор:
cursor.close()
# Закрыть соединение:
connection.close()
