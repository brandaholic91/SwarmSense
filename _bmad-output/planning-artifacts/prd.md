---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-e-01-discovery', 'step-e-02-review', 'step-e-03-edit']
lastEdited: '2026-03-19'
date: '2026-03-19'
editHistory:
  - date: '2026-03-19'
    changes: 'Validation Warning fixes: qualifier collection journey step + FR35/FR36 added; FR13/FR22/FR30 tightened; NFR1/2 measurement methods added; NFR7/10/15/18 impl. leakage removed; NFR19 degradation quantified'
  - date: '2026-03-19'
    changes: 'Critical-first edit pass: RBAC matrix + subscription entitlements added; FR/NFR measurability tightened; explicit MVP out-of-scope and traceability mapping added; frontmatter completeness updated'
  - date: '2026-03-19'
    changes: 'Post-validation warning closure: added user-success KPI, moat/unit-cost success metrics, explicit cap-reached journey moment, and traceability mapping updates'
inputDocuments:
  - '_bmad-output/brainstorming/brainstorming-session-2026-03-18-1730.md'
  - 'docs/vazlat.md'
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 1
  projectDocsCount: 1
workflowType: 'prd'
workflow: 'edit'
classification:
  projectType: saas_b2b
  domain: martech_ai
  complexity: medium
  projectContext: greenfield
---

# Product Requirements Document - SwarmSense

**Author:** Balazs
**Date:** 2026-03-18

## Executive Summary

SwarmSense is a synthetic market research SaaS platform that enables marketers, product managers, and founders to validate ideas, messages, and hypotheses in minutes — not weeks. Users submit a research topic and a target audience description; the platform runs the query across 15–20 dynamically generated AI personas in parallel and delivers a structured, multi-perspective simulation of market sentiment via email.

The product launches as a lead-generation tool (email capture via a freemium web experience), with a roadmap toward a paid token-based SaaS platform. The primary market is Hungarian marketing and product development professionals. The core value proposition: a structured focus group simulation at ~$0.002 per run, with no recruitment, no scheduling, and no waiting.

### What Makes This Special

SwarmSense is not a ChatGPT wrapper. The differentiator is the **persona generation framework**: each simulation produces 15–20 distinct personas built across five attitudinal dimensions — risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve. This guarantees response diversity that a single LLM prompt cannot produce.

The result is closer to quantitative research than to a chatbot answer: users see distribution of sentiment, the strongest objections, and the conditions under which skeptics would change their minds — all structured, readable, and shareable.

The long-term moat is the **hypothesis database**: every query run accumulates structured market intelligence, creating a proprietary dataset that grows with usage and cannot be replicated by competitors.

**Project Classification:** SaaS B2B Platform · MarTech / AI Tools · Medium Complexity · Greenfield · Phase 1 market: Hungarian marketing, product, and agency professionals

## Success Criteria

### User Success

A user submits a research topic and target audience description, provides a verified email address, and receives a structured multi-persona analysis within 1–2 minutes. The "aha moment" is in the email: 15–20 attitudinally distinct personas responding to the same hypothesis — showing sentiment distribution, the strongest objections, and the conditions under which skeptics would change their minds. Success means the user gains a concrete, actionable insight they could not have produced with a single LLM prompt.

**User-success KPI:** At least 70% of first-time verified users complete the post-result reflection action (reply-to email or tracked reflection CTA click) within 24 hours of result delivery.

### Business Success

| Metric | 4-Week Target | 8-Week Target |
|---|---|---|
| Verified email subscribers | 150 | 400 |
| Daily active runs | 10+ | 30+ |
| Qualifier question completion rate | 65%+ | 65%+ |
| Email open rate (automated sequence) | 35%+ | 30%+ |
| Potential paying users identified | 10 | 35 |
| Hypothesis database growth (new structured runs stored) | 120+ | 320+ |
| Average variable AI cost per completed run | <=$0.003 | <=$0.0025 |

**Decision tree at week 4:**
- 150+ verified emails AND recurring pain point identified → Pro tier development begins
- 150+ verified emails BUT no clear direction → Deep interviews with first 50 subscribers
- Under 150 emails → Launch channel strategy revised, LinkedIn activation intensified

