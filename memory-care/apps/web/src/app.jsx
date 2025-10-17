import React,{useRef,useState} from 'react'
const API=(p)=>`${localStorage.getItem('API_BASE')||'http://localhost:8000'}/${p.replace(/^\//,'')}`
export default function App(){
  const v=useRef(null), c=useRef(null)
  const [id,setId]=useState(null), [reg,setReg]=useState(null), [chunks,setChunks]=useState(null), [ans,setAns]=useState(null), [pid,setPid]=useState('')
  const startCam=async()=>{const s=await navigator.mediaDevices.getUserMedia({video:true}); v.current.srcObject=s}
  const snap=()=>{const ctx=c.current.getContext('2d'); ctx.drawImage(v.current,0,0,c.current.width,c.current.height); return new Promise(r=>c.current.toBlob(b=>r(b),'image/jpeg',0.9))}
  const doIdentify=async()=>{const b=await snap(); const fd=new FormData(); fd.append('face_image',b,'f.jpg'); const r=await fetch(API('/api/identify'),{method:'POST',body:fd}); const j=await r.json(); setId(j); if(j.person_id) setPid(j.person_id)}
  const doRegister=async(name)=>{const b=await snap(); const fd=new FormData(); fd.append('full_name',name||'Unknown'); fd.append('relationship_note',''); fd.append('consent_text',''); fd.append('face_image',b,'f.jpg'); const r=await fetch(API('/api/register'),{method:'POST',body:fd}); const j=await r.json(); setReg(j); if(j.person_id) setPid(j.person_id)}
  const doIngest=async(t)=>{const r=await fetch(API('/api/ingest_conversation'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({person_id:pid,transcript:t})}); const j=await r.json(); setChunks(j)}
  const doAsk=async(q)=>{const r=await fetch(API('/api/ask'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({person_id:pid,question:q})}); const j=await r.json(); setAns(j)}
  return <div style={{fontFamily:'system-ui',padding:24}}>
    <h1>Memory Care (React + Vite)</h1>
    <section style={{border:'1px solid #ddd',borderRadius:12,padding:16,marginBottom:16}}>
      <h2>1) Identify</h2>
      <div style={{display:'flex',gap:16,alignItems:'center',flexWrap:'wrap'}}>
        <video ref={v} autoPlay playsInline width="360" height="270"/><canvas ref={c} width="360" height="270" style={{display:'none'}}/>
        <div><button onClick={startCam}>Start Camera</button> <button onClick={doIdentify}>Capture & Identify</button>
        <div style={{fontSize:12,color:'#666',marginTop:8}}>{id&&<>status: <b>{id.status}</b> {id.confidence!==undefined&&<span style={{marginLeft:8}}>confidence {id.confidence.toFixed(2)}</span>} {id.person_id&&<div>person_id: <code>{id.person_id}</code></div>}</>}</div></div>
      </div>
    </section>
    <section style={{border:'1px solid #ddd',borderRadius:12,padding:16,marginBottom:16}}>
      <h2>2) Register</h2>
      <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
        <input placeholder="Full name" id="fn"/><button onClick={()=>doRegister(document.getElementById('fn').value)}>Register With Current Frame</button>
      </div>
      <div style={{fontSize:12,color:'#666',marginTop:8}}>{reg&&<>registered: {String(reg.ok)} person_id: <code>{reg.person_id}</code></>}</div>
    </section>
    <section style={{border:'1px solid #ddd',borderRadius:12,padding:16,marginBottom:16}}>
      <h2>3) Ingest</h2>
      <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
        <input placeholder="Person ID" value={pid} onChange={e=>setPid(e.target.value)}/>
        <input placeholder="Paste transcript..." id="tx" style={{width:400}}/>
        <button onClick={()=>doIngest(document.getElementById('tx').value)}>Ingest</button>
      </div>
      <div style={{fontSize:12,color:'#666',marginTop:8}}>{chunks&&<>chunks added: {chunks.chunks_added}</>}</div>
    </section>
    <section style={{border:'1px solid #ddd',borderRadius:12,padding:16}}>
      <h2>4) Ask</h2>
      <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
        <input placeholder="Question" id="qq" style={{width:400}}/>
        <button onClick={()=>doAsk(document.getElementById('qq').value)}>Ask</button>
      </div>
      <div style={{marginTop:12}}>{ans&&<div style={{border:'1px solid #eee',borderRadius:8,padding:12}}>Answer: {ans.answer}</div>}</div>
    </section>
  </div>
}
