import boto3
import json
from jinja2 import Template

s3_client = boto3.client('s3')
transcribe = boto3.client('transcribe')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    output_bucket = "feedback-summarizer-output"
    
    try:
        response = s3_client.get_object(Bucket=input_bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        
        transcript = transcribe_audio(input_bucket, key)
        print(f"Transcript: {transcript}")
        
        summary = generate_summary(transcript)
        output_file_name = key.replace('.json', '-summary.json')
        
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_file_name,
            Body=json.dumps({"summary": summary}),
            ContentType='application/json'
        )
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error occurred: {e}")
        }

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully summarized feedback for {key} from bucket {input_bucket}.")
    }

def transcribe_audio(bucket_name, file_key):
    job_name = file_key.split('.')[0] + "-transcription"
    job_uri = f"s3://{bucket_name}/{file_key}"

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',  # Assuming the format is mp3
        LanguageCode='en-US'
    )
    
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Waiting for transcription...")
    
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        response = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_response = s3_client.get_object(Bucket=bucket_name, Key=response.split('/')[-1])
        transcript = json.loads(transcript_response['Body'].read().decode('utf-8'))
        return transcript['results']['transcripts'][0]['transcript']

def generate_summary(transcript):
    with open('prompt_template.txt', "r") as file:
        template_string = file.read()

    data = {
        'transcript': transcript
    }
    
    template = Template(template_string)
    prompt = template.render(data)
    
    kwargs = {
        "modelId": "amazon.titan-text-express-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 500,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
        )
    }
    
    response = bedrock_runtime.invoke_model(**kwargs)
    summary = json.loads(response.get('body').read()).get('results')[0].get('outputText')
    
    return summary
