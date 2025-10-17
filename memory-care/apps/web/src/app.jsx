import React, { useState } from "react"
import { Identify } from "./features/identify/"

const API = (p) => `${localStorage.getItem("API_BASE") || "http://localhost:8000"}/${p.replace(/^\/+/,'')}`

export default function App() {
  const [personId, setPersonId] = useState("")
  const [reg, setReg] = useState(null)
  const [chunks, setChunks] = useState(null)
  const [ans, setAns] = useState(null)

  const doRegister = async (fullName) => {
    const video = document.querySelector("video")
    const canvas = document.createElement("canvas")
    canvas.width = 360
    canvas.height = 270
    const ctx = canvas.getContext("2d")
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise((resolve) =>
      canvas.toBlob((b) => resolve(b), "image/jpeg", 0.9)
    )

    const fd = new FormData()
    fd.append("full_name", fullName || "Unknown")
    fd.append("relationship_note", "")
    fd.append("consent_text", "")
    fd.append("face_image", blob, "frame.jpg")
    const res = await fetch(API("/api/register"), { method: "POST", body: fd })
    const j = await res.json()
    setReg(j)
    if (j.person_id) setPersonId(j.person_id)
  }

  const doIngest = async (text) => {
    const res = await fetch(API("/api/ingest_conversation"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_id: personId, transcript: text })
    })
    const j = await res.json()
    setChunks(j)
  }

  const doAsk = async (q) => {
    const res = await fetch(API("/api/ask"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ person_id: personId, question: q })
    })
    const j = await res.json()
    setAns(j)
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>Memory Care (module 1: Identify)</h1>

      <Identify onPersonId={setPersonId} />

      <div style={{ marginTop: 16, border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
        <h2>Register (if unknown)</h2>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <input placeholder="Full name" id="fn" />
          <button onClick={() => doRegister(document.getElementById("fn").value)}>
            Register With Current Frame
          </button>
        </div>
        <div style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
          {reg && <>registered: {String(reg.ok)} person_id: <code>{reg.person_id}</code></>}
        </div>
      </div>

      <div style={{ marginTop: 16, border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
        <h2>Quick test: Ingest → Ask</h2>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <input placeholder="Person ID" value={personId} onChange={(e) => setPersonId(e.target.value)} />
          <input placeholder="Paste transcript..." id="tx" style={{ width: 400 }} />
          <button onClick={() => doIngest(document.getElementById("tx").value)}>Ingest</button>
        </div>
        <div style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
          {chunks && <>chunks added: {chunks.chunks_added}</>}
        </div>

        <div style={{ marginTop: 16 }}>
          <input placeholder="Ask a question…" id="qq" style={{ width: 400 }} />
          <button onClick={() => doAsk(document.getElementById("qq").value)}>Ask</button>
          <div style={{ marginTop: 12 }}>
            {ans && <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 12 }}>Answer: {ans.answer}</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