### Technical Success

- Magic link verification flow succeeds with >=99% completion for valid tokens, measured weekly from authentication event logs
- Persona engine completes 15–20 parallel API calls and delivers results via email within 120 seconds for p95 runs, measured from run start to email dispatch logs
- 1 free run per email address is enforced with 0 duplicate free runs per verified email, measured by weekly run-log audit
- Result email delivery success rate is >=95%, measured from transactional email provider delivery events
- API cost hard limit is capped at $50/month with automatic run blocking at limit, measured from monthly billing telemetry

### Measurable Outcomes

**Conversion funnel targets:**
- Landing → form submission: 40%+
- Form → email submitted: 60%+
- Email submitted → magic link verified: 50%+
- Overall (landing → verified email): ~12–15%

## Product Scope & Roadmap

### MVP Strategy

**Approach:** Experience MVP — the smallest product that delivers the "aha moment": a structured multi-persona analysis delivered to the user's inbox within minutes of submitting a research query.

**Resource requirements:** Solo founder. 1–2 week build. No external dependencies beyond listed integrations.

### Phase 1 — MVP

**Core user journeys supported:** Journey 1 (first-time success), Journey 2 (returning user — blocked + waitlist), Journey 4 (admin/operator monitoring).

| Component | Specification |
|---|---|
| Landing page | Single-screen value proposition, example result preview, one CTA, rotating example queries |
| Form | 2 fields: research topic + target audience; rotating sample inputs |
| Email flow | Email capture → DB check → new: magic link verification → returning: "Ez az emailcím már igénybe vette az ingyenes próbát" + waitlist CTA |
| Waiting screen | Progress indicator during 1–2 minute processing |
| Persona engine | 15–20 parallel API calls; attitudinal framework (5 dimensions); Hungarian cultural context; each persona outputs: name, role, stance, primary argument, condition for changing mind |
| Result email | Aggregate sentiment score; persona cards; unexpected result flag (if 15+/20 unanimous); closing reflection question; interpretive disclaimer; single CTA |
| Infrastructure | Plausible Analytics; Sentry; GDPR consent checkbox; Privacy Policy; Terms of Service; API cost hard limit ($50/month) |

### Phase 2 — V2

**Trigger:** 150+ verified emails AND payment intent signals from qualifier question data.

- User account system (email + token balance)
- Token purchase via Stripe (Starter 10/990 HUF · Value 50/3 990 HUF · Pro 150/9 990 HUF; 1 run = 1 token; tokens never expire)
- "Already used" screen repurposed as token purchase prompt
- Run history per account
- Shareable result image (LinkedIn-ready)
- Referral mechanism

### Phase 3 — V3

**Trigger:** 400+ verified emails AND team/agency demand signals.

- In-browser results page with full visualization
- Counter-hypothesis parallel run
- Hypothesis benchmark database
- Team accounts with shared token pools and agency billing
- Multi-tenant platform architecture

### Risk Mitigation

| Risk | Type | Mitigation |
|---|---|---|
| Persona engine produces homogeneous responses | Technical | Manual review of first 50 runs; prompt engineering iteration before scaling |
| Email capture conversion is low | Market | Magic link flow optimized for minimal friction; value proposition A/B tested |
| Solo founder parallel build and marketing | Resource | Waitlist landing page published early during development; LinkedIn activation begins pre-launch |

### Explicit Out of Scope (MVP)

- Team accounts, seat management, and shared token pools (planned for V3)
- In-browser results dashboard and advanced visualization views (planned for V3)
- Counter-hypothesis dual-run workflow and benchmark database views (planned for V3)
- Automated self-service data deletion portal (email-request flow only in MVP)
- Recurring subscription billing (MVP and V2 use one-time token purchases)
- Multi-language UX beyond Hungarian user-facing content

## User Journeys

### Journey 1: Primary User — First-Time Success

**Kata, 34, marketing manager at a mid-sized Hungarian e-commerce brand.**

Kata's team is preparing a Black Friday campaign. She wrote three headline variants and wants to know which one resonates — but there's no time or budget for real audience testing. A colleague shared a LinkedIn post about SwarmSense with the caption: "tried this, surprisingly useful."

