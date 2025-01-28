import boto3
import time
import requests
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
load_dotenv()

# AWS clients
transcribe_medical = boto3.client('transcribe', region_name=os.getenv('AWS_REGION', 'us-east-1'))
s3_client = boto3.client('s3', region_name="us-east-1")
brt = boto3.client("bedrock-runtime", region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Global variable to store transcription summary
transcription_summary = None

# Default settings from environment variables
BUCKET_NAME = os.getenv('BUCKET_NAME', 'default-bucket-name')
DATA_ACCESS_ROLE_ARN = os.getenv('DATA_ACCESS_ROLE_ARN', 'default-role-arn')
AUDIO_FILE_URL = os.getenv('AUDIO_FILE_URL', 'https://your-bucket-name.s3.us-east-1.amazonaws.com/Sample_data.mp3')

# Pre-defined audio files (all pointing to Sample_data.mp3)
PREDEFINED_AUDIO_FILES = [
    {"label": "Audio File 1", "url": AUDIO_FILE_URL},
    {"label": "Audio File 2", "url": AUDIO_FILE_URL},
    {"label": "Audio File 3", "url": AUDIO_FILE_URL},
]


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    """
    Generate a pre-signed URL for summary.json to allow temporary public access.
    The URL expires in 'expiration' seconds (default: 1 hour).
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration  # URL expires in 1 hour
        )
        print(f"Generated pre-signed URL: {url}")
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {str(e)}")
        return None


def fetch_summary(summary_uri):
    """
    Fetches the summary.json file using a pre-signed URL and formats it into plain text.
    """
    try:
        # Extract the S3 object key from the URI
        object_key = summary_uri.split(f"{BUCKET_NAME}/")[-1]

        # Generate a pre-signed URL for temporary access
        pre_signed_url = generate_presigned_url(BUCKET_NAME, object_key)

        # Fetch the summary.json file from the pre-signed URL
        response = requests.get(pre_signed_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch summary.json: {response.status_code}, {response.text}")

        summary_json = response.json()

        # Parse the JSON to extract summarized text
        summary_text = ""
        sections = summary_json.get("ClinicalDocumentation", {}).get("Sections", [])
        for section in sections:
            section_name = section.get("SectionName", "Unknown Section")
            summary_text += f"\n{section_name}:\n"
            for summary in section.get("Summary", []):
                summarized_segment = summary.get("SummarizedSegment", "")
                summary_text += f"- {summarized_segment}\n"

        return summary_text.strip()

    except Exception as e:
        raise Exception(f"Error fetching summary: {str(e)}")


def start_transcription(job_name, audio_file_uri):
    """
    Ensures only one transcription job runs at a time.
    If an active job exists, it waits for that job to finish before starting a new one.
    """
    try:
        # Check for any active transcription jobs
        existing_jobs = transcribe_medical.list_medical_scribe_jobs(
            Status='IN_PROGRESS',
            MaxResults=5
        )
        active_jobs = existing_jobs.get('MedicalScribeJobSummaries', [])
        if active_jobs:
            active_job = active_jobs[0]
            print(f"An active transcription job is in progress: {active_job['MedicalScribeJobName']}")
            return poll_transcription_job(active_job['MedicalScribeJobName'])
    except Exception as e:
        raise Exception(f"Error checking active transcription jobs: {e}")

    try:
        # Start a new transcription job
        transcribe_medical.start_medical_scribe_job(
            MedicalScribeJobName=job_name,
            Media={'MediaFileUri': audio_file_uri},
            OutputBucketName=BUCKET_NAME,
            DataAccessRoleArn=DATA_ACCESS_ROLE_ARN,
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2
            }
        )
        print(f"Started a new transcription job: {job_name}")
    except Exception as e:
        raise Exception(f"Error starting transcription job: {e}")

    return poll_transcription_job(job_name)


def poll_transcription_job(job_name):
    """
    Polls the transcription job status until it is completed or failed.
    """
    while True:
        try:
            response = transcribe_medical.get_medical_scribe_job(MedicalScribeJobName=job_name)
            status = response['MedicalScribeJob']['MedicalScribeJobStatus']
            if status == 'COMPLETED':
                print(f"Job '{job_name}' completed successfully.")
                return response['MedicalScribeJob']['MedicalScribeOutput']
            elif status == 'FAILED':
                raise Exception(f"Job '{job_name}' failed.")
            time.sleep(15)
        except Exception as e:
            raise Exception(f"Error checking job status: {e}")


@app.route('/audio-files', methods=['GET'])
def get_audio_files():
    """
    Returns the list of pre-defined audio files.
    """
    return jsonify(PREDEFINED_AUDIO_FILES)


@app.route('/start-transcription', methods=['POST'])
def start_transcription_route():
    """
    API endpoint to start transcription for a selected audio file.
    Returns the summarized text as plain text.
    """
    global transcription_summary
    data = request.json
    audio_url = data.get('audioUrl')
    if not audio_url:
        return "Audio URL is required.", 400

    job_name = f"medical_transcription_job_{int(time.time())}"
    try:
        medical_scribe_output = start_transcription(job_name, audio_url)
        summary_uri = medical_scribe_output['ClinicalDocumentUri']

        # Fetch and format summary into plain text
        transcription_summary = fetch_summary(summary_uri)
        return transcription_summary, 200  # Return plain text directly
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/question-ans', methods=['POST'])
def question_answer():
    """
    Flask API endpoint for question answering.
    """
    global transcription_summary
    if not transcription_summary:
        return jsonify({"error": "Transcription summary not available. Complete transcription first."}), 400

    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided."}), 400

    try:
        answer = ask_claude(question, transcription_summary)
        return jsonify({"question": question, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
