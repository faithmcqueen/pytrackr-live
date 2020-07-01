from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
#from django.template.defaulttags import register
from django import template
register = template.Library()


from django.db.models import Sum
from django.db.models import Avg


from .forms import UserForm, ProfileForm, CommentRawProduction, CommentForm, ProjectForm, InvoiceForm, WorkDiaryForm, \
    TaskForm
from .models import Invoices, Projects, Clients, Tasks, Timers, Comments, WorkDiary, Noteboard_Note


from .forms import UserForm, ProfileForm, CommentRawProduction, CommentForm, ProjectForm,TimerForm
from .models import Invoices, Projects, Clients, Tasks, Timers, Comments, Profile

from .forms import UserForm, ProfileForm, CommentRawProduction, CommentForm, ProjectForm
from .models import Invoices, Projects, Clients, Tasks, Timers, Comments, Profile, TaskNotes, ProjectNotes


# for import date and time
from _datetime import datetime
from django.utils import timezone
from django.template import defaultfilters
from django.utils.dateparse import parse_date
from django.views.generic import ListView
from django.db.models import Q, Sum




def home(request):
    mess = 'Welcome to our Work Tracking Application!'
    project_list = Projects.objects.all()
    paginator = Paginator(project_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # context = {'project_list': project_list}

    return render(request, 'PyTraker/index.html', {'page_obj': page_obj, 'mess': mess})


# return render(request, 'PyTraker/index.html')


def sign_up(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form = profile_form.save(commit=False)
            profile_form.user = user
            profile_form.save()
            userN = user_form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + userN)
            return redirect('/PyTraker/login/?next=/')
    else:
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
    return render(request, 'PyTraker/sign_up.html', {'user_form': user_form, 'profile_form': profile_form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is None:
                login(request, user)
                return redirect('login')

        context = {}

        return render(request, 'PyTraker/login.html', context)


def log_out(request):
    if request.method == "POST":
        logout(request)

    mess = "Logged out succesfully!"
    return render(request, 'PyTraker/index.html', {'mess': mess})


# Invoice Views
@login_required
def invoice(request, project_id):
    # Get the invoice whose project id is the one being passed

    obj = Invoices.objects.get(projectID_id=project_id)
    #list of tasks
    tasks = Tasks.objects.filter(projectID_id=obj.projectID)
    #list of timers for the project
    timer = Timers.objects.filter(projectID_id=obj.projectID).values('task_id').annotate(tasktotal=Sum('totalhours'))
    #timersum = Timers.objects.filter(projectID_id=obj.projectID).values('task_id').aggregate(tasktotal=Sum('totalhours'))
    context = {
        'invoice_id': obj.id,
        'project_id': obj.projectID,
        'project_name': obj.projectID.name,
        'client_name': obj.projectID.clientID.name,
        'client_email': obj.projectID.clientID.email,
        'client_phone': obj.projectID.clientID.phone,
        'user_fname': obj.userID.first_name,
        'user_lname': obj.userID.last_name,
        'user_email': obj.userID.email,
        #'user_phone': obj.userID.phonenumber,
        'date_created': obj.dateCreated,
        'date_due': obj.dueDate,
        'hourly_rate': obj.projectID.payRate,
        'tasks_list': tasks,
        'timers': timer,
    }
    return render(request, "PyTraker/invoice.html", context)


@login_required
def invoice_list(request):
    all_invoices = Invoices.objects.order_by("-dateCreated")
    context = {"all_invoices": all_invoices}
    return render(request, "PyTraker/list_invoice.html", context)


@login_required
def new_invoice(request, project_id):
    # AUTO POPULATING THE FORM THE FIRST TIME AROUND
    # Get user information
    current_user = request.user
    userID = User.objects.get(id=current_user.id)

    # Get the project information
    project = Projects.objects.get(id=project_id)
    form = InvoiceForm(initial={
        'userID': userID,
        'projectID': project.id,
        'dateCreated': datetime.now(),
        'dueDate': ""
    })

    #Process form if is being sent by post
    if request.method == 'POST':
        filled_form = InvoiceForm(request.POST)
        if filled_form.is_valid():
            filled_form.save()
            note = "Invoice created!"
            return redirect('/PyTraker/details_project/'+str(project_id))
            #return render(request, 'PyTraker/new_invoice.html', {'note': note, 'form': form})
            #return redirect('PyTraker/details_project/'+str(project_id))

    return render(request, "PyTraker/new_invoice.html", {'form': form})


@login_required
def edit_invoice(request, invoices_id):
    invoice = Invoices.objects.get(pk=invoices_id)
    project_id =invoice.projectID.id
    form = InvoiceForm(instance=invoice)
    if request.method == "POST":
        populated_form = InvoiceForm(request.POST, instance=invoice)
        if populated_form.is_valid():
            populated_form.save()
            form = populated_form
            note = "Invoice has been updated."
            return redirect('/PyTraker/invoice/' + str(project_id))
            #return render(request, 'PyTraker/edit_invoice.html',
                          #{'note': note, 'invoice_form': form, 'invoice': invoice})
    else:
        return render(request, 'PyTraker/edit_invoice.html', {'invoice_form': form, 'invoice': invoice})


#Delete Invoice

@login_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoices, pk=invoice_id)
    return render(request, 'PyTraker/delete_invoice.html', {'invoice': invoice})


@login_required
def delete_invoice_conf(request, invoice_id):
    invoice = int(invoice_id)
    del_invoice = Invoices.objects.get(id=invoice)
    project_id = del_invoice.projectID.id
    del_invoice.delete()
    return redirect('/PyTraker/details_project/' + str(project_id))


# comment page
@login_required
def comment_view(request):
    obj = Comments.objects.all()
    context = {
        'object': obj
    }
    return render(request, "PyTraker/comment_form.html", context)


@login_required
def comment_detail_view(request, comment_id):
    obj = Comments.objects.get(id=comment_id)
    context = {
        'comment': obj
    }
    return render(request, "PyTraker/comment_detail.html", context)


@login_required
def comment_create_view(request):
    if request.method == "POST":
        new_comment = CommentForm()
        current_user = request.user
        my_p = User.objects.get(id=current_user.id)
        new_comment.user = my_p
        new_comment.comment = request.POST.get('comment')
        # new_comment.comment_date = parse_date(request.POST.get('comment_date'))
        new_comment.comment_date = datetime.now()
        print(new_comment.user)
        print(new_comment.comment_date)
        print(new_comment.comment)
        Comments.objects.create(user=new_comment.user, comment=new_comment.comment,
                                comment_date=new_comment.comment_date)
    comments = Comments.objects.all()
    date = datetime.now()
    context = {
        'object': comments,
        'time': defaultfilters.date(date, "Y-m-d h:i A")
    }
    return render(request, "PyTraker/comment_form.html", context)


# Task Views
# list task
@login_required
def tasklist(request):
    all_task_list = Tasks.objects.filter(complete=False)
    context = {"all_task_list": all_task_list}
    return render(request, "PyTraker/tasklist.html", context)


# task detail
@login_required
def task_detail(request, tasks_id):
    tasks = get_object_or_404(Tasks, pk=tasks_id)
    return render(request, 'PyTraker/task_detail.html', {'tasks': tasks})


# create task
@login_required
def new_task(request):
    if request.method == 'POST':
        filled_form = TaskForm(request.POST or None)
        if filled_form.is_valid():
            created_task = filled_form.save()
            created_task_id = created_task.id
            note = 'Your new task: %s has been added.' % (filled_form.cleaned_data['name'])
            filled_form = TaskForm()
        else:
            created_task_id = None
            note = "Your task was not added, please try again."
        return render(request, 'PyTraker/new_task.html',
                      {'created_task_id': created_task_id, 'new_task': filled_form, 'note': note})
    else:
        form = TaskForm()
        return render(request, 'PyTraker/new_task.html', {'new_task': form})


# edit task
@login_required
def edit_task(request, tasks_id):
    task = Tasks.objects.get(pk=tasks_id)
    form = TaskForm(instance=task)
    if request.method == "POST":
        filled_form = TaskForm(request.POST, instance=task)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = "The task has been updated."
            return render(request, 'PyTraker/edit_task.html', {'note': note, 'new_task': form, 'task': task})

    return render(request, 'PyTraker/edit_task.html', {'new_task': form, 'task': task})


# delete task
@login_required
def delete_task(request, tasks_id):
    tasks_id = int(tasks_id)
    try:
        task_del = Tasks.objects.get(id=tasks_id)
    except Tasks.DoesNotExist:
        return redirect('/PyTraker/index')
    task_del.delete()
    return redirect('/PyTraker/index')


# change status of task
@login_required
def change_status(request, tasks_id):
    task = Tasks.objects.get(id=tasks_id)
    try:
        task.complete = True
    except Tasks.DoesNotExist:
        return redirect('/PyTraker/index')
    task.save()
    return redirect('/PyTraker/tasklist')


# Project Views
@login_required
def projects(request):
    all_projects = Projects.objects.order_by("name")
    context = {"all_projects": all_projects}
    return render(request, "PyTraker/projects.html", context)


@login_required
def project_detail(request, projects_id):
    project = get_object_or_404(Projects, pk=projects_id)
    all_tasks = Tasks.objects.filter(projectID_id=projects_id)
    return render(request, 'PyTraker/project_detail.html', project, all_tasks)


@login_required
def new_project(request):
    if request.method == 'POST':
        filled_form = ProjectForm(request.POST or None)
        if filled_form.is_valid():
            created_project = filled_form.save()
            created_project_pk = created_project.id
           # note = 'Your Project with %s has been added.' % (filled_form.cleaned_data['name'])
            #filled_form = ProjectForm()
        return redirect('/PyTraker/index')
       # else:
        #    created_project_pk = None
         #   note = "Your project was not created, please try again."
       # return render(request, 'PyTraker/new_project.html', {'note': note})
                 #    {'created_project_pk': created_project_pk, 'new_project': filled_form, 'note': note})
    else:
        form = ProjectForm()
        return render(request, 'PyTraker/new_project.html', {'new_project': form})


@login_required
def edit_project(request, pk):
    project = Projects.objects.get(pk=pk)
    form = ProjectForm(instance=project)
    if request.method == "POST":
        filled_form = ProjectForm(request.POST, instance=project)
        if filled_form.is_valid():
            filled_form.save()
            form = filled_form
            note = "Project has been updated."
            return render(request, 'PyTraker/edit_project.html',
                          {'note': note, 'new_project': form, 'project': project})

    return render(request, 'PyTraker/edit_project.html', {'new_project': form, 'project': project})


@login_required
def details_project(request, pk):
    project = get_object_or_404(Projects, pk=pk)

    if request.method == 'POST':
        new_timer = TimerForm()
        new_timer.startTime = request.POST.get('stime')
        new_timer.endTime = request.POST.get('stoptime')
        new_timer.totaltime = request.POST.get('totaltime')
        new_timer.totalhours = request.POST.get('totalhours')

        #selected task
        tid = request.POST.get('task')
        tsk = Tasks.objects.get(pk=tid)

        id = request.POST.get('projectid')
        project = Projects.objects.get(id=id)
        Timers.objects.create(startTime=new_timer.startTime, endTime=new_timer.endTime, totaltime=new_timer.totaltime,
                              totalhours=new_timer.totalhours,projectID=project,task=tsk)
    date = datetime.now()
    timer = Timers.objects.filter(projectID=pk)
    task = Tasks.objects.filter(projectID=pk)
    try:
        invoice = Invoices.objects.get(projectID_id=pk)
    except Invoices.DoesNotExist:
        invoice = 'false'
    context = {
        'project':project,
        'time':defaultfilters.date(date, "h:i:s "),
        'stime':defaultfilters.date(date,'Y-m-d h:i:s'),
        'spentdate':defaultfilters.date(date,'Y-m-d'),
        'daylight':defaultfilters.date(date,''),
        'timer':timer,
        'task':task,
        'invoice':invoice
    }
    return render(request, 'PyTraker/details_project.html', context)




    #return render(request, 'PyTraker/details_project.html', {'project': project, 'tasks': tasks, 'invoice': invoice})



@login_required
def list_projects(request):
    project_list = Projects.objects.order_by('dueDate')
    context = {'project_list': project_list}
    return render(request, 'PyTraker/list_projects.html', context)


# def delete_project(request, pk):
#     pk = int(pk)
#     try:
#         project_sel = Projects.objects.get(id=pk)
#     except Projects.DoesNotExist:
#         return redirect('/PyTraker/index')
#     project_sel.delete()
#     return redirect('/PyTraker/index')

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    return render(request, 'PyTraker/delete_project.html', {'project': project})


@login_required
def delete_project_conf(request, pk):
    pk = int(pk)
    del_project = Projects.objects.get(id=pk)
    del_project.delete()
    return redirect('/PyTraker/index')






# Work Diary Views

@login_required
def workdiary(request):
    all_workdiary = WorkDiary.objects.order_by("name")
    context = {"all_workdiary": all_workdiary}
    return render(request, "PyTraker/workdiary.html", context)


@login_required
def workdiary_add(request):
    if request.method == "POST":
        diary_form = WorkDiaryForm(request.POST)
        current_user = request.user
        userID = User.objects.get(id=current_user.id)
        new_workdiary = WorkDiaryForm()
        new_workdiary.userID = userID
        new_workdiary.name = request.POST.get('name')
        new_workdiary.date = datetime.now()
        projectID = request.POST.get('projectID')
        project = Projects.objects.get(id=projectID)
        new_workdiary.projectID = project
        new_workdiary.projectNotes = request.POST.get('projectNotes')
        taskID = request.POST.get('taskID')
        task = Tasks.objects.get(id=taskID)
        new_workdiary.taskID = task
        new_workdiary.taskNotes = request.POST.get('taskNotes')
        WorkDiary.objects.create(userID=new_workdiary.userID, name=new_workdiary.name, date=new_workdiary.date,
                                 projectID=new_workdiary.projectID, projectNotes=new_workdiary.projectNotes,
                                 taskID=new_workdiary.taskID, taskNotes=new_workdiary.taskNotes)

        return redirect('/PyTraker/workdiary')
    else:
        diary_form = WorkDiaryForm()

    context = {
        'workdiary_add': diary_form,
    }
    return render(request, 'PyTraker/workdiary_add.html', context)


@login_required
def workdiary_edit(request, pk):
    workdiary = get_object_or_404(WorkDiary, pk=pk)
    edit_diary = WorkDiaryForm(instance=workdiary)
    if request.method == "POST":
        diary_form = WorkDiaryForm(request.POST, instance=workdiary)
        if diary_form.is_valid():
            diary_form.save()
            edit_diary = diary_form

            return render(request, 'PyTraker/workdiary_edit.html',
                          {'workdiary_edit': edit_diary, 'workdiary': workdiary})

    return render(request, 'PyTraker/workdiary_edit.html', {'workdiary_edit': edit_diary, 'workdiary': workdiary})


@login_required
def workdiary_details(request, pk):
    workdiary = get_object_or_404(WorkDiary, pk=pk)
    if request.method == "POST":
        new_comment = CommentForm()
        # get the login user id
        current_user = request.user
        my_p = User.objects.get(id=current_user.id)
        new_comment.user = my_p
        new_comment.comment = request.POST.get('comment')
        new_comment.workdiary = workdiary
        # new_comment.comment_date = parse_date(request.POST.get('comment_date'))
        new_comment.comment_date = datetime.now()
        # print(new_comment.user)
        # print(new_comment.comment_date)
        # print(new_comment.comment)
        Comments.objects.create(user=new_comment.user, comment=new_comment.comment,
                                comment_date=new_comment.comment_date, workdiary=new_comment.workdiary)
    comments = Comments.objects.filter(workdiary=pk)
    date = datetime.now()
    context = {
        'object': comments,
        'time': defaultfilters.date(date, "Y-m-d h:i A"),
        'workdiary': workdiary

    }
    return render(request, 'PyTraker/workdiary_detail.html', context)


@login_required
def comment_delete(request, comment_id):
    obj = get_object_or_404(Comments, id=comment_id)
    if request.method == "POST":
        obj.delete()
        return redirect('/PyTraker/workdiary')
    context = {
        "object": obj
    }
    return render(request, "PyTraker/comment_delete.html", context)


@login_required
def workdiary_delete(request, pk):
    workdiary = get_object_or_404(WorkDiary, pk=pk)
    return render(request, 'PyTraker/workdiary_delete.html', {'workdiary': workdiary})


@login_required
def workdiary_conf_delete(request, pk):
    pk = int(pk)
    del_workdiary = WorkDiary.objects.get(id=pk)
    del_workdiary.delete()

    return redirect('/PyTraker/workdiary')


class SearchResultsView(ListView):
    model = Projects
    template_name = 'PyTraker/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Projects.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return object_list


@login_required
def user_profile(request, pk):
    profile = get_object_or_404(Profile, user_id=pk)
    return render(request, 'PyTraker/user_profile.html', {'profile': profile})


@login_required
def user_profile_edit(request, pk):
    userprofile = get_object_or_404(Profile, user_id=pk)
    edit_profile = ProfileForm(instance=userprofile)
    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=userprofile)
        if profile_form.is_valid():
            profile_form.save()
            edit_profile = profile_form

            return redirect('/PyTraker/index')

    return render(request, 'PyTraker/user_profile_edit.html',
                  {'user_profile_edit': edit_profile, 'userprofile': userprofile})

# Note_Board
@login_required
def noteboard(request):
    notes = Noteboard_Note.objects.filter(userID=request.user.id)
    context = { "notes": notes}
    return render(request, 'PyTraker/noteboard.html', context)

# Note_Board: Create a new note
@login_required
def noteboard_create(request):
    if request.method == "POST":
        newNoteText = request.POST['newNoteText']
        newNote = Noteboard_Note(userID=request.user, note=newNoteText)
        newNote.save()
        return redirect('/PyTraker/noteboard')
    return render(request, 'PyTraker/noteboard_create.html')

# Note_Board: Update a note
@login_required
def noteboard_update(request, noteId):
    note = Noteboard_Note.objects.get(id=int(noteId))
    if request.method == "POST":
        note.note = request.POST['updatedText']
        note.save()
        return redirect('/PyTraker/noteboard')
    context = { "note": note }
    return render(request, 'PyTraker/noteboard_update.html', context)

# Note_Board: Update a note
@login_required
def noteboard_delete(request, noteId):
    Noteboard_Note.objects.get(id=int(noteId)).delete()
    return redirect('/PyTraker/noteboard')