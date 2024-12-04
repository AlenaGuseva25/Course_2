from re import search
from typing import List, Any, Dict
from src.subclasses import JsonJob, HeadHunterAPI, Vacancy
from src.utils import connect_to_api, format_salary, valid_salary, read_json_file, write_json_file, vacancy_exists

def user_interaction():
    """Функция взаимодействия с пользователем"""
    hh_api = HeadHunterAPI()
    json_job = JsonJob()

    search_query = input("Введите поисковый запрос: ")
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    salary_range = input("Введите диапазон зарплат: ")

    # Получение вакансий с hh
    hh_vacancies = hh_api.get_vacancies(search_query)

    # Получение данных вакансий
    vacancies_list = Vacancy.list_total(hh_vacancies)

    # Фильтрация вакансий по ключевым словам
    filter_vacancies = [v for v in vacancies_list if all(word.lower() in v.description.lower() for word in filter_words)]

    # Фильтрация по зарплате
    min_salary, max_salary = map(int, salary_range.split("-"))
    ranged_vacancies = [v for v in filter_vacancies if min_salary <= v._valid_salary(v.salary) <= max_salary]

    # Сортировка вакансий по имени
    sorted_vacancies = sorted(ranged_vacancies, key=lambda v: v.__name)

    top_vacancies = sorted_vacancies[:top_n]

    # Результаты поиска
    for vacancy in top_vacancies:
        print(f"{vacancy.name}: {vacancy.url}")

    # Запись в файл
    json_job.add_vacancy(top_vacancies)



if __name__ == "__main__":
    user_interaction()