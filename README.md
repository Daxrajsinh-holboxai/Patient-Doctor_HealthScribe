# AWS Healthscribe Doctor-Patient Transcription

This project is a Flask-based application that uses **AWS HealthScribe** and other AWS services to process medical conversations between doctors and patients. It converts audio files into structured text transcriptions and clinical insights, enabling efficient documentation and analysis.

---

## Features

- **AWS HealthScribe Integration**:
  - Automatically transcribes doctor-patient conversations.
  - Extracts clinical insights, including symptoms and diagnoses.
  - Saves structured data as a JSON file.

- **Flask API**:
  - Exposes endpoints for querying the transcriptions and summaries.
  - Allows question-answering based on transcription summaries using **Claude** (via AWS Bedrock).

- **AWS Services**:
  - **Amazon S3**: Stores audio files and transcription outputs.
  - **AWS Bedrock**: Queries foundation models like Claude for Q&A.
  - **Amazon Transcribe Medical**: Converts audio to text with speaker labels.

---

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [License](#license)

---

## Getting Started

### Prerequisites
1. Python 3.7 or above.
2. AWS account with the following services enabled:
   - Amazon S3
   - Amazon Transcribe Medical
   - AWS Bedrock
3. Install **Git** and **AWS CLI**.

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/Healthscribe_Doctor-Patient.git
   cd Healthscribe_Doctor-Patient
   
2. Create and activate a virtual environment::
   ```bash
   python3 -m venv my_env
   source my_env/bin/activate

3. Configure AWS CLI with your credentials:
   ```bash
   aws configure

4. Clone this repository:
   ```bash
   git clone https://github.com/your-username/Healthscribe_Doctor-Patient.git
   cd Healthscribe_Doctor-Patient

5. Set up a .env file with your AWS configurations:
   ```bash
   AWS_REGION=your-region
   BUCKET_NAME=your-s3-bucket
   DATA_ACCESS_ROLE_ARN=your-iam-role-arn
   AUDIO_FILE_URL=s3://your-bucket/audio-file.mp3
   BEDROCK_MODEL_ID=anthropic.claude-3

### Usage
- **Run the Application**:
  - Start the Flask app:
    ```bash
    python app.py

## Upload an Audio File

1. **Upload an audio file to your S3 bucket**:
   - Ensure the audio file is in the correct format (e.g., MP3, WAV).
   - Upload the file to the S3 bucket specified in your `.env` file.

2. **Set the file's public URL**:
   - Update your `.env` file with the public URL of the uploaded audio file:
     ```plaintext
     AUDIO_FILE_URL=https://your-bucket.s3.your-region.amazonaws.com/your-audio-file.mp3
     ```

---

## Process the Transcription

The application processes the transcription in the following steps:
1. **Start an AWS HealthScribe Job**:
   - It uses the **AWS Transcribe Medical Scribe** service to transcribe the uploaded audio file.

2. **Poll the Transcription Job**:
   - The app waits for the transcription job to complete.

3. **Fetch the Transcription Summary**:
   - Once the job is complete, the transcription output (e.g., `summary.json`) is fetched.

4. **Save the Summary to S3**:
   - The transcription summary is stored in the specified S3 bucket.

---

## Question-Answering with Claude

- **Ask Questions About the Transcription**:
  - Use the `/question-ans` API endpoint to submit questions based on the transcription summary.
  - This functionality is powered by **Claude** (via AWS Bedrock).

---

## Endpoints

### **POST /question-ans**
- **Description**: Submit a question to query insights from the transcription summary.

#### **Request Example**:
```json
{
    "question": "What symptoms did the patient describe?"
}
```
#### **Response Example**:
```json
{
    "question": "What symptoms did the patient describe?",
    "answer": "The patient described headache and dizziness."
}
