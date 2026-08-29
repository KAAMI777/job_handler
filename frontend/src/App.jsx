import { AnimatePresence } from "framer-motion";
import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import CommandLine from "./components/terminal/CommandLine.jsx";
import Hero from "./pages/Hero.jsx";
import NotFound from "./pages/NotFound.jsx";

// Route-split the heavy screens: React Flow and the starfield never load on
// the landing page.
const Graph = lazy(() => import("./pages/Graph.jsx"));
const Profile = lazy(() => import("./pages/Profile.jsx"));

function RouteFallback() {
  return (
    <div style={{ minHeight: "60dvh", display: "grid", placeItems: "center" }}>
      <CommandLine command="load_module" running />
    </div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Suspense fallback={<RouteFallback />}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Hero />} />
          <Route element={<Layout transparentBar />}>
            <Route path="/graph" element={<Graph />} />
          </Route>
          <Route element={<Layout />}>
            <Route path="/profile" element={<Profile />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="scanlines">
        <AnimatedRoutes />
      </div>
    </BrowserRouter>
  );
}
