# Optum-Style API Positioning

Optum's public API documentation is useful because it describes the kind of clearinghouse/API transaction surface RevCycleMGMT must be ready to integrate with.

Official reference:

- https://developer.optum.com/eligibilityandclaims/reference/api-overview

## Publicly Observable API Themes

Based on the public Optum API overview, the Medical Network API surface includes:

- OAuth2 bearer-token authorization.
- X12-to-JSON translation for developer-facing application integration.
- Eligibility workflows for X12 270/271.
- Professional and institutional claim workflows for 837P and 837I.
- Claim status workflows for 276/277.
- Claims responses and reports / ERA mailbox retrieval.
- Payer list or payer finder support.
- Sandbox access for development.

## How RevCycleMGMT Should Talk About This

Safe:

> RevCycleMGMT builds EDI/X12 validation and workflow layers that can prepare teams for clearinghouse API integrations such as Optum/Change Healthcare-style eligibility, claims, claim-status, payer-list, report, and remittance endpoints.

Safe:

> We use synthetic test harnesses before production onboarding so teams can validate transaction structure, control numbers, and workflow behavior without exposing PHI.

Not safe unless formally true:

> RevCycleMGMT is an Optum partner.

> RevCycleMGMT is Optum certified.

> RevCycleMGMT has a live production Optum integration.

> RevCycleMGMT can guarantee payer acceptance.

## Demo Strategy

This repository should stay vendor-neutral. The next vendor-aligned project should be a local sandbox adapter that mimics the shape of common clearinghouse API workflows without using real credentials:

- token request
- eligibility request
- claim validation
- claim submission
- claim status
- payer list lookup
- reports/remittance mailbox

That approach proves engineering readiness without overclaiming a vendor relationship.
