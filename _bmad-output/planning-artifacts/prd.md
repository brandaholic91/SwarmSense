---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-e-01-discovery', 'step-e-02-review', 'step-e-03-edit']
lastEdited: '2026-03-19'
editHistory:
  - date: '2026-03-19'
    changes: 'Validation Warning fixes: qualifier collection journey step + FR35/FR36 added; FR13/FR22/FR30 tightened; NFR1/2 measurement methods added; NFR7/10/15/18 impl. leakage removed; NFR19 degradation quantified'
inputDocuments:
  - '_bmad-output/brainstorming/brainstorming-session-2026-03-18-1730.md'
  - 'docs/vazlat.md'
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 1
  projectDocsCount: 1
workflowType: 'prd'
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

### Business Success

| Metric | 4-Week Target | 8-Week Target |
|---|---|---|
| Verified email subscribers | 150 | 400 |
| Daily active runs | 10+ | 30+ |
| Qualifier question completion rate | 65%+ | 65%+ |
| Email open rate (automated sequence) | 35%+ | 30%+ |
| Potential paying users identified | 10 | 35 |

**Decision tree at week 4:**
- 150+ verified emails AND recurring pain point identified → Pro tier development begins
- 150+ verified emails BUT no clear direction → Deep interviews with first 50 subscribers
- Under 150 emails → Launch channel strategy revised, LinkedIn activation intensified

### Technical Success

- Magic link verification flow operates reliably end-to-end
- Persona engine completes 15–20 parallel API calls and delivers results via email within 1–2 minutes
- 1 free run per email address enforced at database level
- Email delivery success rate: 95%+
- API cost hard limit: $50/month (enforced)

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

### Token Model (V2)

- 1 run = 1 token; tokens never expire
- Packages: Starter 10/990 HUF · Value 50/3 990 HUF · Pro 150/9 990 HUF
- Payment processor: Stripe (one-time purchase, no recurring billing)
- Token balance stored in Supabase; deducted at run initiation
- Free-to-paid conversion point: "already used" blocking screen shows token purchase options

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
- **FR3:** Visitors can view a product value proposition and an example result preview on the landing page before submitting a query

### Identity Verification & Access Control

- **FR4:** Visitors can provide their email address to receive their analysis results
- **FR5:** The system can determine whether an email address has previously been used for a free analysis
- **FR6:** First-time users receive a magic link to their email address to verify their identity before analysis processing begins
- **FR7:** Returning users whose email address has already been used for a free analysis see a blocking message indicating this
- **FR8:** Returning users are presented with a Pro tier waitlist signup option on the blocking screen
- **FR35:** Returning users can submit their email address to join the Pro tier waitlist, and the system stores the waitlist signup with a timestamp
- **FR9:** Users can provide explicit consent to data processing and marketing communications at the point of email capture
- **FR36:** After magic link verification, users can answer a 2-question qualifier survey (role and primary use case) before analysis processing begins; responses are stored linked to the verified email address

### Persona Engine

- **FR10:** The system can generate 15–20 distinct AI personas for a given target audience based on five attitudinal dimensions: risk appetite, decision-making style, organizational role, price sensitivity, and technology adoption curve
- **FR11:** The system can run a research query against all generated personas in parallel
- **FR12:** The system can deliver a partial result when one or more personas fail to respond within the processing timeout, noting the actual persona count in the result
- **FR13:** The persona generation system produces persona responses that reflect Hungarian market context — including Hungarian consumer behaviors, local market references, and Hungarian-language idioms — confirmed by operator spot-check of the first 50 runs showing ≥90% culturally relevant output

### Result Delivery

- **FR14:** Users receive their analysis results via email after identity verification and processing completion
- **FR15:** Result emails include an aggregate sentiment score indicating how many personas support or reject the submitted hypothesis
- **FR16:** Result emails include individual persona cards, each showing the persona's stance, primary argument, and the condition under which they would change their mind
- **FR17:** Result emails include a prominent flag when the result is strongly unanimous (15 or more out of 20 personas in agreement)
- **FR18:** Result emails include an interpretive disclaimer clarifying that results are AI-generated synthetic simulations, not real human research
- **FR19:** Result emails include a closing reflection question ("Mit tennél másképp ennek alapján?") and a single next-step call-to-action
- **FR20:** Users can reply to result emails to contact the operator directly

### User Communication

- **FR21:** The system can send a magic link verification email to new users
- **FR22:** Users receive a 3-email automated follow-up sequence at day 1, day 3, and day 7 after analysis delivery, each promoting the Pro tier waitlist signup
- **FR23:** All automated marketing emails include a functional unsubscribe option
- **FR24:** Users can unsubscribe from all marketing communications

### Processing Status

- **FR25:** Users can view the current status of their analysis while it is being processed

### Operator & Administration

- **FR26:** The operator can view a log of all submitted queries and their processing status
- **FR27:** The operator can view qualifier question responses associated with each verified email address
- **FR28:** The system alerts the operator when API spend reaches 80% of the monthly hard limit
- **FR29:** The system enforces a hard monthly API cost limit and rejects or queues new runs when the limit is reached
- **FR30:** The operator can monitor email delivery success rates and open rates

### Legal & Compliance

- **FR31:** Visitors can access the Privacy Policy before submitting their email address
- **FR32:** Visitors can access the Terms of Service before submitting their email address
- **FR33:** Users can submit a personal data deletion request via email
- **FR34:** The submission form warns users not to include personally identifiable information in their research topic or target audience description

## Non-Functional Requirements

### Performance

- **NFR1:** The landing page renders fully within 3 seconds on a 50 Mbps connection as measured by automated performance monitoring targeting a Lighthouse Performance Score ≥ 90
- **NFR2:** Form submission to processing-started confirmation completes within 2 seconds at the 95th percentile under normal load as measured by backend response time logging
- **NFR3:** Magic link verification email is delivered within 60 seconds of email submission
- **NFR4:** Result email is delivered within 2 minutes of successful magic link verification
- **NFR5:** The system delivers partial results (minimum 12 personas) rather than failing entirely if processing exceeds 2 minutes

### Security

- **NFR6:** All data in transit is encrypted via HTTPS/TLS
- **NFR7:** All data at rest is encrypted at the storage level
- **NFR8:** Magic link tokens expire 24 hours after issuance
- **NFR9:** No user's query data or results are accessible to any other user
- **NFR10:** User data access is enforced at the database level — each user can only access their own data, with no cross-user data exposure possible at the query layer
- **NFR11:** The only PII stored in MVP is the user's email address — no names, phone numbers, or payment data

### Reliability

- **NFR12:** Transactional email delivery success rate is 95% or higher
- **NFR13:** All failed or partially failed runs are logged with error details for operator review
- **NFR14:** The system remains operational for all other users when the monthly API cost limit is reached — only new run initiation is blocked
- **NFR15:** All unhandled exceptions and API timeout events are captured by error monitoring within 60 seconds of occurrence

### Scalability & Cost Control

- **NFR16:** The system enforces a hard monthly API spend limit of $50; new runs are rejected (not silently dropped) when the limit is reached
- **NFR17:** The operator receives an automated alert when API spend reaches 80% of the monthly limit
- **NFR18:** The backend service can be horizontally scaled without requiring database schema changes
- **NFR19:** The system supports a minimum of 30 concurrent persona engine runs with p95 result delivery time not exceeding 120 seconds per run

### Accessibility

- **NFR20:** The core user flow (landing page, form, processing screen) meets WCAG 2.1 Level AA contrast and keyboard navigation requirements
- **NFR21:** All user-facing content is in Hungarian; all system error messages presented to users are in Hungarian
