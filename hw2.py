import requests
from bs4 import BeautifulSoup as bs
import sqlite3

# Создание базы данных SQLite
connection = sqlite3.connect("vacancies.db")
cursor = connection.cursor()

# Создание таблицы vacancies, если она не существует
cursor.execute("""
    CREATE TABLE IF NOT EXISTS vacancies (
        company_name TEXT,
        position TEXT,
        job_description TEXT,
        key_skills TEXT
    )
""")

URL = "https://hh.ru"
API_URL = "https://api.hh.ru/vacancies"

# Параметры запроса API
params = {
    "text": "Python",
    "area": 1,  # Код Москвы
    "specialization": 1,  # IT, разработка
    "per_page": 100  # Количество вакансий для загрузки
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Загрузка данных через API
response = requests.get(API_URL, params=params, headers=headers)
data = response.json()
vacancies = data["items"]



for vacancy in vacancies:
    
     company_name = vacancy["employer"]["name"]
     position = vacancy["name"]
     vacancy_page = requests.get(vacancy['url'])
     vacancy_data = vacancy_page.json()
     job_description = bs(vacancy_data['description'], 'lxml').get_text()
     key_skills = ", ".join([skill["name"] for skill in vacancy_data["key_skills"]])
    
     # Вставка данных в таблицу vacancies
     cursor.execute("INSERT INTO vacancies VALUES (?, ?, ?, ?)",
                     (company_name, position, job_description, key_skills))

# Загрузка данных через парсинг web-страниц
response = requests.get(URL + "/search/vacancy?text=Python&area=1", headers=headers)
soup = bs(response.content, "html.parser")


vacancy_items = soup.find_all("div", class_="vacancy-serp-item")


for item in vacancy_items:
    company_name = item.find("a").text.strip()
    position = item.find("a", class_="bloko-link-secondary").text.strip()

    # В некоторых вакансиях могут отсутствовать описание и ключевые навыки,
    # поэтому проверяем на их наличие перед получением
    description = item.find("div", class_="g-user-content").text.strip() if item.find("div", class_="g-user-content") is not None else ""
    skills = ", ".join([skill.text.strip() for skill in item.find_all("span", class_="bloko-tag__section_text")])
    print(skills)
    # Вставка данных в таблицу vacancies
    cursor.execute("INSERT INTO vacancies VALUES (?, ?, ?, ?)",
                   (company_name, position, description, skills))

# Сохранение изменений и закрытие соединения с базой данных
connection.commit()
connection.close()