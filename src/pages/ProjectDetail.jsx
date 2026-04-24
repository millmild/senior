import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function ProjectDetail() {
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  const { id } = useParams();
  const navigate = useNavigate();
  const scrollRef = useRef();

  const [project, setProject] = useState(null);
  const [similar, setSimilar] = useState([]);

  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // ================= SUMMARY =================
  useEffect(() => {
    setLoadingSummary(true);
    fetch(`${API_BASE_URL}/project/${id}/summary`)
      .then((res) => res.json())
      .then((data) => {
        setSummary(data.summary);
        setLoadingSummary(false);
      })
      .catch((err) => {
        console.error(err);
        setLoadingSummary(false);
      });
  }, [id]);
  // ================= LOAD DETAIL =================
  useEffect(() => {
    fetch(`${API_BASE_URL}/project/${id}`)
      .then((res) => res.json())
      .then((data) => setProject(data))
      .catch((err) => console.error(err));
  }, [id]);

  // ================= LOAD SIMILAR =================
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/similar/${id}`)
      .then((res) => res.json())
      .then((data) => setSimilar(data))
      .catch((err) => console.error(err));
  }, [id]);

  // ================= SCROLL =================
  const scroll = (dir) => {
    const container = scrollRef.current;
    const amount = 320;

    if (dir === "left") container.scrollLeft -= amount;
    else container.scrollLeft += amount;
  };

  if (!project) return <p style={{ padding: "30px" }}>Loading...</p>;

  return (
    <div style={container}>
      {/* ================= DETAIL ================= */}
      <h1>{project.title}</h1>

      <p style={info}>
        {project.advisor} • {project.year}
      </p>

      {/* 🏷️ KEYWORDS */}
      <div style={{ margin: "10px 0" }}>
        {project.keywords?.slice(0, 5).map((k, i) => (
          <span key={i} style={tag}>
            {formatTag(k)}
          </span>
        ))}
      </div>

      {/* 📄 ABSTRACT */}
      <p style={{ maxWidth: "800px" }}>{project.abstract}</p>

      {/* 📄 PDF PREVIEW */}
      {project.file_url && (
        <iframe
          src={project.file_url}
          title="PDF"
          width="100%"
          height="500px"
          style={pdf}
        />
      )}
      <div style={summaryBox}>
        <h3 style={{ marginTop: 0, color: "#2c3e50" }}>✨ AI Key Insights</h3>
        {loadingSummary ? (
          <p style={{ color: "#7f8c8d", fontStyle: "italic" }}>
            Analyzing project details...
          </p>
        ) : (
          <div style={summaryContent}>
            {/* This renders the text while preserving newlines from the AI */}
            <pre style={summaryPre}>{summary || "No summary available."}</pre>
          </div>
        )}
      </div>

      {/* ================= SIMILAR ================= */}
      <h2 style={{ marginTop: "20px" }}>🔥 Similar Projects</h2>

      <div style={{ position: "relative" }}>
        <button onClick={() => scroll("left")} style={leftBtn}>
          ‹
        </button>
        <button onClick={() => scroll("right")} style={rightBtn}>
          ›
        </button>

        <div ref={scrollRef} style={scrollContainer}>
          {similar.map((item) => (
            <div
              key={item.id}
              style={card}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = "scale(1.05)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = "scale(1)";
              }}
            >
              {/* YEAR */}
              <p style={year}>📅 {item.year}</p>

              {/* TITLE */}
              <h3>{item.title}</h3>

              {/* ADVISOR */}
              <p style={{ color: "#555" }}>{item.advisor}</p>

              {/* SCORE
              <p style={score}>⭐ {item.similarity?.toFixed(3)}</p> */}

              {/* BUTTONS */}
              <div style={btnRow}>
                <button
                  onClick={() => navigate(`/project/${item.id}`)}
                  style={btn}
                >
                  Detail
                </button>

                <button
                  onClick={() => navigate(`/similar/${item.id}`)}
                  style={btn}
                >
                  Similar
                </button>

                <button
                  onClick={() => {
                    if (item.file_url) {
                      window.open(item.file_url);
                    } else {
                      alert("No file");
                    }
                  }}
                  style={btn}
                >
                  Open
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ================= STYLE ================= */

const container = {
  padding: "30px",
  background: "#f5f6f8",
  minHeight: "100vh",
};

const info = {
  color: "#666",
  marginBottom: "10px",
};

const tag = {
  background: "#e0e7ff",
  padding: "5px 10px",
  borderRadius: "12px",
  fontSize: "12px",
  marginRight: "5px",
};

const pdf = {
  marginTop: "20px",
  marginBottom: "10px", // 👈 Add this line for the gap
  borderRadius: "10px",
  border: "1px solid #ddd",
};

const scrollContainer = {
  display: "flex",
  overflowX: "auto",
  gap: "15px",
  padding: "10px 0",
  scrollBehavior: "smooth",
};

const card = {
  minWidth: "300px",
  background: "white",
  padding: "15px",
  borderRadius: "15px",
  flexShrink: 0,
  cursor: "pointer",
  boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
  transition: "0.2s",
};

const btnRow = {
  marginTop: "10px",
  display: "flex",
  gap: "8px",
};

const btn = {
  padding: "6px 12px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "10px",
  cursor: "pointer",
};

const leftBtn = {
  position: "absolute",
  left: 0,
  top: "40%",
  zIndex: 10,
};

const rightBtn = {
  position: "absolute",
  right: 0,
  top: "40%",
  zIndex: 10,
};

const year = {
  fontSize: "12px",
  color: "#888",
};

const score = {
  fontSize: "12px",
  color: "#888",
};

/* 🔧 FORMAT TAG */

function formatTag(text) {
  return text
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

const summaryBox = {
  backgroundColor: "#f8f9fa",
  padding: "20px",
  borderRadius: "12px",
  border: "1px solid #e1e8ed",
  width: "100%",
  display: "block",
  boxSizing: "border-box",
};

const summaryContent = {
  marginTop: "10px",
};

const summaryPre = {
  whiteSpace: "pre-wrap", // 🔑 Essential: wraps text to next line
  wordBreak: "break-word", // 🔑 Prevents long words from stretching the box
  fontFamily: "inherit", // Makes it look like regular text, not code
  fontSize: "1rem",
  lineHeight: "1.6",
  color: "#34495e",
  margin: 0,
  // 🔑 Fill the container
  width: "100%",
  overflowX: "hidden", // Prevents accidental horizontal scrolling
};
