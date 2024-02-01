# FeedbackSummarizer

## Overview
This project is an application to transcribe and summarize product reviews using AWS Bedrock and Anthropic Claude. It utilizes AWS Transcribe for speech-to-text conversion and Jinja2 for generating brief and insightful summaries.

## Architecture
1. An S3 event triggers the Lambda function.
2. The Lambda function reads the audio file from the input S3 bucket.
3. AWS Transcribe converts the audio to text.
4. The function generates a summary using AWS Bedrock.
5. The summary is stored in the output S3 bucket.

## Files
- `lambda_function.py`: The main code for the Lambda function.
- `requirements.txt`: Lists the dependencies.
- `prompt_template.txt`: Template for generating prompts.

## Setup
1. Deploy the Lambda function.
2. Ensure the required permissions for S3, Transcribe, and Bedrock are configured.
3. Upload audio files to the input S3 bucket to trigger the function.

## Running Locally
To test the function locally:
1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Run the function with a sample event:
    ```bash
    python lambda_function.py
    ```

## Example
Input audio file triggers the Lambda function which generates a summary of the product review.
