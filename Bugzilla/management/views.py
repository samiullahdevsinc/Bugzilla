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



def is_qa_user(user):
    user_profile = userProfile.objects.get(username=user)
    return user_profile.user_type == 'qa'

def is_developer_user(user):
    user_profile = userProfile.objects.get(username=user)
    return user_profile.user_type == 'developer'

def is_manager_user(user):
    user_profile = userProfile.objects.get(username=user)
    return user_profile.user_type == 'manager'

def signupForm(request):
	if request.method == 'POST':
		messages = ''
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages = "User Created successfully"
			return redirect('/loginaccount')
		else:
			messages = "User Creation Failed"
	else:
		messages = ''
		form = SignupForm()
	return render(request, 'signup.html',{'form':form, 'messages':messages})

def loginForm(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            user_profile = userProfile.objects.get(username=user.username)
            if user_profile.user_type == 'manager':
                return redirect('/projects')
            elif user_profile.user_type == 'qa':
                return redirect('/projectsq')
            else:
                return redirect('developer_bug_list')
            
        else:
            messages='Invalid credentials. Please try again'
    else:
        form = LoginForm()
        messages=""

    context = {'form': form, "messages":messages}
    return render(request, 'login.html', context)


@login_required(login_url='/loginaccount', redirect_field_name="next")
def home(request):
    user_profile = userProfile.objects.get(username=request.user)
    if user_profile.user_type == 'manager':
        return redirect('/projects')
    elif user_profile.user_type == 'qa':
        return redirect('/projectsq')
    else:
        return redirect('developer_bug_list')    


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_qa_user, login_url='/notaccess')
def createbug(request):
    if request.method == 'POST':
        form = CreateBugForm(request.POST, request.FILES)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.creator = request.user
            bug.save()
            return redirect('qa_bug_list')
    else:
        # Customize the developer field choices to show only developers
        developers = userProfile.objects.filter(user_type='developer')
        form = CreateBugForm()
        form.fields['developer'].queryset = developers

    context = {'form': form}
    return render(request, 'createbug.html', context)


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_qa_user, login_url='/notaccess')
def reportbug(request, name):
    project = get_object_or_404(Project, name=name)
    
    # Retrieve developers assigned to the project
    assigned_developers = project.developer.all()
    
    if request.method == 'POST':
        form = ReportBugForm(request.POST, request.FILES)
        if form.is_valid():
            bug = form.save(commit=False)
            bug.creator = request.user
            bug.project = project  # Assign the selected project to the bug
            bug.save()
            return redirect('qa_bug_list') 
    else:
        form = ReportBugForm()

    context = {'form': form, 'project': project, 'assigned_developers': assigned_developers}
    return render(request, 'reportbug.html', context)


@user_passes_test(lambda u: u.userprofile.user_type == 'qa', login_url='/loginaccount')
@user_passes_test(is_qa_user, login_url='/notaccess')
def qa_bug_list(request):
    user = request.user
    bugs = Bug.objects.filter(creator=user).order_by('-start_date')
    
    # Retrieve the associated project for the QA member
    project = Project.objects.filter(qa=user).first()
    
    return render(request, 'qa_bug_list.html', {'bugs': bugs, 'project': project})

@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_qa_user, login_url='/notaccess')
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
@user_passes_test(is_qa_user, login_url='/notaccess')
def delete_bug(request, pk):
    bug = get_object_or_404(Bug, pk=pk)
    bug.delete()
    return redirect('qa_bug_list')  # Redirect back to the QA bug list

@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
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
@user_passes_test(is_qa_user, login_url='/notaccess')
def allprojectq(request):
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
@user_passes_test(is_manager_user, login_url='/notaccess')
def allproject(request):
    user = request.user
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type
    if user_type=='manager':
        projects = Project.objects.filter(managers=user_profile)  # Filter projects by the logged-in user

        context = {
            'projects': projects,
            'user_type': user_type
        }

        return render(request, 'projects.html', context)
    else:
        return render(request,'notaccess.html')


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def deleteproject(request,name):

	project = Project.objects.get(name=name)
	project.delete()
	return redirect('/projects')

