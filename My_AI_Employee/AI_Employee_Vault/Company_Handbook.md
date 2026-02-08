# Company Handbook

This file defines rules of engagement for the Personal AI Employee.

## Processing rules

### Priority classification
- HIGH: contains "urgent", "asap", deadlines, payments, security items
- MEDIUM: standard business requests
- LOW: newsletters, FYI, non-actionable

### Communication tone
- Professional, concise, and polite.
- Ask for clarification when details are missing.

### Permission boundaries (Bronze)
- No external actions. Only create plans and drafts.
- Never send emails, post social media, or make payments.

## Output preferences
- Plans should use checkboxes.
- Keep links to source items.

---

## Silver Tier: Approval Thresholds

### Auto-Approve (No Human Review)
- Emails to known contacts (in contact list)
- Recurring payments < $50
- Scheduled LinkedIn posts (pre-approved content)
- Routine status updates to team members

### Require Approval (Human Review)
- All external communications to new contacts
- Payments > $50
- Any commitments > 1 day
- Policy changes
- Banking/financial actions
- Client-facing communications
- LinkedIn posts with new content
- WhatsApp messages to clients

### Never Auto-Retry (Always Require Fresh Approval)
- Banking/payment actions
- Legal/compliance actions
- Account deletions
- Contract commitments
- Financial transactions > $100

## Communication Rules

### Email Guidelines
- Always be professional with clients
- Confirm delivery dates with management first
- Follow brand voice guidelines
- Response time: within 24 hours for clients

### WhatsApp Guidelines
- Urgent keywords: "urgent", "help", "asap", "invoice", "payment"
- Response time: within 2 hours for urgent messages
- Always acknowledge receipt

## Monitored WhatsApp Contacts
- Uneeza


### LinkedIn Guidelines
- Post schedule: Mondays and Thursdays at 9:00 AM
- Tone: Professional, informative, engaging
- Hashtags: #automation #business #innovation
- Engagement: Like and comment on relevant posts

---

## Gold Tier: Autonomous Business Operations

### Odoo Accounting Rules (User Story 1)

#### Invoice Management
- **Auto-Create Draft Invoices**: Always create draft invoices automatically
- **Require Approval Before Sending**: ALL invoices must be approved before sending to customer
- **Invoice Terms**: Net 30 (30 days payment terms)
- **Late Payment Fee**: 1.5% per month after due date
- **Tax Rate**: 10% (adjust per jurisdiction)

#### Payment Processing
- **Auto-Record Payments < $500**: From known customers, auto-record and reconcile
- **Require Approval for Payments > $500**: All payments over $500 require human approval
- **Payment Methods**: Bank transfer, credit card, cash, check
- **Reconciliation**: Always reconcile payments with invoices immediately

#### Expense Categorization
- **Auto-Categorize < $100**: Expenses under $100 auto-categorize based on vendor
- **Require Approval > $100**: Expenses over $100 require approval before categorization
- **Expense Categories**:
  - Office Supplies
  - Travel
  - Software/Subscriptions
  - Marketing
  - Professional Services
  - Utilities
  - Equipment

#### Financial Reporting
- **Weekly Reports**: Generate every Monday morning for CEO briefing
- **Monthly Reports**: Generate on 1st of each month
- **Quarterly Reports**: Generate within 5 days of quarter end
- **Always Require Approval**: All financial reports require approval before distribution

### Social Media Posting Rules (User Story 2)

#### Facebook Posting
- **Auto-Approve**: Scheduled posts from content calendar
- **Require Approval**:
  - Posts mentioning competitors
  - Posts with pricing information
  - Posts during crisis/sensitive events
  - Posts with external links to non-company domains
- **Content Guidelines**:
  - Tone: Professional but friendly
  - Hashtags: Max 3 per post
  - Emojis: Use sparingly, brand-appropriate only
  - Character limit: 40-80 chars optimal

#### Instagram Posting
- **Auto-Approve**: Pre-approved content with images from brand library
- **Require Approval**:
  - New content not in content calendar
  - Posts with user-generated content
  - Posts mentioning partners/clients
- **Content Guidelines**:
  - Tone: Casual, engaging
  - Hashtags: 20-30 hashtags (mix popular and niche)
  - Emojis: Encouraged for engagement
  - Image specs: 1080x1080px (square), 1080x1350px (portrait)

#### Twitter Posting
- **Auto-Approve**: Engagement posts < 280 characters
- **Require Approval**:
  - Threads (multi-tweet posts)
  - Posts mentioning other accounts
  - Posts with controversial topics
- **Content Guidelines**:
  - Tone: Concise, informative
  - Hashtags: 1-2 hashtags max
  - Character limit: 240 chars optimal
  - Thread limit: Max 5 tweets per thread

#### Cross-Platform Posting
- **Always Require Approval**: All cross-platform posts (posting to multiple platforms simultaneously)
- **Content Adaptation**: Automatically adapt content for each platform's character limits and tone
- **Image Requirements**: Use platform-specific image dimensions

