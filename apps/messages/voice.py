from .base import MessageSendingBase
from .montnets.voiceclient import VoiceClient


class VoiceMessageSending(MessageSendingBase):
    def send(self) -> dict:
        _voice = VoiceClient(self.target)
        return _voice.voiceTemplateSend()

    def process_on_call(self, on_call_stuff_object) -> None:
        self.target = on_call_stuff_object.stuff_phone_number

