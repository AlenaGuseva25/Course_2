import json
import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from src.subclasses import HeadHunterAPI, JsonJob, Vacancy


class TestVacancy(unittest.TestCase):

    def test_validate_name_success(self):
        vacancy = Vacancy("Test Vacancy", "https://example.com", "Description", "100k")
        self.assertEqual(vacancy.name, "Test Vacancy")

    def test_validate_name_empty(self):
        with self.assertRaises(ValueError) as context:
            Vacancy("", "https://example.com", "Description", "100k")
        self.assertEqual(str(context.exception), "Название вакансии не должно быть пустой строкой")

    def test_validate_name_not_string(self):
        with self.assertRaises(ValueError) as context:
            Vacancy(123, "https://example.com", "Description", "100k")
        self.assertEqual(str(context.exception), "Название вакансии не должно быть пустой строкой")

    def test_validate_url_success(self):
        vacancy = Vacancy("Test Vacancy", "https://example.com", "Description", "100k")
        self.assertEqual(vacancy.url, "https://example.com")

    def test_validate_url_invalid(self):
        with self.assertRaises(ValueError) as context:
            Vacancy("Test Vacancy", "invalid-url", "Description", "100k")
        self.assertEqual(str(context.exception), 'URL должен начинаться с "http".')

    def test_validate_url_not_string(self):
        with self.assertRaises(ValueError) as context:
            Vacancy("Test Vacancy", 123, "Description", "100k")
        self.assertEqual(str(context.exception), 'URL должен начинаться с "http".')

    def test_validate_salary_success_int(self):
        vacancy = Vacancy("Test Vacancy", "https://example.com", "Description", 100000)
        self.assertEqual(vacancy.salary, 100000)

    def test_validate_salary_success_float(self):
        vacancy = Vacancy("Test Vacancy", "https://example.com", "Description", 100000.50)
        self.assertEqual(vacancy.salary, 100000.50)

    def test_validate_salary_negative(self):
        vacancy = Vacancy("Test Vacancy", "https://example.com", "Description", -100)
        self.assertEqual(vacancy.salary, 'Зарплата не указана')

    def test_eq(self):
        vacancy1 = Vacancy("Test Vacancy", "https://example.com", "Description", "100k")
        vacancy2 = Vacancy("Test Vacancy", "https://example.com", "Description", "100k")
        vacancy3 = Vacancy("Another Vacancy", "https://another.com", "Another Description", "150k")
        self.assertTrue(vacancy1 == vacancy2)
        self.assertFalse(vacancy1 == vacancy3)


class TestHeadHunterAPI(unittest.TestCase):
    def setUp(self):
        self.api = HeadHunterAPI()

    @patch('requests.get')
    def test_get_vacancies_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'pages': 1, 'items': [{'name': 'Test Vacancy'}]}
        mock_get.return_value = mock_response
        with patch('src.subclasses.connect_to_api', return_value=True):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]['name'], 'Test Vacancy')

    @patch('requests.get')
    def test_get_vacancies_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404 error')
        mock_get.return_value = mock_response
        with patch('src.subclasses.connect_to_api', return_value=True):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError('Connection error')
        with patch('src.subclasses.connect_to_api', return_value=False):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_empty_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'pages': 1, 'items': []}
        mock_get.return_value = mock_response
        with patch('src.subclasses.connect_to_api', return_value=True):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_json_decode_error(self, mock_get):
        mock_get.side_effect = json.JSONDecodeError('Decoding error', '', 0)
        with patch('src.subclasses.connect_to_api', return_value=True):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_key_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'pages': 1}
        mock_get.return_value = mock_response
        with patch('src.subclasses.connect_to_api', return_value=True):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 0)

    @patch('src.subclasses.connect_to_api', return_value=False)
    def test_get_vacancies_connection_failure(self, mock_connect):
        vacancies = self.api.get_vacancies("test")
        self.assertEqual(len(vacancies), 0)


class TestJsonJob(unittest.TestCase):
    def setUp(self):
        self.filename = "test_vacancies.json"
        self.json_job = JsonJob(self.filename)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([], f)  # Start with an empty file

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_add_vacancy_success(self):
        vacancy = Vacancy("Test Vacancy 1", "https://example.com", "Description 1", "100k")
        self.json_job.add_vacancy(vacancy)
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Vacancy 1")

    def test_get_vacancies_empty(self):
        vacancies = self.json_job.get_vacancies()
        self.assertEqual(len(vacancies), 0)


if __name__ == '__main__':
    unittest.main()
