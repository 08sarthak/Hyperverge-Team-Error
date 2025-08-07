from api.models import LessonPlanRequest, LessonPlanRequestfromVideo
import api.helper.lessonplan.api_helper as helper
import api.helper.lessonplan.transcribe_helper as transcribe
import os
import shutil

async def content_from_db(state:LessonPlanRequest):
    content = await helper.retrieve_data_from_db(state)
    #print("FILE :",file)
    #content = await helper.extract_pdf_text(file)
    #print("CONTENT :",content)  
    return content

async def content_from_vid(state:LessonPlanRequestfromVideo):

    # audio_path = transcribe.download_audio_from_yt(state.video_url)

    # # Step 2: Transcribe audio using Whisper API
    # transcription = transcribe.transcribe_audio("audio.mp3")

    # print("TRANSCRIPTION :",transcription)
    # return transcription
    return "API DEV IN PROGRESS"

UPLOAD_DIR = "files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def content_from_pdf(file):
    clean_upload_dir(UPLOAD_DIR)
    #print("directory cleaned")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    #print("FILE PATH:",file_path)
    # Save the uploaded file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    
    # Extract content from the PDF
    content = await helper.extract_pdf_text(file_path)
    #print("CONTENT:",content)
    
    # Ensure the file is removed even if an exception occurs
    if os.path.exists(file_path):
        os.remove(file_path)

    return content

async def upload_pdf_to_vs(file):
    clean_upload_dir(UPLOAD_DIR)
    #print("directory cleaned")
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    #print("FILE PATH:",file_path)
    # Save the uploaded file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    
    # Extract content from the PDF
    content = await helper.upload_pdf_to_vector_store(file_path)
    #print("CONTENT:",content)
    
    # Ensure the file is removed even if an exception occurs
    if os.path.exists(file_path):
        os.remove(file_path)

    return content

def clean_upload_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                #print(f"Removed file: {file_path}")
        except Exception as e:
            # print(f"Error removing file {file_path}: {e}")
            pass
