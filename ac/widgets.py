# ac/widgets.py
from django.forms.widgets import FileInput

from django.forms.widgets import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True  # Enable multiple file selection

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True  # Add the 'multiple' attribute to the input
        super().__init__(attrs)
        
    def value_from_datadict(self, data, files, name):
        return files.getlist(name)