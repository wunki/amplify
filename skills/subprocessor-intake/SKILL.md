---
name: subprocessor-intake
description: Research and document new subprocessors/vendors for InfoSec review. Researches vendor compliance docs online, interviews about data scope and business justification, validates claims. Covers data locality (US/EU), retention, deletion rights, opt-out options, encryption, certifications. Triggers on "new subprocessor", "add a vendor", "subprocessor intake", "announce a subprocessor", "new third-party service", "vendor intake".
---

# Subprocessor Intake

Research, interview, and document new subprocessors for InfoSec review. This skill actively researches vendor compliance documentation, interviews about our specific usage, and validates claims against public sources.

## When to Use

- Engineering is adding a new third-party vendor or SDK
- A new service will process customer data
- Any integration that requires client notification under DPA obligations

## Is This Actually a Subprocessor?

**First, confirm this is a subprocessor situation.** Not every third-party integration is a subprocessor.

A service IS a subprocessor if:
- It receives customer/company data that is not anonymized
- Even pseudonymized data counts (still counted as a subprocessor)

A service is NOT a subprocessor if:
- It only receives fully anonymized data
- It never touches customer data at all

If not a subprocessor, inform the user and stop. They may still need vendor security review, but not this process.

## Workflow

### 1) Get Vendor Identity

```text
What vendor/service are you looking to add?
Give me the company name and website if you have it.
```

### 2) Get Vendor Scope

Once you have the vendor identity, clarify exactly what you'll be using:

```text
Before I research, I need to understand the scope:

1) What specific product/API will you use?
   (e.g., "ElevenLabs Text-to-Speech API", "Vertex AI Gemini", "Azure OpenAI API")

2) Are you using their managed platform or direct API calls?
   - Managed platform (vendor hosts everything, you use their UI/dashboard)
   - Direct API integration (you call their API from your code)
   - SDK/library (vendor-provided code running in your infrastructure)

3) What pricing tier are you planning to use?
   (Free, Pro, Enterprise, etc. - this affects available features and policies)

4) Which regions will you deploy to?
   - US only
   - EU only
   - Both US and EU
```

**Why this matters:** Many vendors have multiple products with different data handling policies. ElevenLabs API has different retention than ElevenLabs Agents. Vertex AI has different policies than AI Studio. Getting this wrong means researching the wrong documentation.

### 3) Research the Vendor

Once you have the vendor AND scope, actively research their public documentation.

**IMPORTANT: Distinguish API vs Platform Documentation**

Many vendors have multiple products with different policies. Before citing any policy, confirm you're looking at the right docs:

| Documentation Type     | Common URL Patterns                             | Applies To                         |
| ---------------------- | ----------------------------------------------- | ---------------------------------- |
| API/SDK docs           | `/docs/api-reference/`, `/developers/`          | Direct API integration             |
| Platform docs          | `/docs/platform/`, `/docs/agents/`, `/console/` | Managed services, hosted solutions |
| Consumer/Creative docs | `/docs/studio/`, `/create/`                     | Often NOT relevant for B2B         |
| Enterprise docs        | `/enterprise/`, `/business/`                    | Enterprise tier features           |

**Example mismatches to avoid:**
- ElevenLabs: API docs vs Agents platform (different retention)
- Google: Vertex AI vs AI Studio (different data handling)
- OpenAI: API vs ChatGPT (very different policies)

**Research the documentation that matches the user's stated scope from step 2.**

| Resource | Common Locations | What to Extract |
|----------|------------------|-----------------|
| **Main website** | Homepage, About | Legal name, HQ location, what they do |
| **DPA** | /legal, /dpa, /terms, Trust Center | DPA availability, GDPR compliance, SCCs |
| **Privacy Policy** | /privacy, /legal | Data retention, deletion rights, data locations |
| **Security/Trust Page** | /security, /trust, trust.vendor.com | SOC 2, ISO 27001, certifications |
| **Data Residency** | DPA, Trust Center, Docs | US/EU hosting options, data center locations |
| **Subprocessor List** | Linked from DPA | Their own subprocessors |

**Key things to find:**
- Can they host in US AND EU separately? (critical for data locality)
- What certifications do they have?
- Are there specific endpoints or services we would use from this subprocessor?
- What are their data retention policies on the endpoints we would use?
- Do they use customer data for AI/ML training, will it be used for other purposes?
- Encryption at rest and in transit?

**Data Deletion Capabilities (critical):**

We must always be able to delete data. Research these thoroughly:

