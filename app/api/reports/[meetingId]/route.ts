import { NextRequest, NextResponse } from 'next/server';
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';
import { promises as fs } from 'fs';
import path from 'path';

const s3Client = new S3Client({
  region: process.env.AWS_REGION!,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

const MEETINGS_FILE = path.join(process.cwd(), 'data', 'meetings.json');

// Read meetings from JSON file
async function readMeetings() {
  try {
    const data = await fs.readFile(MEETINGS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return [];
  }
}

// GET - Fetch compliance report for a specific meeting
export async function GET(
  request: NextRequest,
  { params }: { params: { meetingId: string } }
) {
  try {
    const { meetingId } = params;
    
    // Find the meeting to get the original filename
    const meetings = await readMeetings();
    const meeting = meetings.find((m: any) => m.id === meetingId);
    
    if (!meeting) {
      return NextResponse.json(
        { error: 'Meeting not found' },
        { status: 404 }
      );
    }

    // Generate the expected report filename based on the original audio filename
    // The backend creates report files by replacing the audio extension with .json
    // and stores them in the audit/ subfolder of the reports bucket
    const originalFileName = meeting.fileName;
    const reportFileName = `audit/${originalFileName.replace(/\.(mp3|wav|m4a|flac|ogg)$/i, '.json')}`;
    
    try {
      // Fetch the report file from the reports S3 bucket
      const command = new GetObjectCommand({
        Bucket: process.env.S3_REPORTS_BUCKET_NAME!,
        Key: reportFileName,
      });
      
      const response = await s3Client.send(command);
      
      if (!response.Body) {
        throw new Error('No response body');
      }
      
      // Convert the stream to string
      const reportData = await response.Body.transformToString();
      const complianceReport = JSON.parse(reportData);
      
      return NextResponse.json({
        success: true,
        report: complianceReport,
        meeting: meeting
      });
      
    } catch (s3Error: any) {
      console.error('S3 Error:', s3Error);
      
      // If report not found in S3, return a "processing" status
      if (s3Error.name === 'NoSuchKey' || s3Error.Code === 'NoSuchKey') {
        return NextResponse.json({
          success: false,
          error: 'Report not ready',
          message: 'The compliance report is still being processed. Please try again in a few minutes.',
          meeting: meeting
        }, { status: 202 }); // 202 Accepted - processing
      }
      
      throw s3Error;
    }
    
  } catch (error) {
    console.error('Error fetching report:', error);
    return NextResponse.json(
      { error: 'Failed to fetch compliance report' },
      { status: 500 }
    );
  }
}