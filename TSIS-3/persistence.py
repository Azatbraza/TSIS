import json
import os

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"


# Загрузка настроек из файла
def load_settings():
    # Значения по умолчанию
    default = {
        "sound": True,
        "difficulty": "normal",
        "car_color": "yellow"
    }

    # Если файла нет — возвращаем дефолт
    if not os.path.exists(SETTINGS_FILE):
        return default

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Обновляем дефолт значениями из файла
        default.update(data)
        return default

    except:
        # Если ошибка чтения — просто используем дефолт
        return default


# Сохранение настроек
def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Загрузка таблицы рекордов
def load_scores():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# Сохранение нового результата
def save_score(name, score, distance):
    data = load_scores()

    # Добавляем новый результат
    data.append({
        "name": name,
        "score": int(score),
        "distance": int(distance)
    })

    # Сортируем по очкам и дистанции
    data = sorted(
        data,
        key=lambda x: (x["score"], x["distance"]),
        reverse=True
    )[:10]

    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)