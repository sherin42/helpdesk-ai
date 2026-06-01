from django import forms
from .models import Ticket, Department, Comment


class TicketForm(forms.ModelForm):

    class Meta:

        model = Ticket

        fields = [
            'title',
            'description',
            'priority'
        ]

        widgets = {

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ticket title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your issue...',
                'rows': 5
            }),

            'priority': forms.Select(attrs={
                'class': 'form-select'
            })

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['priority'].required = False

class DepartmentForm(forms.ModelForm):

    class Meta:

        model = Department

        fields = ['name']


class CommentForm(forms.ModelForm):

    class Meta:

        model = Comment

        fields = ['message']

        widgets = {

            'message': forms.Textarea(attrs={

                'class': 'form-control',

                'rows': 4,

                'placeholder': 'Write your comment here...'

            })

        }


class TicketEditForm(forms.ModelForm):

    class Meta:

        model = Ticket

        fields = [
            'title',
            'description',
            'status',
            'priority',
            'department',
            'assigned_to'
        ]