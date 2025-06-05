from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

class TypewriterLabel(Label):
    def __init__(self, full_text, interval=0.0002, **kwargs):
        super().__init__(**kwargs)
        self.full_text = full_text
        self.interval = interval
        self.current_index = 0
        self.text = ""
        self.font_size = 24  # Larger font
        self.halign = 'left'
        self.valign = 'top'
        self.size_hint_y = None
        self.bind(width=self.update_text_size)
        Clock.schedule_interval(self.update_text, self.interval)

    def update_text_size(self, *args):
        self.text_size = (self.width, None)
        self.texture_update()
        self.height = self.texture_size[1]

    def update_text(self, dt):
        if self.current_index < len(self.full_text):
            self.text += self.full_text[self.current_index]
            self.current_index += 1
            self.update_text_size()
        else:
            Clock.unschedule(self.update_text)

class TypewriterApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=20)

        scroll = ScrollView(size_hint=(1, 1))
        lorem = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
            "nisi ut aliquip ex ea commodo consequat."
        )
        label = TypewriterLabel(lorem)
        scroll.add_widget(label)
        root.add_widget(scroll)

        return root

if __name__ == '__main__':
    TypewriterApp().run()
