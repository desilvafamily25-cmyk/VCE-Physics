import { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist";

/**
 * Toggle-able formula-sheet reference panel -- a consideration Chemistry
 * never needed (VCE Physics problem-solving depends on the supplied formula
 * sheet, which students are permitted to reference throughout the real
 * exam). Deliberately outside the graded interaction layer: it never reads
 * or writes attempt state, so referencing it can never be confused with (or
 * accidentally recorded as) an answer.
 *
 * Renders the paper's own era-correct formula sheet -- extracted from the
 * back of that specific exam PDF, see scripts/generate_paper_assets.py --
 * via the same PDF.js pipeline used for the exam itself, rather than a
 * separate image format, so there's exactly one rendering code path for
 * every VCAA PDF this app shows.
 */
export function FormulaSheetPanel({ url, onClose }: { url: string; onClose: () => void }) {
  const [pdf, setPdf] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    pdfjsLib.getDocument({ url }).promise.then((doc) => {
      if (!cancelled) setPdf(doc);
    });
    return () => {
      cancelled = true;
    };
  }, [url]);

  useEffect(() => {
    if (!pdf) return;
    let cancelled = false;

    (async () => {
      const page = await pdf.getPage(pageNumber);
      const baseViewport = page.getViewport({ scale: 1 });
      const targetWidth = 500;
      const scale = targetWidth / baseViewport.width;
      const viewport = page.getViewport({ scale });
      const canvas = canvasRef.current;
      if (!canvas || cancelled) return;

      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.floor(viewport.width * dpr);
      canvas.height = Math.floor(viewport.height * dpr);
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;
      const context = canvas.getContext("2d");
      if (!context) return;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      await page.render({ canvas, canvasContext: context, viewport }).promise;
    })();

    return () => {
      cancelled = true;
    };
  }, [pdf, pageNumber]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <>
      <div className="formula-drawer-scrim" onClick={onClose} />
      <div className="formula-drawer" role="dialog" aria-label="Formula sheet">
        <div className="formula-drawer-header">
          <h3>Formula sheet</h3>
          <button type="button" className="btn btn-ghost btn-icon" onClick={onClose} aria-label="Close formula sheet">
            ✕
          </button>
        </div>
        <p className="formula-drawer-note">
          For reference only — matches the sheet supplied with this exam. Never graded, never recorded.
        </p>
        <div className="formula-drawer-body">
          {!pdf && <div className="loading">Loading formula sheet…</div>}
          {pdf && <canvas ref={canvasRef} />}
        </div>
        {pdf && pdf.numPages > 1 && (
          <div className="formula-drawer-pager">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={pageNumber <= 1}
              onClick={() => setPageNumber((p) => Math.max(1, p - 1))}
            >
              ← Prev
            </button>
            <span>
              Page {pageNumber} / {pdf.numPages}
            </span>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={pageNumber >= pdf.numPages}
              onClick={() => setPageNumber((p) => Math.min(pdf.numPages, p + 1))}
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </>
  );
}
