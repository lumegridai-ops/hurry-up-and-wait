"""Verify actual rendered and encoded media; does not replace visual review."""
from pathlib import Path
import subprocess,json,hashlib,wave
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parent
VIDEO=ROOT/"final"/"hurry-up-and-wait.mp4"
frames=sorted((ROOT/"final"/"frames").glob("frame-*.png"))
expected=[f"frame-{i:04}.png" for i in range(1,505)]
assert [p.name for p in frames]==expected,"Missing or unexpected rendered frame"
sizes=set()
for p in frames:
    with Image.open(p) as im:
        im.verify()
    with Image.open(p) as im:
        sizes.add(im.size)
assert sizes=={(1920,1080)},sizes
cmd=["ffprobe","-v","error","-count_frames","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames,nb_read_frames,sample_rate,channels","-of","json",str(VIDEO)]
result=json.loads(subprocess.check_output(cmd))
v=next(x for x in result["streams"] if x["codec_name"]=="h264")
assert (v["width"],v["height"])==(1920,1080)
assert v["r_frame_rate"]=="24/1"
assert int(v["nb_read_frames"])==504
assert abs(float(result["format"]["duration"])-21)<.01
assert any(x["codec_name"]=="aac" for x in result["streams"])
# FFmpeg decode checks corrupted packets as well as the container header.
subprocess.run(["ffmpeg","-v","error","-i",str(VIDEO),"-f","null","-"],check=True,capture_output=True)
result.update({
 "status":"passed","rendered_png_count":len(frames),
 "video_sha256":hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
 "source_sha256":hashlib.sha256((ROOT/"build.py").read_bytes()).hexdigest(),
 "audio_source_sha256":hashlib.sha256((ROOT/"sound.py").read_bytes()).hexdigest(),
 "blender_file_sha256":hashlib.sha256((ROOT/"hurry-up-and-wait.blend").read_bytes()).hexdigest(),
 "wip_sha256":hashlib.sha256((ROOT/"blender-wip.png").read_bytes()).hexdigest(),
 "checks":["504 valid full-resolution PNGs","24 fps / 21 seconds","H.264 + AAC","full FFmpeg decode"],
 "limits":"Technical media checks only; see independent review for visual/temporal observations."
})
(ROOT/"media-qa.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
