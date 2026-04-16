from scripts.regsetup import description

from data.places import Places
from data import db_session
from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty_zcvbn'


def add():
    db_session.global_init("db/places.db")

    name = input("Напишите название места: ")
    dep = input("Напишите описание места (краткое): ")
    dep_full = input("Напишите описание места (полное): ")
    categ = input("Напишите категорию места (Кино, Театры, Парки и т. д.): ")
    addr = input("Напишите адрес места: ")
    hour = input("Напишите часы работы этого места: ")
    hour_open = int(input("Напишите час открытия ЧИСЛОМ"))
    hour_close = int(input("Напишите час закрытия ЧИСЛОМ"))
    lnk_mp = input("Напишите ссылку карт этого места: ")
    name_phot_main = input("Напишите ТОЧНОЕ название главного фото в папке static/images: ")
    name_phot_1 = input("Напишите ТОЧНОЕ название 1-ого фото в папке static/images: ")
    name_phot_2 = input("Напишите ТОЧНОЕ название 2-ого фото в папке static/images: ")


    o = input("Точно хотите добавить? (да/нет): ")

    if o.lower() == "да":
        place = Places(
            title=name,
            description=dep,
            deprecation_full=dep_full,
            category=categ,
            address=addr,
            opening_hours=hour,
            link_map=lnk_mp,
            name_photo_main=name_phot_main,
            name_photo_1=name_phot_1,
            name_photo_2=name_phot_2,
            open_hour=hour_open,
            close_hour=hour_close
        )

        db_sess = db_session.create_session()
        db_sess.add(place)
        db_sess.commit()
        db_sess.close()

        print("Место успешно добавлено!")


def delete():
    db_session.global_init("db/places.db")
    sess = db_session.create_session()

    all_places = sess.query(Places).all()
    if not all_places:
        print("Нет ни одного места в базе данных.")
        sess.close()
        return

    print("\nСписок всех мест:")
    for place in all_places:
        print(f"  ID: {place.id} | Название: {place.title}")

    place_id_input = input("\nВведите ID места для удаления: ")
    try:
        place_id = int(place_id_input)
    except ValueError:
        print("Ошибка: ID должен быть числом.")
        sess.close()
        return

    place = sess.query(Places).get(place_id)
    if not place:
        print(f"Место с ID {place_id} не найдено.")
        sess.close()
        return

    print(f"\nВы выбрали:")
    print(f"  ID: {place.id}")
    print(f"  Название: {place.title}")
    print(f"  Категория: {place.category}")
    print(f"  Адрес: {place.address}")

    confirm = input("\nВы уверены, что хотите удалить это место? (да/нет): ")
    if confirm.lower() == "да":
        sess.delete(place)
        sess.commit()
        print("Место успешно удалено!")
    else:
        print("Удаление отменено.")

    sess.close()


if __name__ == "__main__":
    choice = input("Что вы хотите сделать с базой данных?(добавить место - add; удалить место - del) ").lower()
    if choice == "add":
        add()
    elif choice == "del":
        delete()