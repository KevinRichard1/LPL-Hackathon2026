"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";

// Navigation component
function Navigation() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-navy-900 rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">LPL</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">LPL Financial</span>
          </div>
          
          <nav className="flex space-x-8">
            <Link href="/" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">
              Home
            </Link>
            <Link href="/meetings" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">
              Meetings
            </Link>
            <Link href="/policies" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">
              Policies
            </Link>
            <Link href="/reports" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">
              Reports
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

// Video upload component
function VideoUpload() {
  const [uploading, setUploading] = useState(false);

  const handleVideoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);

    try {
      // Step 1: Get presigned URL from backend
      const response = await fetch('/api/get-upload-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileName: file.name,
          fileType: file.type,
        }),
      });

      const { uploadUrl } = await response.json();

      // Step 2: Upload video directly to S3 using presigned URL
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type,
        },
        body: file,
      });

      if (uploadResponse.ok) {
        console.log('Video uploaded successfully to S3');
      } else {
        console.error('Upload failed:', uploadResponse.statusText);
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] border-2 border-dashed border-gray-300 rounded-lg p-8">
      <Upload className="w-12 h-12 text-gray-400 mb-4" />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Upload Video for Compliance Review
      </h3>
      <p className="text-gray-600 mb-6 text-center">
        Select a video file to analyze for compliance violations
      </p>
      
      <label htmlFor="video-upload">
        <Button 
          className="bg-copper-500 hover:bg-copper-600 text-white"
          disabled={uploading}
          asChild
        >
          <span>
            {uploading ? 'Uploading...' : 'Upload Video'}
          </span>
        </Button>
      </label>
      
      <input
        id="video-upload"
        type="file"
        accept="video/*"
        onChange={handleVideoUpload}
        className="hidden"
      />
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            LPL Financial Call & Meeting Monitor
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered compliance monitoring for advisor meetings and calls
          </p>
        </div>
        
        <VideoUpload />
      </main>
    </div>
  );
}
