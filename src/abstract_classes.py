from abc import ABC, abstractmethod

class JobAPI(ABC):
    """Абстрактный класс для работы с АПИ"""

    @abstractmethod
    def connect(self):
        """Метод подключения к API"""
        pass

    @abstractmethod
    def get_vacancies(self):
        """Метод получения вакансий"""
        pass




class VacancyStorage(ABC):
    """Абстрактный класс для работы с JSON """

    @abstractmethod
    def add_vacancy(self, vacancy):
        """Метод добавления в файл вакансий"""
        pass

    @abstractmethod
    def get_vacancies(self):
        """Метод получения данных из файла"""
        pass

    @abstractmethod
    def remove_vacancy(self, vacancy_name):
        """Метод удаления вакансий"""
        pass
