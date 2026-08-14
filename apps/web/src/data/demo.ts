import type { ResearchDepth, ResearchRun } from "../types/research";

export const defaultQuestion =
  "Compare Mamba architectures for object detection and identify research gaps";

export function createDemoRun(
  question: string = defaultQuestion,
  depth: ResearchDepth = "standard",
): ResearchRun {
  return {
    id: "run_phase1_demo",
    question,
    depth,
    status: "completed",
    created_at: "2026-08-14T00:00:00Z",
    plan: [
      {
        id: "task_plan",
        title: "Define research scope",
        agent: "Supervisor",
        objective: "Decompose the question and select bounded specialist tasks.",
        status: "completed",
      },
      {
        id: "task_academic",
        title: "Map foundational literature",
        agent: "Academic Research",
        objective: "Identify primary Mamba and visual state-space sources.",
        status: "completed",
      },
      {
        id: "task_web",
        title: "Inspect implementations",
        agent: "Web Research",
        objective: "Compare implementation evidence and detection adaptations.",
        status: "completed",
      },
      {
        id: "task_document",
        title: "Search uploaded documents",
        agent: "Document Research",
        objective: "Retrieve project PDFs when available.",
        status: "skipped",
      },
      {
        id: "task_critic",
        title: "Challenge conclusions",
        agent: "Critic",
        objective: "Find unsupported generalizations and missing comparisons.",
        status: "completed",
      },
      {
        id: "task_verify",
        title: "Verify material claims",
        agent: "Fact Checker",
        objective: "Link every material statement to stored evidence.",
        status: "completed",
      },
    ],
    events: [
      {
        sequence: 1,
        agent: "Supervisor",
        status: "completed",
        summary: "Created a five-stage plan and routed only the specialists needed.",
        duration_ms: 180,
      },
      {
        sequence: 2,
        agent: "Academic Research",
        status: "completed",
        summary: "Mapped selective state-space foundations and visual adaptations.",
        duration_ms: 420,
      },
      {
        sequence: 3,
        agent: "Web Research",
        status: "completed",
        summary: "Collected an object-detection implementation and source metadata.",
        duration_ms: 360,
      },
      {
        sequence: 4,
        agent: "Critic",
        status: "completed",
        summary: "Flagged missing hardware-normalized comparisons.",
        duration_ms: 210,
      },
      {
        sequence: 5,
        agent: "Fact Checker",
        status: "completed",
        summary: "Verified core claims and labelled one conclusion partial.",
        duration_ms: 240,
      },
      {
        sequence: 6,
        agent: "Report",
        status: "completed",
        summary: "Produced an evidence-linked technical brief.",
        duration_ms: 290,
      },
    ],
    sources: [
      {
        id: "src_mamba",
        title: "Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
        source_type: "paper",
        url: "https://arxiv.org/abs/2312.00752",
        publisher: "arXiv",
        year: 2023,
      },
      {
        id: "src_vmamba",
        title: "VMamba: Visual State Space Model",
        source_type: "paper",
        url: "https://arxiv.org/abs/2401.10166",
        publisher: "arXiv",
        year: 2024,
      },
      {
        id: "src_mambayolo",
        title: "Mamba-YOLO: SSMs-Based YOLO for Object Detection",
        source_type: "repository",
        url: "https://github.com/HZAI-ZJNU/Mamba-YOLO",
        publisher: "GitHub",
        year: 2024,
      },
    ],
    claims: [
      {
        id: "claim_linear",
        text: "Selective state-space models are designed to scale linearly with sequence length.",
        verdict: "verified",
        confidence: 0.96,
        source_ids: ["src_mamba"],
      },
      {
        id: "claim_visual",
        text: "Visual Mamba variants adapt state-space scanning to two-dimensional features.",
        verdict: "verified",
        confidence: 0.92,
        source_ids: ["src_vmamba"],
      },
      {
        id: "claim_detection",
        text: "Mamba-based detection is promising, but comparisons are not uniform across compute budgets.",
        verdict: "partial",
        confidence: 0.78,
        source_ids: ["src_vmamba", "src_mambayolo"],
      },
    ],
    metrics: {
      sources_found: 3,
      papers_analyzed: 2,
      claims_verified: 2,
      agents_executed: 6,
      total_duration_ms: 1700,
    },
    report_markdown: `# Research brief

## Executive finding

Mamba-style selective state-space models offer a credible route to long-range visual context with linear sequence scaling. Visual adaptations change how features are scanned in two dimensions, while detection projects integrate those blocks into multi-scale pipelines.

## Evidence

- The foundational selective state-space design motivates input-dependent sequence processing with linear scaling [src_mamba].
- VMamba demonstrates a visual state-space design organized around two-dimensional selective scanning [src_vmamba].
- Mamba-YOLO provides an object-detection implementation that makes the direction directly testable [src_mambayolo].

## Research gaps

- Hardware-normalized latency and memory comparisons.
- Ablations that isolate state-space blocks from training-recipe improvements.
- Boundary-sensitive and small-object evaluation.
- Reproducible deployment studies on edge hardware.

## Limitation

This versioned recruiter snapshot remains available when free providers are sleeping or rate-limited. Live runs disclose their active provider mode.`,
    demo: true,
  };
}

export const demoRun = createDemoRun();
