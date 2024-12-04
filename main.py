import json
import requests
from re import search
from typing import List, Any, Dict
from src.subclasses import JsonJob, HeadHunterAPI, Vacancy
from src.utils import connect_to_api, format_salary, valid_salary, read_json_file, write_json_file, vacancy_exists
from src.abstract_classes import JobAPI, VacancyStorage


def user_interaction(filepath: str = "vacancies.json") -> None:  # Added filepath argument
    """Пользовательская функция"""
    hh_api = HeadHunterAPI()
    json_job = JsonJob(filepath)

    try:
        search_query = input("Введите поисковый запрос: ")
        top_n = int(input("Введите количество вакансий для вывода в топ N: "))
        filter_words = input("Введите ключевые слова для фильтрации вакансий (разделяйте запятыми): ").lower().split(",")
        salary_range = input("Введите диапазон зарплат (например, 100000-150000, или оставьте пустым): ")

        hh_vacancies = hh_api.get_vacancies(search_query)

        vacancies_list = [Vacancy(vac['name'], vac['alternate_url'], vac['snippet']['requirement'],
                                  format_salary(vac.get('salary'))) for vac in hh_vacancies]


        filtered_vacancies = [v for v in vacancies_list if v.description is not None and all(word in v.description.lower()
                                                                                             for word in filter_words)]


        ranged_vacancies = filtered_vacancies
        if salary_range:
            try:
                min_salary, max_salary = map(int, salary_range.split("-"))
                ranged_vacancies = [v for v in filtered_vacancies if min_salary <= int(v.salary.split()[0] if v.salary else 0) <= max_salary]  # Improved salary extraction
            except (ValueError, IndexError):
                print("Неверный формат диапазона зарплат. Используйте формат: 100000-150000")


        sorted_vacancies = sorted(ranged_vacancies, key=lambda v: v.name)


        top_vacancies = sorted_vacancies[:top_n]

        for vacancy in top_vacancies:
            print(f"{vacancy.name}: {vacancy.url}")

        json_data = [v.to_dict() for v in top_vacancies]
        return json.dumps(json_data, indent=4, ensure_ascii=False)

    except ValueError:
        return json.dumps({"error": "Некорректный ввод данных."})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Ошибка сети: {e}"})
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Ошибка декодирования JSON: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Произошла ошибка: {e}"})


if __name__ == "__main__":
    filepath = r"C:\Users\Alena\my_1\Course_2\data\vacancies.json"
    json_result = user_interaction(filepath)
    print(json_result)
    with open(filepath, 'w', encoding='utf-8') as f: #Save to file
        f.write(json_result)