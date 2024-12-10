import json
from typing import Any, Dict, List
import requests

from src.abstract_classes import JobAPI, VacancyStorage
from src.utils import connect_to_api


class Vacancy():
    """Дочерний класс для работы с вакансиями"""
    __slots__ = ['name', 'url', 'description', 'salary']

    def __init__(self, _name: str, _url: str, _description: str, _salary: str):
        self.name = _name
        self.url = _url
        self.description = _description
        self.salary = _salary

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'salary': self.salary
        }

    def __repr__(self):
        return f"Vacancy(name='{self.name}', url='{self.url}', salary='{self.salary}')"


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
        self.filename = filename

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

    def get_vacancies(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Vacancy(**vac) for vac in data]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading or parsing JSON file: {e}")
            return []

    def remove_vacancy(self, vacancy_name: str):
        vacancies = self.get_vacancies()
        updated_vacancies = [v for v in vacancies if v['name'] != vacancy_name]
        self._save_vacancies(updated_vacancies)
