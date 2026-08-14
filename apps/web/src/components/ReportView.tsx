interface ReportViewProps {
  markdown: string;
}

export function ReportView({ markdown }: ReportViewProps) {
  return (
    <div className="report-body">
      {markdown.split("\n").map((line, index) => {
        if (!line.trim()) return <div className="report-space" key={`space-${index}`} />;
        if (line.startsWith("# ")) return <h1 key={line}>{line.slice(2)}</h1>;
        if (line.startsWith("## ")) return <h2 key={line}>{line.slice(3)}</h2>;
        if (line.startsWith("- ")) return <li key={`${line}-${index}`}>{line.slice(2)}</li>;
        return <p key={`${line}-${index}`}>{line}</p>;
      })}
    </div>
  );
}
