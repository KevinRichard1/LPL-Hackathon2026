"use client";

import * as React from "react";
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Bell,
  CheckCircle2,
  ChevronDown,
  Download,
  FileText,
  Flag,
  Moon,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Sun,
  User,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

type AlertItem = {
  id: string;
  title: string;
  meeting: string;
  severity: "Low" | "Medium" | "High";
  category: string;
  time: string;
  snippet: string;
  recommendation: string;
  transcript: string;
  confidence: string;
};

type MeetingItem = {
  id: string;
  name: string;
  status: "Listening" | "Speaking" | "Completed";
  duration: string;
  attendees: string;
  advisor: string;
};

type KPIItem = {
  id: string;
  label: string;
  value: string;
  trend: string;
  direction: "up" | "down";
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
};

const alerts: AlertItem[] = [
  {
    id: "alert-1421",
    title: "Potential promissory language",
    meeting: "Quarterly Portfolio Review",
    severity: "High",
    category: "Performance Guarantees",
    time: "Today, 10:42 AM",
    snippet:
      "We can guarantee a 12% return if we rebalance into the new strategy.",
    recommendation:
      "We can discuss historical performance and risk factors, but future returns are not guaranteed.",
    transcript:
      "We can guarantee a 12% return if we rebalance into the new strategy. The client should feel confident about the outcome based on prior results.",
    confidence: "96% confidence",
  },
  {
    id: "alert-1533",
    title: "Missing risk disclosure",
    meeting: "Retirement Planning Call",
    severity: "Medium",
    category: "Risk Disclosure",
    time: "Yesterday, 4:05 PM",
    snippet:
      "This product is safe and suitable for your retirement timeline.",
    recommendation:
      "This product has specific risks and may be suitable depending on your objectives and risk tolerance.",
    transcript:
      "This product is safe and suitable for your retirement timeline. The allocation is aligned with the strategy we discussed.",
    confidence: "88% confidence",
  },
  {
    id: "alert-1677",
    title: "Unverified product claim",
    meeting: "New Client Onboarding",
    severity: "Low",
    category: "Marketing Claims",
    time: "Jan 27, 2:15 PM",
    snippet: "Our platform always outperforms the market.",
    recommendation:
      "Our platform is designed to improve outcomes, but performance can vary based on market conditions.",
    transcript:
      "Our platform always outperforms the market. It has been strong over the last few quarters.",
    confidence: "78% confidence",
  },
  {
    id: "alert-1720",
    title: "Overstated suitability",
    meeting: "Income Strategy Review",
    severity: "High",
    category: "Suitability",
    time: "Jan 26, 1:18 PM",
    snippet: "This solution is perfect for every retirement investor.",
    recommendation:
      "This solution may be suitable depending on your goals, risk tolerance, and timeline.",
    transcript:
      "This solution is perfect for every retirement investor. We can align it based on your objectives.",
    confidence: "92% confidence",
  },
];

const meetings: MeetingItem[] = [
  {
    id: "meet-201",
    name: "Legacy Wealth Review",
    status: "Listening",
    duration: "42 min",
    attendees: "3 attendees",
    advisor: "J. Patel",
  },
  {
    id: "meet-202",
    name: "Business Owner Check-in",
    status: "Speaking",
    duration: "18 min",
    attendees: "2 attendees",
    advisor: "L. Moreno",
  },
  {
    id: "meet-203",
    name: "Investment Policy Update",
    status: "Completed",
    duration: "55 min",
    attendees: "4 attendees",
    advisor: "S. Brooks",
  },
  {
    id: "meet-204",
    name: "Retirement Income Plan",
    status: "Completed",
    duration: "38 min",
    attendees: "2 attendees",
    advisor: "A. Chen",
  },
];

const kpis: KPIItem[] = [
  {
    id: "kpi-total",
    label: "Total Meetings Analyzed",
    value: "1,248",
    trend: "+6.4% vs last 30 days",
    direction: "up",
    icon: FileText,
  },
  {
    id: "kpi-alerts",
    label: "Alerts Flagged",
    value: "94",
    trend: "-3.1% vs last 30 days",
    direction: "down",
    icon: AlertTriangle,
  },
  {
    id: "kpi-high",
    label: "High-Risk Events",
    value: "12",
    trend: "+2.2% vs last 30 days",
    direction: "up",
    icon: ShieldAlert,
  },
  {
    id: "kpi-score",
    label: "Avg Risk Score",
    value: "72.4",
    trend: "+1.8 pts this month",
    direction: "up",
    icon: Sparkles,
  },
  {
    id: "kpi-review",
    label: "Items Needing Review",
    value: "31",
    trend: "-4.6% vs last 30 days",
    direction: "down",
    icon: Flag,
  },
  {
    id: "kpi-policy",
    label: "Policy Coverage",
    value: "98%",
    trend: "+0.4% vs last audit",
    direction: "up",
    icon: ShieldCheck,
  },
];

