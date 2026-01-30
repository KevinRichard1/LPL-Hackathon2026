import { NextRequest, NextResponse } from 'next/server';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

// Initialize S3 client
const s3Client = new S3Client({
  region: process.env.AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function POST(request: NextRequest) {
  try {
    const { fileName, fileType } = await request.json();

    // Validate required environment variables
    if (!process.env.AWS_ACCESS_KEY_ID || !process.env.AWS_SECRET_ACCESS_KEY || !process.env.S3_BUCKET_NAME) {
      console.error('Missing AWS configuration. Please check environment variables.');
      return NextResponse.json(
        { error: 'AWS configuration missing' },
        { status: 500 }
      );
    }

    // Generate unique file name with timestamp
    const uniqueFileName = `audio/${Date.now()}-${fileName}`;

    // Create the S3 PutObject command
    const command = new PutObjectCommand({
      Bucket: process.env.S3_BUCKET_NAME,
      Key: uniqueFileName,
      ContentType: fileType,
      // Add metadata for audio files
      Metadata: {
        'original-name': fileName,
        'upload-type': 'compliance-audio',
        'upload-timestamp': new Date().toISOString()
      }
    });

    // Generate presigned URL (expires in 1 hour)
    const uploadUrl = await getSignedUrl(s3Client, command, { 
      expiresIn: 3600 
    });

    console.log('Generated presigned URL for:', uniqueFileName);

    return NextResponse.json({ 
      uploadUrl,
      fileName: uniqueFileName 
    });

  } catch (error) {
    console.error('Error generating upload URL:', error);
    return NextResponse.json(
      { error: 'Failed to generate upload URL' },
      { status: 500 }
    );
  }
}