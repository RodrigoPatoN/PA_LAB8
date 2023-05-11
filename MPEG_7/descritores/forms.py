from django import forms


class CustomNumberInput(forms.NumberInput):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-select'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class CustomFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

class CustomSelect(forms.Select):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-select'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class InsertImage(forms.Form):
    choices = [("Color Layout", "Color Layout"), ("Edge Histogram", "Edge Histogram")]

    num_images = forms.IntegerField(label="Number of Images",
                                    min_value=1,
                                    max_value=665,
                                    widget=CustomNumberInput())
    
    descriptor = forms.ChoiceField(choices=choices,
                                   label="MPEG7 Descriptor",
                                   widget=CustomSelect())
    
    image = forms.ImageField(label="Image",
                             widget=CustomFileInput())