She lands on the homepage. The value proposition is immediate: *"Give us a topic and a target audience — 15–20 AI personas tell you what they think. Free."* She's skeptical but curious. She fills in two fields: the campaign headline she's most uncertain about, and "Hungarian online shoppers aged 25–45." She hits submit.

An email field appears. She types her work email and clicks the magic link in her inbox. The link takes her to a brief qualifier page with two questions: *"Mi jellemzi legjobban a szerepkörét?"* and *"Milyen célra szeretné leginkább használni a szintetikus kutatást?"* She selects her answers in under 30 seconds. A waiting screen shows progress — *"Running 18 personas…"* — for about 90 seconds.

The results land in her inbox. The subject line: *"Your SwarmSense analysis is ready."* She opens it and sees a bold flag at the top: **⚠ Strong signal: 15/18 personas rejected this headline.** Below it: the top objection — *"feels like a generic discount promise, doesn't feel personal."* One persona — the price-sensitive late adopter — has a specific condition for changing their mind: *"if the discount applies to items already in my wishlist."* At the bottom of the email, a single question: *"Mit tennél másképp ennek alapján?"*

Kata didn't expect this. She rewrites the headline with a personalization angle. She forwards the email to her creative director. She saves SwarmSense to her bookmarks.

**Capabilities revealed:** Landing page, 2-field form, email capture + magic link verification, waiting screen, persona engine (18 parallel calls), result email with aggregate score + unexpected result flag + persona cards + reflection question.

---

### Journey 2: Primary User — Returning (Already Used Free Trial)

**Kata returns two weeks later.** She has a new brief and wants to run another simulation.

She fills in the form and enters her email. The system recognizes it: *"Ez az emailcím már igénybe vette az ingyenes próbát."* She can't run another free analysis. The page shows: *"Szeretnél korlátlan hozzáférést? Iratkozz fel az értesítőre, és elsőként tudsz meg róla, ha megnyílik a Pro tier."* She signs up for the waitlist.

**Capabilities revealed:** Email DB check, "already used" blocking message, Pro tier waitlist CTA, waitlist storage.

---

### Journey 3: Skeptical User — Converted by Evidence

**Márton, 41, owner of a small advertising agency.** He doesn't trust AI for research. *"It just tells you what you want to hear."* A client forwarded him a SwarmSense result that surprised them.

He arrives already critical. His internal objection: *"this is just ChatGPT with extra steps."* But the example result preview on the landing page shows a split — 9 personas in favour, 9 against, with specific named objections. That's not a ChatGPT answer. He submits a deliberately difficult topic: a niche B2B service for logistics companies.

The result email arrives. The personas are distinct: a risk-averse procurement manager, a cost-cutting CFO, a skeptical operations lead. The CFO's condition for changing their mind: *"show me a concrete ROI calculation within the first meeting."* Márton has been trying to crack that exact objection with a client for weeks. He replies to the result email with a question.

**Capabilities revealed:** Example result preview on landing page, persona diversity across roles and attitudes, B2B topic handling, reply-to address on result email.

---

### Journey 4: Admin / Operator

**Balazs, the founder, on a Tuesday morning.**

He checks the Supabase run log: 14 runs overnight. He scans qualifier responses — three people mentioned "social media content testing," two mentioned "product launch messaging." One run flagged: API returned 17/18 personas due to a timeout; email sent with count noted. Email open rate in Resend: 41% on result emails, 29% on day-3 follow-up. API spend: $3.20 for the week, well within the $50/month limit.

At month-end, spend reaches the configured cap. New run attempts are automatically blocked with a clear user-facing message that the monthly free-run capacity has been reached, while existing analytics and operator views remain available.

**Capabilities revealed:** Run log with qualifier data, graceful degradation on partial API failure, email delivery/open rate monitoring, API cost tracking and hard limit enforcement.

---

### Journey Requirements Summary

