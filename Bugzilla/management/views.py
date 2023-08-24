from django.shortcuts import render, redirect, get_object_or_404
from .forms.signupform import SignupForm
from .forms.loginform import LoginForm
from .forms.createproject import projectForm
from .forms.editprojectform import EditProjectForm
from .forms.reportbug import ReportBugForm
from .forms.editbug import EditBugForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .models import Project
from .models import Bug
from .models import userProfile
from django.urls import reverse_lazy
from .forms.createbug import CreateBugForm
from django.contrib.auth.decorators import user_passes_test
# Create your views here.

def signupForm(request):
	if request.method == 'POST':
		messages = ''
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages = "User Created successfully"
		else:
			messages = "User Creation Failed"
	else:
		messages = ''
		form = SignupForm()
	return render(request, 'signup.html',{'form':form, 'messages':messages})

def loginForm(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)  # Pass the request to the form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password =password)
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return redirect('/projects')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, 'login.html', context)



@login_required(login_url='/loginaccount', redirect_field_name="next")
def createbug(request):
    if request.method == 'POST':
        form = CreateBugForm(request.POST, request.FILES)
        if form.is_valid():
            bug = form.save(commit=False)  # Create an instance of the Bug model but don't save it yet
            bug.creator = request.user  # Assign the current logged-in user as the creator
            bug.save()  # Now save the bug instance with the assigned creator
            return redirect('qa_bug_list')  # Redirect to the projects list after bug creation
    else:
        form = CreateBugForm()

    context = {'form': form}
    return render(request, 'createbug.html', context)

@login_required(login_url='/loginaccount', redirect_field_name="next")
def reportbug(request, name):
    project = get_object_or_404(Project, name=name)
    
    if request.method == 'POST':
        form = ReportBugForm(request.POST, request.FILES)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.creator = request.user
            bug.project = project  # Assign the selected project to the bug
            bug.save()
            return redirect('qa_bug_list')  # Redirect to the projects list after bug creation
    else:
        form = ReportBugForm()

    context = {'form': form, 'project': project}
    return render(request, 'reportbug.html', context)

@user_passes_test(lambda u: u.userprofile.user_type == 'qa', login_url='/loginaccount')
def qa_bug_list(request):
    user = request.user
    bugs = Bug.objects.filter(creator=user).order_by('-start_date')
    
    # Retrieve the associated project for the QA member
    project = Project.objects.filter(qa=user).first()
    
    return render(request, 'qa_bug_list.html', {'bugs': bugs, 'project': project})

@login_required(login_url='/loginaccount', redirect_field_name="next")
def edit_bug(request, pk):
    bug = get_object_or_404(Bug, pk=pk)
    
    if request.method == 'POST':
        form = EditBugForm(request.POST, instance=bug)
        if form.is_valid():
            form.save()
            return redirect('qa_bug_list')  # Redirect back to the QA bug list
    else:
        form = EditBugForm(instance=bug)
    
    return render(request, 'edit_bug.html', {'form': form, 'bug': bug})

@login_required(login_url='/loginaccount', redirect_field_name="next")
def delete_bug(request, pk):
    bug = get_object_or_404(Bug, pk=pk)
    bug.delete()
    return redirect('qa_bug_list')  # Redirect back to the QA bug list


@login_required(login_url='/loginaccount', redirect_field_name="next")
def projectcreate(request):
    user = request.user  # This is the logged-in users
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type
    if request.method == "POST":
        if user_type=='manager':
            new_project = Project(name=request.POST['name'],managers=user)
            new_project.save()
            message="Create Project successfully"
            return redirect('/projects',{"message":message})
        else:
            return render(request,'notaccess.html')
    elif request.method == "GET":
        if user_type=="manager":
            message=''
            return render(request,'createproject.html',{"message":message})
        else:
            return render(request, 'notaccess.html')

@login_required(login_url='/loginaccount', redirect_field_name="next")
def allproject(request):
    user = request.user
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type

    projects = Project.objects.all()  # Retrieve all projects

    context = {
        'projects': projects,
        'user_type': user_type  # Pass the user_type to the template context
    }

    return render(request, 'projects.html', context)


