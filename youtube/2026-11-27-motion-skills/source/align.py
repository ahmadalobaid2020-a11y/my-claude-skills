# Build timing.json for a single full-script voice file: whisper word times -> caption segments.
import sys, json, re, subprocess
from faster_whisper import WhisperModel
src=sys.argv[1]
beats=json.load(open("beats.json"))
subprocess.check_call(["ffmpeg","-v","error","-y","-i",src,"-af","loudnorm=I=-14:TP=-1.5","-ar","44100","-ac","1","voice_raw.wav"])
m=WhisperModel("medium",device="cpu",compute_type="int8")
import numpy as np
pcm=subprocess.check_output(["ffmpeg","-v","error","-i","voice_raw.wav","-f","f32le","-ac","1","-ar","16000","-"])
segs,_=m.transcribe(np.frombuffer(pcm,dtype=np.float32),language="ar",word_timestamps=True,vad_filter=False)
W=[(w.start,w.end,w.word.strip()) for s in segs for w in s.words if w.word.strip()]
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","voice_raw.wav"]))
NUM={"56":"ستوخمسين","90":"تسعين","66":"ستةوستين"}
norm=lambda t:len(re.sub(r"[^\w]","",NUM.get(t.strip(),t)))
flat=[t for b in beats for t in b]
import os
spk=[t for b in json.load(open("spoken.json")) for t in b] if os.path.exists("spoken.json") else flat
assert len(spk)==len(flat)
tot=sum(norm(t) for t in spk); wt=sum(norm(w[2]) for w in W)
# cumulative char position of each whisper word start
cum=[];c=0
for w in W: cum.append(c/wt); c+=norm(w[2])
starts=[];c=0
for t in spk:
    f=c/tot; i=min(range(len(W)),key=lambda k:abs(cum[k]-f)); starts.append(i); c+=norm(t)
for k in range(1,len(starts)):
    if starts[k]<=starts[k-1]: starts[k]=min(len(W)-1,starts[k-1]+1)
out=[];k=0
for b in beats:
    S=[]
    for t in b:
        i=starts[k]; j=(starts[k+1]-1) if k+1<len(starts) else len(W)-1
        S.append({"text":t,"start":W[i][0],"end":W[j][1],"heard":" ".join(w[2] for w in W[i:j+1])}); k+=1
    out.append({"start":max(0,S[0]["start"]-0.05),"dur":S[-1]["end"]-S[0]["start"],"segs":S})
json.dump({"beats":out,"total":dur+0.5},open("timing.json","w"),ensure_ascii=False,indent=1)
subprocess.check_call(["ffmpeg","-v","error","-y","-i","voice_raw.wav","-af",f"apad=whole_dur={dur+0.5}","voice.wav"])
print("dur",round(dur,2))
for b in out:
    for s in b["segs"]: print(f'{s["start"]:6.2f}  {s["text"]}  <=  {s["heard"]}')