| Capability Area | Revealed By |
|---|---|
| Landing page with example result preview | Journey 3 |
| 2-field form with rotating examples | Journey 1 |
| Email capture + DB check + magic link verification | Journey 1, 2 |
| Qualifier question collection (2 questions after magic link, before processing) | Journey 1 |
| "Already used" blocking message + Pro waitlist CTA | Journey 2 |
| Waiting screen with progress indicator | Journey 1 |
| Persona engine: 15–20 parallel calls, attitudinal framework | Journey 1, 3 |
| Result email: aggregate score + unexpected result flag + persona cards + reflection question | Journey 1, 3 |
| Reply-to address on result emails | Journey 3 |
| Graceful degradation on partial API failure | Journey 4 |
| Run log + qualifier question storage | Journey 4 |
| Email open rate monitoring | Journey 4 |
| API cost tracking + hard spend limit | Journey 4 |

### Cross-Cutting Compliance & Communication Trace

| Requirement | Journey Moment | Outcome |
|---|---|---|
| FR9 (consent at capture) | Journey 1 - email capture before verification | User gives explicit consent before processing starts |
| FR22 (3-email follow-up) | Journey 1 - post-result lifecycle | User receives day 1/day 3/day 7 follow-up sequence |
| FR23 (unsubscribe option) | Journey 1 and 3 - every marketing email | User always has functional opt-out path |
| FR24 (unsubscribe action) | Journey 1 and 3 - follow-up emails | User can stop future marketing communications |
| FR31/FR32 (Privacy Policy / ToS access) | Journey 1 - email capture and submission step | User can review legal terms before sharing email |
| FR33 (deletion request by email) | Journey 1 and returning lifecycle | User can request deletion from stored personal data |
| FR34 (PII warning) | Journey 1 - query form submission | User is warned not to submit personal data in prompts |

### Compact Traceability Map

| Source Objective | User Journey | Requirements | Metric |
|---|---|---|---|
| Fast actionable validation in minutes | Journey 1 | FR10, FR11, FR14, FR25, NFR2, NFR4, NFR19 | p95 result delivery <=120s |
| High-quality conversion funnel | Journey 1, Journey 2 | FR3, FR4, FR6, FR8, FR35, FR36 | Landing->verified conversion >=12% |
| Compliance-safe MVP operation | Journey 1, Journey 3, Journey 4 | FR9, FR23, FR24, FR31-34, NFR6-11, NFR20 | Consent capture rate, unsubscribe SLA, zero cross-user access incidents |
| Cost-bounded operation for solo founder | Journey 4 | FR28, FR29, NFR16, NFR17 | Monthly API spend <=$50, alert at 80%, and cap-reached run blocking behavior |
| Compounding insight moat growth | Journey 1, Journey 4 | FR10, FR26, FR27, FR36 | Weekly net-new structured runs and qualifier-linked dataset growth |

## Domain-Specific Requirements

### Compliance & Regulatory

**GDPR (EU 2016/679)**
- Consent checkbox required at email capture: explicit opt-in to data processing and marketing communications
- Privacy Policy required at MVP launch: data collected, usage, retention period, deletion contact
- Data deletion handled via email request (no automated self-service deletion in MVP)
- Supabase deployment must use EU region (eu-central-1) for data residency compliance

**EU AI Act**
- All AI-generated content labeled as synthetic simulation, not real human research
- Interpretive disclaimer in every result email: results do not represent real individuals or validated market research
- Current obligations for general-purpose AI tools at this scale are limited; planned disclosure is sufficient for MVP

**Hungarian Electronic Communications Act (EKRTV)**
- All automated emails include a functional unsubscribe link
- Unsubscribe processed within 48 hours
- Sender identity clearly identifiable; real reply-to address on all outbound email

### Technical Constraints

- User-submitted queries stored in Supabase with run metadata; no cross-user data exposure; no public query log
- API cost hard limit: $50/month enforced at infrastructure level
- Kimi K2 (Moonshot AI) data processing terms must be reviewed before launch: confirm prompt training policy; disclose in Privacy Policy if applicable

### Liability & Legal

**Terms of Service** required at MVP launch:
- Results are AI-generated simulations, not validated market research
- Limitation of liability for business decisions based on SwarmSense output
- Acceptable use policy: no harmful, discriminatory, or deceptive content generation

### Risk Mitigations

