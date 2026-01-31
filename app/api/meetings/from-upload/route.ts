import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const MEETINGS_FILE = path.join(process.cwd(), 'data', 'meetings.json');

// Ensure the data directory exists
async function ensureDataDirectory() {
  const dataDir = path.dirname(MEETINGS_FILE);
  try {
    await fs.access(dataDir);
  } catch {
    await fs.mkdir(dataDir, { recursive: true });
  }
}

// Read meetings from JSON file
async function readMeetings() {
  try {
    await ensureDataDirectory();
    const data = await fs.readFile(MEETINGS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    // If file doesn't exist, return empty array
    return [];
  }
}

// Write meetings to JSON file
async function writeMeetings(meetings: any[]) {
  await ensureDataDirectory();
  await fs.writeFile(MEETINGS_FILE, JSON.stringify(meetings, null, 2));
}

// POST - Create meeting from successful upload
export async function POST(request: NextRequest) {
  try {
    const { fileName } = await request.json();
    
    if (!fileName) {
      return NextResponse.json(
        { error: 'fileName is required' },
        { status: 400 }
      );
    }
    
    const meetings = await readMeetings();
    
    // Create new meeting entry
    const newMeeting = {
      id: `meeting-${Date.now()}`,
      date: new Date().toISOString().split('T')[0], // YYYY-MM-DD format
      time: new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      }),
      advisors: "Client Meeting", // Placeholder as requested
      meetingUrl: "Pre-recorded audio",
      status: "Completed",
      fileName: fileName,
      uploadTimestamp: new Date().toISOString()
    };
    
    // Add to beginning of array (most recent first)
    meetings.unshift(newMeeting);
    
    await writeMeetings(meetings);
    
    console.log('Meeting entry created for uploaded file:', fileName);
    
    return NextResponse.json({ 
      success: true, 
      meeting: newMeeting 
    });
    
  } catch (error) {
    console.error('Error creating meeting from upload:', error);
    return NextResponse.json(
      { error: 'Failed to create meeting entry' },
      { status: 500 }
    );
  }
}