# LPL Financial Call & Meeting Monitor

## Implementation Overview

This application implements the requirements specified in the context file for the LPL Hackathon 2026.

## Features Implemented

### 1. Navigation Structure
- **Header Navigation**: Clean navigation with Home, Meetings, Policies, Reports links
- **Functional Routes**: All navigation links route to their respective pages
- **Placeholder Pages**: Each route has a simple page with just the title

### 2. Home Page Upload Component
- **Single Upload Button**: "Upload Video" button as the main component
- **File Selection**: Accepts video files only (`accept="video/*"`)
- **S3 Upload Pipeline**: Implements the exact flow specified:
  1. User selects video file
  2. Frontend requests presigned URL from `/api/get-upload-url`
  3. Backend responds with `{ "uploadUrl": "<presigned_s3_url>" }`
  4. Frontend uploads directly to S3 using PUT request
  5. Success logged to console

### 3. Upload Pipeline Details
- **No Backend File Handling**: Video never sent to backend
- **Presigned URL**: Uses S3 presigned URLs for secure direct upload
- **Clean Implementation**: Minimal, readable React functional components

## File Structure

```
app/
├── page.tsx                    # Home page with upload component
├── meetings/page.tsx           # Meetings placeholder page
├── policies/page.tsx           # Policies placeholder page  
├── reports/page.tsx            # Reports placeholder page
├── dashboard/page.tsx          # Existing dashboard (kept)
└── api/
    └── get-upload-url/
        └── route.ts            # API endpoint for presigned URLs
```

## Key Components

### Navigation Component
- Reusable header with LPL branding
- Functional links to all required routes
- Clean, minimal styling

### VideoUpload Component
- File input with video-only acceptance
- Presigned URL request handling
- Direct S3 upload with PUT method
- Loading states and error handling
- Console logging for success/failure

### API Endpoint
- `/api/get-upload-url` POST endpoint
- Returns presigned S3 URL structure
- Includes commented example of real AWS implementation

## Usage

1. Navigate to the home page
2. Click "Upload Video" button
3. Select a video file
4. File uploads directly to S3 (mock implementation)
5. Check console for upload status

## Next Steps for Production

To make this production-ready:

1. **Configure AWS**: Set up actual S3 bucket and credentials
2. **Environment Variables**: Add AWS configuration to `.env`
3. **Error Handling**: Enhance error states and user feedback
4. **Security**: Implement proper authentication and authorization
5. **Monitoring**: Add logging and analytics for uploads

## Technical Notes

- Uses Next.js 14 App Router
- React functional components with hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Direct S3 upload pattern for scalability