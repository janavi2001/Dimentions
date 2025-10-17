import React, { useEffect, useRef, useState } from "react"

const API = (p) => `${localStorage.getItem("API_BASE") || "http://localhost:8000"}/${p.replace(/^\/+/,'')}`

/**
 * Identify component: webcam preview, capture frame, POST to /api/identify.
 *
 * Props:
 *  - onPersonId(personId: string): optional callback when a person_id is recognized
 *
 * Returns: JSX.Element
 */
export default function Identify({ onPersonId }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [status, setStatus] = useState(null)
  const [confidence, setConfidence] = useState(null)
  const [personId, setPersonId] = useState("")
  const [isStarting, setIsStarting] = useState(false)

  useEffect(() => {
    return () => {
      const v = videoRef.current
      if (v && v.srcObject) {
        const tracks = v.srcObject.getTracks()
        tracks.forEach(t => t.stop())
      }
    }
  }, [])

  const startCamera = async () => {
    setIsStarting(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) videoRef.current.srcObject = stream
    } finally {
      setIsStarting(false)
    }
  }

  const snapshotBlob = () => {
    const v = videoRef.current
    const c = canvasRef.current
    if (!v || !c) return null
    const ctx = c.getContext("2d")
    ctx.drawImage(v, 0, 0, c.width, c.height)
    return new Promise((resolve) => c.toBlob(b => resolve(b), "image/jpeg", 0.9))
  }

  const captureAndIdentify = async () => {
    const blob = await snapshotBlob()
    if (!blob) return
    const fd = new FormData()
    fd.append("face_image", blob, "frame.jpg")
    const res = await fetch(API("/api/identify"), { method: "POST", body: fd })
    const j = await res.json()

    setStatus(j.status || null)
    setConfidence(typeof j.confidence === "number" ? j.confidence : null)
    setPersonId(j.person_id || "")

    if (j.person_id && typeof onPersonId === "function") {
      onPersonId(j.person_id)
    }
  }

  const clearResult = () => {
    setStatus(null)
    setConfidence(null)
    setPersonId("")
  }

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
      <h2>Identify</h2>
      <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
        <video ref={videoRef} autoPlay playsInline width="360" height="270" style={{ background: "#000" }} />
        <canvas ref={canvasRef} width="360" height="270" style={{ display: "none" }} />
        <div>
          <button onClick={startCamera} disabled={isStarting}>
            {isStarting ? "Starting..." : "Start Camera"}
          </button>{" "}
          <button onClick={captureAndIdentify}>Capture & Identify</button>{" "}
          <button onClick={clearResult}>Clear</button>
          <div style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
            {status && (
              <>
                status: <b>{status}</b>
                {typeof confidence === "number" && (
                  <span style={{ marginLeft: 8 }}>confidence {confidence.toFixed(2)}</span>
                )}
                {personId && (
                  <div>person_id: <code>{personId}</code></div>
                )}
                {status === "unsure" && (
                  <div style={{ marginTop: 8 }}>
                    <i>If this looks correct, proceed; otherwise, register as new.</i>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
