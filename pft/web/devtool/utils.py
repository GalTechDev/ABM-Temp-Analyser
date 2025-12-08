class Events:
    events = []

    def register_event(event):
        Events.events.append(event)

    def handler_event(name):
        def deco(func):
            for event in Events.events:
                if event.name == name:
                    event.funcs.append(func)
            return func

        return deco

    def trigger_event(name, *args):
        for event in Events.events:
            if event.name == name:
                event.trigger(args)

class Event:

    def __init__(self, name, *args):
        self.funcs = []

    def trigger(self, *args):
        for func in self.funcs:
            func(*args)