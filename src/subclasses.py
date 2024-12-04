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
        """Метод проверки соединения с АПИ"""
        return connect_to_api(self._BASE_URL)

    def get_vacancies(self, query: str) -> List[Dict[str, Any]]:
        """Метод получения вакансий по запросу"""
        if not self.connect():
            print("Ошибка соединения с API")
            return []

        self._params['text'] = query
        page = 0

        while True:
            self._params['page'] = page
            response = requests.get(self._BASE_URL, headers=self._headers, params=self._params)

            if response.status_code != 200:
                print(f'Ошибка при получении данных: {response.status_code}')
                break

            data = response.json()
            if not data['items']:
                break

            self._vacancies.extend(data['items'])
            page += 1

        return self._vacancies


class Vacancy(JobAPI):
    """Дочерний класс для работы с вакансиями"""
    __slots__ = ['name', 'url', 'description', 'salary']

    def __init__(self, name: str, url: str, description: str, salary: str):
        self.name = name
        self.url = url
        self.description = description
        self.salary = valid_salary(salary)

    def connect(self) -> bool:
        return True

    def get_vacancies(self, query: str) -> List[dict]:
        return []

    @classmethod
    def list_total(cls, vacancies_data: List[Dict[str, Any]]) -> List['Vacancy']:
        """Метод принимает данные вакансий и конвертирует их"""
        vacancies = []
        for vacancy in vacancies_data:
            vacancies_total = {
                "name": vacancy.get("name"),
                "url": vacancy.get("url"),
                "description": vacancy.get('snippet', {}).get('requirement', 'Нет описания'),
                "salary": format_salary(vacancy.get('salary')),
            }
            vacancies.append(cls(**vacancies_total))
        return vacancies

    def _valid_salary(self, salary: Any) -> str:
        """Приватный метод для валидации зарплаты"""
        return valid_salary(salary)


class JsonJob(VacancyStorage):
    """Дочерний класс для работы с JSON"""
    def __init__(self, filename: str = "vacancies.json"):
        self.__filename = filename

    def add_vacancy(self, vacancy: Dict[str, Any]):
        """Метод добавления вакансий в файл"""
        vacancies = read_json_file(self.__filename)

        if vacancy_exists(vacancies, vacancy.get('name')):
            print('Вакансия уже существует')
            return

        vacancies.append(vacancy)
        write_json_file(self.__filename, vacancies)

    def get_vacancies(self) -> List[Dict[str, Any]]:
        """Метод получения данных из файла"""
        return read_json_file(self.__filename)

    def remove_vacancy(self, vacancy_name: str):
        """Метод удаления вакансий"""
        vacancies = self.get_vacancies()
        updated_vacancies = [vac for vac in vacancies if vac.get('name') != vacancy_name]
        write_json_file(self.__filename, updated_vacancies)











