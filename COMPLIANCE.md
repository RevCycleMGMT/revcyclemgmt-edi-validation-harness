# Compliance And PHI Boundary

This repository is a public technical demo for synthetic EDI/X12 validation. It is not a compliance certification, legal opinion, clearinghouse certification, payer companion-guide certification, or production trading-partner approval.

## Allowed

- Synthetic X12 examples.
- Synthetic validation reports.
- Public documentation.
- Placeholder payer and submitter identifiers.

## Not Allowed

- PHI.
- Real claim files.
- Real eligibility files.
- Real remittance files.
- Real attachment documents.
- Payer credentials.
- Clearinghouse credentials.
- Client-specific payer IDs or route IDs.
- Private companion-guide exceptions unless they are approved for public release.

## Production Requirements

A production implementation would require:

- Signed agreements where applicable.
- Formal security review.
- HIPAA privacy and security review.
- Role-based access controls.
- Encrypted transport and storage.
- PHI-safe logs.
- Retention and destruction policy.
- Trading-partner testing.
- Payer and clearinghouse companion-guide validation.
- Incident response procedure.

## Public Claim Boundary

Safe public claim:

> This repository demonstrates RevCycleMGMT's synthetic EDI/X12 validation approach.

Unsafe public claim unless separately certified:

> This repository is production-clearinghouse certified.

> This repository is payer certified.

> This repository is a HIPAA compliance certification.
