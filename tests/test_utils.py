import unittest
from unittest.mock import patch, mock_open
import json
import requests
from typing import Dict, Any, List
from src.utils import (connect_to_api, format_salary, read_json_file, vacancy_exists, filter_vacancies, valid_salary)

class TestUtils(unittest.TestCase):

    @patch('requests.get')
    def test_connect_to_api_success(self, mock_get):
        mock_get.return_value.status_code = 200
        url = 'https://api.hh.ru/vacancies'
        result = connect_to_api(url)
        self.assertTrue(result)

    @patch('requests.get')
    def test_connect_to_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Connection Error")
        url = "http://test.com"
        result = connect_to_api(url)
        self.assertFalse(result)

    def test_format_salary_none(self):
        result = format_salary(None)
        self.assertEqual(result, 'Зарплата не указана')

    def test_format_salary_with_both(self):
        salary_data = {"from": 50000, "to": 70000, "currency": "руб."}
        result = format_salary(salary_data)
        self.assertEqual(result, 'Зарплата: от 50000 до 70000 руб.')

    def test_valid_salary_valid(self):
        result = valid_salary(50000)
        self.assertEqual(result, 50000)

    def test_valid_salary_invalid_negative(self):
        result = valid_salary(-1000)
        self.assertEqual(result, 'Зарплата не указана')

    @patch('builtins.open', new_callable=mock_open, read_data='[{"name": "Vacancy 1"}]')
    def test_read_json_file_success(self, mock_file):
        result = read_json_file('test.json')
        self.assertEqual(result, [{"name": "Vacancy 1"}])


    def test_vacancy_exists_true(self):
        vacancies = [{"name": "Vacancy 1"}, {"name": "Vacancy 2"}]
        result = vacancy_exists(vacancies, "Vacancy 1")
        self.assertTrue(result)

    def test_vacancy_exists_false(self):
        vacancies = [{"name": "Vacancy 1"}, {"name": "Vacancy 2"}]
        result = vacancy_exists(vacancies, "Vacancy 3")
        self.assertFalse(result)

    def test_filter_vacancies(self):
        class Vacancy:
            def __init__(self, description):
                self._description = description

        vacancies_list = [
            Vacancy("Senior Python Developer"),
            Vacancy("Junior Python Developer"),
            Vacancy("Data Scientist")
        ]
        filter_words = ['python']
        filtered = filter_vacancies(vacancies_list, filter_words)
        self.assertEqual(len(filtered), 2)


if __name__ == '__main__':
    unittest.main()