const severityStyles: Record<AlertItem["severity"], string> = {
  Low: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Medium: "bg-amber-50 text-amber-700 border-amber-200",
  High: "bg-rose-50 text-rose-700 border-rose-200",
};

const meetingStatusStyles: Record<MeetingItem["status"], string> = {
  Listening: "bg-blue-50 text-blue-700 border-blue-200",
  Speaking: "bg-orange-50 text-orange-700 border-orange-200",
  Completed: "bg-slate-100 text-slate-600 border-slate-200",
};

export default function ComplianceDashboardPage() {
  const embedUrl = process.env.NEXT_PUBLIC_QUICKSIGHT_EMBED_URL ?? "";
  const [dateRange, setDateRange] = React.useState("30");
  const [severity, setSeverity] = React.useState("All");
  const [policyCategory, setPolicyCategory] = React.useState("All");
  const [meetingType, setMeetingType] = React.useState("All");
  const [searchTerm, setSearchTerm] = React.useState("");
  const [selectedAlert, setSelectedAlert] = React.useState<AlertItem | null>(
    null
  );
  const [iframeLoaded, setIframeLoaded] = React.useState(false);
  const [iframeError, setIframeError] = React.useState(!embedUrl);
  const [iframeKey, setIframeKey] = React.useState(0);
  const [darkMode, setDarkMode] = React.useState(false);

  React.useEffect(() => {
    setIframeError(!embedUrl);
    setIframeLoaded(false);
  }, [embedUrl, iframeKey]);

  const handleApplyFilters = () => {
    setIframeKey((prev) => prev + 1);
  };

  const handleResetFilters = () => {
    setDateRange("30");
    setSeverity("All");
    setPolicyCategory("All");
    setMeetingType("All");
    setSearchTerm("");
  };

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSeverity =
      severity === "All" || alert.severity.toLowerCase() === severity.toLowerCase();
    const matchesCategory =
      policyCategory === "All" ||
      alert.category.toLowerCase() === policyCategory.toLowerCase();
    const matchesSearch =
      searchTerm.trim() === "" ||
      alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.meeting.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-sm">
              <ShieldCheck className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <div className="text-base font-semibold text-slate-900">
                AdvisorGuard
              </div>
              <div className="text-xs uppercase tracking-[0.2em] text-slate-400">
                AI Compliance Copilot
              </div>
            </div>
          </div>
          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 lg:flex">
            {["Dashboard", "Meetings", "Policies", "Reports"].map((item) => (
              <button
                key={item}
                className="transition hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:ring-offset-2"
                aria-label={`Open ${item}`}
              >
                {item}
              </button>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <div className="hidden w-64 lg:block">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search policies, meetings..."
                  aria-label="Global search"
                  className="pl-9"
                />
              </div>
            </div>
            <Button
              variant="outline"
              size="icon"
              aria-label="View notifications"
              className="border-slate-200"
            >
              <Bell className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              aria-label="Toggle theme"
              className="border-slate-200"
              onClick={() => setDarkMode((prev) => !prev)}
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button
              variant="outline"
              aria-label="Open user menu"
              className="flex items-center gap-2 border-slate-200 px-3"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
                AG
              </span>
              <span className="hidden text-sm font-medium text-slate-700 sm:inline">
                Jordan Lee
              </span>
              <ChevronDown className="h-4 w-4 text-slate-500" />
            </Button>
          </div>
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 py-10">
        <section className="flex flex-col justify-between gap-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm lg:flex-row lg:items-center">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
              <Badge variant="outline" className="border-slate-200 text-slate-600">
                Last synced: 2 min ago
              </Badge>
              <Badge variant="outline" className="border-slate-200 text-slate-600">
                Data source: Audit DB
              </Badge>
            </div>
            <h1 className="text-3xl font-semibold text-slate-900">
              Compliance Dashboard
            </h1>
            <p className="max-w-2xl text-base text-slate-600">
              Monitor meeting risk, policy flags, and review status in one place.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button className="bg-orange-600 text-white hover:bg-orange-700">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </Button>
            <Button variant="outline" className="border-slate-200 text-slate-700">
              Upload Audio
            </Button>
          </div>
        </section>

        <Card className="border-slate-200 shadow-sm">
          <CardContent className="grid gap-4 p-6 lg:grid-cols-[1.1fr_1fr_1fr_1fr_1.5fr_auto] lg:items-end">
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Date range
              </span>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger aria-label="Select date range">
                  <SelectValue placeholder="Select range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                  <SelectItem value="90">Last 90 days</SelectItem>
                  <SelectItem value="180">Last 6 months</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Severity
              </span>
              <Select value={severity} onValueChange={setSeverity}>
                <SelectTrigger aria-label="Select severity">
                  <SelectValue placeholder="All severities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="All">All</SelectItem>
                  <SelectItem value="Low">Low</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="High">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Policy category
              </span>
              <Select value={policyCategory} onValueChange={setPolicyCategory}>
                <SelectTrigger aria-label="Select policy category">
                  <SelectValue placeholder="All policies" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="All">All</SelectItem>
                  <SelectItem value="Performance Guarantees">
                    Performance Guarantees
                  </SelectItem>
                  <SelectItem value="Risk Disclosure">Risk Disclosure</SelectItem>
                  <SelectItem value="Marketing Claims">Marketing Claims</SelectItem>
                  <SelectItem value="Suitability">Suitability</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Meeting type
              </span>
              <Select value={meetingType} onValueChange={setMeetingType}>
                <SelectTrigger aria-label="Select meeting type">
                  <SelectValue placeholder="All meetings" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="All">All</SelectItem>
                  <SelectItem value="Review">Portfolio review</SelectItem>
                  <SelectItem value="Planning">Retirement planning</SelectItem>
                  <SelectItem value="Onboarding">Client onboarding</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Search
              </span>
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search meetings or alerts"
                  aria-label="Search meetings or alerts"
                  className="pl-9"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" onClick={handleResetFilters}>
                Reset
              </Button>
              <Button
                className="bg-slate-900 text-white hover:bg-slate-800"
                onClick={handleApplyFilters}
              >
                Apply
              </Button>
            </div>
          </CardContent>
        </Card>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {kpis.map((metric) => {
            const Icon = metric.icon;
            const isUp = metric.direction === "up";
            return (
              <Card key={metric.id} className="border-slate-200 shadow-sm">
                <CardHeader className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      {metric.label}
                    </span>
                    <span className="rounded-full bg-slate-100 p-2 text-slate-700">
                      <Icon className="h-4 w-4" aria-hidden="true" />
                    </span>
                  </div>
                  <CardTitle className="text-3xl font-semibold text-slate-900">
                    {metric.value}
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-between text-sm text-slate-600">
                  <div className="flex items-center gap-2">
                    {isUp ? (
                      <ArrowUpRight className="h-4 w-4 text-emerald-600" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-rose-600" />
                    )}
                    <span>{metric.trend}</span>
                  </div>
                  <div className="h-8 w-20 rounded-full bg-slate-100" aria-hidden="true" />
                </CardContent>
              </Card>
            );
          })}
        </section>

        <section className="grid gap-6 lg:grid-cols-[2.2fr_1fr]">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="space-y-2">
              <CardTitle className="text-lg font-semibold text-slate-900">
                Analytics
              </CardTitle>
              <CardDescription>
                QuickSight dashboard embedded from your audit data warehouse.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative min-h-[360px] overflow-hidden rounded-3xl border border-slate-200 bg-white">
                {!iframeError && (
                  <iframe
                    key={iframeKey}
                    src={embedUrl || "about:blank"}
                    title="AdvisorGuard analytics dashboard"
                    className="h-[560px] w-full rounded-3xl border-0"
                    onLoad={() => setIframeLoaded(true)}
                    onError={() => setIframeError(true)}
                  />
                )}
                {!iframeError && !iframeLoaded && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-white/80 text-slate-600">
                    <div className="h-10 w-10 animate-spin rounded-full border-2 border-slate-300 border-t-orange-500" />
                    <span className="text-sm">Loading analytics…</span>
                  </div>
                )}
                {iframeError && (
                  <div className="flex h-[560px] flex-col items-center justify-center gap-3 text-center text-slate-600">
                    <AlertTriangle className="h-8 w-8 text-amber-600" />
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-slate-900">
                        QuickSight embed not configured
                      </p>
                      <p className="text-sm text-slate-600">
                        Add `NEXT_PUBLIC_QUICKSIGHT_EMBED_URL` to your environment.
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => setIframeKey((prev) => prev + 1)}
                      disabled={!embedUrl}
                    >
                      Retry
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="flex flex-col gap-6">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="space-y-2">
                <CardTitle className="text-lg font-semibold text-slate-900">
                  Live Alerts
                </CardTitle>
                <CardDescription>
                  Most recent policy flags from monitored meetings.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="max-h-[360px] space-y-3 overflow-y-auto pr-1">
                  {filteredAlerts.map((alert) => (
                    <button
                      key={alert.id}
                      type="button"
                      onClick={() => setSelectedAlert(alert)}
                      aria-label={`Open alert for ${alert.title}`}
                      className="flex w-full flex-col gap-2 rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:ring-offset-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-semibold text-slate-900">
                          {alert.title}
                        </span>
                        <Badge
                          variant="outline"
                          className={`text-xs ${severityStyles[alert.severity]}`}
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        <span>{alert.time}</span>
                        <span>•</span>
                        <span>{alert.category}</span>
                      </div>
                      <p className="text-sm text-slate-600">{alert.snippet}</p>
                    </button>
                  ))}
                  {filteredAlerts.length === 0 && (
                    <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
                      No alerts match the current filters.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="space-y-2">
                <CardTitle className="text-lg font-semibold text-slate-900">
                  Active Meetings
                </CardTitle>
                <CardDescription>
                  Live monitoring across advisor sessions.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {meetings.map((meeting) => (
                  <div
                    key={meeting.id}
                    className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
                  >
                    <div>
                      <p className="text-sm font-semibold text-slate-900">
                        {meeting.name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {meeting.advisor} • {meeting.duration} • {meeting.attendees}
                      </p>
                    </div>
                    <Badge
                      variant="outline"
                      className={`text-xs ${meetingStatusStyles[meeting.status]}`}
                    >
                      {meeting.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </section>
      </div>

      <Sheet
        open={!!selectedAlert}
        onOpenChange={(open) => {
          if (!open) setSelectedAlert(null);
        }}
      >
        <SheetContent className="w-full max-w-lg sm:max-w-xl">
          {selectedAlert && (
            <div className="flex h-full flex-col">
              <SheetHeader className="space-y-2">
                <SheetTitle className="text-xl font-semibold text-slate-900">
                  Alert details
                </SheetTitle>
                <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
                  <Badge
                    variant="outline"
                    className={`${severityStyles[selectedAlert.severity]}`}
                  >
                    {selectedAlert.severity} severity
                  </Badge>
                  <Badge variant="outline" className="border-slate-200 text-slate-600">
                    {selectedAlert.category}
                  </Badge>
                  <Badge variant="outline" className="border-slate-200 text-slate-600">
                    {selectedAlert.confidence}
                  </Badge>
                </div>
              </SheetHeader>

              <div className="mt-6 space-y-6 overflow-y-auto pb-6 text-sm text-slate-700">
                <div className="space-y-1">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Meeting context
                  </p>
                  <p className="text-base font-medium text-slate-900">
                    {selectedAlert.meeting}
                  </p>
                  <p className="text-xs text-slate-500">{selectedAlert.time}</p>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Transcript snippet
                  </p>
                  <p className="rounded-2xl border border-slate-200 bg-slate-50 p-4 leading-relaxed text-slate-700">
                    {selectedAlert.transcript.replace(selectedAlert.snippet, "")}
                    <mark className="rounded-sm bg-orange-100 px-1 text-orange-800">
                      {selectedAlert.snippet}
                    </mark>
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Recommended compliant alternative language
                  </p>
                  <p className="rounded-2xl border border-slate-200 bg-white p-4 text-slate-700 shadow-sm">
                    {selectedAlert.recommendation}
                  </p>
                </div>
              </div>

              <SheetFooter className="mt-auto flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex flex-wrap gap-2">
                  <Button className="bg-orange-600 text-white hover:bg-orange-700">
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Mark Reviewed
                  </Button>
                  <Button variant="outline">
                    <ShieldAlert className="mr-2 h-4 w-4" />
                    Escalate
                  </Button>
                </div>
                <Button variant="ghost" className="text-slate-600">
                  <Download className="mr-2 h-4 w-4" />
                  Download Log
                </Button>
              </SheetFooter>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
