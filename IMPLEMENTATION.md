# LPL Financial Call & Meeting Monitor

## Implementation Overview

This application implements the requirements specified in the context file for the LPL Hackathon 2026.

## Features Implemented

### 1. Navigation Structure
- **Header Navigation**: Clean navigation with Home, Meetings, Policies, Reports links
- **Functional Routes**: All navigation links route to their respective pages
- **Active State**: Current page highlighted in navigation
- **Consistent Layout**: All pages share the same navigation header

### 2. Home Page Upload Component
- **Single Upload Button**: "Upload Video" button as the main component
- **File Selection**: Accepts video files only (`accept="video/*"`)
- **S3 Upload Pipeline**: Implements the exact flow specified:
  1. User selects video file
  2. Frontend requests presigned URL from `/api/get-upload-url`
  3. Backend responds with `{ "uploadUrl": "<presigned_s3_url>" }`
  4. Frontend uploads directly to S3 using PUT request
  5. Success logged to console

### 3. Meetings Page
- **Upcoming Meetings Table**: Professional table layout with columns:
  - Date (with time)
  - Advisor(s)
  - Meeting URL (clickable links)
  - Passcode (monospace font)
  - Meeting Notes
- **Past Meetings Table**: Table layout with columns:
  - Date (with time)
  - Advisor(s) 
  - Meeting URL (clickable links)
  - Status (badge styling)
  - Action (View Report button)
- **Mock Data**: Static data for demonstration
- **Professional Formatting**: Clean table design with hover states

### 4. Dynamic Reports Page
- **Route**: `/reports/[meetingId]` for individual meeting reports
- **Meeting ID Display**: Shows the specific meeting ID in header
- **Compliance Information**:
  - Risk Level (HIGH/MEDIUM/LOW with color coding and icons)
  - Flagged Phrases (highlighted compliance violations)
  - Compliance Notes (detailed analysis and recommendations)
- **Meeting Overview**: Date, advisor(s), duration
- **Mock Data**: Different compliance scenarios based on meeting ID
- **Professional Layout**: Card-based design with clear sections

### 5. Upload Pipeline Details
- **No Backend File Handling**: Video never sent to backend
- **Presigned URL**: Uses S3 presigned URLs for secure direct upload
- **Clean Implementation**: Minimal, readable React functional components

## File Structure

```
app/
├── page.tsx                    # Home page with upload component
├── meetings/page.tsx           # Meetings page with tables
├── policies/page.tsx           # Policies placeholder page  
├── reports/
│   ├── page.tsx               # Reports main page
│   └── [meetingId]/
│       └── page.tsx           # Dynamic report page
├── dashboard/page.tsx          # Existing dashboard (kept)
└── api/
    └── get-upload-url/
        └── route.ts            # API endpoint for presigned URLs
```

## Key Components

### Navigation Component
- Reusable header with LPL branding
- Functional links to all required routes
- Active state highlighting
- Clean, minimal styling

### VideoUpload Component
- File input with video-only acceptance
- Presigned URL request handling
- Direct S3 upload with PUT method
- Loading states and error handling
- Console logging for success/failure

### Meetings Tables
- Professional table layouts
- Responsive design
- Hover states for better UX
- Clickable meeting URLs
- Action buttons routing to reports

### Dynamic Report Component
- Meeting ID parameter handling
- Risk level visualization with colors and icons
- Flagged phrases highlighting
- Comprehensive compliance analysis
- Back navigation to meetings

### API Endpoint
- `/api/get-upload-url` POST endpoint
- Returns presigned S3 URL structure
- Includes commented example of real AWS implementation

## Mock Data Examples

### Meeting Data
- 4 upcoming meetings with full details
- 4 past meetings with completion status
- Realistic advisor names and meeting URLs
- Various meeting types (portfolio review, planning, etc.)

### Compliance Data
- Different risk levels (HIGH, MEDIUM, LOW)
- Sample flagged phrases for each risk level
- Contextual compliance notes and recommendations
- Automated action suggestions based on risk level

## Usage

1. **Home**: Upload videos for compliance analysis
2. **Meetings**: View upcoming and past meetings in table format
3. **Reports**: Click "View Report" from past meetings to see compliance analysis
4. **Navigation**: Use header links to navigate between sections

## Next Steps for Production

To make this production-ready:

1. **Configure AWS**: Set up actual S3 bucket and credentials
2. **Database Integration**: Replace mock data with real database
3. **Authentication**: Implement user authentication and authorization
4. **Real-time Updates**: Add WebSocket connections for live meeting monitoring
5. **Advanced Analytics**: Integrate with actual compliance analysis AI
6. **Audit Trail**: Add comprehensive logging and audit capabilities

## Technical Notes

- Uses Next.js 14 App Router with dynamic routes
- React functional components with hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Professional table layouts
- Color-coded risk indicators
- Direct S3 upload pattern for scalability
- Mock data structure ready for database integration