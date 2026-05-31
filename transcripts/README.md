# Transcript Workflow

Model-run transcripts are not required for local task validation, but every
model sweep should write transcript records here.

Recommended path shape:

`transcripts/<job_id>/<task_id>.jsonl`

Each JSONL record should include:

- `task_id`
- `split`
- `scaffold`
- `model`
- `attempt_index`
- `prompt_path`
- `submission_path`
- `score`
- `primary_failure_label`
- `feedback_excerpt`
- `timestamp_utc`

After a run, use `data/failure_label_schema.json` and
`data/failure_labels.csv` to classify failed attempts. The primary label should
be the dominant reason the attempt failed, not every symptom in the transcript.
