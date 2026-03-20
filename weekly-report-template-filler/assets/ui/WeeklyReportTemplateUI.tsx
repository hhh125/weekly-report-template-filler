import React, { useMemo, useState } from "react";

type Section = {
  id: string;
  heading: string;
  fixed_text: string;
  placeholder: string;
  required: boolean;
};

type TemplateSchema = {
  template_name: string;
  source_type: string;
  tone: string;
  format: string;
  sections: Section[];
};

function classifyNotes(raw: string) {
  const lines = raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  return {
    completed: lines.filter((line) => /本周|完成|进展|done|completed|progress/i.test(line)),
    blockers: lines.filter((line) => /风险|问题|阻塞|risk|issue|blocker/i.test(line)),
    next: lines.filter((line) => /下周|计划|next|plan|upcoming/i.test(line)),
    general: lines.filter(
      (line) => !/本周|完成|进展|done|completed|progress|风险|问题|阻塞|risk|issue|blocker|下周|计划|next|plan|upcoming/i.test(line)
    ),
  };
}

function chooseBucket(heading: string): "completed" | "blockers" | "next" | "general" {
  if (/本周|完成|进展|work|done|completed|progress/i.test(heading)) return "completed";
  if (/风险|问题|阻塞|risk|issue|blocker/i.test(heading)) return "blockers";
  if (/下周|计划|next|plan|upcoming/i.test(heading)) return "next";
  return "general";
}

function renderSectionContent(section: Section, notes: string, mode: "blank" | "filled") {
  if (mode === "blank") return section.placeholder;
  const classified = classifyNotes(notes);
  const bucket = chooseBucket(section.heading);
  const selected = classified[bucket].length ? classified[bucket] : classified.general;
  if (!selected.length) return section.placeholder;
  return selected.map((line) => `- ${line}`).join("\n");
}

export default function WeeklyReportTemplateUI() {
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [schema, setSchema] = useState<TemplateSchema | null>(null);
  const [weeklyNotes, setWeeklyNotes] = useState("");
  const [mode, setMode] = useState<"blank" | "filled">("filled");

  const markdownPreview = useMemo(() => {
    if (!schema) return "";
    return schema.sections
      .map((section) => {
        const body = renderSectionContent(section, weeklyNotes, mode);
        const content = section.fixed_text ? `${section.fixed_text}\n${body}` : body;
        return `## ${section.heading}\n${content}`;
      })
      .join("\n\n");
  }, [schema, weeklyNotes, mode]);

  const jsonPreview = useMemo(() => {
    if (!schema) return "";
    return JSON.stringify(
      {
        template_name: schema.template_name,
        mode,
        tone: schema.tone,
        markdown_preview: markdownPreview,
        sections: schema.sections.map((section) => ({
          heading: section.heading,
          required: section.required,
          content: renderSectionContent(section, weeklyNotes, mode),
        })),
      },
      null,
      2
    );
  }, [schema, weeklyNotes, mode, markdownPreview]);

  const handleMockParse = async () => {
    if (!templateFile) return;
    const filename = templateFile.name.toLowerCase();
    const sourceType = filename.split(".").pop() || "txt";
    setSchema({
      template_name: templateFile.name.replace(/\.[^.]+$/, ""),
      source_type: sourceType,
      tone: "formal",
      format: "markdown",
      sections: [
        { id: "section_1", heading: "本周工作", fixed_text: "", placeholder: "[填写本周工作]", required: true },
        { id: "section_2", heading: "问题风险", fixed_text: "", placeholder: "[填写问题风险]", required: false },
        { id: "section_3", heading: "下周计划", fixed_text: "", placeholder: "[填写下周计划]", required: true },
      ],
    });
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <header className="rounded-3xl border p-6 shadow-sm">
        <h1 className="text-3xl font-semibold tracking-tight">Weekly Report Template Filler</h1>
        <p className="mt-2 text-sm text-slate-600">
          Upload a weekly report template, paste this week&apos;s notes, preview the result in Markdown and JSON,
          then export it to Word.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-3xl border p-5 shadow-sm">
          <h2 className="text-lg font-medium">Step 1 · Upload Template</h2>
          <p className="mt-2 text-sm text-slate-600">Supported: txt, md, docx, pdf</p>
          <input
            className="mt-4 block w-full text-sm"
            type="file"
            accept=".txt,.md,.docx,.pdf"
            onChange={(e) => setTemplateFile(e.target.files?.[0] || null)}
          />
          <button
            type="button"
            onClick={handleMockParse}
            className="mt-4 rounded-2xl border px-4 py-2 text-sm font-medium shadow-sm"
          >
            Parse Template
          </button>
          {templateFile && <p className="mt-3 text-sm">Current file: {templateFile.name}</p>}
        </div>

        <div className="rounded-3xl border p-5 shadow-sm">
          <h2 className="text-lg font-medium">Step 2 · Weekly Notes</h2>
          <div className="mt-3 flex flex-wrap gap-4 text-sm">
            <label className="inline-flex items-center gap-2">
              <input type="radio" checked={mode === "filled"} onChange={() => setMode("filled")} />
              Completed Report
            </label>
            <label className="inline-flex items-center gap-2">
              <input type="radio" checked={mode === "blank"} onChange={() => setMode("blank")} />
              Blank Fillable
            </label>
          </div>
          <textarea
            className="mt-4 min-h-[260px] w-full rounded-2xl border p-3 text-sm"
            placeholder="Paste this week's updates here..."
            value={weeklyNotes}
            onChange={(e) => setWeeklyNotes(e.target.value)}
          />
        </div>

        <div className="rounded-3xl border p-5 shadow-sm">
          <h2 className="text-lg font-medium">Step 3 · Export</h2>
          <p className="mt-2 text-sm text-slate-600">
            Export the currently generated Markdown content to a Word document.
          </p>
          <button type="button" className="mt-4 rounded-2xl border px-4 py-2 text-sm font-medium shadow-sm">
            Export Word
          </button>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border p-5 shadow-sm">
          <h2 className="text-lg font-medium">Markdown Preview</h2>
          <pre className="mt-4 whitespace-pre-wrap rounded-2xl bg-slate-50 p-4 text-sm">{markdownPreview}</pre>
        </div>

        <div className="rounded-3xl border p-5 shadow-sm">
          <h2 className="text-lg font-medium">Structured JSON</h2>
          <pre className="mt-4 whitespace-pre-wrap rounded-2xl bg-slate-50 p-4 text-sm">{jsonPreview}</pre>
        </div>
      </section>
    </div>
  );
}
