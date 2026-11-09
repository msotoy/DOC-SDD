---
name: spec-initial-definition
description: "Converts user stories into complete technical spec.md with BDD. USE WHEN: 'create spec from user story', 'BDD spec for', 'technical spec from requirements', 'convert story to spec', 'define technical specification'."
---

# Spec Initial Definition Skill

## Language Handling

**Always respond in the same language the user writes in.**
Detect the user's language from their prompt and use it consistently throughout
your entire response, including examples, explanations, and any generated content.
The internal instructions of this skill are in English for consistency, but
your output language must always match the user's input language.

## Purpose

Convert user stories and requirements into complete technical specification (spec.md) following BDD (Behavior-Driven Development) methodology.

## Activation Triggers

- "create spec from user story" / "crear spec desde historia"
- "BDD spec for [feature]"
- "technical spec from requirements"
- "convert story to spec"
- "define technical specification"
- Provided user story or requirements document

## BDD Structure (MANDATORY)

### Complete spec.md Template

```markdown
# Technical Specification: [Feature Name]

## 1. Overview

### User Story
**As a** [role]
**I want** [feature/action]
**So that** [benefit/value]

### Acceptance Criteria (Gherkin)
```gherkin
Given [initial context]
When [action/event]
Then [expected outcome]
And [additional outcome]
```

## 2. Functional Requirements

### FR-1: [Requirement Name]
**Description**: [What it does]
**Priority**: Must/Should/Could
**Acceptance Criteria**: AC-1, AC-2

### FR-2: [Requirement Name]
...

## 3. Non-Functional Requirements

### NFR-1: Performance
- [Metric]: [Threshold]
- Example: Response time < 200ms for 95th percentile

### NFR-2: Security
- Authentication: [Method]
- Authorization: [Roles]

## 4. API Endpoints (if applicable)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/resource | Create resource | Yes |
| GET | /api/resource/{id} | Get by ID | Yes |

## 5. Data Model

### Entity: [Entity Name]
```json
{
  "id": "uuid",
  "field1": "type",
  "createdAt": "datetime"
}
```

## 6. Dependencies

- [Service/System Name]: [What it provides]
- Example: User Service - provides user authentication

## 7. Edge Cases

| Scenario | Expected Behavior |
|----------|--------------------|
| Invalid input | Return 400 with error message |
| Unauthorized | Return 401 |

## 8. Open Questions

- [ ] Question 1
- [ ] Question 2
```

## Input Formats Accepted

### User Story (Agile/Scrum)
```
As a [role]
I want [feature]
So that [benefit]
```

### Requirements List
```
1. System must allow users to register
2. System must send confirmation email
3. System must validate email uniqueness
```

### Jira/ADO Ticket
```
Summary: User Registration
Description: As a new visitor...
Acceptance Criteria:
- Given I am on registration page
- When I fill form and submit
- Then account is created
```

## Output Artifact

```markdown
# spec.md - [Feature Name]

[Complete BDD specification as shown above]

## Metadata
- **Created**: [date]
- **Version**: 1.0.0
- **Author**: [user/agent]
- **Status**: Draft / Approved
```

## Must Do

- Follow BDD structure (User Story → Acceptance Criteria → Functional Requirements)
- Include both functional and non-functional requirements
- Define API endpoints if applicable
- Document data models (JSON schema)
- List all dependencies
- Identify edge cases
- Use Gherkin syntax for acceptance criteria

## Must Not Do

- Never skip user story section
- Never omit acceptance criteria
- Never create spec without non-functional requirements
- Never forget edge cases
- Never skip data model documentation
