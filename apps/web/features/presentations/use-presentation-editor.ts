'use client';
import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { api, apiEmpty, ApiError, Material, Presentation, PresentationDraft } from '../../lib/api';
import { registerPendingEdits } from '../../lib/pending-edits';
import { useI18n } from '../../lib/i18n';

/** Editor state only: Python owns drafts, revisions and conflict validation. */
export function usePresentationEditor(
  notebook: string,
  material: Material,
  initial: Presentation,
  report: (message: string) => void,
  scope: 'artifacts' | 'studio',
) {
  const client = useQueryClient();
  const { tr } = useI18n();
  const base = `/notebooks/${notebook}/materials/${encodeURIComponent(material.id)}/presentation`;
  const [document, setDocument] = useState(initial);
  const [saved, setSaved] = useState(initial);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [recovered, setRecovered] = useState(false);
  const [conflict, setConflict] = useState(false);
  const current = useRef(initial);
  const expected = useRef(initial.revision);
  const changed = useRef(false);
  const alive = useRef(true);
  const initialRevision = useRef(initial.revision);
  const writes = useRef<Promise<boolean>>(Promise.resolve(true));
  const saving = useRef<Promise<boolean> | null>(null);
  const reportRef = useRef(report);
  reportRef.current = report;

  useEffect(() => {
    alive.current = true;
    void api<PresentationDraft | null>(`${base}/draft`)
      .then((draft) => {
        if (!alive.current || !draft) return;
        current.current = draft.presentation;
        expected.current = draft.expected_revision;
        changed.current = true;
        setDocument(draft.presentation);
        setDirty(true);
        setRecovered(true);
        setConflict(draft.expected_revision !== initialRevision.current);
      })
      .catch((error) => {
        if (alive.current) reportRef.current(error.message);
      })
      .finally(() => {
        if (alive.current) setLoading(false);
      });
    return () => {
      alive.current = false;
    };
  }, [base]);

  // A second view can save this same material. Refresh only a clean editor;
  // incoming query data must never replace an in-progress local edit.
  useEffect(() => {
    if (loading || changed.current || saving.current || initial.revision <= expected.current)
      return;
    expected.current = initial.revision;
    current.current = initial;
    setDocument(initial);
    setSaved(initial);
  }, [initial, loading]);

  const refresh = (result: Material) => {
    client.setQueryData(['material', notebook, material.id], result);
    void client.invalidateQueries({ queryKey: ['materials', notebook] });
  };
  const writeDraft = (snapshot: Presentation, revision: number) => {
    const task = writes.current.then(async () => {
      try {
        await api(`${base}/draft`, 'PUT', { expected_revision: revision, presentation: snapshot });
        return true;
      } catch (error) {
        if (alive.current) {
          if (error instanceof ApiError && error.status === 409) setConflict(true);
          reportRef.current((error as Error).message);
        }
        return false;
      }
    });
    writes.current = task;
    return task;
  };
  const persist = (): Promise<boolean> => {
    if (saving.current) return saving.current;
    if (!changed.current) return Promise.resolve(true);
    const run = async () => {
      setBusy(true);
      const snapshot = current.current;
      const revision = expected.current;
      try {
        if (!(await writeDraft(snapshot, revision))) return false;
        const result = await api<Material>(base, 'PATCH', {
          expected_revision: revision,
          presentation: snapshot,
        });
        const next = result.presentation!;
        expected.current = next.revision;
        changed.current = current.current !== snapshot;
        current.current = changed.current ? { ...current.current, revision: next.revision } : next;
        if (alive.current) {
          setDocument(current.current);
          setSaved(next);
          setDirty(changed.current);
          setRecovered(false);
          setConflict(false);
        }
        refresh(result);
        return !changed.current;
      } catch (error) {
        if (alive.current) {
          setConflict(error instanceof ApiError && error.status === 409);
          reportRef.current((error as Error).message);
        }
        return false;
      } finally {
        saving.current = null;
        if (alive.current) setBusy(false);
      }
    };
    saving.current = run();
    return saving.current;
  };
  const persistRef = useRef(persist);
  persistRef.current = persist;
  useEffect(() => registerPendingEdits(() => persistRef.current(), scope), [scope]);
  useEffect(() => {
    if (!dirty || busy || loading || conflict || recovered) return;
    const timer = setTimeout(() => {
      void writeDraft(current.current, expected.current);
    }, 500);
    return () => clearTimeout(timer);
  }, [document, dirty, busy, loading, conflict, recovered]);
  useEffect(() => {
    const handler = (event: BeforeUnloadEvent) => {
      if (!changed.current) return;
      event.preventDefault();
      event.returnValue = '';
      void writeDraft(current.current, expected.current);
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [base]);

  const edit = (next: Presentation) => {
    current.current = next;
    changed.current = true;
    setDocument(next);
    setDirty(true);
    setRecovered(false);
  };
  const discard = async () => {
    if (!window.confirm(tr('presentation.discardConfirm'))) return;
    setBusy(true);
    try {
      await writes.current;
      await apiEmpty(`${base}/draft?revision=${expected.current}`, 'DELETE');
      const result = await api<Material>(
        `/notebooks/${notebook}/materials/${encodeURIComponent(material.id)}`,
      );
      const next = result.presentation!;
      expected.current = next.revision;
      current.current = next;
      changed.current = false;
      setDocument(next);
      setSaved(next);
      setDirty(false);
      setRecovered(false);
      setConflict(false);
      refresh(result);
    } catch (error) {
      reportRef.current((error as Error).message);
    } finally {
      if (alive.current) setBusy(false);
    }
  };
  return {
    base,
    document,
    saved,
    dirty,
    busy,
    loading,
    recovered,
    conflict,
    edit,
    persist,
    discard,
  };
}
