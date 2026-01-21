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

### 2) Research the Vendor

Once you have the vendor, actively research their public documentation:

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
- Do they use customer data for AI/ML training, will it be user for other purposes?
- What's their deletion process, to facilitate purging user data?
- Encryption at rest and in transit?

**Research tips:**
- Check `vendor.com/legal/dpa`, `vendor.com/trust`, `trust.vendor.com`
- Look in footer links under "Legal" or "Privacy"
- Enterprise vendors may gate docs behind sales; note this

If you can't find something, note it as "Not found publicly - request from vendor."

### 3) Understand the Feature (Open Conversation)

**Before asking structured questions, have an open conversation.** This gives context about the data sensitivity and use case.

After presenting research findings, start with:

```text
I've researched [Vendor]. Here's what I found:
- Data residency options: [US/EU/both/unclear]
- DPA: [Available at URL / Not found]
- Certifications: [SOC 2, ISO 27001, etc.]
- AI/ML training: [Opt-out available / No mention / Explicitly excluded]

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

### 4) Interview: Detailed Questions

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

*(Note: User may provide link to current network diagram for reference)*

### 5) Validate Claims

Cross-check user statements against research:

| User Says | Validate By |
|-----------|-------------|
| "Data stays in US/EU" | Verify data residency options in DPA |
| "They're SOC 2 certified" | Find on trust page |
| "They don't train on our data" | Check privacy policy, DPA, AI terms |
| "We can delete anytime" | Verify deletion process in docs |
| "Encryption at rest" | Check security page |

**Flag discrepancies:**
```text
Note: You mentioned [X], but their documentation says [Y].
This needs clarification before proceeding.
```

### 6) Produce Outputs

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
| Can clients trigger deletion? | Yes / No / Via request |
| Can we request deletion (individual)? | Yes / No |
| Can we request deletion (company-wide)? | Yes / No |
| Deletion process | [Description] |

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
- [ ] Deletion capabilities

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

### 7) File Locations

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

**Control & Deletion**
- [ ] Client opt-out possibility documented
- [ ] Mandatory vs optional clarified
- [ ] Client deletion trigger documented
- [ ] Our deletion request process documented

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
- **Don't send notices**: Drafts only; InfoSec handles notification

## Handoff

After producing outputs:
1. Summarize findings and open items
2. Highlight any discrepancies needing resolution
3. Confirm data locality meets US/EU requirements
4. Remind user that InfoSec handles final validation and client notification
