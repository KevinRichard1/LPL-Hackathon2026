"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, CheckCircle, XCircle, Loader2, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

type ComplianceReport = {
  severity: "Low" | "Medium" | "High";
  issues_found: string[];
  summary: string;
  source_file: string;
  model: string;
  processed_at: string;
  request_id: string;
  guardrails_enabled: boolean;
};

type Meeting = {
  id: string;
  date: string;
  time: string;
  advisors: string;
  meetingUrl: string;
  status: string;
  fileName: string;
  uploadTimestamp: string;
};

const getRiskLevelColor = (severity: string) => {
  switch (severity) {
    case "High":
      return "bg-red-100 text-red-800 border-red-200";
    case "Medium": 
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    case "Low":
      return "bg-green-100 text-green-800 border-green-200";
    default:
      return "bg-gray-100 text-gray-800 border-gray-200";
  }
};

const getRiskIcon = (severity: string) => {
  switch (severity) {
    case "High":
      return <XCircle className="w-5 h-5 text-red-600" />;
    case "Medium":
      return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    case "Low":
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    default:
      return <AlertTriangle className="w-5 h-5 text-gray-600" />;
  }
};

export default function ReportPage({ params }: { params: { meetingId: string } }) {
  const { meetingId } = params;
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/reports/${meetingId}`);
      const data = await response.json();
      
      if (response.ok && data.success) {
        setReport(data.report);
        setMeeting(data.meeting);
        setIsProcessing(false);
      } else if (response.status === 202) {
        // Report is still processing
        setMeeting(data.meeting);
        setIsProcessing(true);
        setError(data.message);
      } else {
        setError(data.error || 'Failed to fetch report');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Error fetching report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [meetingId]);

  // Auto-refresh if report is still processing
  useEffect(() => {
    if (isProcessing) {
      const interval = setInterval(() => {
        fetchReport();
      }, 10000); // Check every 10 seconds
      
      return () => clearInterval(interval);
    }
  }, [isProcessing]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-gray-600" />
          <p className="text-gray-600">Loading compliance report...</p>
        </div>
      </div>
    );
  }

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
              <Link href="/meetings" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                Meetings
              </Link>
              <Link href="/policies" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">
                Policies
              </Link>
              <Link href="/reports" className="text-gray-900 px-3 py-2 text-sm font-medium border-b-2 border-copper-500">
                Reports
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Compliance Report</h1>
              <p className="text-gray-600 mt-1">Meeting ID: {meetingId}</p>
              {meeting && (
                <p className="text-sm text-gray-500 mt-1">
                  Source File: {meeting.fileName}
                </p>
              )}
            </div>
            <div className="flex items-center gap-3">
              {isProcessing && (
                <Button 
                  onClick={fetchReport}
                  variant="outline"
                  className="text-sm"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              )}
              <Link 
                href="/meetings"
                className="text-copper-500 hover:text-copper-600 text-sm font-medium"
              >
                ← Back to Meetings
              </Link>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && !isProcessing && (
          <Card className="mb-6 border-red-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-2 text-red-600">
                <XCircle className="w-5 h-5" />
                <p className="font-medium">Error Loading Report</p>
              </div>
              <p className="text-red-700 mt-2">{error}</p>
              <Button 
                onClick={fetchReport}
                className="mt-4"
                variant="outline"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Processing State */}
        {isProcessing && (
          <Card className="mb-6 border-yellow-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-2 text-yellow-600">
                <Loader2 className="w-5 h-5 animate-spin" />
                <p className="font-medium">Report Processing</p>
              </div>
              <p className="text-yellow-700 mt-2">
                The compliance analysis is still being processed. This page will automatically refresh every 10 seconds.
              </p>
              {meeting && (
                <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>File:</strong> {meeting.fileName}<br />
                    <strong>Uploaded:</strong> {new Date(meeting.uploadTimestamp).toLocaleString()}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Report Content */}
        {report && meeting && (
          <>
            {/* Meeting Overview */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">Meeting Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Date</p>
                    <p className="text-gray-900">{meeting.date}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Advisor(s)</p>
                    <p className="text-gray-900">{meeting.advisors}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Processed At</p>
                    <p className="text-gray-900">
                      {new Date(report.processed_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Risk Level */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  {getRiskIcon(report.severity)}
                  Compliance Risk Level
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Badge 
                  variant="outline" 
                  className={`text-lg px-4 py-2 font-semibold ${getRiskLevelColor(report.severity)}`}
                >
                  {report.severity.toUpperCase()} RISK
                </Badge>
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-500">Analysis Model</p>
                    <p className="text-gray-900">{report.model}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-500">Guardrails Status</p>
                    <p className="text-gray-900">
                      {report.guardrails_enabled ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Issues Found */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">Issues Found</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {report.issues_found.length > 0 ? (
                    report.issues_found.map((issue: string, index: number) => (
                      <div 
                        key={index}
                        className="p-4 bg-red-50 border border-red-200 rounded-lg"
                      >
                        <div className="flex items-start gap-2">
                          <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-red-800 font-medium text-sm">Issue #{index + 1}</p>
                            <p className="text-red-700 mt-1">{issue}</p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <p className="text-green-800">No compliance violations detected in this meeting.</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Compliance Summary */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">Compliance Analysis Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-800 leading-relaxed">
                    {report.summary}
                  </p>
                </div>
                
                {/* Additional Actions */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-500 mb-2">Recommended Actions:</p>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {report.severity === "High" && (
                      <>
                        <li>• Immediate supervisor notification required</li>
                        <li>• Client corrective disclosure recommended</li>
                        <li>• Mandatory compliance training scheduled</li>
                      </>
                    )}
                    {report.severity === "Medium" && (
                      <>
                        <li>• Advisor coaching session recommended</li>
                        <li>• Review compliance guidelines for flagged areas</li>
                        <li>• Monitor future meetings closely</li>
                      </>
                    )}
                    {report.severity === "Low" && (
                      <>
                        <li>• Continue current compliance practices</li>
                        <li>• No immediate action required</li>
                        <li>• Regular monitoring continues</li>
                      </>
                    )}
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Technical Details */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Technical Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-500">Request ID</p>
                    <p className="text-gray-900 font-mono text-xs">{report.request_id}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-500">Source File</p>
                    <p className="text-gray-900">{report.source_file}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}