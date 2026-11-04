'use client';
import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, apiBlob, Evidence, GenerationJob, Material, Presentation } from '../../lib/api';
import { useI18n } from '../../lib/i18n';
import { settlePendingEdits } from '../../lib/pending-edits';
import { AnswerView } from '../chat/answer-view';
import { GenerationJobCard } from '../jobs/generation-job';
import { isActiveJob, useGenerationJobs } from '../jobs/use-generation-jobs';
import { usePresentationEditor } from './use-presentation-editor';
import { PresentationPreview } from './presentation-preview';
import { SlideFields } from './slide-fields';

export function PresentationEditor({
  notebook,
  material,
  document,
  cite,
  report,
  openMaterial,
  editScope,
}: {
  notebook: string;
  material: Material;
  document: Presentation;
  cite: (evidence: Evidence) => void;
  report: (message: string) => void;
  openMaterial: (id: string) => void;
  editScope: 'artifacts' | 'studio';
}) {
  const { tr } = useI18n();
  const client = useQueryClient();
  const editor = usePresentationEditor(notebook, material, document, report, editScope);
  const jobs = useGenerationJobs(notebook, report);
  const [jobId, setJobId] = useState('');
  const [working, setWorking] = useState(false);
  const [exporting, setExporting] = useState('');
  const request = useRef<{ revision: number; id: string } | null>(null);
  const task = useRef(false);
  const matchesOutline = (item: GenerationJob) =>
    item.outline_id === material.id && item.outline_revision === editor.saved.revision;
  const job =
    jobs.data?.find((item) => item.id === jobId && matchesOutline(item)) ||
    jobs.data?.find(matchesOutline);
  const active = !!job && isActiveJob(job);
  const locked = editor.busy || editor.loading || working || active;
  useEffect(() => {
    if (job?.status !== 'completed' || !job.result?.material_id) return;
    void client.invalidateQueries({ queryKey: ['materials', notebook] });
  }, [job?.status, job?.result?.material_id, client, notebook]);
  const generate = async () => {
    if (task.current || editor.dirty || locked || job || jobs.isPending || jobs.isError) return;
    task.current = true;
    setWorking(true);
    const revision = editor.saved.revision;
    if (request.current?.revision !== revision)
      request.current = { revision, id: crypto.randomUUID() };
    try {
      const result = await api<GenerationJob>(`/notebooks/${notebook}/jobs`, 'POST', {
        request_id: request.current.id,
        kind: 'presentation',
        outline_id: material.id,
        outline_revision: revision,
        language: editor.saved.language,
      });
      setJobId(result.id);
      client.setQueryData<GenerationJob[]>(['jobs', notebook], (old) => [
        result,
        ...(old || []).filter((item) => item.id !== result.id),
      ]);
      await client.invalidateQueries({ queryKey: ['jobs', notebook] });
    } catch (error) {
      report((error as Error).message);
    } finally {
      task.current = false;
      setWorking(false);
    }
  };
  const download = async (format: 'pptx' | 'pdf') => {
    if (exporting || editor.dirty || locked) return;
    setExporting(format);
    try {
      const blob = await apiBlob(
        `${editor.base}/export?format=${format}&revision=${editor.saved.revision}`,
      );
      const url = URL.createObjectURL(blob);
      const anchor = window.document.createElement('a');
      anchor.href = url;
      anchor.download = `Racall-${material.id.replace(/[^a-zA-Z0-9_-]/g, '_')}.${format}`;
      window.document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {
      report((error as Error).message);
    } finally {
      setExporting('');
    }
  };
  const move = (index: number, direction: -1 | 1) => {
    const slides = [...editor.document.slides];
    const target = index + direction;
    if (target < 0 || target >= slides.length) return;
    [slides[index], slides[target]] = [slides[target], slides[index]];
    editor.edit({ ...editor.document, slides });
  };
  return (
    <article className="material-view presentation-editor" data-material-id={material.id}>
      <div className="material-heading">
        <div>
          <small>
            {tr(
              editor.document.stage === 'outline' ? 'presentation.outline' : 'presentation.title',
            )}
          </small>
          <h2>{material.title}</h2>
        </div>
        {editor.document.stage === 'slides' && (
          <div className="material-actions">
            {(['pptx', 'pdf'] as const).map((format) => (
              <button
                className="secondary"
                type="button"
                key={format}
                disabled={locked || editor.dirty || !!exporting}
                onClick={() => void download(format)}
              >
                {exporting === format
                  ? tr('presentation.exporting')
                  : tr('presentation.exportFormat', { format: format.toUpperCase() })}
              </button>
            ))}
          </div>
        )}
      </div>
      {material.context_info?.evidence_truncated && (
        <p className="muted" role="status">
          {tr('materials.partialContext')}
        </p>
      )}
      <p className="presentation-notice">
        {tr(
          editor.document.stage === 'outline'
            ? 'presentation.outlineHint'
            : 'presentation.editHint',
        )}
      </p>
      {editor.recovered && (
        <p className="presentation-notice" role="status">
          {tr('presentation.recovered')}
        </p>
      )}
      {editor.conflict && (
        <p className="presentation-notice" role="alert">
          {tr('presentation.conflict')}
        </p>
      )}
      {editor.loading && <p role="status">{tr('common.loading')}</p>}
      <form
        onSubmit={(event) => {
          event.preventDefault();
          void editor.persist();
        }}
      >
        <fieldset disabled={locked} className="presentation-details">
          <label>
            {tr('presentation.deckTitle')}
            <input
              value={editor.document.title}
              maxLength={160}
              required
              onChange={(event) => editor.edit({ ...editor.document, title: event.target.value })}
            />
          </label>
          <label>
            {tr('presentation.template')}
            <select
              aria-label={tr('presentation.template')}
              value={editor.document.template}
              onChange={(event) =>
                editor.edit({
                  ...editor.document,
                  template: event.target.value as Presentation['template'],
                })
              }
            >
              <option value="light">{tr('presentation.light')}</option>
              <option value="dark">{tr('presentation.dark')}</option>
            </select>
          </label>
        </fieldset>
        <div className="presentation-slides">
          {editor.document.slides.map((slide, index) => (
            <SlideFields
              key={slide.id}
              slide={slide}
              index={index}
              count={editor.document.slides.length}
              disabled={locked}
              saved={editor.saved.slides.find((item) => item.id === slide.id)}
              titleEdited={editor.document.title !== editor.saved.title}
              citations={material.answer.citations}
              cite={cite}
              change={(next) =>
                editor.edit({
                  ...editor.document,
                  slides: editor.document.slides.map((item) => (item.id === next.id ? next : item)),
                })
              }
              move={(direction) => move(index, direction)}
              remove={() =>
                editor.edit({
                  ...editor.document,
                  slides: editor.document.slides.filter((item) => item.id !== slide.id),
                })
              }
            />
          ))}
        </div>
        <div className="presentation-save-actions">
          <button className="primary" type="submit" disabled={locked || !editor.dirty}>
            {tr(editor.busy ? 'presentation.saving' : 'presentation.save')}
          </button>
          {editor.dirty && (
            <button
              type="button"
              className="text-button"
              disabled={locked}
              onClick={() => void editor.discard()}
            >
              {tr('presentation.discard')}
            </button>
          )}
          <span role="status" className="muted">
            {tr(editor.dirty ? 'presentation.unsaved' : 'presentation.saved', {
              revision: editor.saved.revision,
            })}
          </span>
        </div>
      </form>
      {editor.document.stage === 'outline' && (
        <div className="presentation-generate">
          <button
            type="button"
            className="primary"
            disabled={locked || editor.dirty || !!job || jobs.isPending || jobs.isError}
            onClick={() => void generate()}
          >
            {tr(working ? 'studio.starting' : 'presentation.generateSlides')}
          </button>
          {editor.dirty && <p className="muted">{tr('presentation.saveFirst')}</p>}
        </div>
      )}
      {job && (
        <GenerationJobCard
          notebook={notebook}
          job={job}
          report={report}
          retried={(next) => setJobId(next.id)}
          openResult={async (next) => {
            if (!(await settlePendingEdits(editScope))) return;
            if (next.result?.material_id) openMaterial(next.result.material_id);
          }}
        />
      )}
      {editor.saved.stage === 'slides' && (
        <PresentationPreview base={editor.base} revision={editor.saved.revision} />
      )}
      {!!material.answer?.citations.length && (
        <AnswerView
          answer={{ ...material.answer, claims: [], message: '', validated: false }}
          cite={cite}
        />
      )}
    </article>
  );
}
