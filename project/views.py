from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Profile,Project
from .forms import PostProject,UpdateUser,UpdateProfile,Votes
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProjectSerailizer,UserSerializer
from rest_framework import status
from .permission import IsAdminOrReadOnly
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import numpy as np

# Create your views here.

class ProjectList(APIView):
    def get(self,response,format=None):
        projects=Project.objects.all()
        serializer=ProjectSerailizer(projects,many=True)
        return Response(serializer.data)
    
    @login_required
    def post(self,request,format=None):
        permission_classes=(IsAdminOrReadOnly,)
        serializer=ProjectSerailizer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
        permission_classes=(IsAdminOrReadOnly,)

class UserList(APIView):
    def get(self,response,format=None):
        users=User.objects.all()
        serializer=UserSerializer(users,many=True)
        return Response(serializer.data)
 
 #GETS A PROJECT BY AN ID 
class ProjectDescription(APIView):
    permission_classes=(IsAdminOrReadOnly,)  
    def get_project(self,pk):
        return get_object_or_404(Project,pk=pk)
    #gets project by id
    def get(self, request, pk ,format=None):
        project= self.get_project(pk)
        serializer=ProjectSerailizer(project)
        return Response(serializer.data)
    #updates a specific project
    def put(self, request,pk, format=None):
        project=self.get_project(pk)
        serializer=ProjectSerailizer(project,request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #DELETES A PROJECT    
    def delete(self,request,pk,format=None):
        project=self.get_project(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
#GETS USER BY ID        
class UserDescription(APIView):
    permission_classes=(IsAdminOrReadOnly,)  
    def get_user(self,pk):
        return get_object_or_404(User,pk=pk)
    #gets user by id
    def get(self, request, pk ,format=None):
        user= self.get_user(pk)
        serializer=UserSerializer(user)
        return Response(serializer.data)
    #updates a specific user
    def put(self, request,pk, format=None):
        user=self.get_user(pk)
        serializer=UserSerializer(user,request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #DELETES A user   
    def delete(self,request,pk,format=None):
        user=self.get_user(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        
    


#Index view
def index(request):
    projects=Project.objects.order_by('-posted')
    return render(request,'project/index.html',{'projects':projects})

#user profile
@login_required
def profile(request):
    # profile = Profile.objects.create(user=request.user)
    return render(request,'project/profile.html')


#specific project
@login_required
def project(request,project_id):
    project=get_object_or_404(Project,pk=project_id)
    votes=Votes()
    votes_list=project.votes_set.all()
    for vote in votes_list:
        vote_mean=[]
        usability=vote.usability
        vote_mean.append(usability)
        content=vote.content
        vote_mean.append(content)
        design=vote.design
        vote_mean.append(design)
        mean=np.mean(vote_mean)
        mean=round(mean,2)
        if mean:
            return render(request, 'project/project.html',{'project':project,'votes':votes,'votes_list':votes_list,'mean':mean})

        
    return render(request, 'project/project.html',{'project':project,'votes':votes,'votes_list':votes_list})

@login_required
def new_project(request):
    current_user=request.user
    if request.method=='POST':
        form=PostProject(request.POST,request.FILES)
        if form.is_valid():
            project=form.save(commit=False)
            project.user=current_user
            project.save()
        return redirect('project:project_index')
    
    else:
        form=PostProject()
        
    return render(request,'project/new_project.html',{'form':form})

@login_required
def posted_by(request, user_id):
    user=get_object_or_404(User,pk=user_id)
    return render(request,'project/posted_by.html', {'user':user})

@login_required
def vote(request, project_id):
    project=get_object_or_404(Project, pk=project_id)
    votes=Votes()
    votes=Votes(request.POST)
    if votes.is_valid():
        vote=votes.save(commit=False)
        vote.user=request.user
        vote.project=project
        vote.save() 
        messages.success(request,'Votes Successfully submitted')
        return HttpResponseRedirect(reverse('project:project',  args=(project.id,)))
    
    else:
        messages.warning(request,'ERROR! Voting Range is from 0-10')
        votes=Votes()     
    return render(request, 'project/project.html',{'project':project,'votes':votes})
        
    
    
def update_settings(request):
    update_user=UpdateUser(request.POST,instance=request.user)
    update_profile=UpdateProfile(request.POST,request.FILES,instance=request.user.profile)
    if update_user.is_valid() and update_profile.is_valid():
        update_user.save()
        update_profile.save()
        
        messages.success(request, 'Profile Updated Successfully')
        return redirect('project:profile')
    
    else:
        update_user=UpdateUser(instance=request.user)
        update_profile=UpdateProfile(instance=request.user.profile)
    return render(request, 'project/update_profile.html',{'update_user':update_user,'update_profile':update_profile})

#API PAGE
def api(request):
    return render(request,'project/api.html')