### Ralph Wiggum Loop Configuration (User Story 3)

#### Autonomous Operation
- **Max Iterations**: 10 iterations per task (configurable via RALPH_MAX_ITERATIONS)
- **Stop Condition**: Task file moved to /Done/ folder
- **State Persistence**: .ralph_state.json tracks current iteration and task status
- **Crash Loop Protection**: Max 3 restarts within 5 minutes, then alert and stop

#### Autonomous Boundaries
- **Allowed Actions**:
  - Process all items in /Needs_Action/
  - Create plans in /Plans/
  - Route items for approval
  - Execute approved actions
  - Update Dashboard.md
  - Generate CEO briefings
- **Prohibited Actions**:
  - Never override human rejections
  - Never retry failed approvals without fresh approval
  - Never modify Company_Handbook.md or Business_Goals.md
  - Never delete audit logs

#### Iteration Limits
- **Per Task**: 10 iterations max
- **Per Day**: Unlimited (runs continuously)
- **Per Week**: Unlimited (scheduled tasks run weekly)

### CEO Briefing Configuration (User Story 4)

#### Generation Schedule
- **Weekly Briefing**: Every Sunday at 8:00 PM (cron: 0 20 * * 0)
- **Monthly Audit**: 1st of each month at 9:00 AM
- **Quarterly Review**: Within 5 days of quarter end

#### Data Sources
- **Completed Tasks**: /Done/ folder (last 7 days)
- **Financial Data**: Odoo (revenue, expenses, cash flow, aged receivables)
- **Social Media**: Facebook, Instagram, Twitter metrics (engagement, reach, posts)
- **Business Goals**: Business_Goals.md (targets and KPIs)

#### Metrics to Track
- **Revenue**: Weekly total, MTD, vs target ($50,000/month)
- **Task Completion**: Count, average time, bottlenecks (>1.5x expected time)
- **Expenses**: Weekly total, by category, anomalies (>20% increase)
- **Social Media**: Posts, engagement rate, reach, top performers
- **Subscriptions**: Usage, cost, optimization opportunities (unused >30 days)

#### Alert Thresholds
- **Revenue < 80% of weekly target**: Alert in briefing
- **Task delay > 3 days**: Flag as bottleneck
- **Expense > 20% increase**: Investigate and report
- **Subscription unused > 30 days**: Suggest cancellation
- **Upcoming deadline < 7 days**: Highlight in briefing

#### Proactive Suggestions
- **Cost Optimization**: Identify unused subscriptions, duplicate tools
- **Revenue Opportunities**: Follow up on outstanding invoices, propose annual contracts
- **Process Improvements**: Identify workflow bottlenecks, suggest automation
- **Risk Mitigation**: Flag overdue invoices, upcoming deadlines, resource constraints

### Error Recovery Policies (User Story 5)

#### Token Refresh
- **Facebook/Instagram**: Auto-refresh tokens when expired (60-day validity)
- **Gmail**: Auto-refresh OAuth tokens when expired
- **LinkedIn**: Auto-refresh OAuth tokens when expired
- **Twitter**: Tokens don't expire, but validate before each use

#### Retry Logic
- **Exponential Backoff**:
  - Retry 1: After 25 seconds
  - Retry 2: After 2 minutes
  - Retry 3: After 8 minutes
- **Max Retries**: 3 attempts per action
- **Never Auto-Retry**: Banking/payment actions, legal/compliance actions, account deletions

#### Graceful Degradation
- **Queue Files**: Use local .jsonl queue files when MCP servers unavailable
- **Offline Mode**: Continue processing non-external actions when offline
- **Audit Logging**: Always log actions even if execution fails

#### Health Monitoring
- **Watchdog Check Interval**: 60 seconds
- **Component Health Checks**: Email MCP, Odoo MCP, Social Media MCPs
- **Auto-Restart**: Restart crashed components automatically
- **Crash Loop Detection**: Max 3 restarts within 5 minutes
- **Alert Notifications**: Notify on critical errors, crash loops, token expiration

#### Audit Logging
- **Log All Actions**: Email sends, social posts, invoices, payments, expenses
- **Credential Sanitization**: Automatically redact API keys, tokens, passwords
- **Retention**: 90 days in /Logs/, then archive for 2 years
- **Immutability**: Logs are write-once, no deletion during retention period

---

## Compliance & Security

### Data Protection
- **PII Handling**: Email addresses truncated in logs (user@*****.com)
- **Payment Data**: Card numbers show last 4 digits only
- **API Keys**: Never log full tokens, always redact
- **Audit Trail**: Complete record of who did what when

### Approval Workflow
- **Financial Actions**: ALL require approval (invoices, payments, expenses >$100)
- **External Communications**: New contacts require approval
- **Social Media**: New content requires approval
- **System Changes**: Configuration changes require approval

### Business Continuity
- **Backup Strategy**: Daily Odoo database backups
- **Disaster Recovery**: Queue files enable offline operation
- **State Persistence**: Ralph state file enables crash recovery
- **Audit Trail**: Complete history for compliance and debugging
