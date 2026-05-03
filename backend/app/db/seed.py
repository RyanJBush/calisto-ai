from sqlalchemy.orm import Session
import hashlib

from app.core.security import get_password_hash
from app.models import Document, IngestionRun, Organization, User
from app.services.embedding_index_service import embedding_index_service
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService


def seed_demo_data(db: Session) -> None:
    org = db.query(Organization).filter(Organization.name == "Calisto Demo Org").first()
    if org is None:
        org = Organization(name="Calisto Demo Org")
        db.add(org)
        db.flush()

    users = db.query(User).filter(User.organization_id == org.id).all()
    if not users:
        users = [
            User(
                organization_id=org.id,
                email="admin@calisto.ai",
                full_name="Admin User",
                role="admin",
                password_hash=get_password_hash("password123"),
            ),
            User(
                organization_id=org.id,
                email="member@calisto.ai",
                full_name="Member User",
                role="member",
                password_hash=get_password_hash("password123"),
            ),
            User(
                organization_id=org.id,
                email="viewer@calisto.ai",
                full_name="Viewer User",
                role="viewer",
                password_hash=get_password_hash("password123"),
            ),
        ]
        db.add_all(users)
        db.commit()

    if db.query(Document).first():
        return

    ingestion_service = IngestionService()
    embedding_service = EmbeddingService()
    demo_docs = [
        (
            "Employee Handbook",
            "hr-handbook.md",
            """# Employee Handbook — Calisto AI

## Leave Policy
Employees receive 20 paid leave days per year. Leave may be taken in increments of at least half a day.
Unused leave of up to 5 days rolls over to the following calendar year.
Emergency leave (up to 3 days) is granted for immediate family bereavement.
Leave requests must be submitted at least two weeks in advance except in emergency situations.

## Remote Work Policy
Calisto AI supports hybrid remote work. Employees may work remotely up to 3 days per week with manager approval.
Remote work schedules are reviewed quarterly and adjusted based on project needs.
Fully remote arrangements require VP-level sign-off and are granted on a case-by-case basis.

## Performance Reviews
Performance reviews are conducted twice yearly: mid-year (June) and end-of-year (December).
Employees are evaluated on goals, collaboration, and technical impact.
Ratings range from 1 (needs improvement) to 5 (exceeds expectations).
A rating of 4 or higher for two consecutive cycles qualifies the employee for a promotion review.

## Expense Policy
Business expenses up to $500 can be reimbursed with manager approval and a valid receipt.
Expenses above $500 require director approval before incurring.
All expense claims must be submitted within 30 days of the expense date.

## Code of Conduct
Employees must treat all colleagues with respect and professionalism.
Harassment, discrimination, or retaliation of any kind will result in immediate disciplinary action.
Conflicts of interest must be disclosed to HR within 14 days of identification.
""",
        ),
        (
            "Security Operations Guide",
            "security-guide.txt",
            """# Security Operations Guide — Calisto AI

## Incident Severity Levels
Incidents are classified P1 through P4 based on business impact.

P1 – Critical: Complete service outage or data breach affecting customers.
Escalation window: 15 minutes. On-call engineer must be paged immediately.
All-hands war room is activated within 30 minutes.

P2 – High: Major feature degradation or performance impact for >20% of users.
Escalation window: 30 minutes. Engineering lead notified within 1 hour.

P3 – Medium: Minor feature degradation or isolated customer impact.
Escalation window: 2 hours. Ticket created and assigned within 4 hours.

P4 – Low: Cosmetic issues, documentation gaps, or potential future risks.
Addressed in the next sprint cycle.

## Incident Response Procedure
1. Detect and classify the incident.
2. Create an incident ticket in the ops tracker with severity label.
3. Page the on-call engineer using the PagerDuty rotation.
4. Open a dedicated incident Slack channel: #incident-YYYYMMDD-HHMM.
5. Assign an incident commander for P1 and P2 events.
6. Conduct a post-mortem within 5 business days of incident resolution.

## Vulnerability Management
All critical CVEs must be patched within 72 hours of public disclosure.
High severity CVEs must be patched within 2 weeks.
A security scan is run on every pull request and every production deployment.

## Access Control
Least-privilege access is enforced for all cloud resources.
Service account keys are rotated every 90 days.
MFA is required for all engineers with production access.
""",
        ),
        (
            "Support SLA",
            "support-sla.txt",
            """# Customer Support SLA — Calisto AI

## Response Time Targets
Enterprise (Critical): First response within 1 hour, 24/7.
Enterprise (Standard): First response within 8 business hours.
Professional (Critical): First response within 4 hours during business hours.
Professional (Standard): First response within 2 business days.
Starter: First response within 5 business days.

## Resolution Time Targets
Critical issues (data loss, security breach, complete outage): resolved within 4 hours or escalated to engineering.
High priority issues (major functionality broken): resolved within 24 hours.
Medium priority issues (partial degradation): resolved within 3 business days.
Low priority (cosmetic, enhancement requests): resolved within 10 business days.

## Escalation Procedure
If a ticket is not acknowledged within the first-response SLA:
1. Auto-escalation email sent to support manager.
2. If no response within 2x the SLA window, VP of Customer Success is notified.
3. Enterprise customers with active breaches receive a direct call from the account team.

## Support Channels
- Email: support@calisto.ai (all plans)
- Live chat: available for Professional and Enterprise plans during business hours
- Priority hotline: available for Enterprise customers 24/7

## SLA Credits
Customers receive a 10% monthly service credit for every full SLA breach hour beyond agreed targets.
Credits are applied automatically to the next invoice.
""",
        ),
        (
            "Engineering Onboarding Guide",
            "engineering-onboarding.md",
            """# Engineering Onboarding Guide — Calisto AI

## First Week Checklist
- Set up your local development environment using the README quick-start guide.
- Complete security training and acknowledge the acceptable use policy.
- Shadow a senior engineer on one production deployment.
- Attend the architecture overview session with the CTO.

## Development Workflow
We use GitHub Flow: feature branches cut from main, reviewed via pull request, merged after CI passes and one approval.
Branch naming convention: `feat/<ticket-id>-<short-description>` or `fix/<ticket-id>-<short-description>`.
Every pull request must include a description, test coverage, and a linked issue.
Code review turnaround SLA is 1 business day.

## Technology Stack
Backend: Python 3.11+, FastAPI, SQLAlchemy, Alembic, pytest.
Frontend: React 18, Vite, Tailwind CSS.
Infrastructure: Docker Compose (local), cloud-ready with PostgreSQL and Redis.
CI/CD: GitHub Actions with lint, test, and build gates on every PR.

## Deployment Process
Deployments to staging occur automatically on merge to main.
Production deployments require a manual approval from a senior engineer.
Rollbacks are performed via the deployment dashboard and complete within 5 minutes.

## On-Call Rotation
Engineers join the on-call rotation after 90 days of employment.
Each rotation block is 1 week, Sunday to Saturday.
On-call engineers must acknowledge pages within 5 minutes.
Compensation for P1 incidents outside business hours is one day of compensatory time off.
""",
        ),
        (
            "Data Retention Policy",
            "data-retention.md",
            """# Data Retention Policy — Calisto AI

## Customer Data
Customer documents uploaded to the platform are retained for the duration of the subscription plus 90 days.
After subscription termination, data is deleted from all primary and backup systems within 90 days.
Customers can request immediate deletion at any time; deletion completes within 30 days of request.

## Audit Logs
System audit logs are retained for 2 years to support compliance and security investigations.
Access logs are retained for 90 days.
Security incident logs are retained for 5 years.

## Chat and Query History
User chat histories are retained for 12 months by default.
Enterprise customers may configure custom retention periods from 30 days to 7 years.
Anonymized query analytics are retained indefinitely for product improvement.

## Backup Policy
Database backups are taken daily and retained for 30 days.
Weekly backups are retained for 6 months.
Monthly backups are retained for 2 years.

## Compliance
Calisto AI complies with GDPR, CCPA, and SOC 2 Type II requirements.
Data processing agreements (DPAs) are available upon request for EU customers.
Annual third-party security audits cover data retention and deletion procedures.
""",
        ),
    ]
    for title, source_name, content in demo_docs:
        doc = Document(
            organization_id=org.id,
            uploaded_by=users[0].id,
            title=title,
            source_name=source_name,
            content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            version=1,
            content=content,
        )
        db.add(doc)
        db.flush()
        run = IngestionRun(document_id=doc.id, status="completed", attempts=1)
        db.add(run)
        chunks = ingestion_service.chunk_document(doc)
        for chunk in chunks:
            db.add(chunk)
        db.flush()
        for chunk in chunks:
            embedding_index_service.upsert_chunk_embedding(db, chunk.id, embedding_service.embed_text(chunk.content))
    db.commit()
