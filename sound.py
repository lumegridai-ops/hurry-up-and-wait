"""Original synthetic Foley for the film; no recordings or samples."""
from pathlib import Path
import numpy as np, wave, json
ROOT=Path(__file__).resolve().parent
SR=48000
DURATION=21
rng=np.random.default_rng(47)
mix=np.zeros((SR*DURATION,2),dtype=np.float64)
def place(start,signal,gain=.1,pan=0):
    i=round(start*SR);n=min(len(signal),len(mix)-i)
    if n<=0:return
    left=np.sqrt((1-pan)/2);right=np.sqrt((1+pan)/2)
    mix[i:i+n,0]+=signal[:n]*gain*left
    mix[i:i+n,1]+=signal[:n]*gain*right
def tone(freq,dur,decay=4):
    t=np.arange(round(dur*SR))/SR
    return (np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*2.01*t))*np.exp(-decay*t)*np.minimum(t/.012,1)
def hum(start,dur,lo,hi,gain,pan):
    t=np.arange(round(dur*SR))/SR
    freq=np.linspace(lo,hi,len(t))
    phase=np.cumsum(freq)/SR*2*np.pi
    env=np.minimum(t/.15,1)*np.minimum((dur-t)/.25,1)
    signal=(np.sin(phase)+.18*np.sin(phase*2)+.08*np.sin(phase*3))*env
    place(start,signal,gain,pan)
# An original understated opening pair.
place(.2,tone(330,.6),.12,-.3)
place(.52,tone(440,.8),.12,.3)
# Red's acceleration, followed by impatient, small mechanical bursts.
hum(52/24,56/24,80,220,.09,.4)
for f in [118,141,167,195,222,247]:
    hum(f/24,.27,140,210,.048,.4)
    place(f/24+.02,tone(850,.09,25),.020,.45)
# Cyan's rolling rhythm is gentler, with the same toy-material sound.
for f in range(74,267,17):
    place(f/24,tone(300,.10,32),.027,-.35)
# Last countdown ticks, then the shared-departure bell.
for f in [203,227,251]:
    place(f/24,tone(640,.12,19),.036,.1)
place(275/24,tone(784,.8,4),.115,0)
place(275/24+.10,tone(1176,.9,4),.075,.1)
hum(276/24,.85,100,160,.028,-.4)
# Ferry winch and a light arrival thunk.
hum(326/24,108/24,62,74,.065,0)
place(434/24,tone(105,.30,13),.10,0)
place(439/24,tone(330,.8,4),.06,-.15)
place(447/24,tone(440,1.1,4),.06,.15)
peak=float(np.max(np.abs(mix)))
# No limiter/clipping; bound peak well below full scale.
if peak>.78:mix*=.78/peak
data=np.round(np.clip(mix,-1,1)*32767).astype("<i2")
path=ROOT/"foley.wav"
with wave.open(str(path),"wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(data.tobytes())
(ROOT/"audio-manifest.json").write_text(json.dumps({"duration":DURATION,"sample_rate":SR,"channels":2,"seed":47,"peak":float(np.max(np.abs(mix))),"source":"Original additive synthesized Foley in sound.py","samples_or_recordings":[]},indent=2))
print(path)
