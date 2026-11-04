'use client';
import type { Evidence, PresentationSlide } from '../../lib/api';
import { useI18n } from '../../lib/i18n';
import { SlideEvidence } from './slide-evidence';

export function SlideFields({
  slide,
  index,
  count,
  disabled,
  saved,
  titleEdited,
  citations,
  cite,
  change,
  move,
  remove,
}: {
  slide: PresentationSlide;
  index: number;
  count: number;
  disabled: boolean;
  saved: PresentationSlide | undefined;
  titleEdited: boolean;
  citations: Evidence[];
  cite: (evidence: Evidence) => void;
  change: (slide: PresentationSlide) => void;
  move: (direction: -1 | 1) => void;
  remove: () => void;
}) {
  const { tr } = useI18n();
  const edited =
    slide.review_state === 'edited' ||
    titleEdited ||
    !saved ||
    slide.title !== saved.title ||
    slide.notes !== saved.notes ||
    JSON.stringify(slide.bullets) !== JSON.stringify(saved.bullets);
  return (
    <fieldset className="presentation-slide" disabled={disabled} data-slide-id={slide.id}>
      <legend>{tr('presentation.slide', { number: index + 1 })}</legend>
      <div className="presentation-slide-actions">
        <button
          type="button"
          className="secondary"
          disabled={index === 0}
          onClick={() => move(-1)}
          aria-label={tr('presentation.moveUp')}
        >
          ↑
        </button>
        <button
          type="button"
          className="secondary"
          disabled={index === count - 1}
          onClick={() => move(1)}
          aria-label={tr('presentation.moveDown')}
        >
          ↓
        </button>
        <button type="button" className="text-button" disabled={count === 1} onClick={remove}>
          {tr('presentation.removeSlide')}
        </button>
      </div>
      <label>
        {tr('presentation.slideTitle')}
        <input
          aria-label={tr('presentation.slideTitle')}
          value={slide.title}
          maxLength={160}
          required
          onChange={(e) => change({ ...slide, title: e.target.value })}
        />
      </label>
      {slide.bullets.map((bullet, n) => (
        <div className="presentation-bullet" key={n}>
          <label>
            {tr('presentation.bullet', { number: n + 1 })}
            <textarea
              aria-label={tr('presentation.bullet', { number: n + 1 })}
              rows={2}
              maxLength={220}
              value={bullet}
              required
              onChange={(e) =>
                change({
                  ...slide,
                  bullets: slide.bullets.map((item, i) => (i === n ? e.target.value : item)),
                })
              }
            />
          </label>
          <button
            type="button"
            className="text-button"
            aria-label={tr('presentation.removeBullet', { number: n + 1 })}
            onClick={() => change({ ...slide, bullets: slide.bullets.filter((_, i) => i !== n) })}
          >
            ×
          </button>
        </div>
      ))}
      {slide.bullets.length < 5 && (
        <button
          type="button"
          className="text-button"
          onClick={() => change({ ...slide, bullets: [...slide.bullets, ''] })}
        >
          {tr('presentation.addBullet')}
        </button>
      )}
      <label>
        {tr('presentation.notes')}
        <textarea
          aria-label={tr('presentation.notes')}
          rows={3}
          maxLength={1200}
          value={slide.notes}
          onChange={(e) => change({ ...slide, notes: e.target.value })}
        />
      </label>
      <SlideEvidence
        evidenceIds={slide.evidence_ids}
        citations={citations}
        edited={edited}
        cite={cite}
      />
    </fieldset>
  );
}
