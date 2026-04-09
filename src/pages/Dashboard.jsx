// import { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";

// export default function Dashboard() {
//   const navigate = useNavigate();

//   // ======================
//   // 🔍 SEARCH
//   // ======================
//   const [query, setQuery] = useState("");
//   const [results, setResults] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const handleSearch = async () => {
//     if (!query) return;

//     setLoading(true);

//     try {
//       const res = await fetch("http://127.0.0.1:8000/search", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ query }),
//       });

//       const data = await res.json();
//       setResults(data);
//     } catch (err) {
//       console.error("Search error:", err);
//     }

//     setLoading(false);
//   };

//   // ======================
//   // 👨‍🏫 TOP ADVISORS
//   // ======================
//   const [advisors, setAdvisors] = useState([]);
//   const [year, setYear] = useState(2021);

//   useEffect(() => {
//     fetch("http://127.0.0.1:8000/stats/advisors")
//       .then((res) => res.json())
//       .then((data) => setAdvisors(data));
//   }, []);

//   const filteredAdvisors = advisors
//     .filter((a) => a.year === year)
//     .slice(0, 5);

//   // ======================
//   // 🎨 UI
//   // ======================
//   return (
//     <div className="p-6 bg-gray-100 min-h-screen">
//       <h1 className="text-3xl font-bold mb-6">📊 Dashboard</h1>

//       {/* ================= SEARCH ================= */}
//       <div className="bg-white p-4 rounded-xl shadow">
//         <h2 className="text-lg font-semibold mb-3">🔎 Search Projects</h2>