| Risk | Mitigation |
|---|---|
| User submits PII in query | Form placeholder warning: "Ne adj meg személyes adatokat a kutatási témában" |
| AI provider uses prompts for training | Review Kimi K2 T&C pre-launch; Privacy Policy disclosure |
| User disputes result accuracy | Disclaimer in every result email; ToS limitation of liability |
| Data breach | EU region deployment; only email address stored as PII |

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Attitudinal Persona Framework**
Existing synthetic research tools generate personas based on demographic profiles. SwarmSense generates personas based on attitudinal dimensions: risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve. A campaign message that appeals to all age groups may still fail with risk-averse, price-sensitive decision-makers — demographic tools miss this; attitudinal tools surface it.

**2. Swarm Simulation Architecture**
The same query runs across 15–20 parallel LLM instances, each with a distinct system prompt defining a unique attitudinal profile. This treats LLM inference as a population sampling mechanism, not a question-answering mechanism — producing a simulated distribution of market sentiment rather than a single AI answer.

**3. Hungarian Market First Mover**
No direct Hungarian-language synthetic market research tool exists at launch. Prompts, personas, and result interpretation are purpose-built for Hungarian cultural context — not a localization of a global tool.

**4. Hypothesis Database as Compounding Moat**
Every run contributes structured data: topics tested, persona types that reject which arguments, conditions that convert skeptics. Over time this becomes a proprietary benchmark — "similar hypotheses are rejected 68% of the time for price reasons" — that no new entrant can replicate without equivalent run volume.

### Market Context & Competitive Landscape

Global adjacent tools: Synthetic Users (US, demographic-based, English only), various GPT-wrapper audience simulation tools (single LLM response, no persona diversity). No known competitor in the Hungarian market with attitudinal simulation at this price point ($0.002/run).

Primary competition is not a tool — it is inaction: marketing managers currently skip validation or rely on intuition.

### Validation Approach

- **Attitudinal framework validity:** First 50 runs reviewed manually; if personas produce near-identical responses, prompt engineering is adjusted before scaling
- **Swarm simulation reliability:** Partial result handling planned — timeout results in partial delivery with count noted
- **Market fit signal:** Qualifier question data from first 150 subscribers validates whether attitudinal framework addresses real pain points

### Innovation Risk Mitigation

| Risk | Mitigation |
|---|---|
| Attitudinal personas produce homogeneous responses | Manual review of first 50 runs; prompt iteration before scale |
| LLM output degrades for niche Hungarian topics | Hungarian cultural context in all prompts; manual spot-check protocol |
| Global competitor enters Hungarian market | Hypothesis database moat; local brand trust advantage |
| Swarm approach is replicable | Speed advantage; first-mover; database moat compounds over time |

## SaaS Platform Specific Requirements

### Tenant Model

| Phase | Model | Description |
|---|---|---|
| MVP | No accounts | 1 free run per verified email, no login |
| V2 | Individual accounts | Token-based paid access, single user per account |
| V3 | Team accounts | Shared token pools, multiple seats, agency billing |

### Subscription Tiers & Entitlements (V2)

| Tier | Price | Tokens | Included Entitlements | Billing Rules |
|---|---|---|---|---|
| Starter | 990 HUF | 10 | Single-user account, run history access, standard email support | One-time purchase, tokens never expire, no auto-renew |
| Value | 3 990 HUF | 50 | Starter entitlements + priority processing queue during peak periods | One-time purchase, tokens never expire, no auto-renew |
| Pro | 9 990 HUF | 150 | Value entitlements + early-access feature flags and referral unlock | One-time purchase, tokens never expire, no auto-renew |

### Token Rules (V2)

- 1 run consumes 1 token at run initiation
- Runs rejected due to monthly API hard limit do not consume tokens
- Failed runs with fewer than 12 persona outputs trigger automatic token credit restoration
- Free-to-paid conversion point: "already used" blocking screen presents token purchase options

### RBAC Matrix (MVP/V2/V3)

| Role | Phase | Permissions |
|---|---|---|
| Visitor | MVP+ | Submit query and audience input, view value proposition and sample output |
| Verified User | MVP+ | Verify email, answer qualifier survey, receive and view own results, use unsubscribe link |
| Waitlist User | MVP+ | Join Pro waitlist, receive waitlist updates, request removal from waitlist |
| Paid User | V2+ | Purchase tokens, run analyses with available balance, view own run history |
| Operator/Admin | MVP+ | View run log, qualifier responses, delivery/open metrics, cost alerts, process deletion requests |

