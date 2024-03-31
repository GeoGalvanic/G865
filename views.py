from django.shortcuts import render
from .forms import QueueEntryForm
from .models import QueueEntry, Buff
import boto3
import json
import re
from datetime import datetime
from django.db import connections
from django.core.files.base import ContentFile
from django.core.serializers import serialize
from .sqs_pw import access_key, secret_key

sqs = boto3.resource(
    'sqs',
    region_name='us-east-1',
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key
    )
queue = sqs.get_queue_by_name(QueueName= 'Distributed_GP.fifo')

# Create EC2 client and handle state operations
ec2_client = boto3.client(
    'ec2',
    region_name='us-east-1',
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key
    )

ec2_server_list = {
    'i-0f50d780337bade67' : 'Server 1',
    'i-0766c91f58e8e60b7' : 'Server 2',
    'i-04db7d858e14ba37d' : 'Server 3'
    }

def get_ec2_status():
    pulse_results = {}
    
    pulse = ec2_client.describe_instance_status(
        InstanceIds = list(ec2_server_list.keys()),
        IncludeAllInstances = True
        )

    for i_pulse in pulse['InstanceStatuses']:
        server = i_pulse['InstanceId']
        state = i_pulse['InstanceState']['Name']

        pulse_results[ec2_server_list[server]] = state
    
    return pulse_results

#Check if a task has been finished
def check_status(queue_entry):
    with connections['G865'].cursor() as cursor:
        cursor.execute(
            """SELECT COUNT(*) FROM "distributed_results" WHERE "Group_ID" = %s """,
            [queue_entry.id]
        )
        number_in_database = cursor.fetchone()[0]

        return (
            True if number_in_database >= queue_entry.number_features * queue_entry.number_buffers else False,
            number_in_database
            )

#Process the task now that it is complete
def entry_complete(entry):
    buffers = Buff.objects.using("G865").raw(
        """SELECT
        "Feat_ID" + "Buffer_Size" as fake_id,
        "Feat_ID",
        "Group_ID",
        "Buffer_Size",
        %s as "Shape" FROM distributed_results;"""% (
            connections["G865"].ops.select % '"Shape"'
            )
        )
    geojson_buffers = serialize('geojson', buffers, geometry_field='"Shape"')

    buffer_string = json.dumps(geojson_buffers)
    buffer_file = ContentFile(buffer_string)

    entry.output_file.save(
        f"{entry.creator_user.username}-{entry.id}.geojson",
        buffer_file,
        save = False
        )
    
    entry.complete = True

    entry.save()


# Create your views here.
def index(request):
    return render(request, 'G865/index.html')

def l4_video(request):
    return render(request, 'G865/l4-video.html')

def final_video(request):
    return render(request, 'G865/final-video.html')

def test(request):
    return render(request, 'G865/test.html')

def lesson5(request):
    return render(request, 'G865/lesson5.html')

def final_queue(request):
    if request.method == "POST":
        form = QueueEntryForm(request.POST, request.FILES)
        if form.is_valid():
            #Serialize uploaded file into JSON format
            uploaded_file = request.FILES['upload_file']
            geojson = json.load(uploaded_file)

            #Ensure the buffers string only contains numbers and commas
            buffers = ''.join( re.findall(r'[\d,\,.]+', request.POST.get('buffers')) )
            
            #Create a new model for the entry
            new_entry = QueueEntry(
                name = request.POST.get('name'),
                upload_file_name = request.FILES['upload_file'].name,
                buffer_string = buffers,
                number_features = len(geojson['features']),
                number_buffers = len(buffers.split(',')),
                creator_user = request.user,
                start_time = datetime.now()
                )

            new_entry.save()

            #Send the task to the SQS queue
            feat_num = 0 #Used to create message deduplication id
            for feature in geojson['features']:
                feat_num += 1
                if feature['geometry']['type'] == 'Point':
                    feat_id = '0'
                    if 'oid' in feature['properties']:
                        feat_id = str(feature['properties']['oid'])
                    elif 'fid' in feature['properties']:
                        feat_id = str(feature['properties']['fid'])
                    elif 'id' in feature['properties']:
                        feat_id = str(feature['properties']['id'])
                    else:
                        feat_id = feat_num
                    
                    queue.send_message(
                        MessageAttributes={
                            'Feat-Id' : {
                                'DataType' : 'String',
                                'StringValue' : str(feat_id),
                            },
                            'X-Coordinate' : {
                                'DataType' : 'Number',
                                'StringValue' : str(feature['geometry']['coordinates'][0]),
                            },
                            'Y-Coordinate' : {
                                'DataType' : 'Number',
                                'StringValue' : str(feature['geometry']['coordinates'][1]),
                            },
                        },
                        MessageGroupId = str(new_entry.id),
                        MessageBody = f'Buffer:{buffers}',
                        MessageDeduplicationId = f'{str(new_entry.id)}-{str(feat_num)}'
                    )

            #Render the success page
            return render(request, 'G865/queue-submit.html', {
                'group_id' : new_entry.id,
                'task_name' : new_entry.name
            })

    else:
        form = QueueEntryForm()
    
    return render(request, 'G865/final-queue.html', {
            'form' : form
        })

def ec2(request):
    if request.method == "POST":
        switch = request.POST.get('Switch')
        if switch == 'On':
            ec2_client.start_instances(
                InstanceIds = list(ec2_server_list.keys())
                )
        elif switch == 'Off':
            ec2_client.stop_instances(
                InstanceIds = list(ec2_server_list.keys())
                )

    return render(request, 'G865/ec2.html', {
        'statuses' : get_ec2_status()
    })

def task_list(request):
    tasks = QueueEntry.objects.filter(creator_user = request.user)
    for task in tasks:
        if not task.complete:
            status = check_status(task)
            if status[0] == True:
                entry_complete(task)
    return render(request, 'G865/task-list.html', {
        'tasks' : tasks,
        'completed_features' : status[1] if not task.complete else 'All'
    })

def task_item(request, task_id):
    item = QueueEntry.objects.get(id = task_id)
    if not item.complete:
        status = check_status(item)
        if status[0] == True:
            entry_complete(item)
    return render(request, 'G865/task-item.html', {
        'item' : item,
        'completed_features' : status[1] if not item.complete else 'All'
    })


