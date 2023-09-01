from abc import ABC
from abc import abstractmethod
import copy


class MessageSendingBase(ABC):
    def __init__(self, message_body: dict, target: str) -> None:
        self.message_body = copy.deepcopy(message_body)
        self.target = target

    @abstractmethod
    def send(self) -> dict:
        """
        sending the self.message_body to target
        :return: dict
        """

    @abstractmethod
    def process_on_call(self, on_call_stuff_object) -> None:
        """
        process on call info
        :return: None
        """

    def process_additional_args(self, additional_args):
        pass
