import json
from typing import Any, Dict, List

import requests

from src.abstract_classes import JobAPI, VacancyStorage
from src.utils import connect_to_api


class Vacancy():
    """Дочерний класс для работы с вакансиями"""
    __slots__ = ['name', 'url', 'description', 'salary']

    def __init__(self, _name: str, _url: str, _description: str, _salary: str):
        self.name = self._validate_name(_name)
        self.url = self._validate_url(_url)
        self.description = _description
        self.salary = self._validate_salary(_salary)

    def _validate_name(self, _name: str) -> str:
        """Проверка корректности названия вакансии"""
        if not isinstance(_name, str) or not _name.strip():
            raise ValueError('Название вакансии не должно быть пустой строкой')
        return _name

    def _validate_url(self, _url: str) -> str:
        """Проверка корректности url"""
        if not isinstance(_url, str) or not _url.startswith('http'):
            raise ValueError('URL должен начинаться с "http".')
        return _url

    def _validate_salary(self, _salary: Any) -> str:
        """Валидация значения зарплаты."""
        if isinstance(_salary, (int, float)) and _salary >= 0:
            return _salary
        return 'Зарплата не указана'


    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'salary': self.salary
        }

    def __repr__(self):
        return f"Vacancy(name='{self.name}', url='{self.url}', salary='{self.salary}')"

    def __eq__(self, other):
        """Сравнение двух объектов класса на равенство по имени, URL и ЗП"""
        if isinstance(other, Vacancy):
            return self.name == other.name and self.url == other.url and self.salary == other.salary
        return False

    def __lt__(self, other):
        """Проверка меньше ли текущая ЗП, чем у другого объекта"""
        if isinstance(other, Vacancy):
            return self.name < other.name
        return NotImplemented

    def __le__(self, other):
        """Проверка меньше или равна ЗП, чем у другого объекта"""
        if isinstance(other, Vacancy):
            return self.name <= other.name
        return NotImplemented

    def __gt__(self, other):
        """Проверка больше ли ЗП, чем у другого объекта"""
        if isinstance(other, Vacancy):
            return self.name > other.name
        return NotImplemented

    def __ge__(self, other):
        """Проверка больше или равна ЗП чем у другого объекта"""
        if isinstance(other, Vacancy):
            return self.name >= other.name
        return NotImplemented


class HeadHunterAPI(JobAPI):
    def __init__(self):
        self._BASE_URL: str = 'https://api.hh.ru/vacancies'
        self._headers: dict = {'User-Agent': 'HH-User-Agent'}
        self._params: dict = {'text': '', 'page': 0, 'per_page': 100}
        self._vacancies: list = []

    def connect(self) -> bool:
        return connect_to_api(self._BASE_URL)

    def get_vacancies(self, query: str) -> List[Dict[str, Any]]:
        """Метод получает вакансии из АПИ на основе запроса"""
        if not self.connect():
            print("Ошибка соединения с API")
            return []

        self._params['text'] = query
        all_vacancies = []
        page = 0
        total_pages = 1

        while page < total_pages:
            self._params['page'] = page
            try:
                response = requests.get(self._BASE_URL, headers=self._headers, params=self._params)
                response.raise_for_status()

                data = response.json()

                total_pages = data.get('pages',
                                       total_pages)
                if not data['items']:
                    break
                all_vacancies.extend(data['items'])
                page += 1
            except requests.exceptions.HTTPError as e:
                print(f"HTTP Ошибка (page {page}): {e}")
                break
            except requests.exceptions.RequestException as e:
                print(f"Ошибка сети (page {page}): {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Ошибка декодирования JSON (page {page}): {e}")
                break
            except KeyError as e:
                print(f"Ключ не найден в ответе (page {page}): {e}")
                break

        return all_vacancies


class JsonJob(VacancyStorage):
    """Дочерний класс для работы с JSON"""
    def __init__(self, filename: str = "vacancies.json"):
        self._filename = filename

    @property
    def filename(self) -> str:
        """Геттер для имени файла"""
        return self._filename

    def add_vacancy(self, vacancy: Vacancy):
        vacancies = self.get_vacancies()
        if any(v['name'] == vacancy.name for v in vacancies):
            print('Вакансия уже существует')
            return
        vacancies.append(vacancy.to_dict())
        self._save_vacancies(vacancies)

    def _save_vacancies(self, vacancies: List[Dict[str, Any]]):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(vacancies, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка записи в файл '{self.filename}': {e}")

    def get_vacancies(self) -> List[Vacancy]:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Vacancy(**vac) for vac in data]
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Error reading or parsing JSON file: {e}")
            return []

    def remove_vacancy(self, vacancy_name: str):
        vacancies = self.get_vacancies()
        updated_vacancies = [v for v in vacancies if v['name'] != vacancy_name]
        self._save_vacancies(updated_vacancies)
