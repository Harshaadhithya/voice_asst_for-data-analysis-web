from django.shortcuts import render, redirect
from chat.models import *
import pandas as pd
import json
import numpy as np
from chat.constants import USER_MESSAGE_TYPE, SYSTEM_MESSAGE_TYPE
from django.http import JsonResponse
from chat.actions import chat_with_analyzer_agent, speech_to_text, text_to_speech
from data_analyzer_assistant import settings
from django.core.files.storage import default_storage

# Create your views here.


def my_analysis(request):
    # if request.user.is_authenticated:
    my_chats = Chat.objects.filter(user = request.user)
    return render(request, 'chat/my_chats.html', context={"my_chats":my_chats})
    # return redirect('home')

def new_analysis(request):
    chat_sessions = Chat.objects.filter()
    if not chat_sessions.exists():
        chat_session = Chat.objects.create(user = request.user)
    else:
        last_session = chat_sessions.first()
        if not last_session.is_empty_chat:
            chat_session = Chat.objects.create(user = request.user)
        else:
            chat_session = last_session
            
    return redirect('analyze', pk=chat_session.id)


def analyze(request, pk):
    chat_obj = Chat.objects.get(id=pk)

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']        
        chat_attachment = ChatAttachment(chat=chat_obj, attachment_file=uploaded_file)
        chat_attachment.save()

    chat_messages = chat_obj.chat_messages.all()
    chat_attachments = chat_obj.chat_attachments.all()
    # chat_attachments=[]
    if len(chat_attachments) > 0:
        attachment = chat_attachments[0]
        file_path = attachment.attachment_file.path
        
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                df = pd.DataFrame({})
            
            # initial_file_data = [df.columns.tolist()] + df.values.tolist()
            # initial_file_data = json.dumps(initial_file_data)
            # Convert DataFrame to JSON-safe format
            initial_file_data = df.replace({np.nan: None}).values.tolist()
            initial_file_data.insert(0, df.columns.tolist())
            initial_file_data = json.dumps(initial_file_data)
        except Exception as e:
            print(f"Error processing file: {e}")
            initial_file_data = json.dumps([])
    else:
        initial_file_data = json.dumps([])
    print(initial_file_data)
    return render(request, 'chat/analyze.html', {"chat_obj":chat_obj, "chat_messages": chat_messages, "chat_attachments": chat_attachments, "initial_file_data":initial_file_data})


def chat(request, pk):
    chat_obj = Chat.objects.get(id=pk)
    if request.method == 'POST':
        print("POST",request.POST)
        print("body", json.loads(request.body))
        data = json.loads(request.body)
        message = data.get("message")
        input_message = ChatMessage.objects.create(
            chat=chat_obj,
            message_type = USER_MESSAGE_TYPE,
            message=message
        )
        print("message", message)
        print("sending the question to agent")
        success, response = chat_with_analyzer_agent(chat_obj=chat_obj, user_message=message)
        if not success:
            response = "Something went wrong with the analyzer agent :/"
        output_message = ChatMessage.objects.create(
            chat=chat_obj,
            message_type = SYSTEM_MESSAGE_TYPE,
            message=response.get("output")
        )
        audio_url = text_to_speech(chat_message_obj=output_message)

        print("response",response)
        response["input_chat_message_id"] = input_message.id
        response["output_chat_message_id"] = output_message.id
        response["output_audio_url"] = audio_url

    return JsonResponse(response)


def save_audio_file(audio_file):
    audio_file_name = f"{audio_file.name}.wav" if not audio_file.name.endswith('.wav') else audio_file.name
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file_name)

    # Save the file using default storage system
    if not os.path.exists(os.path.dirname(audio_file_path)):
        os.makedirs(os.path.dirname(audio_file_path))  # Create the directory if it doesn't exist

    with default_storage.open(audio_file_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    print("audio_file_path",audio_file_path)
    return audio_file_path


def audio_chat(request, pk):
    chat_obj = Chat.objects.get(id=pk)
    if request.method == 'POST' and request.FILES.get('audio'):
        # Get the audio file from the request
        audio_file = request.FILES['audio']

        # Save the audio file to the media directory
        audio_path = save_audio_file(audio_file)
        text_from_speech = speech_to_text(audio_path)

        print(audio_path)

        input_message = ChatMessage.objects.create(
            chat=chat_obj,
            message_type = USER_MESSAGE_TYPE,
            message=text_from_speech
        )
        success, response = chat_with_analyzer_agent(chat_obj=chat_obj, user_message=text_from_speech)
        if not success:
            response = "Something went wrong with the analyzer agent :/"
        output_message = ChatMessage.objects.create(
            chat=chat_obj,
            message_type = SYSTEM_MESSAGE_TYPE,
            message=response.get("output")
        )
        audio_url = text_to_speech(chat_message_obj=output_message)

        print("response",response)
        response["input_chat_message_id"] = input_message.id
        response["output_chat_message_id"] = output_message.id
        response["output_audio_url"] = audio_url

    return JsonResponse(response)


def get_file_data(request, pk):
    attachment = ChatAttachment.objects.get(id=pk)
    file_path = attachment.attachment_file.path
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame({})
        
        
        file_data = df.replace({np.nan: None}).values.tolist()
        file_data.insert(0, df.columns.tolist())
        # file_data = json.dumps(file_data)
    except Exception as e:
        print(f"Error processing file: {e}")
        file_data = json.dumps([])
    print(file_data)

    return JsonResponse({"file_data":file_data})


