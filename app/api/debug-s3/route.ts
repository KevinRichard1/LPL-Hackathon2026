import { NextResponse } from 'next/server';
import { S3Client, ListObjectsV2Command } from '@aws-sdk/client-s3';

const s3Client = new S3Client({
  region: process.env.AWS_REGION!,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function GET() {
  try {
    // Check environment variables
    const bucketName = process.env.S3_REPORTS_BUCKET_NAME;
    const region = process.env.AWS_REGION;
    const accessKeyId = process.env.AWS_ACCESS_KEY_ID;
    
    const envCheck = {
      bucketName: bucketName || 'MISSING',
      region: region || 'MISSING',
      accessKeyId: accessKeyId ? 'SET' : 'MISSING'
    };
    
    if (!bucketName) {
      return NextResponse.json({
        error: 'Missing S3_REPORTS_BUCKET_NAME',
        env: envCheck
      });
    }
    
    // List objects in the audits folder
    const command = new ListObjectsV2Command({
      Bucket: bucketName,
      Prefix: 'audits/',
      MaxKeys: 20
    });
    
    const response = await s3Client.send(command);
    
    return NextResponse.json({
      success: true,
      env: envCheck,
      bucket: bucketName,
      objects: response.Contents?.map(obj => ({
        key: obj.Key,
        size: obj.Size,
        lastModified: obj.LastModified
      })) || []
    });
    
  } catch (error: any) {
    return NextResponse.json({
      error: 'S3 Error',
      message: error.message,
      name: error.name,
      code: error.Code
    }, { status: 500 });
  }
}