from django.db import models
from django.contrib.auth.models import User
import uuid
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    allowed_extensions = ['.gif', '.png']
    if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError('Only GIF and PNG files are allowed.')

class CustomCloudinaryField(CloudinaryField):
    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [validate_file_extension]
        super().__init__(*args, **kwargs)

class userProfile(User):
    USER_TYPES = [('developer', 'Developer'), ('manager', 'Manager'), ('qa', 'QA')]
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    def __str__(self):
    	return self.username


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    developer = models.ManyToManyField(User, related_name='projects', blank=True)
    qa = models.ManyToManyField(User, related_name='projectsq', blank=True)
    managers = models.ForeignKey(User, related_name='managed_projects', on_delete=models.CASCADE,blank=True)

    def __str__(self):
    	return self.name

class Bug(models.Model):
    BUG_TYPES = [('feature','Feature'),('bug','Bug')]
    BUG_STATUS = [('new', 'New'), ('started', 'Started'), ('resolved', 'Resolved'),('completed','Completed')]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    screenshot = CustomCloudinaryField('image')
    type = models.CharField(max_length=20, choices=BUG_TYPES)
    status = models.CharField(max_length=20, choices=BUG_STATUS, default=BUG_STATUS[0][0])
    start_date = models.DateField()
    deadline = models.DateField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bugs_created')
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bugs_assigned')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')

    def __str__(self):
        return self.title

