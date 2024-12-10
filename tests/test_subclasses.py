import unittest
from unittest.mock import patch, mock_open,MagicMock
import json
from src.subclasses import Vacancy, HeadHunterAPI, JsonJob
from typing import Dict,Any, List
import os
import requests


class TestVacancy(unittest.TestCase):
    def setUp(self):
        """Создадим экземпляр класса Vacancy для тестов"""
        self.vacancy = Vacancy(
            _name="Software Engineer",
            _url="http://example.com/vacancy/1",
            _description="Develop software applications.",
            _salary="100000"
        )

    def test_initialization(self):
        """Тестируем инициализацию объекта Vacancy"""
        self.assertEqual(self.vacancy.name, "Software Engineer")
        self.assertEqual(self.vacancy.url, "http://example.com/vacancy/1")
        self.assertEqual(self.vacancy.description, "Develop software applications.")
        self.assertEqual(self.vacancy.salary, "100000")

    def test_to_dict(self):
        """Тестируем метод to_dict"""
        expected_dict = {
            'name': "Software Engineer",
            'url': "http://example.com/vacancy/1",
            'description': "Develop software applications.",
            'salary': "100000"
        }
        self.assertEqual(self.vacancy.to_dict(), expected_dict)

    def test_repr(self):
        """Тестируем метод __repr__"""
        expected_repr = "Vacancy(name='Software Engineer', url='http://example.com/vacancy/1', salary='100000')"
        self.assertEqual(repr(self.vacancy), expected_repr)

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
        mock_response.json.return_value = {'pages':1} #Missing 'items' key
        mock_get.return_value = mock_response
        with patch('src.subclasses.connect_to_api', return_value=True):
            vacancies = self.api.get_vacancies('test')
        self.assertEqual(len(vacancies), 0)

    @patch('src.subclasses.connect_to_api', return_value=False)
    def test_get_vacancies_connection_failure(self, mock_connect):
        vacancies = self.api.get_vacancies("test")
        self.assertEqual(len(vacancies), 0)




if __name__ == '__main__':
    unittest.main()
