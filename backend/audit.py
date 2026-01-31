import boto3
import json
import os
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client("s3")
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    # 1. Get S3 info
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    print(f"Auditing file: {key} from bucket: {bucket}")

    # 2. Read file from S3
    transcript_obj = s3.get_object(Bucket=bucket, Key=key)
    raw_body = transcript_obj["Body"].read().decode("utf-8")

    # 3. Extract transcript (Transcribe JSON OR raw text)
    try:
        parsed = json.loads(raw_body)
        transcript_text = parsed["results"]["transcripts"][0]["transcript"]
        print("Parsed Amazon Transcribe JSON")
    except (json.JSONDecodeError, KeyError, IndexError):
        transcript_text = raw_body
        print("Parsed raw text transcript")

    # 4. Compliance prompt (STRICT JSON)
    prompt = f"""
You are a Senior FINRA Compliance Auditor at LPL Financial.

Analyze the transcript below for compliance risks.

Detect and extract:
- Guaranteed or promissory returns
- Aggressive or coercive language
- Misleading or unauthorized financial advice

Return ONLY a valid JSON object with this exact schema:
{{
  "severity": "Low | Medium | High",
  "issues_found": ["string", "string"], 
  "summary": "2 sentence overview"
}}

Transcript:
{transcript_text}
"""

    # 5. Bedrock request body
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    try:
        # 6. Invoke Bedrock (with guardrails)
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body,
            guardrailIdentifier=os.environ.get("GUARDRAIL_ID"),
            guardrailVersion=os.environ.get("GUARDRAIL_VERSION", "DRAFT")
        )

        response_body = json.loads(response["body"].read())
        raw_model_output = response_body["content"][0]["text"]

        # 7. Parse Claude output into JSON
        try:
            audit_json = json.loads(raw_model_output)
        except json.JSONDecodeError:
            audit_json = {
                "severity": "Unknown",
                "issues": [],
                "summary": "Model output could not be parsed.",
                "raw_output": raw_model_output
            }

        # 8. Enrich audit metadata
        audit_json["source_file"] = key
        audit_json["model"] = "claude-3-haiku"
        audit_json["processed_at"] = datetime.utcnow().isoformat() + "Z"
        audit_json["request_id"] = context.aws_request_id
        audit_json["guardrails_enabled"] = bool(os.environ.get("GUARDRAIL_ID"))

        # 9. Save audit JSON to S3
        output_key = f"audits/{key.split('/')[-1].replace('.json', '').replace('.txt', '')}_audit.json"

        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(audit_json, indent=2),
            ContentType="application/json"
        )

        return {
            "status": "success",
            "audit_file": output_key
        }

    except Exception as e:
        print(f"Audit failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
