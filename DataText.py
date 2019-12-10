import threading
import tkinter
from tkinter import scrolledtext
from queue import Queue
from Matcher import get_matched_options_formatted
class DataText(scrolledtext.ScrolledText):
    def __init__(self, master, backs, lays, **options):
        scrolledtext.ScrolledText.__init__(self, master, **options)
        self.setup(backs, lays)
        self.update(backs, lays)
    def setup(self, backs, lays):
        threads = [
            threading.Thread(
                target=x.setup,
                name="Thread_{}".format(x.name),
                args=[],
            ) for x in backs+lays
        ]
        for t in threads: t.start()
        for t in threads: t.join()
    def update(self, backs, lays):
        '''
        back_queue = Queue()
        lay_queue = Queue()
        threads = [
            threading.Thread(
                target=x.get_events,
                name="Thread_{}".format(x.name),
                args=[back_queue],
            ) for x in backs
        ] + [
            threading.Thread(
                target=x.get_events,
                name="Thread_{}".format(x.name),
                args=[lay_queue],
            ) for x in lays
        ]
        for t in threads: t.start()
        if not all(not t.is_alive() for t in threads): self.after(100)
        for t in threads: t.join()
        back_events = []
        lay_events = []
        while not back_queue.empty(): back_events.append(back_queue.get_nowait())
        while not lay_queue.empty(): lay_events.append(lay_queue.get_nowait())
        '''
        thread_queue = Queue()
        t = threading.Thread(
            target=get_matched_options_formatted,
            name="Thread_get_matched_options_formatted",
            args=[backs,lays,thread_queue]
        )
        t.start()
        while not t.is_alive(): self.after(100)
        t.join()
        data_text = thread_queue.get_nowait()
        self.delete(1.0,tkinter.END)
        self.insert(tkinter.INSERT, data_text)
        self.after(100,self.update,backs,lays)