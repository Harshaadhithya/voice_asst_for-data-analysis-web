from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
import pandas as pd
from data_analyzer_assistant.settings import OPENAI_API_KEY, MEDIA_ROOT
import os
from chat.models import *
from django.core.files.uploadedfile import InMemoryUploadedFile
from pathlib import Path



from openai import OpenAI



def chat_with_analyzer_agent(chat_obj, user_message):
    chat_attachments = chat_obj.chat_attachments.all()
    dataframes = list()
    for attachment_obj in chat_attachments:
        file_path = attachment_obj.attachment_file.path
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                continue
            dataframes.append(df)
        except Exception as e:
            print(f"Error processing file: {e}")
    llm = ChatOpenAI(model='gpt-3.5-turbo-1106', api_key=OPENAI_API_KEY, temperature=0)
    if len(dataframes)==1:
        agent = create_pandas_dataframe_agent(llm=llm, df=dataframes[0], verbose=True, allow_dangerous_code=True)
    else:
        agent = create_pandas_dataframe_agent(llm=llm, df=dataframes, verbose=True, allow_dangerous_code=True)
    try:
        response = agent.invoke(user_message)
        return True, response
    except Exception as e:
        print("exception with agent", e)
        return False, None
    

def speech_to_text(audio_file_path):
    client = OpenAI(api_key=OPENAI_API_KEY)
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text"
    )
    print(transcription)
    return transcription


def text_to_speech(chat_message_obj):
    client = OpenAI(api_key=OPENAI_API_KEY)
    speech_file_path = Path(MEDIA_ROOT) / f"{chat_message_obj.id}.mp3"  # Generate unique file name

    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=chat_message_obj.message,
    )
    response.stream_to_file(speech_file_path)
    chat_message_obj.audio.name = str(speech_file_path.relative_to(MEDIA_ROOT))
    chat_message_obj.save()
    audio_url = chat_message_obj.audio.url
    print(audio_url)
    return audio_url




