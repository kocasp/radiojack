from kivy.config import Config
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')

import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition, FallOutTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

RECORDINGS_FOLDER = 'recordings'


class ThemedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.082, 0.137, 0.239, 1)  # #15233d
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos


class FileListScreen(ThemedScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        scroll = ScrollView()
        inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        inner.bind(minimum_height=inner.setter('height'))

        for file in os.listdir(RECORDINGS_FOLDER):
            if file.endswith('.wav'):
                display_name = os.path.splitext(file)[0]
                btn = Button(
                    text=display_name,
                    size_hint_y=None,
                    height=120,
                    background_normal='',
                    background_color=(1, 1, 1, 1),
                    color=(0.082, 0.137, 0.239, 1),
                    font_size=44
                )
                btn.full_name = file
                btn.bind(on_release=lambda btn: self.open_file(btn.full_name))
                inner.add_widget(btn)

        scroll.add_widget(inner)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def open_file(self, filename):
        self.manager.get_screen('details').load_file(filename)
        self.manager.transition = RiseInTransition()
        self.manager.current = 'details'


class FileDetailScreen(ThemedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound = None
        self.current_file = None
        self.full_text = ""
        self.displayed_words = []
        self.word_index = 0
        self.typing_event = None

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Top: Play button
        self.toggle_btn = Button(
            text="Play",
            size_hint_y=None,
            height=120,
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0.082, 0.137, 0.239, 1),
            font_size=44
        )
        self.toggle_btn.bind(on_release=self.toggle_playback)
        self.layout.add_widget(self.toggle_btn)

        # Middle: Scrollable transcription text
        self.scroll = ScrollView(size_hint_y=1)
        self.transcription_label = Label(
            text="",
            size_hint_y=None,
            size_hint_x=1,
            halign='left',
            valign='top',
            color=(1, 1, 1, 1),
            font_size=40
        )
        self.transcription_label.bind(
            width=self._update_text_width,
            texture_size=self._update_text_height
        )
        self.scroll.add_widget(self.transcription_label)
        self.layout.add_widget(self.scroll)

        # Bottom: Back button
        self.back_btn = Button(
            text="Back",
            size_hint_y=None,
            height=120,
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0.082, 0.137, 0.239, 1),
            font_size=44
        )
        self.back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def _update_text_width(self, *args):
        self.transcription_label.text_size = (self.transcription_label.width, None)

    def _update_text_height(self, *args):
        self.transcription_label.height = self.transcription_label.texture_size[1]

    def load_file(self, filename):
        self.current_file = filename
        path = os.path.join(RECORDINGS_FOLDER, filename)
        if self.sound:
            self.sound.stop()
        self.sound = SoundLoader.load(path)

        self.toggle_btn.text = "Play"

        txt_file = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(txt_file):
            with open(txt_file, 'r', encoding='utf-8') as f:
                self.full_text = f.read()
        else:
            self.full_text = "No transcription"

        # Reset for typewriter animation
        self.word_index = 0
        self.displayed_words = []
        self.transcription_label.text = ""
        self._update_text_width()
        self._update_text_height()

        if self.typing_event:
            self.typing_event.cancel()
        self.typing_event = Clock.schedule_interval(self._type_next_word, 0.08)

    def _type_next_word(self, dt):
        words = self.full_text.split()
        if self.word_index < len(words):
            self.displayed_words.append(words[self.word_index])
            self.transcription_label.text = ' '.join(self.displayed_words)
            self._update_text_width()
            self._update_text_height()
            self.word_index += 1
        else:
            if self.typing_event:
                self.typing_event.cancel()
                self.typing_event = None

    def toggle_playback(self, *args):
        if self.sound:
            if self.sound.state == 'play':
                self.sound.stop()
                self.sound.seek(0)
                self.toggle_btn.text = "Play"
            else:
                self.sound.play()
                self.toggle_btn.text = "Stop"

    def stop(self):
        if self.sound:
            self.sound.stop()
            self.sound.seek(0)
            self.toggle_btn.text = "Play"

    def go_back(self, *args):
        self.stop()
        if self.typing_event:
            self.typing_event.cancel()
            self.typing_event = None
        self.manager.transition = FallOutTransition()
        self.manager.current = 'list'


class RecordingApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(FileListScreen(name='list'))
        sm.add_widget(FileDetailScreen(name='details'))
        return sm


if __name__ == '__main__':
    if not os.path.exists(RECORDINGS_FOLDER):
        os.makedirs(RECORDINGS_FOLDER)
    RecordingApp().run()
