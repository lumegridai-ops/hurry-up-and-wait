# Hurry Up and Wait

An original 21-second procedural Blender short about two very different journeys to the same ferry departure. Created with disclosed Codex assistance for the RenderJuice Speed contest. **No contest submission has been made.**

## Watch and inspect

- [Watch or download the completed 1080p film](https://github.com/lumegridai-ops/hurry-up-and-wait/releases/download/v0.1.0/hurry-up-and-wait.mp4)
- [Release and verification notes](https://github.com/lumegridai-ops/hurry-up-and-wait/releases/tag/v0.1.0)
- Editable scene: `hurry-up-and-wait.blend`
- Genuine Blender UI screenshot: `blender-wip.png`
- Representative beauty renders: `final/still-*.png` (these are renders, not UI screenshots)
- Creative decisions: `CONCEPT.md`
- Entry copy and exact submission conditions: `ENTRY_DRAFT.md`
- Technical checks: `scene-qa.json`, `media-qa.json`
- Independent critique: `INDEPENDENT_REVIEW.md` (completed on the delivered final export)

The delivered film is 1920×1080, with 504 frames at 24 fps and a duration of exactly 21 seconds. The final media report records the actual decoded file and its hash.

## Reproduce

Production environment: Blender 5.2.1 LTS (build 9e2066aef7ef), local EEVEE, Python with NumPy, FFmpeg. No cloud render service or paid API is required.

From this directory:

```sh
blender -b --factory-startup --python build.py -- --quality preview --stills --animation
python3 sound.py
ffmpeg -framerate 24 -i preview/frames/frame-%04d.png -i foley.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart preview/hurry-up-and-wait-preview.mp4

blender -b --factory-startup --python build.py -- --quality final --stills --animation
blender -b hurry-up-and-wait.blend --python qa_scene.py
ffmpeg -framerate 24 -i final/frames/frame-%04d.png -i foley.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart final/hurry-up-and-wait.mp4
python3 verify_media.py
```

On this host the Blender binary is `/Applications/Blender.app/Contents/MacOS/Blender`. Re-running to an existing MP4 requires an explicit overwrite choice or FFmpeg's `-y` flag. A frame range can be rendered with `--start` and `--end`; the film's animation remains authored across frames 1–504.

## Production disclosure

Codex generated the Python source and revised the scene after inspection. All vehicle/dock/ferry geometry, materials, keyframes and camera movement were made for this project. Blender's bundled Bfont is used for typography. Foley is original additive synthesis in `sound.py`, with no samples or recordings.

The motion is **choreographed**, not a physical simulation. The water is a stylized static surface. Red intentionally spins its wheels while waiting; wheels roll with forward travel during approach/boarding and remain still relative to the ferry during transport.

The story uses a familiar idea about haste and waiting. We claim original execution and assets, not invention of that theme, audience-tested humour, or a guaranteed award.

## Rendering and QA history

The first still pass exposed incorrect wheel axes and text overlap. Later temporal/kinematic review found backward tire rotation and wheel rotation continuing during passive ferry travel. These were corrected. Earlier development renders are retained locally under `development-v2-*` for audit; they are not the final submission film. The final render must be paired with its own `final/build-manifest.json` and QA reports.

The source package and film are public. No official contest submission has been made; the submission window opens October 15, 2026.
