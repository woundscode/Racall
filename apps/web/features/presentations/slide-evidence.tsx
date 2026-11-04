'use client';
import { ArrowUpRight } from '@phosphor-icons/react';
import { Evidence, locationLabel } from '../../lib/api';
import { useI18n } from '../../lib/i18n';

/** Saved passages remain available even after edits invalidate the AI claims. */
export function SlideEvidence({
  evidenceIds,
  citations,
  edited,
  cite,
}: {
  evidenceIds: string[];
  citations: Evidence[];
  edited: boolean;
  cite: (evidence: Evidence) => void;
}) {
  const { tr } = useI18n();
  const sources = citations.filter((evidence) => evidenceIds.includes(evidence.id));
  if (!sources.length) return edited ? <p className="muted">{tr('presentation.edited')}</p> : null;
  return (
    <section className="presentation-slide-evidence">
      <details>
        <summary>{tr('presentation.slideSources')}</summary>
        <ul>
          {sources.map((evidence) => (
            <li key={evidence.id}>
              <button type="button" className="text-button" onClick={() => cite(evidence)}>
                <span>
                  <strong>{evidence.title}</strong>
                  <small>{locationLabel(evidence)}</small>
                </span>
                <ArrowUpRight size={16} aria-hidden="true" />
              </button>
              <blockquote>{evidence.quote}</blockquote>
            </li>
          ))}
        </ul>
      </details>
      {edited && (
        <p className="muted presentation-evidence-note">{tr('presentation.editedSources')}</p>
      )}
    </section>
  );
}
