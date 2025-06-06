# core/events/command_events.py

class CommandAckReceivedEvent:
    def __init__(self, command_id: int, result: int):
        self.command_id = command_id
        self.result = result
