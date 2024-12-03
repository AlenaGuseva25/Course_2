import requests
import json
from src.abstract_classes import JobAPI, VacancyStorage



class HeadHunterAPI(JobAPI):
    def __init__(self):
        self.__BASE_URL = 'http://api.hh.ru/vacancies'
        self.__headers = self.headers = {'User-Agent': 'HH-User-Agent'}
        self.__params = {'text': '', 'page': 0, 'per_page': 100}
        self.__vacancies = []

    def __connect(self):
        """Метод проверки соединения с АПИ"""
        response = requests.get(self.__BASE_URL)
        return response.status_code == 200

    def get_vacancies(self, query):
        """Метод получения вакансий по запросу"""
        if not self.__connect():
            print(f"Ошибка соединения с API")
            return []

        self.__params['text'] = query
        page = 0

        while True:
            self.__params['page'] = page
            response = requests.get(self.__BASE_URL, headers=self.headers, params=self.__params)

            if response.status_code == 200:
                print(f'Ошибка при получении данных: {response.status_code}')
                break

            data = response.json()
            if not data['items']:
                break

            self.__vacancies.extend(data['items'])
            page += 1

        return self.__vacancies




class Vacancy(JobAPI):
    """Дочерний класс для работы с вакансиями"""
    def __init__(self, name: str, url: str, description: str, salary: str,):
        self.name = name
        self.url = url
        self.description = description
        self.salary = salary if salary else "Зарплата не указана"

    @classmethod
    def list_total(cls, vacancies_data):
        """Метод принимает данные вакансий и конвертирует их"""
        vacancies = []
        for vacancy in vacancies_data:
            vacancies_total = {
            "name": vacancy.get("name"),
            "url": vacancy.get("url"),
            "description": vacancy.get('snippet', {}).get('requirement', 'Нет описания'),
            "salary": cls._format_salary(vacancy.get('salary')),
            }
            vacancies.append(cls(**vacancies_total))
        return vacancies

    @classmethod
    def _format_salary(salary_data):
        """Метод работы с данными о зарплате"""
        if salary_data is None:
            return 'Зарплата не указана'
        salary_from = salary_data.get("from")
        salary_to = salary_data.get('to')
        currency = salary_data.get("currency", 'руб.')

        if salary_from and salary_to:
            return f'Зарплата: от {salary_from} до {salary_to} {currency}'
        elif salary_from:
            return f'Зарплата: от {salary_from} {currency}'
        elif salary_to:
            return f'Зарплата: до {salary_to} {currency}'
        else:
            return 'Зарплата не указана'


class JsonJob(VacancyStorage):
    """Дочерний класс для работы с JSON"""
    def __init__(self, filename="vacancies.json"):
        self.filename = filename


    def add_vacancies(self, vacancies_data):
        """Метод добавления в файл вакансий"""












