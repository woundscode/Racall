import type { Evidence } from '../../lib/api';
import type { SourceDetailController } from './use-source-detail';

export function SourceDocument({
  detail,
  evidence,
}: {
  detail: SourceDetailController;
  evidence?: Evidence;
}) {
  const { tr, fileUrl, shown, document, anchor } = detail;
  return (
    <>
      {fileUrl && shown.type === 'pdf' ? (
        <iframe
          title={tr('source.pdf')}
          className="pdf-preview"
          src={`${fileUrl}#page=${evidence?.location.page || 1}`}
        />
      ) : (
        <div className="source-content">
          {document.isPending ? (
            <div className="skeleton h-40" />
          ) : !document.data?.document ? (
            <p className="muted">{tr('source.processingNotice')}</p>
          ) : (
            document.data.document.elements.map((element, i) => {
              // Stored Python offsets count Unicode code points, not UTF-16 units.
              const characters = evidence?.location.element === i ? Array.from(element.text) : [];
              const highlighted =
                !!evidence &&
                evidence.version === shown.version &&
                evidence.location.element === i &&
                characters
                  .slice(evidence.location.offset_start, evidence.location.offset_end)
                  .join('') === evidence.quote;
              return (
                <div
                  key={i}
                  ref={highlighted ? anchor : undefined}
                  className={`source-element ${highlighted ? 'highlighted' : ''}`}
                >
                  {(element.page || element.section) && (
                    <small>
                      {element.page ? tr('source.page', { page: element.page }) : element.section}
                    </small>
                  )}
                  <p>
                    {highlighted && evidence ? (
                      <>
                        {characters.slice(0, evidence.location.offset_start).join('')}
                        <mark>{evidence.quote}</mark>
                        {characters.slice(evidence.location.offset_end).join('')}
                      </>
                    ) : (
                      element.text
                    )}
                  </p>
                </div>
              );
            })
          )}
        </div>
      )}
    </>
  );
}
