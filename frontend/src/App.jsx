import { AnimatePresence } from "framer-motion";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Graph from "./pages/Graph.jsx";
import Hero from "./pages/Hero.jsx";
import NotFound from "./pages/NotFound.jsx";
import Profile from "./pages/Profile.jsx";

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
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
