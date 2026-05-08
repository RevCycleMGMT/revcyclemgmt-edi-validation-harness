# Implementation Notes

## Scope

This repository intentionally validates synthetic X12 structure only. It is not a replacement for payer companion-guide certification, clearinghouse enrollment, production trading-partner testing, or formal EDI translator certification.

## Current Validation Checks

- Required envelope segments: `ISA`, `GS`, `ST`, `SE`, `GE`, `IEA`.
- Transaction type detection from `ST01`.
- 837P/837I distinction from service-line segment: `SV1` or `SV2`.
- 277CA/277 distinction using available claim-status segments.
- Required transaction-specific segment presence.
- ISA/IEA, GS/GE, and ST/SE control-number matching.
- SE01 transaction segment count.
- Basic claim-line presence when `CLM` exists.
- Folder-level summary reporting for implementation review and demo readiness.

## Next Technical Upgrades

- Companion-guide rule packs by payer or clearinghouse route.
- Multiple ST/SE transaction sets per functional group.
- More detailed loop-level validation.
- JSON report schema for CI/CD use.
- Golden fixtures for rejected 999 and 277CA cases.
- Integration contract for the RevCycleMGMT claims pipeline repository.

## Public Claims Boundary

Safe public claim:

> The harness demonstrates how RevCycleMGMT checks synthetic X12 structure and produces actionable validation reports.

Unsafe public claim unless formally proven:

> Certified for production clearinghouse submission.

> Official Optum integration.

> Guaranteed denial reduction.
