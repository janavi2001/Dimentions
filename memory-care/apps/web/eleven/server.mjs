// apps/web/eleven/server.mjs
import express from "express";
import cors from "cors";
import multer from "multer";
import dotenv from "dotenv";
import { spawn } from "node:child_process";

dotenv.config();

// ---------------------- Express setup ----------------------
const app = express();
app.use(cors({ origin: ["http://localhost:5173", "http://127.0.0.1:5173"] }));
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 25 * 1024 * 1024 },
});

const ELEVEN_API_KEY = process.env.ELEVENLABS_API_KEY;
if (!ELEVEN_API_KEY) console.warn("⚠️ ELEVENLABS_API_KEY missing in .env");

// ---------------------- Utility helpers ----------------------
function isWav(buffer) {
  if (!buffer || buffer.length < 12) return false;
  // RIFF....WAVE
  return (
    buffer[0] === 0x52 && buffer[1] === 0x49 && buffer[2] === 0x46 && buffer[3] === 0x46 &&
    buffer[8] === 0x57 && buffer[9] === 0x41 && buffer[10] === 0x56 && buffer[11] === 0x45
  );
}

function hexdump(buf, n = 16) {
  return Array.from(buf.slice(0, n))
    .map(b => b.toString(16).padStart(2, "0"))
    .join(" ");
}

// Some browsers sometimes emit WebM chunks missing the leading 0x1A of the EBML header.
// Valid: 1A 45 DF A3 ...
// Broken:   45 DF A3 ...
function looksLikeWebmMissingLeadByte(buf) {
  if (!buf || buf.length < 4) return false;
  return buf[0] === 0x45 && buf[1] === 0xDF && buf[2] === 0xA3;
}
function maybeRepairWebm(buf, mime) {
  const isWebm = (mime || "").includes("webm");
  if (!isWebm) return buf;
  if (looksLikeWebmMissingLeadByte(buf)) {
    const fixed = new Uint8Array(buf.length + 1);
    fixed[0] = 0x1A; // prepend missing EBML lead byte
    fixed.set(buf, 1);
    return Buffer.from(fixed);
  }
  return buf;
}

// Transcode any audio into 16 kHz mono WAV (auto-detect container)
function transcodeToWav16kMono(buffer) {
  return new Promise((resolve, reject) => {
    if (isWav(buffer)) return resolve(buffer); // already WAV

    const args = [
      "-hide_banner", "-loglevel", "error",
      "-i", "pipe:0",
      "-ac", "1", "-ar", "16000",
      "-f", "wav", "pipe:1",
    ];
    const ff = spawn("ffmpeg", args);
    const out = [];
    let errText = "";

    ff.stdout.on("data", d => out.push(d));
    ff.stderr.on("data", d => { errText += d.toString(); });
    ff.on("error", reject);
    ff.on("close", code => {
      if (code !== 0) {
        console.error("ffmpeg error:", errText.trim());
        return reject(new Error("ffmpeg exit " + code));
      }
      resolve(Buffer.concat(out));
    });

    ff.stdin.write(buffer);
    ff.stdin.end();
  });
}

// ---------------------- Route ----------------------
app.post("/upload", upload.single("file"), async (req, res) => {
  try {
    const file = req.file;
    if (!file?.buffer) {
      return res.status(400).json({ ok: false, error: "no file" });
    }

    const inMime = (file.mimetype || "").toLowerCase();
    let inBuf = file.buffer;
    let inSize = inBuf.length;
    let head = hexdump(inBuf, 16);

    // Reject obviously tiny chunks (common right after start/stop)
    if (inSize < 1024) {
      return res.status(400).json({ ok: false, error: "tiny chunk", info: { inMime, inSize, head } });
    }

    // Repair common WebM issue (missing leading EBML byte)
    const repaired = maybeRepairWebm(inBuf, inMime);
    if (repaired !== inBuf) {
      inBuf = repaired;
      inSize = inBuf.length;
      head = hexdump(inBuf, 16);
    }

    // 1) Convert to WAV (or pass through if already WAV)
    let wav;
    try {
      wav = await transcodeToWav16kMono(inBuf);
    } catch (e) {
      const fs = await import("node:fs/promises");
      const dump = `/tmp/bad-chunk-${Date.now()}.bin`;
      await fs.writeFile(dump, inBuf);
      console.error(`Saved failing chunk to ${dump} (mime=${inMime}, size=${inSize}, head=${head})`);
      throw e;
    }

    // 2) ElevenLabs STT REST call
    const form = new FormData();
    form.append("model_id", "scribe_v1");
    form.append("file", new Blob([wav], { type: "audio/wav" }), "chunk.wav");

    const r = await fetch("https://api.elevenlabs.io/v1/speech-to-text", {
      method: "POST",
      headers: { "xi-api-key": ELEVEN_API_KEY },
      body: form,
    });

    const txt = await r.text();
    let json;
    try { json = JSON.parse(txt); } catch { json = { raw: txt }; }

    if (!r.ok) {
      return res.status(r.status).json({
        ok: false,
        providerStatus: r.status,
        detail: json,
        info: { inMime, inSize, head, wavBytes: wav.length },
      });
    }

    const text = (json?.text || "").trim();
    return res.json({
      ok: true,
      info: { inMime, inSize, head, wavBytes: wav.length },
      transcription: { text },
    });
  } catch (err) {
    console.error("STT error:", err);
    return res.status(400).json({ ok: false, error: err?.message || "transcription failed" });
  }
});

// ---------------------- Start server ----------------------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Eleven STT server running on http://localhost:${PORT}`));
