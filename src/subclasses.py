import requests
import json
from typing import List, Dict, Any
from src.abstract_classes import JobAPI, VacancyStorage




class HeadHunterAPI(JobAPI):
    def __init__(self):
        self.__BASE_URL = 'http://api.hh.ru/vacancies'
        self.__headers = self.headers = {'User-Agent': 'HH-User-Agent'}
        self.__params = {'text': '', 'page': 0, 'per_page': 100}
        self.__vacancies = []

    def __connect(self) -> bool:
        """Метод проверки соединения с АПИ"""
        response = requests.get(self.__BASE_URL)
        return response.status_code == 200

    def get_vacancies(self, query: str) ->List[Dict[str, Any]]:
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
    __slots__ = ['name', 'url', 'description', 'salary']

    def __init__(self, name: str, url: str, description: str, salary: str,):
        self.name = name
        self.url = url
        self.description = description
        self.salary = self._valid_salary(salary)

    @classmethod
    def list_total(cls, vacancies_data: List[Dict[str, Any]]) -> List['Vacancy']:
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
    def _format_salary(salary_data: Dict[str, Any]) -> str:
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

    def _valid_salary(self, salary: Any) -> str:
        """Приватный метод для валидации зарплаты"""
        if isinstance(salary, (int, float)) and salary >= 0:
            return salary
        return 'Зарплата не указана'

    def __lt__(self, other: 'Vacancy') -> bool:
        return self.salary < other.salary

    def __le__(self, other: 'Vacancy') -> bool:
        return self.salary <= other.salary

    def __gt__(self, other: 'Vacancy') -> bool:
        return self.salary > other.salary

    def __ge__(self, other: 'Vacancy') -> bool:
        return self.salary >= other.salary


class JsonJob(VacancyStorage):
    """Дочерний класс для работы с JSON"""
    def __init__(self, filename: str = "vacancies.json"):
        self.__filename = filename

    def add_vacancy(self, vacancy: Dict[str, Any]):
        """Метод добавления вакансий в файл"""
        vacancies = self.get_vacancies()

        if any(vac.get('name') == vacancy.get('name') for vac in vacancies):
            print('Вакансия уже существует')
            return

        vacancies.append(vacancy)

        with open(self.__filename, 'w') as f:
            json.dump(vacancies, f, indent=4)


    def get_vacancies(self) -> List[Dict[str, Any]]:
        """Метод получения данных из файла"""
        try:
            with open(self.__filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def remove_vacancy(self, vacancy_name: str):
        """Метод удаления вакансий"""
        vacancies = self.get_vacancies()
        updated_vacancies = [vac for vac in vacancies if vac.get('name') != vacancy_name]

        with open(self.__filename, 'w') as f:
            json.dump(updated_vacancies, f, indent=4)












