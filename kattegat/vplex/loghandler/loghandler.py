import os
from abc import ABC, abstractmethod

class LogHandler(ABC):
    @abstractmethod
    def parse(self):
        pass