//         <div className="flex gap-2">
//           <input
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={(e) => {
//               if (e.key === "Enter") handleSearch();
//             }}
//             placeholder="Search เช่น IoT, AI..."
//             className="flex-1 border px-4 py-2 rounded-lg"
//           />

//           <button
//             onClick={handleSearch}
//             className="bg-blue-500 text-white px-4 py-2 rounded-lg"
//           >
//             Search
//           </button>
//         </div>

//         {/* loading */}
//         {loading && (
//           <p className="mt-3 text-gray-500 animate-pulse">
//             🔍 Searching...
//           </p>
//         )}

//         {/* results */}
//         <div className="mt-4">
//           {results.map((item) => (
//             <div
//               key={item.id}
//               onClick={() => navigate(`/project/${item.id}`)}
//               className="p-3 border-b cursor-pointer hover:bg-gray-100"
//             >
//               {item.title}
//             </div>
//           ))}
//         </div>
//       </div>

//       {/* ================= TOP ADVISORS ================= */}
//       <div className="bg-white p-4 mt-6 rounded-xl shadow">
//         <h2 className="text-lg font-semibold mb-3">👨‍🏫 Top Advisors</h2>

//         {/* select year */}
//         <select
//           value={year}
//           onChange={(e) => setYear(Number(e.target.value))}
//           className="border px-3 py-1 rounded mb-4"
//         >
//           <option value={2020}>2020</option>
//           <option value={2021}>2021</option>
//           <option value={2022}>2022</option>
//           <option value={2023}>2023</option>
//         </select>

//         <div className="grid grid-cols-5 gap-4">
//           {filteredAdvisors.map((a, i) => (
//             <div
//               key={i}
//               className="bg-gray-50 p-4 rounded-xl text-center shadow"
//             >
//               <p className="font-bold">#{i + 1}</p>
//               <p>{a.advisor}</p>
//               <p className="text-sm text-gray-500">
//                 {a.count} projects
//               </p>
//             </div>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// }

// import { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";

// export default function Dashboard() {
//   const navigate = useNavigate();

//   // ======================
//   // 🔍 SEARCH
//   // ======================
//   const [query, setQuery] = useState("");
//   const [results, setResults] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const handleSearch = async () => {
//     if (!query.trim()) return;

//     setLoading(true);

//     try {
//       const res = await fetch("http://127.0.0.1:8000/search", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           query: query,
//           year: null,      // 🔥 ต้องใส่
//           advisor: null,   // 🔥 ต้องใส่
//         }),
//       });

//       const data = await res.json();

//       // 🔥 เอาแค่ 10 อันดับ
//       setResults(data.slice(0, 10));
//     } catch (err) {
//       console.error("Search error:", err);
//     }

//     setLoading(false);
//   };

//   // ======================
//   // 👨‍🏫 TOP ADVISORS
//   // ======================
//   const [advisors, setAdvisors] = useState([]);
//   const [year, setYear] = useState(2021);

//   useEffect(() => {
//     fetch("http://127.0.0.1:8000/stats/advisors")
//       .then((res) => res.json())
//       .then((data) => setAdvisors(data));
//   }, []);

//   const filteredAdvisors = advisors
//     .filter((a) => a.year === year)
//     .slice(0, 5);

//   // ======================
//   // 🎨 UI
//   // ======================
//   return (
//     <div className="p-6 bg-gray-100 min-h-screen">
//       <h1 className="text-3xl font-bold mb-6">📊 Dashboard</h1>

//       {/* ================= SEARCH ================= */}
//       <div className="bg-white p-4 rounded-xl shadow">
//         <h2 className="text-lg font-semibold mb-3">🔎 Search Projects</h2>

//         <div className="flex gap-2">
//           <input
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={(e) => {
//               if (e.key === "Enter") handleSearch();
//             }}
//             placeholder="Search เช่น IoT, AI..."
//             className="flex-1 border px-4 py-2 rounded-lg"
//           />

//           <button
//             onClick={handleSearch}
//             className="bg-blue-500 text-white px-4 py-2 rounded-lg"
//           >
//             Search
//           </button>
//         </div>

//         {/* loading */}
//         {loading && (
//           <p className="mt-3 text-gray-500 animate-pulse">
//             🔍 Searching...
//           </p>
//         )}

//         {/* results */}
//         <div className="mt-4">
//           {results.length === 0 && !loading && (
//             <p className="text-gray-400">No results</p>
//           )}

//           {results.map((item) => (
//             <div
//               key={item.id}
//               onClick={() => navigate(`/project/${item.id}`)}
//               className="p-3 border-b cursor-pointer hover:bg-gray-100"
//             >
//               <p className="font-medium">{item.title}</p>
//               <p className="text-sm text-gray-500">
//                 {item.advisor} • {item.year}
//               </p>
//             </div>
//           ))}
//         </div>
//       </div>

//       {/* ================= TOP ADVISORS ================= */}
//       <div className="bg-white p-4 mt-6 rounded-xl shadow">
//         <h2 className="text-lg font-semibold mb-3">👨‍🏫 Top Advisors</h2>

//         <select
//           value={year}
//           onChange={(e) => setYear(Number(e.target.value))}
//           className="border px-3 py-1 rounded mb-4"
//         >
//           <option value={2020}>2020</option>
//           <option value={2021}>2021</option>
//           <option value={2022}>2022</option>
//           <option value={2023}>2023</option>
//         </select>

//         <div className="grid grid-cols-5 gap-4">
//           {filteredAdvisors.map((a, i) => (
//             <div
//               key={i}
//               className="bg-gray-50 p-4 rounded-xl text-center shadow"
//             >
//               <p className="font-bold">#{i + 1}</p>
//               <p>{a.advisor}</p>
//               <p className="text-sm text-gray-500">
//                 {a.count} projects
//               </p>
//             </div>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// }


import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  // ======================
  // 🔍 SEARCH
  // ======================
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const controllerRef = useRef(null); // 🔥 ใช้ cancel request

  const handleSearch = async () => {
    if (!query.trim()) return;

    // 🔥 ยกเลิก request เก่า
    if (controllerRef.current) {
      controllerRef.current.abort();
    }

    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal, // 🔥 สำคัญมาก
        body: JSON.stringify({
          query,
          year: null,
          advisor: null,
        }),
      });

      const data = await res.json();

      setResults(data.slice(0, 10));
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Search error:", err);
      }
    }

    setLoading(false);
  };

  // ======================
  // 👨‍🏫 TOP ADVISORS
  // ======================
  const [advisors, setAdvisors] = useState([]);
  const [year, setYear] = useState(2021);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stats/advisors")
      .then((res) => res.json())
      .then((data) => setAdvisors(data));
  }, []);

  const filteredAdvisors = advisors
    .filter((a) => a.year === year)
    .slice(0, 5);

  // ======================
  // 🎨 UI
  // ======================
  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">📊 Dashboard</h1>

      {/* ================= SEARCH ================= */}
      <div className="bg-white p-4 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-3">🔎 Search Projects</h2>

        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) handleSearch();
            }}
            placeholder="Search เช่น IoT, AI..."
            className="flex-1 border px-4 py-2 rounded-lg"
          />

          <button
            onClick={handleSearch}
            disabled={loading} // 🔥 กันกดซ้ำ
            className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* loading */}
        {loading && (
          <p className="mt-3 text-gray-500 animate-pulse">
            🔍 Searching...
          </p>
        )}

        {/* results */}
        <div className="mt-4">
          {!loading && results.length === 0 && (
            <p className="text-gray-400">No results</p>
          )}

          {results.map((item) => (
            <div
              key={item.id}
              onClick={() => navigate(`/project/${item.id}`)}
              className="p-3 border-b cursor-pointer hover:bg-gray-100"
            >
              <p className="font-medium">{item.title}</p>
              <p className="text-sm text-gray-500">
                {item.advisor} • {item.year}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ================= TOP ADVISORS ================= */}
      <div className="bg-white p-4 mt-6 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-3">👨‍🏫 Top Advisors</h2>

        <select
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
          className="border px-3 py-1 rounded mb-4"
        >
          <option value={2020}>2020</option>
          <option value={2021}>2021</option>
          <option value={2022}>2022</option>
          <option value={2023}>2023</option>
        </select>

        <div className="grid grid-cols-5 gap-4">
          {filteredAdvisors.map((a, i) => (
            <div
              key={i}
              className="bg-gray-50 p-4 rounded-xl text-center shadow"
            >
              <p className="font-bold">#{i + 1}</p>
              <p>{a.advisor}</p>
              <p className="text-sm text-gray-500">
                {a.count} projects
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}