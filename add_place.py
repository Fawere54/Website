from data.places import Places
from data import db_session
from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '?'


def main():
    db_session.global_init("db/places.db")

    name = input("Напишите название места: ")
    dep = input("Напишите описание места: ")
    categ = input("Напишите категорию места (Кино, Театры, Парки и т. д.): ")
    addr = input("Напишите адрес места: ")
    hour = input("Напишите часы работы этого места: ")

    o = input("Точно хотите добавить? (да/нет): ")

    if o.lower() == "да":
        place = Places(
            title=name,
            description=dep,
            category=categ,
            opening_hours=hour,
            address=addr
        )

        db_sess = db_session.create_session()
        db_sess.add(place)
        db_sess.commit()
        db_sess.close()

        print("Место успешно добавлено!")


if __name__ == "__main__":
    main()