**Access boundary rule:** Non-operator users can access only their own records and outcomes; operator access is restricted to operational and compliance needs.

### Integration List

| Integration | Purpose | Phase |
|---|---|---|
| Kimi K2 API (Moonshot AI) | Persona engine — primary LLM | MVP |
| Claude API (Anthropic) | Persona engine — fallback/premium model | MVP |
| Supabase (EU region) | Database: users, runs, qualifier responses, token balances | MVP |
| Resend | Transactional email: magic link, result email, follow-up sequence | MVP |
| Vercel | Frontend hosting (Next.js) | MVP |
| Railway | Backend hosting (FastAPI) | MVP |
| Plausible Analytics | Privacy-first analytics, GDPR-compliant, no cookie consent required | MVP |
| Sentry | Error tracking, API timeout monitoring, partial result alerts | MVP |
| Stripe | Token package purchases | V2 |

### Implementation Considerations

- **Token flow (V2):** Form submitted → email verified → token balance checked → if sufficient: run initiates, token deducted → result email sent; if insufficient: purchase prompt shown
- **Stripe scope (V2):** One-time payments only; webhook confirms payment → Supabase credits tokens
- **Cost control:** $50/month hard limit enforced at FastAPI level; Sentry alert at 80% of limit; runs rejected (not silently dropped) when limit reached

## Functional Requirements

### Query Submission

- **FR1:** Visitors can submit a research query by providing a research topic and a target audience description
- **FR2:** Visitors can view rotating example queries on the submission form to understand the expected input format
- **FR3:** Visitors can view a product value proposition and an example result preview above the primary submission CTA on desktop and mobile before submitting a query

### Identity Verification & Access Control

- **FR4:** Visitors can provide their email address to receive their analysis results
- **FR5:** The system can determine whether an email address has previously been used for a free analysis
- **FR6:** First-time users can receive a magic link to their email address to verify identity before analysis processing begins
- **FR7:** Returning users whose email address has already been used for a free analysis can view a blocking message indicating the free run has already been used
- **FR8:** Returning users can view a Pro tier waitlist signup option on the blocking screen
- **FR35:** Returning users can submit their email address to join the Pro tier waitlist, and the system stores the waitlist signup with a timestamp
- **FR9:** Users can provide explicit consent to data processing and marketing communications at the point of email capture
- **FR36:** After magic link verification, users can answer a 2-question qualifier survey (role and primary use case) before analysis processing begins; responses are stored linked to the verified email address

### Persona Engine

- **FR10:** The system can generate 15–20 distinct AI personas for a given target audience based on five attitudinal dimensions: risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve
- **FR11:** The system can run a research query against all generated personas in parallel
- **FR12:** The system can deliver a partial result when 1-8 personas fail to respond within the processing timeout, requiring at least 12 completed personas and displaying the delivered persona count in the result
- **FR13:** The persona generation system produces persona responses that reflect Hungarian market context — including Hungarian consumer behaviors, local market references, and Hungarian-language idioms — confirmed by operator spot-check of the first 50 runs showing ≥90% culturally relevant output

### Result Delivery

- **FR14:** Users can receive their analysis results via email after identity verification and processing completion
- **FR15:** Result emails can include an aggregate sentiment score indicating how many personas support or reject the submitted hypothesis
- **FR16:** Result emails can include individual persona cards, each showing the persona's stance, primary argument, and the condition under which they would change their mind
- **FR17:** Result emails can display a top-of-email consensus alert when at least 15 of 20 personas align on support or rejection
- **FR18:** Result emails can include an interpretive disclaimer clarifying that results are AI-generated synthetic simulations, not real human research
- **FR19:** Result emails can include a closing reflection question ("Mit tennél másképp ennek alapján?") and a single next-step call-to-action
- **FR20:** Users can reply to result emails to contact the operator directly

### User Communication

- **FR21:** The system can send a magic link verification email to new users
- **FR22:** The system can send a 3-email automated follow-up sequence at day 1, day 3, and day 7 after analysis delivery, each promoting the Pro tier waitlist signup
- **FR23:** The system can include a functional unsubscribe option in all automated marketing emails
- **FR24:** Users can unsubscribe from all marketing communications

