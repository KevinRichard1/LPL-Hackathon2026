# LPL-Hackathon2026

# 🛡️ ComplianceGuard: Autonomous Compliance Agent
**ComplianceGuard** is an enterprise-grade, AI-driven compliance engine designed for LPL Financial. It transforms passive advisor-client interactions (audio, video, text) into proactive intelligence, shifting compliance from reactive sampling to 100% autonomous oversight.

## 🚀 The Vision
Financial firms currently audit less than 1% of advisor interactions due to the high cost of manual labor. This creates massive regulatory blind spots and leads to millions in FINRA/SEC fines. ComplianceGuard closes this gap by:
- **Auditing 100% of interactions** for a fraction of the cost ($0.68/audit).
- **Providing Real-Time Coaching** to advisors to prevent violations before they happen.
- **Autonomously Escalating** high-risk threats to legal teams instantly.

## 🛠️ Technical Architecture: The "Sense-Reason-Act" Loop
The project is built on a 100% Serverless, Event-Driven Architecture on AWS:
1. **Sense (Ingestion)**: Files are uploaded to Amazon S3, triggering an asynchronous event.
2. **Transcribe (Processing)**: Amazon Transcribe converts financial dialogue into structured text using domain-specific vocabulary.
3. **Reason (Intelligence)**: Amazon Bedrock (Claude 3 Haiku) analyzes the transcript against regulatory guidelines (FINRA/SEC). It identifies violations, assigns severity, and generates corrective scripts
4. **Act (Response)**: 
    - Low/Med Risk: Reports are saved to S3 and visualized in a Next.js dashboard.
    - High Risk: The agent autonomously triggers Amazon SNS to send immediate email/SMS alerts to compliance officers.
    - Insights: **Amazon QuickSight** provides natural language querying (Amazon Q) for executive-level trend analysis.

## ✨ Key Features
- Autonomous Escalation: High-severity flags trigger out-of-band alerts without human intervention.
- AI-Powered Coaching: Every violation includes a "Corrective Script" to train advisors in real-time.
- PII Masking & Guardrails: Utilizes Amazon Bedrock Guardrails to ensure sensitive client data is protected and hallucinations are minimized.
- Queryable Audit Trail: Metadata is stored in a structured JSON format, making the entire firm's history searchable via natural language.

## 💻 Tech Stack
- Frontend: Next.js 14, Tailwind CSS, Lucide React
- Backend: AWS Lambda (Python/Node.js)
- AI/ML: Amazon Bedrock (Claude 3), Amazon Transcribe
- Data/Storage: Amazon S3, Amazon Athena
- Communication: Amazon SNSAnalytics: Amazon QuickSight + Amazon Q

| Metric | Manual Audit | ComplianceGuard |
| :--- | :--- | :--- |
| **Coverage** | ~1% Sampling | **100% Universal** |
| **Cost per Audit** | ~$45.00 | **$0.68** |
| **Latency** | Days/Weeks | **< 10 Seconds** |
| **Risk Model** | Reactive | **Proactive & Agentic** |