import boto3
import json
import os

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1') # Adjust region if needed
    
    # 1. Get the transcript file from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    print(f"Auditing file: {key} from bucket: {bucket}")
    
    # 2. Read the transcript text
    transcript_obj = s3.get_object(Bucket=bucket, Key=key)
    transcript_text = transcript_obj['Body'].read().decode('utf-8')
    
    # 3. The "Compliance Prompt" - This is your secret sauce
    prompt = f"""
    You are a Senior Compliance Auditor at LPL Financial. 
    Review the following transcript for:
    - Guaranteed returns (e.g., "I promise 20% gain")
    - Aggressive sentiment
    - Unauthorized financial advice
    
    Provide a JSON response with:
    - "severity": (Low/Medium/High)
    - "issues_found": list of specific flags
    - "summary": 2-sentence overview
    
    Transcript:
    {transcript_text}
    """
    
    # 4. Call Bedrock (Claude 3 / Haiku is fastest/cheapest for hackathons)
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
        response_body = json.loads(response.get('body').read())
        audit_result = response_body['content'][0]['text']
        
        # 5. Save the Audit Result to S3 (The "Analysis" Bucket)
        output_key = f"audits/{key.split('/')[-1].replace('.txt', '.json')}"
        s3.put_object(
            Bucket='transcripts-raw-lpl-26', # Save it back or to a new bucket
            Key=output_key,
            Body=audit_result
        )
        
        return {"status": "success", "audit_path": output_key}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}