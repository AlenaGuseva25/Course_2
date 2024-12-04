import json
import requests
from typing import List, Dict, Any
from src.abstract_classes import JobAPI, VacancyStorage
from src.utils import connect_to_api, format_salary, valid_salary, read_json_file, write_json_file, vacancy_exists



class HeadHunterAPI(JobAPI):
    def __init__(self):
        self._BASE_URL = 'https://api.hh.ru/vacancies'
        self._headers = {'User-Agent': 'HH-User-Agent'}
        self._params = {'text': '', 'page': 0, 'per_page': 100}
        self._vacancies = []


    def connect(self) -> bool:
        """Метод проверки соединение с API HeadHunter."""
        return connect_to_api(self._BASE_URL)

    def get_vacancies(self, query: str) -> List[Dict[str, Any]]:
        """Метод получения вакансии по заданному запросу"""
        if not self.connect():
            print("Ошибка соединения с API")
            return []

        self._params['text'] = query
        all_vacancies = []
        page = 0

        while True:
            self._params['page'] = page
            try:
                response = requests.get(self._BASE_URL, headers=self._headers, params=self._params)
                response.raise_for_status()
                data = response.json()
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
                print(f"Ошибка декодирования (page {page}): {e}")
                break

        return all_vacancies


class Vacancy():
    """Дочерний класс для работы с вакансиями"""
    __slots__ = ['name', 'url', 'description', 'salary']

    def __init__(self, name: str, url: str, description: str, salary: str):
        self.name = name
        self.url = url
        self.description = description
        self.salary = salary

    def to_dict(self):
        """Метод преобразования объект Vacancy в словарь."""
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'salary': self.salary
        }

    def __repr__(self):
        """Метод возвращает строковое представление объекта Vacancy."""
        return f"Vacancy(name='{self.name}', url='{self.url}', salary='{self.salary}')"


class JsonJob(VacancyStorage):
    """Дочерний класс для работы с JSON"""
    def __init__(self, filename: str = "vacancies.json"):
        self.filename = filename

    def add_vacancy(self, vacancy: Vacancy):
        """Метод добавляет вакансию в JSON файл."""
        vacancies = self.get_vacancies()
        if any(v['name'] == vacancy.name for v in vacancies):
            print('Вакансия уже существует')
            return
        vacancies.append(vacancy.__dict__)
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
