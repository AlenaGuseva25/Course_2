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
        pass
