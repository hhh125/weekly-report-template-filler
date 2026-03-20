# Template Schema

Use this normalized schema for extracted weekly report templates.

```json
{
  "template_name": "weekly report",
  "source_type": "txt|md|docx|pdf",
  "tone": "formal|concise|status-oriented|custom",
  "format": "markdown",
  "sections": [
    {
      "id": "section_1",
      "heading": "本周工作",
      "fixed_text": "",
      "placeholder": "[填写本周工作]",
      "required": true
    },
    {
      "id": "section_2",
      "heading": "问题风险",
      "fixed_text": "",
      "placeholder": "[填写问题风险]",
      "required": false
    },
    {
      "id": "section_3",
      "heading": "下周计划",
      "fixed_text": "",
      "placeholder": "[填写下周计划]",
      "required": true
    }
  ]
}
```

## Rules

- `heading` keeps the user's original wording whenever possible.
- `fixed_text` stores section text that should remain unchanged in the reusable template.
- `placeholder` is used in blank mode and when required content is missing.
- `required` indicates whether the section should be flagged when empty.
- `format` remains `markdown` for preview generation even when the source was docx or pdf.

## Mapping guidance

When filling a report, map weekly notes using heading intent where possible.

Common heading categories:
- completed work: 本周工作, 本周完成情况, 进展, progress, completed
- blockers: 风险, 问题, blockers, risks, issues
- next steps: 下周计划, next week, next steps, upcoming
- support needed: 需协调事项, support needed, dependencies

When a note could fit multiple sections, prefer the more specific section.
