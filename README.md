# RevCycleMGMT EDI Validation Harness

Synthetic, local-first validation harness for EDI/X12 revenue cycle transactions.

This repository proves that RevCycleMGMT can test the structure of claim, eligibility, remittance, claim-status, acknowledgment, and attachment files before they touch a clearinghouse connection.

No PHI. No production payer files. No clearinghouse credentials. No client data.

## What This Proves

For a buyer, this repo demonstrates implementation discipline:

1. X12 files are not treated like random text files.
2. The transaction type is identified from the `ST` segment.
3. Required envelope segments and transaction segments are checked.
4. Control numbers are compared across ISA/IEA, GS/GE, and ST/SE.
5. Bad files produce clear errors that a billing or integration team can act on.
6. The same test harness can later support Optum/Change Healthcare, Availity, Waystar, payer-direct, or custom clearinghouse onboarding without hard-coding one vendor.

## Supported Synthetic Transactions

| Transaction | Purpose |
| --- | --- |
| 837P | Professional claim validation |
| 837I | Institutional claim validation |
| 835 | Remittance and ERA validation |
| 999 | Implementation acknowledgment validation |
| 277CA | Claim acknowledgment validation |
| 270 | Eligibility request validation |
| 271 | Eligibility response validation |
| 276 | Claim status request validation |
| 277 | Claim status response validation |
| 275 | Claim attachment validation |

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest -q
python -m revcyclemgmt_edi_validation validate tests/fixtures/valid_837p.edi
```

## Example Output

```json
{
  "valid": true,
  "transaction_type": "837P",
  "errors": [],
  "warnings": [],
  "segment_count": 11
}
```

## Optum / Clearinghouse API Readiness

Optum public API documentation describes Medical Network APIs that translate standard X12 transactions to JSON, including eligibility 270/271, professional and institutional claims 837P/837I, claim status 276/277, reports/remittance retrieval, payer lists, and sandbox testing.

This repo does not claim a live Optum integration or partnership. It provides the validation layer that should exist before connecting to any clearinghouse API.

Correct public wording:

> RevCycleMGMT builds validation and test harnesses for EDI/X12 transactions used by clearinghouse APIs, including eligibility, claims, acknowledgments, claim status, remittance, payer routing, and attachment workflows.

## Repository Layout

```text
src/revcyclemgmt_edi_validation/
  cli.py              command-line interface
  parser.py           X12 segment parser
  rules.py            transaction required-segment rules
  validator.py        validation engine
tests/
  fixtures/           synthetic X12 examples
  test_validator.py   parser and validation tests
docs/
  website-card-copy.md
  implementation-notes.md
```

## Safety Boundary

This is a public synthetic demo. Do not place real claims, real patient records, payer credentials, clearinghouse credentials, private keys, or production EDI files in this repository.

See:

- `SECURITY.md`
- `COMPLIANCE.md`
- `docs/optum-api-positioning.md`

## License

MIT.
