# PoTours — Туристический портал

Дизайн перенесён из Figma. Проект на Django.

## Структура проекта

```
PoTours/
├── potours/          # Настройки Django
├── tours/            # Приложение туров
├── templates/        # HTML-шаблоны
│   ├── base.html     # Базовый layout (header, footer)
│   ├── index.html    # Главная страница
│   ├── tours.html    # Список туров с фильтрами
│   └── tour_detail.html  # Детали тура
├── static/
│   └── css/
│       ├── variables.css   # Дизайн-система (цвета, типографика)
│       ├── base.css        # Базовые стили, кнопки
│       ├── components.css  # Компоненты (header, карточки, footer)
│       └── main.css        # Главный файл стилей
├── manage.py
└── requirements.txt
```

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# База данных (первый запуск или после клонирования)
python manage.py migrate

# Запуск сервера
python manage.py runserver
```

Откройте http://127.0.0.1:8000/

## База данных и контент (media)

- **База:** `db.sqlite3` в корне проекта. В репозиторий не попадает (см. `.gitignore`). После клонирования выполните `python manage.py migrate`. Для суперпользователя: `python manage.py createsuperuser`.
- **Медиа (контент):** папка `media/` — загруженные файлы, изображения из Figma. В репозиторий не коммитится. Структура и скрипт копирования: см. `media/README.md`, `organize_media.py`.

## Страницы

- **/** — Главная (hero, популярные направления, «почему мы»)
- **/tours/** — Список туров с фильтрами
- **/tours/1/** — Детали тура, бронирование

## Дизайн из Figma

- Основной цвет: красный (#E31837)
- Шрифт: Inter
- Адаптивная вёрстка
- Компоненты: header, footer, карточки туров, кнопки, фильтры
