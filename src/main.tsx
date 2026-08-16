import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import * as pdfjsLib from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.mjs?url";
import "./styles.css";
import { Shell } from "./app/Shell";
import { DashboardRoute } from "./routes/Dashboard";
import { PastPapersRoute } from "./routes/PastPapers";
import { AttemptRoute } from "./routes/Attempt";
import { ReviewRoute } from "./routes/Review";
import { TopicPracticeRoute } from "./routes/TopicPractice";
import { TopicSessionRoute } from "./routes/TopicSession";
import { ErrorBankRoute } from "./routes/ErrorBank";
import { ProgressRoute } from "./routes/Progress";
import { AuthProvider } from "./auth/AuthContext";
import { AuthGate } from "./auth/AuthGate";

pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

function App() {
  return (
    <AuthProvider>
      <AuthGate>
        <BrowserRouter>
          <Routes>
            <Route element={<Shell />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardRoute />} />
              <Route path="/papers" element={<PastPapersRoute />} />
              <Route path="/review/:paperId" element={<ReviewRoute />} />
              <Route path="/topics" element={<TopicPracticeRoute />} />
              <Route path="/errors" element={<ErrorBankRoute />} />
              <Route path="/progress" element={<ProgressRoute />} />
              {/* Nested inside Shell (not a standalone top-level route) so the
                  main site navigation stays visible during a paper attempt --
                  a student mid-Practice or -Timed attempt can still reach
                  Dashboard/Past Papers/theme toggle/sign-out without the header
                  disappearing. See .topbar's sticky offset in styles.css, which
                  stacks below .shell-nav rather than overlapping it. */}
              <Route path="/attempt/:paperId/:mode" element={<AttemptRoute />} />
              <Route path="/topics/session" element={<TopicSessionRoute />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthGate>
    </AuthProvider>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
