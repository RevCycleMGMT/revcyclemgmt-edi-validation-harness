# Website Card Copy

## Card Title

EDI Validation Harness

## Short Description

Tests synthetic X12 files before they touch a clearinghouse route.

## Button Text

View EDI Validation Harness

## Public Repo

https://github.com/RevCycleMGMT/revcyclemgmt-edi-validation-harness

## Long Description

RevCycleMGMT validates synthetic 837, 835, 999, 277CA, 270/271, 276/277, and 275 transaction files for required segments, control-number consistency, and clean folder-level readiness reporting. This proves the implementation discipline needed before connecting to API-enabled clearinghouse, payer-direct, or custom EDI routes.

## Buyer Takeaway

The goal is simple: catch structural EDI problems early, explain them clearly, and keep avoidable claim workflow rework out of the launch path.

## Proof Points

- Generated SVG coverage report rendered from the synthetic fixture folder.
- Ten transaction families covered: 837P, 837I, 835, 999, 277CA, 270, 271, 276, 277, and 275.
- Intentional failure fixtures show missing required segment and control-number mismatch reporting.
- JSON output is ready for CI, implementation review, dashboards, or workqueue routing.
