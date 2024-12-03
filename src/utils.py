# Файл для функций, чтобы избежать дублирования
from typing import Dict, Any, List
import json
import requests


def connect_to_api(url: str) -> bool:
    """Функция проверки соединения с АПИ"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при подключении к API: {e}')
        return False


def format_salary(salary_data: Dict[str, Any]) -> str:
    """Функция форматирует данные о зарплате."""
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


def valid_salary(salary: Any) -> str:
    """Валидация значения зарплаты."""
    if isinstance(salary, (int, float)) and salary >= 0:
        return salary
    return 'Зарплата не указана'


def read_json_file(filename: str) -> List[Dict[str, Any]]:
    """Функция читает данные из JSON-файла и возвращает их."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка, файл '{filename}' не найден")
        return []

def write_json_file(filename: str, data: List[Dict[str, Any]]):
    """Функция записывает данные в JSON-файл."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def vacancy_exists(vacancies: List[Dict[str, Any]], vacancy_name: str) -> bool:
    """Функция проверяет, существует ли вакансия с данным именем."""
    return any(vac.get('name') == vacancy_name for vac in vacancies)