### Processing Status

- **FR25:** Users can view processing states (Queued, Running Personas, Composing Result, Completed) with refresh at least every 5 seconds, and can view a delayed notice if processing exceeds 120 seconds

### Operator & Administration

- **FR26:** The operator can view a log of all submitted queries and their processing status
- **FR27:** The operator can view qualifier question responses associated with each verified email address
- **FR28:** The system can alert the operator when API spend reaches 80% of the monthly hard limit
- **FR29:** The system can enforce a hard monthly API cost limit and reject or queue new runs when the limit is reached
- **FR30:** The operator can monitor email delivery success rates and open rates

### Legal & Compliance

- **FR31:** Visitors can access the Privacy Policy before submitting their email address
- **FR32:** Visitors can access the Terms of Service before submitting their email address
- **FR33:** Users can submit a personal data deletion request via email, receive an acknowledgement within 15 minutes, and receive completion confirmation within 7 calendar days
- **FR34:** The system can display a form warning instructing users not to include personally identifiable information in their research topic or target audience description

## Non-Functional Requirements

### Performance

- **NFR1:** The system shall render the landing page within 3 seconds for p95 visits on a 50 Mbps connection, as measured daily by synthetic web performance checks
- **NFR2:** The system shall complete form submission to processing-started confirmation within 2 seconds for p95 submissions under normal load, as measured by backend request timing logs
- **NFR3:** The system shall deliver magic link verification emails within 60 seconds for >=95% of requests, as measured by transactional email event timestamps
- **NFR4:** The system shall deliver result emails within 120 seconds of successful verification for p95 completed runs, as measured by run lifecycle and email dispatch logs
- **NFR5:** The system shall deliver partial results with at least 12 persona outputs when full completion exceeds 120 seconds, as measured by run output-count logs

### Security

- **NFR6:** The system shall enforce TLS 1.2+ for 100% of user-facing and API traffic, as measured by weekly transport-security scans
- **NFR7:** The system shall encrypt all stored user and run data at rest with provider-managed encryption, as verified by quarterly infrastructure configuration audits
- **NFR8:** The system shall expire magic link tokens exactly 24 hours after issuance, as verified by automated authentication integration tests
- **NFR9:** The system shall prevent cross-user access to query data and result data with 0 unauthorized-access incidents, as measured by access-control audit logs
- **NFR10:** The system shall enforce per-user data isolation so users can access only their own records, as verified by authorization test suites on each release
- **NFR11:** The system shall store only email address as PII during MVP, with 0 persisted names, phone numbers, or payment data, as measured by monthly schema and data-retention audits

### Reliability

- **NFR12:** The system shall maintain a transactional email delivery success rate of >=95% per rolling 7-day window, as measured by provider delivery events
- **NFR13:** The system shall log 100% of failed and partially failed runs with error code and timestamp metadata, as measured by weekly run-log completeness checks
- **NFR14:** The system shall keep non-run features operational when the monthly API limit is reached, blocking only new run initiation, as verified by limit-reached scenario tests
- **NFR15:** The system shall capture unhandled exceptions and API timeout events within 60 seconds of occurrence, as measured by error-monitoring ingest timestamps

### Scalability & Cost Control

- **NFR16:** The system shall enforce a hard monthly API spend cap of $50 and reject new runs at cap with explicit user feedback, as measured by monthly spend and rejection logs
- **NFR17:** The system shall send an automated operator alert within 60 seconds after spend reaches 80% of the monthly cap, as measured by alert event timestamps
- **NFR18:** The system shall support doubling concurrent run throughput versus baseline without service interruption, as measured by controlled load-test execution each release cycle
- **NFR19:** The system shall support at least 30 concurrent persona engine runs with p95 result delivery <=120 seconds per run, as measured by scheduled concurrency load tests

### Accessibility

- **NFR20:** The system shall meet WCAG 2.1 AA contrast and keyboard navigation requirements for landing, form, and processing screens, as measured by automated accessibility scans plus quarterly manual audit
- **NFR21:** The system shall present 100% of user-facing content and user-visible error messages in Hungarian during MVP, as measured by release checklist localization review
