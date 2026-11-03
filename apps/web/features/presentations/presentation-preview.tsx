'use client';
import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api';
import { useI18n } from '../../lib/i18n';

type Preview = { pages: string[]; width: number; height: number };
export function PresentationPreview({ base, revision }: { base: string; revision: number }) {
  const { tr } = useI18n();
  const [page, setPage] = useState(0);
  const [url, setUrl] = useState('');
  const query = useQuery({
    queryKey: ['presentation-preview', base, revision],
    queryFn: () => api<Preview>(`${base}/preview?revision=${revision}`),
    retry: false,
  });
  const pages = query.data?.pages || [];
  const index = Math.min(page, Math.max(pages.length - 1, 0));
  const svg = pages[index];
  useEffect(() => {
    if (!svg) {
      setUrl('');
      return;
    }
    const next = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }));
    setUrl(next);
    return () => URL.revokeObjectURL(next);
  }, [svg]);
  return (
    <section className="presentation-preview" aria-label={tr('presentation.preview')}>
      <div className="presentation-preview-heading">
        <h3>{tr('presentation.preview')}</h3>
        {!!pages.length && (
          <label>
            {tr('presentation.page')}
            <select
              aria-label={tr('presentation.page')}
              value={index}
              onChange={(e) => setPage(Number(e.target.value))}
            >
              {pages.map((_, n) => (
                <option key={n} value={n}>
                  {n + 1} / {pages.length}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      <p className="muted">{tr('presentation.savedPreview', { revision })}</p>
      {query.isPending && <p role="status">{tr('common.loading')}</p>}
      {query.error && <p role="alert">{query.error.message}</p>}
      {url && (
        <img
          src={url}
          width={query.data?.width}
          height={query.data?.height}
          alt={tr('presentation.pageAlt', { page: index + 1 })}
        />
      )}
    </section>
  );
}
