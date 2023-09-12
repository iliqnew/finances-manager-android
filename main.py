import kivy
kivy.require("1.9.0")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line
from kivy.clock import Clock
from kivy.core.window import Window
# Window.fullscreen = "auto"

import threading

from utils import (
    get_data,
    clean_reason,
)


class TableCellTextInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.update({
            "multiline": False,
        })
        super().__init__(**kwargs)


class EditableTableCell(Button):
    def __init__(self, coords, **kwargs):
        self.coords = coords
        super().__init__(**kwargs)
        self.background_color = "#000000"
        self.background_normal = ""

    def click(self):
        self.background_color = "#add8e6"
    
    def click_other(self):
        self.background_color = "#000000"
    
    def add_bottom_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1,1,1,1)  # Border color (black in this example)
            Line(points=[self.x, self.y, self.x + self.width, self.y], width=1)  # Draw a line at the bottom
    
    def remove_bottom_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,0,0,1)  # Border color (black in this example)
            Line(points=[self.x, self.y, self.x + self.width, self.y], width=1)  # Remove the line at the bottom
    
    def add_left_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1,1,1,1)  # Border color (black in this example)
            Line(points=[self.x, self.y, self.x, self.y + self.height + 1], width=1)  # Draw a line at the left
    
    def remove_left_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,0,0,1)  # Border color (black in this example)
            Line(points=[self.x, self.y, self.x, self.y + self.height + 1], width=1)  # Remove the line at the left
    
    def add_top_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1,1,1,1)  # Border color (black in this example)
            Line(points=[self.x, self.y + self.height, self.x + self.width, self.y + self.height], width=1)  # Draw a line at the bottom
    
    def remove_top_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,0,0,1)  # Border color (black in this example)
            Line(points=[self.x, self.y + self.height, self.x + self.width, self.y + self.height], width=1)  # Remove the line at the bottom
    
    def add_right_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1,1,1,1)  # Border color (black in this example)
            Line(points=[self.x, self.y, self.x, self.y + self.height + 1], width=1)  # Draw a line at the left
    
    def remove_right_border(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,0,0,1)  # Border color (black in this example)
            Line(points=[self.x, self.y, self.x, self.y + self.height + 1], width=1)  # Remove the line at the left


class Table(GridLayout):
    def __init__(self, data, **kwargs):
        self.data = data
        headers, *rows = self.data
        self.column_widths = [len(header) for header in headers]

        kwargs.update({"cols": len(headers)})
        super().__init__(**kwargs)

        self.bind(
            minimum_height=self.setter('height'),
            minimum_width=self.setter('width')
        )
        
        self.load_data(headers, rows)
        
    
    def load_data(self, headers, rows):
        # Create and add table headers
        for i, header in enumerate(headers):
            cell_text = str(header)
            cell = EditableTableCell(coords=(0, i), text=cell_text, height=30, size_hint_x=None, width=self.column_widths[i], halign="center")
            cell.bind(size=cell.setter('text_size'))
            self.add_widget(cell)

        # Create table rows and data
        for i, row in enumerate(rows, start=1):
            for j, col in enumerate(row):
                cell_text = str(col)

                if headers[j] == "ОСНОВАНИЕ":
                    cell_text = clean_reason(cell_text)
                
                # update columns width if needed
                self.column_widths[j] = max(self.column_widths[j], len(cell_text))

                cell = EditableTableCell(coords=(i, j), text=cell_text, height=30)
                cell.bind(on_press=self.on_press_cell)
                cell.bind(on_release=self.show_text_input_popup)
                self.add_widget(cell)

        # Set column widths based on the maximum widths
        for i, width in enumerate(self.column_widths):
            self.cols_minimum[i] = width * 10
        
        for child in self.children:
            if not isinstance(child, EditableTableCell):
                continue
            i = child.coords[1]
            child.size_hint = (self.column_widths[i], None)
        print("Done!")

    def show_text_input_popup(self, cell):
        text_input = TableCellTextInput(text=cell.text)
        popup = Popup(title='Edit Button Text', content=text_input, size_hint=(None, None), size=(300, 150))
        text_input.bind(on_text_validate=lambda text_input: self.update_button_text(text_input, cell, popup))
        popup.open()

    def update_button_text(self, text_input, cell, popup):
        cell.text = text_input.text
        i = cell.coords[1]
        self.column_widths[i] = max(self.column_widths[i], len(cell.text))
        popup.dismiss()
        for i, width in enumerate(self.column_widths):
            self.cols_minimum[i] = width * 10

    def on_press_cell(self, cell: EditableTableCell):
        for child in self.children:
            if not isinstance(child, EditableTableCell):
                continue
            if child is cell:
                cell.click()
                continue
            child.click_other()
            
            if child.coords[0] == cell.coords[0]:
                child.add_bottom_border()
                child.add_top_border()
            elif child.coords[1] == cell.coords[1]:
                child.add_right_border()
                child.add_left_border()
            else:
                child.remove_bottom_border()
                child.remove_left_border()


class FinancesManager(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView()
        table_layout = Table(get_data()[:20], spacing=(1, 2), size_hint=(None, None))
        scroll_view.add_widget(table_layout)
        main_layout.add_widget(scroll_view)

        return main_layout


finances_manager = FinancesManager()
finances_manager.run()