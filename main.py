# main.py
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.lang import Builder
from rembg import remove
from PIL import Image as PILImage
import io
import time

# Load KV design file
Builder.load_file('kivy_design/main.kv')

class BackgroundRemoverApp(App):
    def build(self):
        return MainScreen()

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_image = None
        self.processed_image = None
        
    def select_image(self, *args):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserIconView()
        file_chooser.filters = ['*.png', '*.jpg', '*.jpeg']
        
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn_cancel = Button(text='Cancel')
        btn_select = Button(text='Select')
        
        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_select)
        
        content.add_widget(file_chooser)
        content.add_widget(btn_layout)
        
        self.popup = Popup(title='Select an image',
                          content=content,
                          size_hint=(0.9, 0.9))
        
        btn_cancel.bind(on_release=self.popup.dismiss)
        btn_select.bind(on_release=lambda x: self._on_image_selected(file_chooser))
        
        self.popup.open()
    
    def _on_image_selected(self, file_chooser):
        if file_chooser.selection:
            self.selected_image = file_chooser.selection[0]
            self.ids.original_image.source = self.selected_image
            self.ids.original_image.reload()
            self.ids.process_button.disabled = False
        self.popup.dismiss()
    
    def process_image(self):
        if not self.selected_image:
            return
            
        self.ids.status_label.text = "Processing..."
        self.ids.process_button.disabled = True
        
        # Process in a separate thread (using Clock for simplicity)
        Clock.schedule_once(lambda dt: self._process_background_removal(), 0.1)
    
    def _process_background_removal(self):
        try:
            start_time = time.time()
            
            # Read the image
            with open(self.selected_image, 'rb') as f:
                input_image = f.read()
            
            # Remove background
            output_image = remove(input_image)
            
            # Save the processed image
            processed_path = os.path.join(os.path.dirname(self.selected_image), 
                                        'processed_' + os.path.basename(self.selected_image))
            
            with open(processed_path, 'wb') as f:
                f.write(output_image)
            
            self.processed_image = processed_path
            self.ids.processed_image.source = processed_path
            self.ids.processed_image.reload()
            
            end_time = time.time()
            self.ids.status_label.text = f"Done! ({end_time-start_time:.2f}s)"
            self.ids.save_button.disabled = False
            
        except Exception as e:
            self.ids.status_label.text = f"Error: {str(e)}"
            self.ids.process_button.disabled = False
    
    def save_image(self):
        if not self.processed_image:
            return
            
        # In a real app, you would implement proper saving functionality
        self.ids.status_label.text = "Image saved to gallery!"
        Clock.schedule_once(lambda dt: setattr(self.ids.status_label, 'text', ""), 2)

if __name__ == '__main__':
    Window.clearcolor = (0.1, 0.1, 0.1, 1)
    BackgroundRemoverApp().run()
