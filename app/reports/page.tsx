import Link from "next/link";

export default function ReportsPage() {
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold text-gray-900 text-center">
          Reports
        </h1>
        <p className="text-center text-gray-600 mt-4">
          Access compliance reports from the meetings page
        </p>
      </div>
    </div>
  );
}