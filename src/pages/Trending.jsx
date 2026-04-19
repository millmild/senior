// import { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";

// export default function TrendingCluster() {
//   const [clusters, setClusters] = useState({});
//   const navigate = useNavigate();

//   useEffect(() => {
//     fetch("http://127.0.0.1:8000/keywords/cluster")
//       .then((res) => res.json())
//       .then((data) => {
//         console.log("CLUSTERS:", data);
//         setClusters(data || {});
//       })
//       .catch((err) => console.error(err));
//   }, []);

//   const go = (keyword) => {
//     navigate(`/database?query=${keyword}`);
//   };

//   return (
//     <div style={container}>
//       <h1>🧠 AI Topic Clustering</h1>

//       {Object.entries(clusters).map(([category, items]) => (
//         <div key={category} style={{ marginBottom: "30px" }}>
//           <h2>{category}</h2>

//           <div style={grid}>
//             {items.map((k, i) => (
//               <div
//                 key={i}
//                 style={tag}
//                 onClick={() => go(k)}
//               >
//                 {format(k)}
//               </div>
//             ))}
//           </div>
//         </div>
//       ))}
//     </div>
//   );
// }

// /* 🎨 STYLE */

// const container = {
//   padding: "30px",
//   background: "#f5f6f8",
//   minHeight: "100vh",
// };

// const grid = {
//   display: "flex",
//   flexWrap: "wrap",
//   gap: "10px",
// };

// const tag = {
//   background: "#6366f1",
//   color: "white",
//   padding: "8px 12px",
//   borderRadius: "20px",
//   cursor: "pointer",
// };

// /* 🔧 */

// function format(text) {
//   return text
//     .toLowerCase()
//     .replace(/_/g, " ")
//     .replace(/\b\w/g, (c) => c.toUpperCase());
// }


import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function Trending() {
  const [clusters, setClusters] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8000/projects/cluster")
      .then(res => res.json())
      .then(data => {
        console.log("CLUSTERS:", data);
        setClusters(data || {});
      })
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={container}>
      <h1>Trending Projects </h1>

      {Object.entries(clusters).map(([category, items]) => (
        <ClusterRow
          key={category}
          title={category}
          items={items}
          navigate={navigate}
        />
      ))}
    </div>
  );
}

/* 🔥 COMPONENT แถวแบบ Netflix */
function ClusterRow({ title, items, navigate }) {
  const scrollRef = useRef();

  const scroll = (dir) => {
    const el = scrollRef.current;
    const amount = 300;
    if (dir === "left") el.scrollLeft -= amount;
    else el.scrollLeft += amount;
  };

  return (
    <div style={{ marginBottom: "40px", position: "relative" }}>
      <h2 style={{ marginBottom: "10px" }}>{title}</h2>

      {/* ปุ่มเลื่อน */}
      <button onClick={() => scroll("left")} style={leftBtn}>‹</button>
      <button onClick={() => scroll("right")} style={rightBtn}>›</button>

      {/* แถวเลื่อน */}
      <div ref={scrollRef} style={scrollRow}>
        {items.map((p) => (
          <div key={p.id} style={card}>
            <p style={{ fontSize: "12px", color: "#888" }}>{p.year}</p>

            <h3 style={{ margin: "5px 0" }}>{p.title}</h3>

            <p style={{ color: "#555" }}>{p.advisor}</p>

            <div style={{ marginTop: "10px", display: "flex", gap: "5px" }}>
              <button onClick={() => navigate(`/project/${p.id}`)} style={btn}>
                Detail
              </button>

              <button onClick={() => navigate(`/similar/${p.id}`)} style={btn}>
                Similar
              </button>

              <button
                onClick={() => p.file_url && window.open(p.file_url)}
                style={btn}
              >
                Open
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* 🎨 STYLE */

const container = {
  padding: "30px",
  background: "#f5f6f8",
  minHeight: "100vh",
};

const scrollRow = {
  display: "flex",
  overflowX: "auto",
  gap: "15px",
  scrollBehavior: "smooth",
};

const card = {
  minWidth: "250px",
  background: "white",
  padding: "15px",
  borderRadius: "15px",
  flexShrink: 0,
  boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
};

const btn = {
  padding: "5px 10px",
  background: "#f3f4f6",
  border: "none",
  borderRadius: "8px",
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