| Question                                         | Where to Look                                     | Why It Matters                            |
| ------------------------------------------------ | ------------------------------------------------- | ----------------------------------------- |
| Can individual users delete their own data?      | Privacy policy, user docs, settings/account pages | GDPR right to erasure, user control       |
| Can we (the company) request deletion?           | DPA, API docs, admin console docs                 | Our ability to fulfill deletion requests  |
| Can we trigger deletion at company/tenant level? | DPA, enterprise docs, account termination terms   | Offboarding clients, contract termination |
| What's the deletion process?                     | DPA, support docs, API reference                  | Must be documented and reliable           |
| What's the deletion timeline?                    | DPA, privacy policy                               | GDPR requires "without undue delay"       |
| Is deletion complete or just deidentification?   | Privacy policy, DPA fine print                    | True deletion vs. anonymization           |
| Are backups purged?                              | Security docs, DPA                                | Data may persist in backups               |

**Why this matters:** We should never be in a position where we cannot delete data for business or compliance reasons. If a vendor cannot confirm deletion capabilities, flag this as a blocker.

**Research tips:**
- Check `vendor.com/legal/dpa`, `vendor.com/trust`, `trust.vendor.com`
- Look in footer links under "Legal" or "Privacy"
- Enterprise vendors may gate docs behind sales; note this

If you can't find something, note it as "Not found publicly - request from vendor."

### 4) Verify Research Source

**Before proceeding, confirm your research applies to the user's actual integration.**

After completing initial research, pause to validate:

```text
I found the following policies. Quick check that I researched the right docs:

You said you're using: [specific product/API from step 2]
I researched: [document title/URL]
This source covers: [what the documentation is for]

Does this match your integration?
- If yes, we can proceed
- If no, tell me what's different and I'll re-research
```

**Why this step exists:** Platforms often have multiple offerings with different policies. Catching a mismatch early avoids backtracking after the detailed interview.

**Common mismatches:**
- User says "API" but you found platform/console docs
- User says "Enterprise" but you found free tier policies
- User is using a specific service but you found general company policies

If there's a mismatch, go back to step 3 and research the correct documentation before continuing.

### 5) Understand the Feature (Open Conversation)

**Before asking structured questions, have an open conversation.** This gives context about the data sensitivity and use case.

After presenting research findings, start with:

```text
I've researched [Vendor]. Here's what I found:
- Data residency options: [US/EU/both/unclear]
- DPA: [Available at URL / Not found]
- Certifications: [SOC 2, ISO 27001, etc.]
- AI/ML training: [Opt-out available / No mention / Explicitly excluded]
- Data deletion:
  - Individual user deletion: [Self-service / Via request / Not found]
  - Company-level deletion: [API available / Admin console / Via support / Not found]
  - Deletion timeline: [X days / "without undue delay" / Not specified]
  - Backup purging: [Confirmed / Not mentioned]

Before I ask specific questions, tell me about this feature:
- What are you building or enabling with [Vendor]?
- How will users interact with it?
- Walk me through the data flow from a user's perspective.
```

**Listen for:**
- What type of data (text, voice, files, PII, etc.)
- How sensitive the data is
- Whether it's user-generated content or metadata
- The user journey that involves this vendor

This open conversation will inform the specific questions that follow and help you understand context that structured questions might miss.

### 6) Interview: Detailed Questions

Now ask structured questions, but **require detailed answers, not just selections**.

#### Data Scope & Purpose

| Question | Why It Matters |
|----------|----------------|
| What specific data will be stored/processed? | InfoSec needs exact data types |
| What is the purpose of storing this data? | Must explain HOW and WHY in detail |
| What is our required retention period? | Must be a specific duration |
| Will any documents or content be uploaded? | Affects deletion requirements |

```text
1) What specific customer data will flow to [Vendor]?
   Be specific: user IDs, emails, names, file contents, voice recordings,
   usage logs, etc. List each data type.

2) Explain in detail: How and why will this data be used?
   Don't just say "core functionality" - describe the specific use case.
   Example: "Core product functionality - used in the assessment feature
   to support real-time transcription of user voice responses."

3) What is the exact retention period required?
   Give a specific duration (e.g., "30 days", "90 days", "1 year").
   Also explain WHY this duration is needed.
```

#### Access & Control

| Question | Why It Matters |
|----------|----------------|
| Who from our team will access this system? | Access control documentation |
| Can companies opt out of using this? | Client choice requirements |
| What if they say no - is it mandatory? | Product/architecture implications |
| Can clients trigger deletion of their data? | Deletion rights compliance |
| Can we request deletion (individual/company level)? | Our control over data lifecycle |

```text
4) Who from our team will have access to view data in [Vendor]?
   List specific teams/roles.

5) Can a client company opt out of their data going to [Vendor]?
   a) Yes, it's optional - explain how they opt out
   b) No, it's required for the product to work
   c) Partial - they can opt out of [specific feature]

6) If opt-out isn't possible, explain why this is mandatory.
   What breaks if we don't use this vendor for this client?

7) Can clients trigger deletion of their data from [Vendor]?
   a) Yes, self-service - describe how
   b) Yes, via support request - describe process
   c) No direct trigger, but deleted when account closes
   d) Not yet determined - needs product decision
```

