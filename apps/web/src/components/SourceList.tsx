import { ArrowUpRight, BookOpen, GitBranch } from "lucide-react";

import type { Source } from "../types/research";

interface SourceListProps {
  sources: Source[];
}

export function SourceList({ sources }: SourceListProps) {
  return (
    <section className="panel sources-panel" aria-labelledby="sources-title">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Evidence registry</span>
          <h2 id="sources-title">Sources</h2>
        </div>
        <span className="panel-count">{sources.length} linked</span>
      </div>

      <div className="source-list">
        {sources.map((source) => {
          const Icon = source.source_type === "repository" ? GitBranch : BookOpen;
          return (
            <a href={source.url} target="_blank" rel="noreferrer" className="source" key={source.id}>
              <span className="source-icon" aria-hidden="true">
                <Icon size={17} />
              </span>
              <span className="source-copy">
                <strong>{source.title}</strong>
                <small>
                  {source.publisher} · {source.year} · {source.id}
                </small>
              </span>
              <ArrowUpRight size={16} aria-hidden="true" />
            </a>
          );
        })}
      </div>
    </section>
  );
}
