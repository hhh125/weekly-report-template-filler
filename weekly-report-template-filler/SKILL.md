---
name: weekly-report-template-filler
description: generate weekly reports from a user-provided template. use when the user uploads or pastes a weekly report template in txt, markdown, docx, or pdf format and wants chatgpt to extract the structure, preserve headings, wording style, and formatting, then fill the template with weekly updates in later turns. also use when the user wants markdown preview, structured json output, or word export based on the same reusable template in a project.
---

# Weekly Report Template Filler

Use this skill to turn a user-provided weekly report template into a reusable structure, then generate future reports from brief weekly notes.

Assume the user keeps the template in the same Project for long-term reuse. Prefer the most recently confirmed valid template in the current Project context.

## Supported inputs

Accept weekly report templates in these formats:
- `.txt`
- `.md`
- `.docx`
- `.pdf`

Do not treat Excel as a supported input format.

## Core workflow

1. Identify the active template.
   - Prefer the most recently confirmed template in the current Project.
   - If a user uploads a new template, treat it as the active one unless the user says otherwise.
2. Parse the template with `scripts/extract_template.py`.
3. Inspect the extracted schema and confirm the sections look reasonable.
4. Generate one of two output modes with `scripts/fill_weekly_report.py`:
   - `blank`: reusable fillable version
   - `filled`: completed weekly report from the user's notes
5. Return:
   - markdown preview for direct review
   - structured json for downstream use
   - optional `.docx` export using `scripts/export_to_docx.py`

## Template interpretation rules

When parsing a template:
- preserve section titles whenever possible
- preserve section order
- keep fixed wording that appears to be intentional template text
- mark fillable regions with clear placeholders
- infer tone from the template language when possible: `formal`, `concise`, `status-oriented`, or `custom`

When generating output:
- keep section order unchanged
- keep heading wording unchanged unless the user asks to optimize it
- map the user's weekly notes into the most relevant sections
- expand rough bullet points into polished weekly-report language when appropriate
- do not fabricate facts, dates, blockers, deliverables, or achievements
- if required content is missing, leave a clear placeholder instead of guessing

## Output requirements

For every completed generation, prefer returning these artifacts:
1. Markdown preview
2. Structured JSON summary with sections and rendered content
3. Word export when requested

### Blank mode

Use when the user wants a fillable version or a reusable skeleton.
- replace variable content with placeholders
- keep the original structure
- keep placeholders concise and human-readable

### Filled mode

Use when the user provides weekly notes and wants a completed report.
- place content under the most relevant section
- preserve the user's tone when possible
- keep the output directly usable with minimal edits

## Missing information rules

If required information is missing:
- do not invent content
- leave a placeholder in the missing section
- optionally include a brief note after the report only when necessary

## Multiple-template rules

If multiple templates appear in the same Project:
1. prefer the most recently confirmed valid template
2. if two templates conflict, briefly say so and use the most recent one
3. if one file is a completed report and another is a blank template, use the blank template for structure and the completed report only as a tone reference

## Scripts

- `scripts/utils.py`
  - reads and normalizes text from txt, md, docx, and pdf files
- `scripts/extract_template.py`
  - converts a template into normalized schema json
- `scripts/fill_weekly_report.py`
  - renders markdown preview and structured json in blank or filled mode
- `scripts/export_to_docx.py`
  - exports markdown to a `.docx` file

Refer to `references/template-schema.md` for the normalized schema.

## UI resource

Use `assets/ui/WeeklyReportTemplateUI.tsx` as the reference UI for a three-step flow:
1. Upload template
2. Paste weekly notes and choose mode
3. Review markdown/json and export to Word

## Final checks

Before returning a result:
- confirm every major template section is present
- confirm content was mapped to the correct section as well as possible
- confirm no unsupported facts were added
- confirm missing data remains visibly unfilled
