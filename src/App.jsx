import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import SeniorDatabase from "./pages/Seniordatabase";
import ProjectDetail from "./pages/ProjectDetail";
import Similar from "./pages/Similar";
import Navbar from "./components/Navbar";
import Trending from "./pages/Trending";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} /> {/* ✅ Home */}
        <Route path="/dashboard" element={<Dashboard />} />{" "}
        {/* ✅ Dashboard ใหม่ */}
        <Route path="/database" element={<SeniorDatabase />} />
        <Route path="/project/:id" element={<ProjectDetail />} />
        <Route path="/similar/:id" element={<Similar />} />
        <Route path="/trending" element={<Trending />} />
      </Routes>
    </BrowserRouter>
  );
}
