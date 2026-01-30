# AWS S3 Setup Guide

## Step 1: Configure Your Environment Variables

1. Open the `.env.local` file in your project root
2. Replace the placeholder values with your actual AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_REGION=your_bucket_region
S3_BUCKET_NAME=your_actual_bucket_name
```

## Step 2: Get Your AWS Credentials

You'll need these 4 pieces of information:

### 1. AWS Access Key ID & Secret Access Key
- Go to AWS Console → IAM → Users
- Select your user → Security credentials tab
- Create access key if you don't have one
- **Important**: Save both the Access Key ID and Secret Access Key

### 2. AWS Region
- This is where your S3 bucket is located
- Common regions: `us-east-1`, `us-west-2`, `eu-west-1`
- Check your S3 bucket location in AWS Console

### 3. S3 Bucket Name
- Go to AWS Console → S3
- Find your bucket name (the one you created with your teammate)

## Step 3: Set Up S3 Bucket Permissions

Your S3 bucket needs proper permissions. Add this bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowPresignedUploads",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_USERNAME"
            },
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
        }
    ]
}
```

## Step 4: Test the Upload

1. Save your `.env.local` file with real values
2. Restart your development server: `npm run dev`
3. Go to the home page
4. Try uploading a video file
5. Check the browser console for success/error messages
6. Verify the file appears in your S3 bucket

## Step 5: Enable CORS (if needed)

If you get CORS errors, add this CORS configuration to your S3 bucket:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["PUT", "POST"],
        "AllowedOrigins": ["http://localhost:3000", "https://your-domain.com"],
        "ExposeHeaders": []
    }
]
```

## Example .env.local File

```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=lpl-hackathon-videos-2026
```

## Troubleshooting

### Common Issues:

1. **"AWS configuration missing"**
   - Check that all 4 environment variables are set
   - Restart your dev server after changing .env.local

2. **"Access Denied"**
   - Verify your AWS credentials are correct
   - Check S3 bucket permissions
   - Ensure your IAM user has S3 permissions

3. **CORS errors**
   - Add CORS configuration to your S3 bucket
   - Include your localhost URL in allowed origins

4. **"Bucket not found"**
   - Double-check your bucket name spelling
   - Verify the bucket exists in the specified region

## Next Steps: Adding Transcription

Once uploads work, you can add transcription by:

1. Creating a Lambda function triggered by S3 uploads
2. Using AWS Transcribe service
3. Storing transcription results back in S3 or a database
4. Updating your app to show transcription status

## Security Notes

- Never commit `.env.local` to git (it's already in .gitignore)
- Use IAM roles with minimal permissions
- Consider using temporary credentials for production
- Rotate access keys regularly