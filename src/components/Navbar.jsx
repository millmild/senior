import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();

  // ✅ menu ต้องประกาศก่อน
  const menu = [
    { name: "Home", path: "/" },
    { name: "Senior Database", path: "/database" },
    { name: "Trending", path: "/trending" },
    { name: "Dashboard", path: "/dashboard" },
  ];

  return (
    <div className="bg-blue-600 text-white px-6 py-3 flex justify-between items-center shadow">
      
      {/* LOGO */}
      <div className="flex items-center gap-3">
        <div className="bg-white text-blue-600 font-bold px-2 py-1 rounded">
          SPR
        </div>
        <span className="font-semibold text-lg">
          Senior Project Repo
        </span>
      </div>

      {/* MENU */}
      <div className="flex gap-6">
        {menu.map((item, i) => (
          <Link
            key={i}
            to={item.path}
            className={`hover:underline ${
              location.pathname === item.path
                ? "underline font-bold text-yellow-300"
                : ""
            }`}
          >
            {item.name}
          </Link>
        ))}
      </div>
    </div>
  );
}