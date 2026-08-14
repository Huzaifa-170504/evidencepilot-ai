import { Check, CircleMinus, Clock3 } from "lucide-react";

import type { AgentEvent, PlanTask } from "../types/research";

interface AgentTimelineProps {
  plan: PlanTask[];
  events: AgentEvent[];
}

export function AgentTimeline({ plan, events }: AgentTimelineProps) {
  return (
    <section className="panel agent-panel" aria-labelledby="agent-timeline-title">
      <div className="panel-header">
        <div>
          <span className="eyebrow">Orchestration trace</span>
          <h2 id="agent-timeline-title">Agent activity</h2>
        </div>
        <span className="panel-count">{events.length} events</span>
      </div>

      <div className="timeline">
        {events.map((event) => (
          <article className="timeline-event" key={`${event.sequence}-${event.agent}`}>
            <div className={`timeline-marker ${event.status}`}>
              {event.status === "completed" ? <Check size={14} /> : <Clock3 size={14} />}
            </div>
            <div className="timeline-copy">
              <div className="timeline-heading">
                <strong>{event.agent}</strong>
                <span>{event.duration_ms} ms</span>
              </div>
              <p>{event.summary}</p>
            </div>
          </article>
        ))}
      </div>

      <div className="routing-note">
        <CircleMinus size={16} aria-hidden="true" />
        <span>
          {plan.filter((task) => task.status === "skipped").length} specialist skipped by
          conditional routing
        </span>
      </div>
    </section>
  );
}
