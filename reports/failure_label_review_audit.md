# Failure Label Review Audit

This generated audit checks the committed transcript-review adjudication file against the non-local transcript queue. It verifies queue coverage, label validity, transcript evidence excerpts, and claim-boundary wording. It does not create model results and does not make the smoke rows representative.

## Summary

- checks: `6`
- statuses: `{"pass": 6}`
- areas: `{"claim_boundary": 1, "coverage": 1, "evidence": 1, "labels": 1, "review_process": 1, "schema": 1}`

## Check Table

| check | area | status | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `review_schema` | schema | pass | review rows=3; required_fields_covered=11/11; duplicates=[]; schema_exists=True | The schema records review metadata; it does not imply independent adjudication. | Keep review rows keyed by run_id and update the schema before adding new review fields. |
| `queue_coverage` | coverage | pass | queue_rows=3; review_rows=3; missing_reviews=[]; extra_reviews=[]; model_rows_missing_queue=[] | Coverage is over the tiny committed smoke queue only. | After any provider sweep, regenerate the queue and add review rows before failure-taxonomy summaries. |
| `label_validity` | labels | pass | valid_labels=14; invalid_labels=[]; none_on_failure=[]; run_result_label_mismatches=[] | The review currently agrees with the run-record label; it has not been independently double-coded. | Use a second reviewer for broader sweeps and adjudicate disagreements before reporting distributions. |
| `transcript_evidence` | evidence | pass | evidence_excerpt_missing_or_not_in_transcript=[]; short_rationales=[] | Evidence excerpts are short anchors, not a substitute for full transcript inspection. | Keep transcript files committed and cite concrete transcript text in every review row. |
| `review_metadata` | review_process | pass | reviewers={"codex_internal_review": 3}; bad_confidence=[]; bad_adjudication_flags=[]; adjudication_needed=[] | All current rows are single internal reviews; this is weaker than independent adjudication. | For research claims about failure distributions, require at least two reviewers or an explicit adjudication log. |
| `claim_boundary` | claim_boundary | pass | transcript_packet_mentions_distribution_boundary=True | A reviewed smoke queue can support transcript-provenance claims only, not model-failure prevalence claims. | Keep failure-taxonomy wording caveated until broad, independently adjudicated transcripts are available. |

## Interpretation

`pass` means the committed review rows are internally consistent with the transcript queue and evidence excerpts. It does not mean the labels are independently adjudicated or sufficient for failure-mode distribution claims.
