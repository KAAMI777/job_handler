import { AnimatePresence } from "framer-motion";
import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import CommandLine from "./components/terminal/CommandLine.jsx";
import { useAuth } from "./lib/auth-context.js";
import Hero from "./pages/Hero.jsx";
import NotFound from "./pages/NotFound.jsx";

// Route-split the heavy screens: React Flow and the starfield never load on
// the landing page; the auth pages carry the glass backdrop + tilt springs.
const Graph = lazy(() => import("./pages/Graph.jsx"));
const Profile = lazy(() => import("./pages/Profile.jsx"));
const Login = lazy(() => import("./pages/Login.jsx"));
const Register = lazy(() => import("./pages/Register.jsx"));

function RouteFallback() {
  return (
    <div style={{ minHeight: "60dvh", display: "grid", placeItems: "center" }}>
      <CommandLine command="load_module" running />
    </div>
  );
}

/** Gate for routes that need a signed-in user. A no-op when auth is not configured. */
function RequireAuth({ children }) {
  const { authRequired, loading, session } = useAuth();
  const location = useLocation();

  if (!authRequired) return children;
  if (loading) return <RouteFallback />;
  if (!session) return <Navigate to="/login" replace state={{ from: location }} />;
  return children;
}

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Suspense fallback={<RouteFallback />}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Hero />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            element={
              <RequireAuth>
                <Layout transparentBar />
              </RequireAuth>
            }
          >
            <Route path="/graph" element={<Graph />} />
          </Route>
          <Route
            element={
              <RequireAuth>
                <Layout />
              </RequireAuth>
            }
          >
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
