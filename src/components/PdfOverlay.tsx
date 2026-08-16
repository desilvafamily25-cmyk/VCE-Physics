import React, { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist";
import type { Interaction, Rect } from "../data/types";

export type DragState = {
  page: number;
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
};

export type PageSize = { width: number; height: number };

/**
 * Renders the original exam PDF pages with an absolutely-positioned
 * interaction layer on top -- the visual source of truth (the exam content
 * itself is never re-typeset). Renders an arbitrary subset of pages (for
 * Topic Practice, which only needs the pages containing a selected question
 * and its required stimulus) and delegates control rendering to the caller
 * so Timed/Practice/Topic modes can each decide what an interaction looks
 * like without forking the PDF pipeline.
 */
export function PdfOverlay({
  pdf,
  pages,
  interactionsByPage,
  developerMode = false,
  drag = null,
  setDrag,
  setSelectedRect,
  renderControl
}: {
  pdf: pdfjsLib.PDFDocumentProxy;
  pages: number[];
  interactionsByPage: Record<number, Interaction[]>;
  developerMode?: boolean;
  drag?: DragState | null;
  setDrag?: React.Dispatch<React.SetStateAction<DragState | null>>;
  setSelectedRect?: React.Dispatch<React.SetStateAction<Rect | null>>;
  renderControl: (interaction: Interaction, pageSize: PageSize) => React.ReactNode;
}) {
  return (
    <>
      {pages.map((pageNumber) => (
        <PdfPage
          key={pageNumber}
          pdf={pdf}
          pageNumber={pageNumber}
          interactions={interactionsByPage[pageNumber] ?? []}
          developerMode={developerMode}
          drag={drag}
          setDrag={setDrag}
          setSelectedRect={setSelectedRect}
          renderControl={renderControl}
        />
      ))}
    </>
  );
}

function PdfPage({
  pdf,
  pageNumber,
  interactions,
  developerMode,
  drag,
  setDrag,
  setSelectedRect,
  renderControl
}: {
  pdf: pdfjsLib.PDFDocumentProxy;
  pageNumber: number;
  interactions: Interaction[];
  developerMode: boolean;
  drag: DragState | null;
  setDrag?: React.Dispatch<React.SetStateAction<DragState | null>>;
  setSelectedRect?: React.Dispatch<React.SetStateAction<Rect | null>>;
  renderControl: (interaction: Interaction, pageSize: PageSize) => React.ReactNode;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const renderTaskRef = useRef<pdfjsLib.RenderTask | null>(null);
  const [pageSize, setPageSize] = useState({ width: 1, height: 1 });

  useEffect(() => {
    const wrapper = wrapperRef.current;
    if (!wrapper) {
      return;
    }

    let cancelled = false;

    const renderPage = async () => {
      const canvas = canvasRef.current;
      if (!canvas) {
        return;
      }

      const page = await pdf.getPage(pageNumber);
      const baseViewport = page.getViewport({ scale: 1 });
      const targetWidth = Math.min(940, wrapper.parentElement?.clientWidth ?? 940);
      const cssWidth = Math.max(320, targetWidth);
      const scale = cssWidth / baseViewport.width;
      const viewport = page.getViewport({ scale });
      const dpr = window.devicePixelRatio || 1;

      renderTaskRef.current?.cancel();
      canvas.width = Math.floor(viewport.width * dpr);
      canvas.height = Math.floor(viewport.height * dpr);
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;
      wrapper.style.width = `${viewport.width}px`;
      wrapper.style.height = `${viewport.height}px`;
      setPageSize({ width: viewport.width, height: viewport.height });

      const context = canvas.getContext("2d");
      if (!context || cancelled) {
        return;
      }

      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      renderTaskRef.current = page.render({ canvas, canvasContext: context, viewport });
      try {
        await renderTaskRef.current.promise;
      } catch (error) {
        if (!(error instanceof Error && error.name === "RenderingCancelledException")) {
          throw error;
        }
      }
    };

    renderPage();
    const observer = new ResizeObserver(renderPage);
    observer.observe(document.body);

    return () => {
      cancelled = true;
      observer.disconnect();
      renderTaskRef.current?.cancel();
    };
  }, [pdf, pageNumber]);

  const pointFromEvent = (event: React.PointerEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    return {
      x: Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)),
      y: Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height))
    };
  };

  const draftRect =
    drag && drag.page === pageNumber ? normalizeRect(drag.startX, drag.startY, drag.currentX, drag.currentY) : null;

  return (
    <section className="pdf-page" aria-label={`PDF page ${pageNumber}`} ref={wrapperRef}>
      <canvas className="pdf-canvas" ref={canvasRef} />
      <div
        className={developerMode ? "interaction-layer dev-mode" : "interaction-layer"}
        onPointerDown={(event) => {
          if (!developerMode || !setDrag) {
            return;
          }
          const point = pointFromEvent(event);
          event.currentTarget.setPointerCapture(event.pointerId);
          setDrag({ page: pageNumber, startX: point.x, startY: point.y, currentX: point.x, currentY: point.y });
        }}
        onPointerMove={(event) => {
          if (!developerMode || !drag || drag.page !== pageNumber || !setDrag) {
            return;
          }
          const point = pointFromEvent(event);
          setDrag({ ...drag, currentX: point.x, currentY: point.y });
        }}
        onPointerUp={() => {
          if (!developerMode || !drag || drag.page !== pageNumber || !setDrag || !setSelectedRect) {
            return;
          }
          const rect = normalizeRect(drag.startX, drag.startY, drag.currentX, drag.currentY);
          setSelectedRect(roundRect(rect));
          setDrag(null);
        }}
      >
        {interactions.map((item) => (
          <React.Fragment key={item.id}>{renderControl(item, pageSize)}</React.Fragment>
        ))}
        {draftRect && (
          <div
            className="draft-rect"
            style={{
              left: `${draftRect.x * pageSize.width}px`,
              top: `${draftRect.y * pageSize.height}px`,
              width: `${draftRect.width * pageSize.width}px`,
              height: `${draftRect.height * pageSize.height}px`
            }}
          />
        )}
      </div>
    </section>
  );
}

function normalizeRect(x1: number, y1: number, x2: number, y2: number): Rect {
  return {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    width: Math.abs(x2 - x1),
    height: Math.abs(y2 - y1)
  };
}

function roundRect(rect: Rect): Rect {
  return {
    x: Number(rect.x.toFixed(3)),
    y: Number(rect.y.toFixed(3)),
    width: Number(rect.width.toFixed(3)),
    height: Number(rect.height.toFixed(3))
  };
}