@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def assigndeveloperdetail(request, name):
    project = Project.objects.get(name=name)
    available_developers = userProfile.objects.filter(user_type='developer').exclude(projects=project)
    return render(request, 'assigndeveloper.html', {"project": project, 'users': available_developers})


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def assigndeveloper(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        developer_username = request.POST['developer']
        developer = userProfile.objects.get(username=developer_username)
        developer.save()
        project.developer.add(developer)
        return redirect('/projects')


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def dischargedeveloperdetail(request, name):
    project = Project.objects.get(name=name)
    assigned_developers = project.developer.all()
    return render(request, 'dischargedeveloper.html', {"project": project, 'assigned_developers': assigned_developers})

@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def dischargedeveloper(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        developer_username = request.POST['developer']
        developer = userProfile.objects.get(username=developer_username)
        project.developer.remove(developer)
        return redirect('/projects')


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def dischargeqadetail(request, name):
    project = Project.objects.get(name=name)
    assigned_qas = project.qa.all()
    return render(request, 'dischargeqa.html', {"project": project, 'assigned_qas': assigned_qas})


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def dischargeqa(request, name):
    if request.method == 'POST':
        project = Project.objects.get(name=name)
        qa_username = request.POST['qa']
        qa = userProfile.objects.get(username=qa_username)
        project.qa.remove(qa)
        return redirect('/projects')      



@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
def assignqadetail(request, name):
    user = request.user  # This is the logged-in users
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type
    if user_type=='manager':  
        project = Project.objects.get(name=name)
        available_qas = userProfile.objects.filter(user_type='qa').exclude(projectsq=project)
        print(available_qas.values_list('username', flat=True))  
        return render(request, 'assignqa.html', {"project": project, 'available_qas': available_qas})
    else:
        return render(request,'notaccess.html')

@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_manager_user, login_url='/notaccess')
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
    user = request.user  # This is the logged-in users
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type
    if user_type=='manager':  
        project = get_object_or_404(Project, name=name)
        
        if request.method == 'POST':
            form = EditProjectForm(request.POST, instance=project)  # Pass the instance to update the existing project
            if form.is_valid():
                print("test")
                form.save()
                return redirect('/projects')  # Redirect to the projects list after editing
        else:
            form = EditProjectForm(instance=project)

        context = {
            'form': form,
            'project': project,
        }
        return render(request, 'editproject.html', context)
    else:
        return render(request,'notaccess.html')

@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_developer_user, login_url='/notaccess')
def assign_bug_to_self(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    # Check if the bug is in 'new' status and the user is assigned to the bug's project
    if bug.status == 'new':
        print("yes")
        bug.status = 'started'
        bug.developer = request.user
        bug.save()
        project_name = bug.project.name  # Get the project name
        return redirect('developer_bug_list')  # Redirect to the developer's bug list with the project name




@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_developer_user, login_url='/notaccess')
def developer_bug_list(request):
    user = request.user  # This is the logged-in users
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type
    if user_type=='developer':
        bugs = Bug.objects.filter(developer=user)
        return render(request, 'developer_bug_list.html', {'bugs': bugs})
    else:
        return render(request, 'notaccess.html')


@login_required(login_url='/loginaccount', redirect_field_name="next")
@user_passes_test(is_developer_user, login_url='/notaccess')
def resolve_bug_to_self(request, bug_id):
    user = request.user  # This is the logged-in users
    user_profile = userProfile.objects.get(username=user.username)
    user_type = user_profile.user_type
    if user_type=='developer':      
        bug = get_object_or_404(Bug, id=bug_id)
        # Check if the bug is in 'new' status and the user is assigned to the bug's project
        if bug.status == 'started':
            print("yes")
            if bug.type == 'feature':
                bug.status = 'completed'
            else:
                bug.status='resolved'
            bug.developer = request.user
            bug.save()
            return redirect('developer_bug_list')  # Redirect to the developer's bug list
    else:
        return render(request, 'notaccess.html')  # Or any appropriate template

def notaccess(request):
    return render(request, 'notaccess.html')