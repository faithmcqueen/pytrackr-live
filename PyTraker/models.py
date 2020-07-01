from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

# Create your models here.



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(verbose_name="first name", max_length=50)
    lastname = models.CharField(verbose_name="last name", max_length=50)
    phonenumber = models.CharField(verbose_name="phone number", max_length=10)
    email = models.CharField(verbose_name="email", max_length=100)



class Clients(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Projects(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    clientID = models.ForeignKey(Clients, on_delete=models.CASCADE)
    payRate = models.IntegerField()
    startDate = models.DateTimeField()
    dueDate = models.DateTimeField()

    def __str__(self):
        return self.name


class Tasks(models.Model):
    projectID = models.ForeignKey(Projects, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    complete = models.BooleanField(default=False)
    due_date = models.DateTimeField()


    def __str__(self):
        return self.name


class Timers(models.Model):
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    totaltime = models.CharField(max_length=100,default="0")
    totalhours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    projectID = models.ForeignKey(Projects, on_delete=models.CASCADE,default='1')
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, default='4')




class TaskNotes(models.Model):
    note = models.TextField(max_length=250)
    taskID = models.ForeignKey(Tasks, on_delete=models.CASCADE)

    def __str__(self):
        return self.note


class ProjectNotes(models.Model):
    note = models.TextField(max_length=250)
    projectID = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def __str__(self):
        return self.note


class Invoices(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    projectID = models.ForeignKey(Projects, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField()
    dueDate = models.DateTimeField()

    def __str__(self):
        return self.projectID.name


class WorkDiary(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date = models.DateTimeField()
    projectID = models.ForeignKey(Projects, on_delete=models.CASCADE)
    projectNotes = models.CharField(max_length=2000, default='coming soon')
    taskID = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    taskNotes = models.CharField(max_length=2000, default='coming soon')

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=2000)
    comment_date = models.DateTimeField()
    workdiary = models.ForeignKey(WorkDiary, on_delete=models.CASCADE, default='1')


class Noteboard_Note(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
