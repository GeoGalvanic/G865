from django.urls import path
from . import views

app_name = 'G865'
urlpatterns = [
            path('', views.index, name='G865'),
            path('l4video', views.l4_video, name='lesson-4-video'),
            path('test', views.test, name='test'),
            path('lesson5', views.lesson5, name='lesson5'),
            path('final/queue', views.final_queue, name="final-queue"),
            path('final/ec2', views.ec2, name='final-ec2'),
            path('final/queue/tasks', views.task_list, name='task-list'),
            path('final/queue/tasks/<str:task_id>', views.task_item, name='task-item'),
            path('final/video', views.final_video, name='final-video')
            ]