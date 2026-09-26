# Production QA — September 26, 2026

## Visual and temporal review actually performed

- Reviewed real preview stills at frames 1, 90, 190, 270, 305, 380 and 474.
- Opened the corrected encoded 21-second preview in Chrome using a local-only review server.
- Observed actual unpaused playback at reported video times 0.010, 7.788, 12.354, 15.560 and 19.268 seconds. These observations cover the opening, waiting, gate/boarding, ferry travel and payoff hold. This is sampled observation of continuous playback, not a claim to have manually inspected every video frame.
- The source file opened successfully in the real Blender UI. `blender-wip.png` is that actual UI capture.
- Another agent independently reviewed the story and gate/boarding sequence and caught a terminal visibility-key collision. Its completed `INDEPENDENT_REVIEW.md` also records independent decoding of the final 1080p MP4, inspection of its one-second contact sheet and exact final frame, and browser playback reaching 21 seconds with `ended=true` and no media error. Its verdict is acceptable with subjective limitations; no remaining blocker was found in that bounded review.

## Corrections resulting from QA

1. Wheel spin initially used the wrong axis; corrected to the axle's +Y axis.
2. The rolling direction was backward, and decorative tire ticks were inside the rubber. Corrected direction and exposed ticks on each outer tire face.
3. World-coordinate wheel animation incorrectly kept rolling during passive ferry travel. The ferry's carried distance is now removed, so wheels remain still relative to the deck.
4. The final title and GO signal hid on frame 504 because a terminal key overwrote the visible key. Visibility now remains set through the last frame.
5. The endnote overlapped the miniature. Moved above the payoff title.

## Actual scene checks

The saved Blender scene passes the checks in `qa_scene.py` / `scene-qa.json`:

- 23 conservative gate-envelope checks while the cars cross the barrier plane; minimum computed separation approximately 0.586 scene units.
- Wheel circumferential travel matches forward movement during sampled approach and boarding intervals, with maximum numerical error under 0.000001 scene units.
- Vehicle positions remain fixed relative to the ferry during transport, with numerical drift under 0.000001 scene units.
- Wheel axles remain parallel to Y, and wheel angles remain constant while the ferry carries them.
- Payoff title, endnote and GO lamp remain visible at frame 504.

These checks certify those narrow conditions, not general physical realism. Red's deliberate waiting shudder includes a slight tire/road intersection at some frames. The reviewer considered it a minor cartoon stylization, not a blocking defect. This is explicitly not a physical simulation.

## Media and audio

`verify_media.py` passed on the delivered final PNG sequence and MP4: 504 valid PNGs at 1920×1080, 504 decoded H.264 video frames, 24 fps, exactly 21 seconds, stereo AAC at 48 kHz, and complete FFmpeg decode without an error. Actual output and source/media hashes are saved in `media-qa.json`. The final full-resolution images at frames 190 and 504 were also inspected; the payoff and GO lamp persist through the final frame.

Foley is original synthesized sound with a measured bounded peak, recorded in `audio-manifest.json`. Browser visual playback was muted. No claim of a critical listening test or subjective audio approval is made.

## Limits

No audience study or organizer feedback has occurred. The story is familiar; original scene construction does not establish a novel theme. No prize or ranking is predicted. The film has not been submitted or published by this build agent.
