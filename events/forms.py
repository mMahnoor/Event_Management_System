from django import forms
from events.models import Event, Category, EventImage, Participants

class StyledFormMixin:
    """ Mixing to apply style to form field"""

    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 p-3 rounded-lg shadow-sm focus:outline-none focus:border-yellow-400 focus:ring-yellow-400 placeholder-yellow-700/50"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} w-full",
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': f"{self.default_classes} w-full resize-none",
                    'placeholder':  f"Enter {field.label.lower()}",
                    'rows': 5
                })
            elif isinstance(field.widget, forms.SelectDateWidget):
                field.widget.attrs.update({
                    "class": self.default_classes,
                })
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({
                    "type": "time",
                    "class": self.default_classes,
                })
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    "type": "email",
                    "class": self.default_classes,
                    'placeholder': f"Enter {field.label.lower()}"
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    "class": self.default_classes,
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class': "space-y-2"
                })
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                })
            else:
                # print("Inside else")
                field.widget.attrs.update({
                    'class': self.default_classes
                })

class EventModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'event_date', 'event_time', 'location', 'category', 'participants']
        widgets = {
            # 'event_time': forms.SplitDateTimeWidget,
            'event_date': forms.SelectDateWidget,
            'participants': forms.CheckboxSelectMultiple
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ["image"]
        widgets = {
            "image": MultipleFileInput(),
        }

class CategoryModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ParticipantModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Participants
        fields = ['name', 'email']
        widgets = {
            'email':forms.EmailInput
        }