@login_required(login_url='/loginaccount', redirect_field_name="next")
def deleteproject(request,name):
	project = Project.objects.get(name=name)
	project.delete()
	return redirect('/projects')

@login_required(login_url='/loginaccount', redirect_field_name="next")
def assigndeveloperdetail(request, name):
    project = Project.objects.get(name=name)
    available_developers = userProfile.objects.filter(user_type='developer').exclude(projects=project)
    return render(request, 'assigndeveloper.html', {"project": project, 'users': available_developers})

@login_required(login_url='/loginaccount', redirect_field_name="next")
def assigndeveloper(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        developer_username = request.POST['developer']
        developer = userProfile.objects.get(username=developer_username)
        developer.save()
        project.developer.add(developer)
        return redirect('/projects')


@login_required(login_url='/loginaccount', redirect_field_name="next")
def dischargedeveloperdetail(request, name):
    project = Project.objects.get(name=name)
    assigned_developers = project.developer.all()
    return render(request, 'dischargedeveloper.html', {"project": project, 'assigned_developers': assigned_developers})

@login_required(login_url='/loginaccount', redirect_field_name="next")
def dischargedeveloper(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        developer_username = request.POST['developer']
        developer = userProfile.objects.get(username=developer_username)
        project.developer.remove(developer)
        return redirect('/projects')

@login_required(login_url='/loginaccount', redirect_field_name="next")
def dischargeqadetail(request, name):
    project = Project.objects.get(name=name)
    assigned_qas = project.qa.all()
    return render(request, 'dischargeqa.html', {"project": project, 'assigned_qas': assigned_qas})

@login_required(login_url='/loginaccount', redirect_field_name="next")
def dischargeqa(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        qa_username = request.POST['qa']
        qa = userProfile.objects.get(username=qa_username)
        project.qa.remove(qa)
        return redirect('/projects')        



@login_required(login_url='/loginaccount', redirect_field_name="next")
def assignqadetail(request, name):
    project = Project.objects.get(name=name)
    available_qas = userProfile.objects.filter(user_type='qa').exclude(projectsq=project)
    print(available_qas.values_list('username', flat=True))  
    return render(request, 'assignqa.html', {"project": project, 'available_qas': available_qas})

@login_required(login_url='/loginaccount', redirect_field_name="next")
def assignqa(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        qa_username = request.POST['qa']
        qa = userProfile.objects.get(username=qa_username)
        project.qa.add(qa)
        return redirect('/projects')



@login_required(login_url='/loginaccount', redirect_field_name="next")
def logoutaccount(request):
    logout(request)
    return redirect('/loginaccount')

@login_required(login_url='/loginaccount', redirect_field_name="next")
def editproject(request, name):
    project = get_object_or_404(Project, name=name)

    if request.method == 'POST':
        form = EditProjectForm(request.POST, instance=project)
        if form.is_valid():
            developers_selected = request.POST.getlist('developers')  # Get the selected developers
            qa_selected = request.POST.getlist('qa')  # Get the selected QA members
            
            # Clear existing developer and QA assignments
            project.developer.clear()
            project.qa.clear()
            
            # Add the selected developers and QA members
            for developer_username in developers_selected:
                developer = userProfile.objects.get(username=developer_username)
                project.developer.add(developer)
            
            for qa_username in qa_selected:
                qa = userProfile.objects.get(username=qa_username)
                project.qa.add(qa)
            
            form.save()
            return redirect('/projects')  # Redirect to the projects list after editing
    else:
        form = EditProjectForm(instance=project)

    # Retrieve all developers and QA members
    all_developers = userProfile.objects.filter(user_type='developer')
    all_qas = userProfile.objects.filter(user_type='qa')

    context = {
        'form': form,
        'project': project,
        'all_developers': all_developers,
        'all_qas': all_qas,
    }
    return render(request, 'editproject.html', context)


