"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

// Mock data for upcoming meetings (keeping as static for now)
const upcomingMeetings = [
  {
    id: "1",
    date: "2026-02-03",
    time: "10:00 AM",
    advisors: "Sarah Johnson, Mike Chen",
    meetingUrl: "https://zoom.us/j/123456789",
    passcode: "ABC123",
    notes: "Quarterly portfolio review with high-net-worth client"
  },
  {
    id: "2", 
    date: "2026-02-03",
    time: "2:30 PM",
    advisors: "David Rodriguez",
    meetingUrl: "https://teams.microsoft.com/l/meetup-join/...",
    passcode: "DEF456",
    notes: "Retirement planning consultation"
  },
  {
    id: "3",
    date: "2026-02-04",
    time: "9:15 AM", 
    advisors: "Lisa Park, Tom Wilson",
    meetingUrl: "https://webex.com/meet/advisor123",
    passcode: "GHI789",
    notes: "Estate planning discussion"
  },
  {
    id: "4",
    date: "2026-02-05",
    time: "11:00 AM",
    advisors: "Jennifer Adams",
    meetingUrl: "https://zoom.us/j/987654321",
    passcode: "JKL012",
    notes: "New client onboarding session"
  }
];

type PastMeeting = {
  id: string;
  date: string;
  time: string;
  advisors: string;
  meetingUrl: string;
  status: string;
  fileName?: string;
  uploadTimestamp?: string;
};

export default function MeetingsPage() {
  const [pastMeetings, setPastMeetings] = useState<PastMeeting[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch meetings from API
  useEffect(() => {
    async function fetchMeetings() {
      try {
        const response = await fetch('/api/meetings');
        if (response.ok) {
          const data = await response.json();
          setPastMeetings(data.meetings);
        } else {
          console.error('Failed to fetch meetings');
        }
      } catch (error) {
        console.error('Error fetching meetings:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchMeetings();
    
    // Refresh meetings every 30 seconds to catch new uploads
    const interval = setInterval(fetchMeetings, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
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
              <Link href="/meetings" className="text-gray-900 px-3 py-2 text-sm font-medium border-b-2 border-copper-500">
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Meetings</h1>
        
        {/* Upcoming Meetings Table */}
        <div className="mb-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Meetings</h2>
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Advisor(s)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meeting URL
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Passcode
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meeting Notes
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {upcomingMeetings.map((meeting) => (
                  <tr key={meeting.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>
                        <div className="font-medium">{meeting.date}</div>
                        <div className="text-gray-500">{meeting.time}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {meeting.advisors}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <a 
                        href={meeting.meetingUrl}
                        className="text-copper-500 hover:text-copper-600 underline truncate block max-w-xs"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {meeting.meetingUrl}
                      </a>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                      {meeting.passcode}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs truncate">
                        {meeting.notes}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Past Meetings Table */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Past Meetings</h2>
            <Button 
              onClick={() => window.location.reload()}
              variant="outline"
              className="text-sm"
            >
              Refresh
            </Button>
          </div>
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Advisor(s)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meeting URL
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                      Loading meetings...
                    </td>
                  </tr>
                ) : pastMeetings.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                      No past meetings found. Upload an audio file to create your first meeting entry.
                    </td>
                  </tr>
                ) : (
                  pastMeetings.map((meeting) => (
                    <tr key={meeting.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>
                          <div className="font-medium">{meeting.date}</div>
                          <div className="text-gray-500">{meeting.time}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {meeting.advisors}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <span className="text-gray-600 italic">
                          {meeting.meetingUrl}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          {meeting.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Button 
                          asChild
                          className="bg-copper-500 hover:bg-copper-600 text-white text-xs px-3 py-1"
                        >
                          <Link href={`/reports/${meeting.id}`}>
                            View Report
                          </Link>
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}