# Optional Local OCR, ASR, And Keyframes

`source2study` keeps OCR and ASR local and optional.

It does not download platform videos by default, does not bypass DRM, and does not call cloud transcription APIs.

## OCR

```bash
source2study ocr ./slide.png --output ./slide.png.ocr.txt
```

OCR priority:

1. User-provided `.ocr.txt` sidecar.
2. Local `tesseract` CLI if installed.
3. Low-confidence placeholder evidence.

Low-confidence OCR must remain visible in intake reports and learning packs.

## ASR

```bash
source2study asr inspect ./lecture.mp4
source2study asr transcribe ./lecture.mp4 --output ./lecture.txt
```

ASR uses a local `whisper` CLI only when it is already installed. If no local engine is available, the command returns structured `unavailable` status and suggests uploading a transcript.

## Video Keyframes

```bash
source2study keyframes inspect ./lecture.mp4
source2study keyframes extract ./lecture.mp4 --output-dir ./workspace/demo/screenshots --interval-seconds 30
```

Keyframe extraction uses a local `ffmpeg` CLI only when it is already installed. It never downloads Bilibili, YouTube, or course-platform videos. Generated frames should be treated as visual evidence and can be paired with OCR sidecars.

## Safety Boundaries

- No default Bilibili/YouTube download.
- No paid-course extraction.
- No DRM bypass.
- No cloud upload.
- No cookie or login-session access.
- User-provided local files only.
