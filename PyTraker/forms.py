from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Profile, Comments, Projects, Invoices, Clients, WorkDiary, Tasks, Timers

# for import date and time
from _datetime import datetime
from django.utils import timezone
from django.template import defaultfilters


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProfileForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'phonenumber', 'email']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CommentForm(forms.ModelForm):
    comment = forms.CharField(required=True, widget=forms.Textarea)

    class Meta:
        model = Comments
        fields = [
            'user',
            'comment',
            'comment_date',
        ]

    def clean_user(self, *args, **kwargs):
        user = self.cleaned_data.get("user")


class TimerForm(forms.ModelForm):
    class Meta:
        model = Timers
        fields = [
            'startTime',
            'endTime',
            'totaltime',
            'totalhours',
        ]


class CommentRawProduction(forms.Form):
    user = forms.CharField()
    comment = forms.CharField(required=True, widget=forms.Textarea)
    comment_date = forms.DateTimeField()


class ProjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class': 'form-control', }
        self.fields['description'].widget.attrs = {'class': 'form-control', }
        self.fields['clientID'].widget.attrs = {'class': 'form-control', }
        self.fields['payRate'].widget.attrs = {'class': 'form-control', }
        self.fields['startDate'].widget.attrs = {'class': 'form-control', }
        self.fields['dueDate'].widget.attrs = {'class': 'form-control', }

        # for visible in self.visible_fields():
        #     visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Projects
        fields = ['name', 'description', 'clientID', 'payRate', 'startDate', 'dueDate']
        labels = {'name': 'Name', 'description': 'Description', 'clientID': 'Client', 'payRate': 'Pay Rate',
                  'startDate': 'Start Date', 'dueDate': 'Due Date'}


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoices
        fields = ['userID',
                  'projectID',
                  'dateCreated',
                  'dueDate']


class WorkDiaryForm(forms.ModelForm):
    name = forms.CharField()
    projectNotes = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 100}))
    taskNotes = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 100}))

    def __init__(self, *args, **kwargs):
        super(WorkDiaryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class': 'form-control', }
        self.fields['projectID'].widget.attrs = {'class': 'form-control', }
        self.fields['projectNotes'].widget.attrs = {'class': 'form-control', }
        self.fields['taskID'].widget.attrs = {'class': 'form-control', }
        self.fields['taskNotes'].widget.attrs = {'class': 'form-control', }

    class Meta:
        model = WorkDiary
        fields = ['name', 'projectID', 'projectNotes', 'taskID', 'taskNotes']
        labels = {'name': 'Name', 'projectID': 'Project', 'projectNotes': 'Project Notes', 'taskID': 'Task',
                  'taskNotes': 'Task Notes'}


# Create a task

class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class': 'form-control', }
        self.fields['description'].widget.attrs = {'class': 'form-control', }
        self.fields['projectID'].widget.attrs = {'class': 'form-control', }
        self.fields['due_date'].widget.attrs = {'class': 'form-control', }

    class Meta:
        model = Tasks
        fields = ['name',
                  'description',
                  'projectID',
                  'due_date']
        labels = {'name': 'Task',
                  'description': 'Task Description',
                  'projectID': 'Project',
                  'due_date': 'Task Due'}
