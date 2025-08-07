from api.models import LessonPlanRequest
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

API_URL_Retrieve_DATA = os.getenv('API_URL_Retrieve_DATA')
API_URL_GET_CHAPTER = os.getenv('API_URL_GET_CHAPTER')
API_URL_PDF_TO_TEXT = os.getenv('API_URL_PDF_TO_TEXT')
API_URL_UPLOAD_PDF_TO_VECTORSTORE = os.getenv('API_URL_UPLOAD_PDF_TO_VECTORSTORE')
API_URL_RETURN_RELEVANT_CHUNKS = os.getenv('API_URL_RETURN_RELEVANT_CHUNKS')


async def retrieve_data_from_db(state: LessonPlanRequest):
    # Prepare query parameters from `state`
    data = {
        "board": state.Board,
        "grade": state.Grade,
        "subject": state.Subject,
        "chapter_number": state.Chapter_Number
    }
    #print("DATA :",data)
    try:
        # Send POST request
        #print("API_URL :",API_URL_Retrieve_DATA)
        response = requests.get(API_URL_Retrieve_DATA, params=data)

        # Handle response
        if response.status_code == 200:
            #print("Response Data:", response.json())
            return response.json()
        else:
            #print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        #print("Exception occurred:", str(e))
        return None


def get_json_data(state: LessonPlanRequest):
    # Prepare query parameters from `state`
    data = {
        "board": state.Board,
        "grade": state.Grade,
        "subject": state.Subject,
    }
    #print("DATA :",data)
    try:
        # Send POST request
        #print("API_URL :",API_URL_GET_CHAPTER)
        response = requests.get(API_URL_GET_CHAPTER, params=data)

        # Handle response
        if response.status_code == 200:
            #print("Response Data:", response.json())
            return response.json()
        else:
            #print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        #print("Exception occurred:", str(e))
        return None


async def extract_pdf_text(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {
                # Use just the filename in the tuple
                "file": (
                    os.path.basename(file_path),  # e.g. "4.pdf"
                    f,
                    "application/pdf"
                )
            }
            headers = {"accept": "application/json"}

            # Send the POST request
            response = requests.post(API_URL_PDF_TO_TEXT, headers=headers, files=files)

        # Handle the response
        if response.status_code == 200:
            output = response.json()
            #print(type(output))
            #print("Response Data:", output)
            return output

        else:
            #print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        #print(f"Exception occurred: {e}")
        return None     

async def upload_pdf_to_vector_store(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {
                # Use just the filename in the tuple
                "file": (
                    os.path.basename(file_path),  # e.g. "4.pdf"
                    f,
                    "application/pdf"
                )
            }
            parsing_mode = "parse_page_with_agent"
            headers = {"accept": "application/json"}
            data = {"parsing_mode": parsing_mode}

            # Send the POST request
            response = requests.post(API_URL_UPLOAD_PDF_TO_VECTORSTORE, headers=headers, files=files, params=data)

        # Handle the response
        if response.status_code == 200:
            output = response.json()
            # print(type(output))
            # print("Response Data:", output)
            return output["store_id"]

        else:
            #print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        #print(f"Exception occurred: {e}")
        return None     

async def get_relevant_chunks(query,store_id):
    # Prepare query parameters from `state`
    data = {
        "query": query,
        "store_id": store_id
    }
    #print("DATA :",data)
    try:
        # Send POST request
        # print("API_URL :",API_URL_GET_CHAPTER)
        response = requests.post(API_URL_RETURN_RELEVANT_CHUNKS, params=data)

        # Handle response
        if response.status_code == 200:
            # print("Response Relevant chunk:", response.json())
            return response.json()
        else:
            # print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        # print("Exception occurred:", str(e))
        return None
    
def get_chapter_name_from_number(response_json, chapter_number):
    try:
        chapters = response_json.get("data", {}).get("data", [])
        for chapter in chapters:
            if str(chapter[0]) == str(chapter_number):
                return chapter[1]
        return f"Chapter number {chapter_number} not found."
    except Exception as e:
        return f"Error occurred: {str(e)}"


# import fitz  # pip install PyMuPDF

# async def extract_pdf_text(file_path):
#     combined_text = ""
#     with fitz.open(file_path) as pdf:
#         for page_num in range(pdf.page_count):
#             page = pdf[page_num]
#             combined_text += page.get_text() + "\n\n"  # type: ignore # Separate pages with newlines
#     os.remove(file_path)
#     return combined_text
