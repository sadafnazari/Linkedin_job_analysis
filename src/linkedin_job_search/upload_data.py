from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from dotenv import dotenv_values

secrets = dotenv_values("configs/.env")

def upload_file_to_gdrive(file_path, file_name, folder_id, custom_file_id):
    try:
        creds = Credentials.from_service_account_file('configs/linkedin-job-analysis-api-key.json')
        service = build('drive', 'v3', credentials=creds)

        query = f"name='{file_name}' and '{folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            print(f"File already exists with ID: {files[0]['id']}. Deleting it.")
            service.files().delete(fileId=files[0]['id']).execute()

        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
            'description': f'Custom File ID: {custom_file_id}'
        }

        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"New file uploaded successfully!\nGenerated File ID: {uploaded_file.get('id')}")
        return uploaded_file.get('id')

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

folder_id = secrets["FOLDER_ID"]
file_path = 'data/jobs.db'
file_name = 'jobs.db'
custom_file_id = secrets["FILE_ID"]

file_id = upload_file_to_gdrive(file_path, file_name, folder_id, custom_file_id)
print(f"Uploaded Google Drive File ID: {file_id}")