#### Business Justification

```text
8) What's the business justification for adding [Vendor]?
   Explain: Why this vendor? Why now? What problem does it solve?
   What happens if we don't add this vendor?

9) Were alternatives evaluated? If yes, which ones and why was
   [Vendor] chosen over them?
```

#### Architecture Impact

```text
10) Does this require updating the network diagram?
    If yes, describe the new data flow.
```

**Current network diagram references:**
- [Figma: Infrastructure Architecture](https://www.figma.com/board/gTZqLqhHVRm5HmtjK9zifV/Infrastructure-Architecture?node-id=0-1&p=f&t=Z6r1oiv0f9pEJ7NP-0)
- [Vanta: Network Diagram](https://app.vanta.com/c/workera.ai/tests/network-diagram?tab=results)

### 7) Validate Claims

Cross-check user statements against research:

| User Says | Validate By |
|-----------|-------------|
| "Data stays in US/EU" | Verify data residency options in DPA |
| "They're SOC 2 certified" | Find on trust page |
| "They don't train on our data" | Check privacy policy, DPA, AI terms |
| "We can delete anytime" | Verify deletion process in docs |
| "Encryption at rest" | Check security page |

**Deletion validation (always verify):**

| Claim                         | How to Verify                                                | Red Flags                                            |
| ----------------------------- | ------------------------------------------------------------ | ---------------------------------------------------- |
| "Users can delete their data" | Find self-service deletion in user docs or privacy policy    | No documented process, "contact support" with no SLA |
| "We can request deletion"     | Check for API endpoint, admin console, or documented process | Only available via legal/support with no timeline    |
| "Deletion is complete"        | DPA should specify true deletion vs. anonymization           | "May retain for legal purposes" without limits       |
| "Backups are purged"          | Security docs or DPA should mention backup retention         | No mention of backup deletion timeline               |

**If deletion capabilities are unclear or insufficient, this is a potential blocker.** We must be able to honor deletion requests from our users and clients.

**Flag discrepancies:**
```text
Note: You mentioned [X], but their documentation says [Y].
This needs clarification before proceeding.
```

### 8) Produce Outputs

Create two documents:

#### Output 1: InfoSec Intake Document

```markdown
# Subprocessor Intake: [Company Name]

**Date:** [Today's date]
**Requested by:** [Person/team]
**Status:** Pending InfoSec Review

---

## Vendor Information

| Field | Value | Source |
|-------|-------|--------|
| Legal Name | | |
| Product/Service | | |
| Website | | |
| HQ Location | | |

## Data Locality

| Region | Available | Source |
|--------|-----------|--------|
| US Hosting | Yes / No / Unknown | [Link] |
| EU Hosting | Yes / No / Unknown | [Link] |
| Data Residency Controls | Yes / No | [Link] |

**Note:** US clients require US-only processing. EU clients require EU-only processing.

## Compliance Documentation

| Document | Status | URL |
|----------|--------|-----|
| DPA | | |
| Privacy Policy | | |
| Security/Trust Page | | |
| Subprocessor List | | |

## Security & Certifications

| Item | Status | Source |
|------|--------|--------|
| SOC 2 Type II | | |
| ISO 27001 | | |
| GDPR Compliant | | |
| Encryption at Rest | | |
| Encryption in Transit | | |
| Other Certs | | |

## AI/ML Training

| Question | Answer | Source |
|----------|--------|--------|
| Do they use customer data for training? | | |
| Can we opt out? | | |

---

## Our Usage

### Feature Overview

**What we're building/enabling:**
[Description from open conversation - what the feature does, how users interact with it]

### Data Scope

**What data will be stored/processed:**
- [List each specific data type]

**Data sensitivity:**
[Text / Voice / Files / PII / Metadata / etc. - note sensitivity level]

**Purpose of data processing (detailed):**
[Full explanation of HOW and WHY - not just a category.
Example: "Core product functionality - used in the assessment feature to support
real-time transcription of user voice responses. The voice data is processed
to generate text transcripts that are stored for review by the user."]

**Who will have access from our team:**
- [Specific roles/teams]

### Integration Method

[SDK / API / Manual integration]

**Data flow description:**
[How data moves from our systems to vendor]

### Business Justification

**Why this vendor:**
[Justification]

**Alternatives considered:**
[List or N/A]

---

## Client Control

| Question | Answer |
|----------|--------|
| Can clients opt out? | Yes / No / Partial |
| If no, why is it mandatory? | [Explanation] |

---

## Data Deletion Capabilities

| Capability                               | Status                             | Process | Source |
| ---------------------------------------- | ---------------------------------- | ------- | ------ |
| Individual user self-service deletion    | Yes / No / Unknown                 |         |        |
| Individual user deletion via our request | Yes / No / Unknown                 |         |        |
| Company/tenant-level deletion            | Yes / No / Unknown                 |         |        |
| Deletion timeline                        | [X days / unspecified]             |         |        |
| Backup purging confirmed                 | Yes / No / Unknown                 |         |        |
| True deletion vs. anonymization          | Deletion / Anonymization / Unknown |         |        |

**Deletion process documentation:**
[Link to vendor docs describing deletion process, or "Not found publicly"]

**Assessment:**
- [ ] We can delete individual user data on request
- [ ] We can delete all data for a client/company
- [ ] Deletion timeline is acceptable
- [ ] No business reason would prevent us from deleting data

**Gaps or concerns:**
[List any deletion capability gaps that need resolution before approval]

---

## Data Retention

| Item | Our Requirement | Vendor Capability | Source |
|------|-----------------|-------------------|--------|
| Retention period | [Specific duration, e.g., "30 days"] | | |
| Why this duration | [Explanation] | | |
| Deletion on termination | | | |

---

## Architecture Impact

**Network diagram update needed:** Yes / No

**Data flow changes:**
[Description if applicable]

---

## Validation Summary

**Verified against public sources:**
- [ ] Data residency options
- [ ] Certifications
- [ ] Encryption standards
- [ ] AI/ML training policy
- [ ] Individual user deletion capability
- [ ] Company-level deletion capability
- [ ] Deletion process and timeline

**Discrepancies or clarifications needed:**
- [List any mismatches]

**Not found publicly (request from vendor):**
- [List items to request]

---

## Open Items

- [ ] [Unknowns to resolve]

## Next Steps

- [ ] InfoSec review
- [ ] Legal review DPA terms
- [ ] Request missing documentation from vendor
- [ ] Confirm data residency meets US/EU requirements
- [ ] Client notification (after approval)
```

#### Output 2: Draft Client Notice

```markdown
# Draft Client Notice: New Subprocessor

**[Company Name]** - [Service Category]

We are adding [Company Name] ([website]) as a subprocessor for [purpose].

**Service:** [What they do for us]

**Data processed:** [Customer data types]

**Data location:**
- US customers: [US data center]
- EU customers: [EU data center]

**Security:** [Key certifications]

**Data retention:** [Period and purpose]

**Effective date:** [Date or TBD]

**Vendor documentation:** [Link to DPA/Trust page]

---
*Draft for InfoSec review. Do not send without approval.*
```

### 9) File Locations

- Intake doc: `docs/subprocessors/intake-[company-name-lowercase].md`
- Create directory if needed
- Ask before writing

---

## Quick Reference: InfoSec Questions Checklist

Use this to ensure nothing is missed:

**Vendor & Compliance**
- [ ] Legal company name
- [ ] Certifications (SOC 2, ISO 27001, etc.)
- [ ] DPA available and reviewed
- [ ] Encryption at rest and in transit

**Data Locality**
- [ ] US hosting available
- [ ] EU hosting available
- [ ] Data residency controls confirmed

**Data Scope**
- [ ] Specific data types documented
- [ ] Purpose of data processing clear
- [ ] Retention period defined
- [ ] AI/ML training policy checked

**Control & Opt-out**
- [ ] Client opt-out possibility documented
- [ ] Mandatory vs optional clarified

**Data Deletion (critical)**
- [ ] Individual user self-service deletion researched
- [ ] Individual user deletion via our request confirmed
- [ ] Company/tenant-level deletion confirmed
- [ ] Deletion process documented
- [ ] Deletion timeline acceptable
- [ ] Backup purging policy verified
- [ ] No business blockers to deletion identified

**Access & Architecture**
- [ ] Internal access roles defined
- [ ] Network diagram update assessed
- [ ] Data flow documented

**Business**
- [ ] Business justification provided
- [ ] Alternatives considered

---

## Anti-patterns

- **Don't skip research**: Always attempt to find public documentation first
- **Don't assume data locality**: Must verify US AND EU options explicitly
- **Don't trust without verifying**: If user says "SOC 2", find the source
- **Don't accept vague data scope**: "User data" is not specific enough
- **Don't skip opt-out question**: Client choice is a real requirement
- **Don't skip deletion research**: Deletion capability is critical; unclear deletion = potential blocker
- **Don't accept "we can delete" without proof**: Find the documented process, API, or admin flow
- **Don't send notices**: Drafts only; InfoSec handles notification

## Handoff

After producing outputs:
1. Summarize findings and open items
2. Highlight any discrepancies needing resolution
3. Confirm data locality meets US/EU requirements
4. Remind user that InfoSec handles final validation and client notification
