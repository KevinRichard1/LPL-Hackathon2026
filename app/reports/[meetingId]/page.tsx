import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, CheckCircle, XCircle } from "lucide-react";

// Mock compliance data based on meeting ID
const getComplianceData = (meetingId: string) => {
  const mockData: Record<string, any> = {
    "past-1": {
      riskLevel: "LOW",
      flaggedPhrases: [
        "Based on historical performance, this strategy has shown consistent results."
      ],
      complianceNotes: "Meeting conducted within compliance guidelines. Minor language adjustment recommended for future discussions.",
      advisorName: "Sarah Johnson",
      meetingDate: "2026-01-29",
      duration: "45 minutes"
    },
    "past-2": {
      riskLevel: "HIGH", 
      flaggedPhrases: [
        "I can guarantee you'll see at least 15% returns this year",
        "This investment is completely risk-free",
        "Let's discuss the details over WhatsApp later"
      ],
      complianceNotes: "URGENT: Multiple compliance violations detected. Immediate corrective action required. Client follow-up disclosure sent automatically.",
      advisorName: "Mike Chen, David Rodriguez",
      meetingDate: "2026-01-28",
      duration: "62 minutes"
    },
    "past-3": {
      riskLevel: "MEDIUM",
      flaggedPhrases: [
        "This product always outperforms the market",
        "You won't find a better deal anywhere else"
      ],
      complianceNotes: "Moderate risk language detected. Advisor training recommended on performance claims and competitive statements.",
      advisorName: "Lisa Park", 
      meetingDate: "2026-01-27",
      duration: "38 minutes"
    },
    "past-4": {
      riskLevel: "LOW",
      flaggedPhrases: [
        "Our platform is designed to help optimize your portfolio"
      ],
      complianceNotes: "Compliant meeting overall. Language used was appropriate and within guidelines.",
      advisorName: "Tom Wilson, Jennifer Adams",
      meetingDate: "2026-01-26", 
      duration: "52 minutes"
    }
  };

  return mockData[meetingId] || {
    riskLevel: "MEDIUM",
    flaggedPhrases: ["Sample flagged phrase for unknown meeting"],
    complianceNotes: "Compliance analysis not available for this meeting ID.",
    advisorName: "Unknown Advisor",
    meetingDate: "Unknown Date",
    duration: "Unknown Duration"
  };
};

const getRiskLevelColor = (riskLevel: string) => {
  switch (riskLevel) {
    case "HIGH":
      return "bg-red-100 text-red-800 border-red-200";
    case "MEDIUM": 
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    case "LOW":
      return "bg-green-100 text-green-800 border-green-200";
    default:
      return "bg-gray-100 text-gray-800 border-gray-200";
  }
};

const getRiskIcon = (riskLevel: string) => {
  switch (riskLevel) {
    case "HIGH":
      return <XCircle className="w-5 h-5 text-red-600" />;
    case "MEDIUM":
      return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    case "LOW":
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    default:
      return <AlertTriangle className="w-5 h-5 text-gray-600" />;
  }
};

export default function ReportPage({ params }: { params: { meetingId: string } }) {
  const { meetingId } = params;
  const complianceData = getComplianceData(meetingId);

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
            </div>
            <Link 
              href="/meetings"
              className="text-copper-500 hover:text-copper-600 text-sm font-medium"
            >
              ← Back to Meetings
            </Link>
          </div>
        </div>

        {/* Meeting Overview */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Meeting Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Date</p>
                <p className="text-gray-900">{complianceData.meetingDate}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Advisor(s)</p>
                <p className="text-gray-900">{complianceData.advisorName}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Duration</p>
                <p className="text-gray-900">{complianceData.duration}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Level */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              {getRiskIcon(complianceData.riskLevel)}
              Compliance Risk Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge 
              variant="outline" 
              className={`text-lg px-4 py-2 font-semibold ${getRiskLevelColor(complianceData.riskLevel)}`}
            >
              {complianceData.riskLevel} RISK
            </Badge>
          </CardContent>
        </Card>

        {/* Flagged Phrases */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Flagged Phrases</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {complianceData.flaggedPhrases.map((phrase: string, index: number) => (
                <div 
                  key={index}
                  className="p-4 bg-red-50 border border-red-200 rounded-lg"
                >
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-red-800 font-medium text-sm">Compliance Violation #{index + 1}</p>
                      <p className="text-red-700 mt-1">"{phrase}"</p>
                    </div>
                  </div>
                </div>
              ))}
              {complianceData.flaggedPhrases.length === 0 && (
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

        {/* Compliance Notes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Compliance Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <p className="text-gray-800 leading-relaxed">
                {complianceData.complianceNotes}
              </p>
            </div>
            
            {/* Additional Actions */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-500 mb-2">Recommended Actions:</p>
              <ul className="text-sm text-gray-700 space-y-1">
                {complianceData.riskLevel === "HIGH" && (
                  <>
                    <li>• Immediate supervisor notification sent</li>
                    <li>• Client corrective disclosure email dispatched</li>
                    <li>• Mandatory compliance training scheduled</li>
                  </>
                )}
                {complianceData.riskLevel === "MEDIUM" && (
                  <>
                    <li>• Advisor coaching session recommended</li>
                    <li>• Review compliance guidelines for performance claims</li>
                  </>
                )}
                {complianceData.riskLevel === "LOW" && (
                  <>
                    <li>• Continue current compliance practices</li>
                    <li>• No immediate action required</li>
                  </>
                )}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}