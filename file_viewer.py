import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.uix.slider import Slider
from kivy.clock import Clock

RECORDINGS_FOLDER = 'recordings'


class FileListScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView()
        inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        inner.bind(minimum_height=inner.setter('height'))

        for file in os.listdir(RECORDINGS_FOLDER):
            if file.endswith('.wav'):
                btn = Button(text=file, size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.9, 1))
                btn.bind(on_release=lambda btn: self.open_file(btn.text))
                inner.add_widget(btn)

        scroll.add_widget(inner)
        layout.add_widget(Label(text='Select a Recording', size_hint_y=None, height=40, bold=True))
        layout.add_widget(scroll)
        self.add_widget(layout)

    def open_file(self, filename):
        self.manager.get_screen('details').load_file(filename)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'details'


class FileDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.sound = None
        self.slider = Slider(min=0, max=1, value=0, size_hint_y=None, height=30)
        self.current_file = None

        self.transcription_label = Label(text="", size_hint_y=None, height=200, halign='left', valign='top')
        self.transcription_label.bind(size=self.transcription_label.setter('text_size'))

        controls = BoxLayout(size_hint_y=None, height=50, spacing=5)
        for name, func in [("Play", self.play), ("Pause", self.pause), ("Stop", self.stop),
                           ("<<", self.backward), (">>", self.forward)]:
            btn = Button(text=name)
            btn.bind(on_release=func)
            controls.add_widget(btn)

        self.back_btn = Button(text="Back", size_hint_y=None, height=50, background_color=(0.8, 0.2, 0.2, 1))
        self.back_btn.bind(on_release=self.go_back)

        self.layout.add_widget(Label(text='Audio Player', size_hint_y=None, height=40))
        self.layout.add_widget(self.slider)
        self.layout.add_widget(controls)
        self.layout.add_widget(Label(text='Transcription', size_hint_y=None, height=40))
        self.layout.add_widget(self.transcription_label)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)

        Clock.schedule_interval(self.update_slider, 0.5)

    def load_file(self, filename):
        self.current_file = filename
        path = os.path.join(RECORDINGS_FOLDER, filename)
        if self.sound:
            self.sound.stop()
        self.sound = SoundLoader.load(path)
        if self.sound:
            self.slider.max = self.sound.length

        txt_file = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(txt_file):
            with open(txt_file, 'r', encoding='utf-8') as f:
                self.transcription_label.text = f.read()
        else:
            self.transcription_label.text = "No transcription"

    def play(self, *args):
        if self.sound:
            self.sound.play()

    def pause(self, *args):
        if self.sound and self.sound.state == 'play':
            self.sound.pause()

    def stop(self, *args):
        if self.sound:
            self.sound.stop()
            self.sound.seek(0)
            self.slider.value = 0

    def forward(self, *args):
        if self.sound:
            new_pos = min(self.sound.get_pos() + 5, self.sound.length)
            self.sound.seek(new_pos)
            self.slider.value = new_pos

    def backward(self, *args):
        if self.sound:
            new_pos = max(self.sound.get_pos() - 5, 0)
            self.sound.seek(new_pos)
            self.slider.value = new_pos

    def update_slider(self, dt):
        if self.sound and self.sound.state == 'play':
            self.slider.value = self.sound.get_pos()

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
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
