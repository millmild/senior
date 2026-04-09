import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function ProjectCard({ p, onDetail, onSimilar }) {
  const navigate = useNavigate()
  return (
    <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
      <div className="text-xs text-black/60">#{p.id} • {p.year}</div>
      <h3 className="text-lg font-semibold my-1">{p.title}</h3>
      <div className="text-sm text-black/60">Advisor: {p.advisor}</div>
      <div className="my-2 flex flex-wrap gap-2">
        {p.keywords.map(k => (
          <span key={k} className="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-700">{k}</span>
        ))}
      </div>
      <p className="text-sm min-h-[48px]">{p.abstract}</p>
      <div className="flex gap-2 mt-2">
        <button className="px-3 py-1.5 rounded-xl border hover:bg-gray-50" onClick={() => onDetail?.(p.id)}>Detail</button>
        <button className="px-3 py-1.5 rounded-xl border hover:bg-gray-50" onClick={() => onSimilar?.(p.id)}>Similar</button>
        <button className="px-3 py-1.5 rounded-xl border hover:bg-gray-50" onClick={() => navigate('/project/'+p.id)}>Open</button>
      </div>
    </div>
  )
}
