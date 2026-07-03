# Open-Source Stack for "Six Thinkers: Dialogues" (2026)

**Prepared for:** The Kiwi Dialectic (NZ, socialist political education)
**Series:** *Six Thinkers: Dialogues* — Gramsci, Kropotkin, Graeber, Freire, Deleuze, and Bakunin "talking to each other" via animated pencil-sketch portraits.
**Scope:** TTS voices, portrait animation, compositing, distribution, catalogue architecture, and licensing/ethics — evaluated as of mid-2026 for a solo/small-team, budget-constrained, Mac-plus-cloud-GPU workflow that must slot into the existing `six-thinkers` / `thinkers-mapper` / `courses.json` GitHub Pages convention.

---

## Executive Summary — Recommended Pipeline

> **Script → TTS (Chatterbox Multilingual, fallback XTTS-v2) → portrait animation (SadTalker, fallback LivePortrait audio-driven fork) → ffmpeg round-table composite (primary) / Shotcut (GUI backup) → multi-aspect export → self-hosted PeerTube + Postiz multi-poster → static HTML catalogue (plain-HTML, matching existing `six-thinkers` convention) reading a new `dialogues.json` that federates into `courses.json` for `thinkers-mapper`.**

| Stage | Primary tool | Why | Fallback |
|---|---|---|---|
| TTS / voice | **Chatterbox Multilingual v2/v3** (Resemble AI) | MIT-licensed end-to-end (code *and* weights), zero-shot cloning from ~10s clip, 23+ languages including Italian/Russian/French, emotion-exaggeration control fits "dialectical" back-and-forth delivery, built-in PerTh watermarking addresses deepfake-ethics concerns out of the box ([GitHub](https://github.com/resemble-ai/chatterbox), [Resemble AI](https://www.resemble.ai/learn/models/chatterbox)) | **Coqui XTTS-v2** for widest language/accent coverage (17 languages incl. it/ru/pt/fr) if Chatterbox's accent transfer on a given clip is weak — but note CPML is non-commercial only ([Hugging Face](https://huggingface.co/coqui/XTTS-v2)) |
| Portrait animation | **SadTalker** (Apache-2.0, updated to remove non-commercial clause) | Fastest CPU-friendly setup, best documented `--enhancer gfpgan` pipeline, most forgiving of stylised/non-photographic input relative to diffusion-heavy alternatives, integrates cleanly with ffmpeg via simple CLI ([GitHub](https://github.com/OpenTalker/SadTalker), [license](https://github.com/OpenTalker/SadTalker/blob/main/LICENSE)) | **LivePortrait** (MIT code, Apache weights) audio-driven fork for higher-fidelity motion when a GPU is available, noting the stock repo is image/video-driven and needs an audio-driven wrapper ([GitHub](https://github.com/KwaiVGI/LivePortrait), [audio-driven fork](https://github.com/Hekenye/LivePortrait-AudioDriven)) |
| Compositing | **ffmpeg command pipeline** (`xstack`/`overlay` + `drawtext`/`subtitles`) | Free, scriptable, reproducible, runs headless on any CI box or Mac, one script emits 16:9 / 9:16 / 1:1 in a single pass | **Shotcut** (MIT, cross-platform, native macOS build) for manual fine cuts and reviewing rough assemblies before scripting the final ffmpeg pass |
| Hosting | **Self-hosted PeerTube** (AGPL-3.0) on a small VPS (~€5–20/mo) | Full ownership, no de-platforming risk for socialist political-education content, ActivityPub federation gives organic reach to other left/education instances, HTML5 `<iframe>` embed drops straight into the existing plain-HTML site ([PeerTube docs](https://docs.joinpeertube.org/api/embed-player), [European Purpose review](https://europeanpurpose.com/tool/peertube)) | Join a sympathetic shared instance (e.g. a Fediverse/BreadTube-adjacent instance) if standing up a VPS is not yet worth it — same embed code, zero hosting cost |
| Multi-platform posting | **Postiz** (AGPL-3.0, self-hostable, 13+ networks incl. YouTube Shorts/TikTok/IG/X) | Fully open-source scheduler with the widest network coverage of the OSS options, avoids per-seat SaaS fees ([Postiz](https://postiz.com), [comparison](https://bulkpublish.com/compare/mixpost-vs-postiz)) | **Mixpost** (self-hosted, one-time license) if Postiz's Docker/Node stack is too heavy for the VPS |
| Catalogue / site | **Plain HTML + Python `build.py`** (matches existing `six-thinkers` repo convention) reading a new `dialogues.json` | Zero framework overhead, consistent with the publisher's existing GitHub Pages stack, trivially interoperable with `thinkers-mapper`'s `courses.json` reader | **Eleventy** if the catalogue outgrows hand-rolled Python templating — closest in spirit to "just HTML," minimal JS |

**Total monthly cash cost for a solo creator:** roughly **NZ$10–35/month** (one small VPS for PeerTube + Postiz, or $0 if using a shared PeerTube instance and free tiers of TTS/animation run locally on a Mac + occasional rented GPU-hour for animation renders).

---

## 1. Open-Source TTS with Distinct Expressive Voices

### Comparison table

| Model | License (code / weights) | Self-host difficulty | Voice cloning | Accent range relevant to the six thinkers | CPU/GPU | Mac-friendliness |
|---|---|---|---|---|---|---|
| **Chatterbox / Chatterbox Multilingual** | MIT / MIT ([GitHub](https://github.com/resemble-ai/chatterbox), [HF](https://huggingface.co/ResembleAI/chatterbox)) | Easy — `pip install chatterbox-tts`, single 0.5B Llama-backbone model, community Web UI ([devnen/Chatterbox-TTS-Server](https://github.com/devnen/Chatterbox-TTS-Server)) | Zero-shot from ~5-10s clip, no fine-tune step; emotion-exaggeration control ([Resemble AI](https://www.resemble.ai/learn/models/chatterbox)) | 23+ languages incl. Italian, Russian, French; v3 adds dialects and "language pack" tuned models ([Resemble AI v3 post](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages)) | Runs on CPU (slow) or modest GPU; sub-200ms latency on GPU | Works via pip/PyTorch on Apple Silicon (MPS) with community reports; no official Mac binary but Python stack is portable |
| **Coqui XTTS-v2** | MPL-2.0 (toolkit) / **CPML — non-commercial** (weights) ([Coqui HF](https://huggingface.co/coqui/XTTS-v2)) | Moderate — `coqui-tts` PyPI fork (idiap) needed since original repo unmaintained; Docker image available ([QWE guide](https://www.qwe.edu.pl/ai-tools/xtts-v2-open-source-voice-cloning-install/)) | Best-in-class 6-second zero-shot cloning, cross-lingual transfer (clone in English, speak in Italian/Russian/French/Portuguese) ([XTTS-v2 HF](https://huggingface.co/coqui/XTTS-v2)) | 17 languages incl. it, ru, pt, fr, es — the widest coverage of any option evaluated | 4–6GB VRAM recommended; CPU works but "significantly slower," fine for overnight batch | Runs via Python; Coqui Inc. shut down Jan 2024 so **no commercial license is purchasable** — treat as non-commercial/research use only ([PromptQuorum](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)) |
| **F5-TTS** | MIT (code) / **CC-BY-NC-4.0** (official weights, trained on Emilia dataset) ([GitHub](https://github.com/SWivid/F5-TTS)) | Easy pip/Docker install; Gradio UI included | Zero-shot from 5-15s reference + matching transcript; flow-matching architecture, RTF ~0.15 | English-centric out of the box; multilingual community checkpoints exist but vary in quality | GPU strongly recommended; CPU ~10x slower | `f5-tts-mlx` gives a native Apple Silicon/MLX implementation ([GitHub](https://github.com/lucasnewman/f5-tts-mlx)) — best Mac-native option among cloning models |
| **StyleTTS2** | MIT (code) / pretrained weights carry an ethics **usage covenant** (must disclose synthetic speech, only clone consenting voices) ([GitHub](https://github.com/yl4579/StyleTTS2), [TERMS.md](https://github.com/yl4579/StyleTTS2/blob/main/TERMS.md)) | Moderate — GPL-licensed phonemizer dependency complicates pure-MIT distribution; MIT-only fork exists via gruut | Voice cloning via LibriTTS-trained checkpoint | English-only officially | GPU preferred for quality parity with commercial tools | Works on Mac via PyTorch, but is the fiddliest install of the group |
| **Chatterbox** *(see above — kept for pairwise comparison only)* | — | — | — | — | — | — |
| **OpenVoice v2** | MIT (both V1 and V2, free commercial use since April 2024) ([GitHub](https://github.com/myshell-ai/OpenVoice)) | Easy; API server wrapper available ([ValyrianTech/OpenVoice_server](https://github.com/ValyrianTech/OpenVoice_server)) | Clones from just 1-5s reference; uniquely **decouples timbre from speaking style** — same cloned voice can be delivered cheerful/angry/whispering, useful for dialectical sparring between characters ([Local AI Master](https://localaimaster.com/blog/openvoice-v2-guide)) | Cross-lingual cloning across en/es/fr/zh/ja/ko natively; accent control (US/UK/Indian/Australian English + others) | Fast, runs on modest GPU or CPU | Clean MIT license, straightforward Python install, good Mac compatibility reported |
| **MetaVoice-1B** | Apache-2.0, "usable without restriction" ([GitHub mirror](https://github.com/NeuralVox/metavoice-e)) | Moderate — needs flash-attention setup | Zero-shot cloning for American/British voices out of the box; other accents need fine-tuning | Weak outside English — not suitable for Italian/Russian/Brazilian accents without retraining | GPU recommended | No official Mac path documented; project has seen little activity in 2025-26 |
| **Fish Speech / OpenAudio S1** | Apache-2.0 (code) / **CC-BY-NC-SA-4.0** (weights) ([GitHub](https://github.com/fishaudio/fish-speech)) | Moderate; Docker image published | 10-second clip zero-shot cloning, strong multilingual support (en, zh, ja, ko, fr, de, ar, es) | Good multilingual breadth but non-commercial weights block direct use in a monetised/public-facing series without care | GPU strongly preferred (~9GB checkpoint) | Runs on Mac via PyTorch but heavier than Chatterbox/OpenVoice |
| **Kokoro (82M)** | Apache-2.0 (weights and code) ([GitHub](https://github.com/hexgrad/kokoro), [HF](https://huggingface.co/hexgrad/Kokoro-82M)) | Very easy — tiny model, `kokoro-web` self-hosted OpenAI-compatible endpoint exists ([GitHub](https://github.com/eduardolat/kokoro-web)) | **No voice cloning** — fixed voice bank only; built on a StyleTTS2 architecture | English-strong; not designed for accent cloning | Runs comfortably on CPU thanks to 82M parameter size | Excellent Mac-friendliness (lightweight, fast on CPU) but unsuitable where per-thinker cloned/accented voices are required |
| **Piper** | MIT (rhasspy) / GPL-3.0 (successor `OHF-Voice/piper1-gpl`) ([GitHub](https://github.com/rhasspy/piper), [successor](https://github.com/OHF-Voice/piper1-gpl)) | Easiest of all — single static binary, ONNX voice files, HTTP server mode ([Pipecat docs](https://docs.pipecat.ai/api-reference/server/services/tts/piper)) | **No voice cloning** — pre-trained multi-speaker voices only | Wide language voice-pack library (60+ languages) but fixed voices, not per-character cloning | Runs fast on CPU alone — designed for Raspberry Pi-class hardware | Best Mac-friendliness of any option (no GPU, no Python env needed for the binary) |

### Recommendation

- **Primary: Chatterbox Multilingual.** MIT on both code and weights removes the single biggest licensing risk in this list (XTTS-v2's CPML and F5-TTS/Fish Speech's non-commercial weights all block confident public redistribution). Its 23+ language multilingual model covers Italian (Gramsci), Russian (Bakunin/Kropotkin), French (Deleuze), Brazilian Portuguese (Freire), and American English (Graeber) accent targets from the brief, and the emotion-exaggeration control is well suited to dramatised philosophical debate. The built-in PerTh watermark is a meaningful, "for free" mitigation for the deceased-persons ethics question in §6 ([Resemble AI](https://www.resemble.ai/learn/models/chatterbox)).
- **Fallback: Coqui XTTS-v2** when a specific accent clone needs XTTS's stronger cross-lingual transfer quality — but gate any such output for **non-commercial/research use only** given CPML, or substitute a from-scratch fine-tune on permissively-licensed audio.
- **Not recommended for character voices:** Piper and Kokoro — excellent for narration/voice-over UI chrome (e.g., a genderless "narrator" reading captions) precisely because they are fully open, fast, CPU-only, but they cannot clone a "Gramsci accent," so they don't serve the "distinct expressive voices per thinker" requirement.

```bash
# Chatterbox Multilingual — minimal clone + generate
pip install chatterbox-tts
python - <<'PY'
from chatterbox.tts import ChatterboxMultilingualTTS
tts = ChatterboxMultilingualTTS.from_pretrained(device="mps")  # or "cuda"/"cpu"
wav = tts.generate(
    text="Il pessimismo dell'intelligenza, l'ottimismo della volontà.",
    audio_prompt_path="voices/gramsci_reference.wav",
    language_id="it",
)
tts.save(wav, "out/gramsci_line01.wav")
PY
```

---

## 2. Portrait Animation / Talking-Head from a Still Image + Audio

### Comparison table

| Tool | License | Input | Hardware | Quality on **sketch/painted** portraits | ffmpeg pipeline fit |
|---|---|---|---|---|---|
| **SadTalker** | Apache-2.0 (non-commercial clause removed) ([GitHub](https://github.com/OpenTalker/SadTalker), [license file](https://github.com/OpenTalker/SadTalker/blob/main/LICENSE)) | Single image + audio (WAV/MP3) | Runs on modest GPU (~15fps quoted), CPU fallback works but slow | Docs explicitly note the model is trained on **real faces**: *"Our model only works on REAL people or the portrait image similar to REAL person"* — stylised/anime input is flagged as future work, meaning painted portraits need careful pre-processing (higher facial contrast, `--preprocess full`, `--enhancer gfpgan`) to hold together ([best_practice.md](https://github.com/OpenTalker/SadTalker/blob/main/docs/best_practice.md)) | Simple CLI (`python inference.py --driven_audio ... --source_image ... --enhancer gfpgan`) outputs an MP4 directly consumable by ffmpeg ([GitHub](https://github.com/OpenTalker/SadTalker)) |
| **LivePortrait** | MIT (code) / Apache-2.0 (weights); note InsightFace `buffalo_l` face-detection dependency is itself non-commercial, which can taint a fully "commercial" claim ([Replicate note](https://replicate.com/fofr/live-portrait)) | Image + **driving video or (via community fork) audio** | Extremely fast — 12.8ms/frame on RTX 4090; the stock repo is not natively audio-driven | Highest-fidelity motion and best identity preservation of any tool tested, including on non-photoreal input, per side-by-side reviews, but needs the community **audio-driven extension** to skip recording a driving video ([Hekenye fork](https://github.com/Hekenye/LivePortrait-AudioDriven)) | ComfyUI nodes and CLI both exist; output MP4 chains into ffmpeg easily; heavier setup (InsightFace, conda) than SadTalker |
| **EchoMimic (v1/v2/v3)** | Apache-2.0 ([GitHub](https://github.com/antgroup/echomimic), [v3](https://github.com/antgroup/echomimic_v3)) | Audio + landmark/pose conditioning, half-body support in v2 | GPU required, diffusion-based, slower than SadTalker/LivePortrait | Landmark-conditioned approach gives more explicit control over mouth shapes, potentially more forgiving of stylised faces since it doesn't rely purely on learned photoreal priors — but community reports are thinner than for SadTalker | conda-based pipeline, ComfyUI nodes exist (`smthemex/ComfyUI_EchoMimic`); more moving parts (unet, audio processor, vae checkpoints) to wire into a script |
| **Hallo / Hallo2** | MIT ([GitHub](https://github.com/fudan-generative-vision/hallo2)) | Single image + English WAV audio, long-duration (up to 1hr) and up to 4K | GPU required, slower — designed for quality over speed | Explicit guidance: face 50-70% of frame, forward-facing, <30° rotation — workable for a formal painted portrait bust, but English-only audio training data is limiting for non-English thinker dialogue mixed with English narration | `scripts/inference_long.py` CLI outputs MP4; ComfyUI wrapper exists (`ComfyUI_Hallo2`) |
| **MuseTalk** | MIT (code and model, "no limitation for academic and commercial usage") ([GitHub](https://github.com/TMElyralab/MuseTalk)) | Real-time lip-sync on existing video/image + audio, 30+ FPS at 256×256 | Lightweight enough for real-time use, GPU still preferred | Works by inpainting the lower half of the face in latent space — best suited to **already-animated or video-driven** faces rather than a single static sketch; less proven on painted stills | Very ffmpeg-friendly due to real-time design; good for live/interactive extensions later |
| **AniPortrait** | Apache-2.0 ([GitHub](https://github.com/Zejun-Yang/AniPortrait)) | Audio + reference portrait/video | GPU required | Aimed at "photorealistic" portrait animation — its diffusion prior is tuned for photographic faces, so **sketch input risks realism artifacts fighting the pencil aesthetic** | ComfyUI nodes exist; CLI is more research-grade |
| **V-Express** | Code: commercial-permitted; **checkpoints/model card: non-commercial research only** ([GitHub](https://github.com/tencent-ailab/V-Express/)) | Reference image + audio + V-Kps pose sequence | GPU required | Capable of subtle expression control, but the extra pose-sequence input adds pipeline complexity that isn't justified for a static-portrait "talking sketch" | License blocks it outright for public-facing commercial-adjacent use unless retrained |

### Which best preserves the sketchy/zine aesthetic?

None of these models were trained to explicitly preserve non-photoreal art — all were trained predominantly on real human face video. In practice:

1. **SadTalker is the most forgiving and easiest to keep "sketchy."** Its 3DMM-coefficient approach only drives head pose/expression/mouth landmarks rather than hallucinating photographic detail, and disabling the `gfpgan`/`realesrgan` enhancers (which push toward photorealism) keeps the output closer to the original pencil linework. This makes it the pragmatic default despite the "real face" caveat in its own docs.
2. **LivePortrait (via the audio-driven fork)** is the upgrade path once a GPU budget exists: it has the best documented track record animating *illustrated/painted* portraits in community tests (VTuber/anime communities use it heavily) because its stitching-and-retargeting approach transforms motion fields rather than re-synthesizing texture, so linework is less likely to melt.
3. **EchoMimic's landmark-conditioning** is a reasonable experimental alternative if SadTalker's mouth shapes look too "photographic" against a sketch — its editable-landmark design gives more manual control over how exaggerated the mouth movement is, which could suit a woodcut/zine look better, at the cost of a heavier pipeline.
4. Avoid AniPortrait and V-Express for this use case: the former's diffusion prior actively fights sketch aesthetics ("photorealistic" is in the paper title), and the latter's license blocks confident use anyway.

**Recommendation: SadTalker primary, LivePortrait (audio-driven fork) fallback/upgrade.**

```bash
# SadTalker — one portrait, one line of cloned dialogue
python inference.py \
  --driven_audio out/gramsci_line01.wav \
  --source_image portraits/gramsci_sketch.png \
  --result_dir renders/gramsci/ \
  --still --preprocess full
  # omit --enhancer to keep the sketch look; add --enhancer gfpgan only if lines look too jittery
```

---

## 3. Compositing / Editing Pipeline

### Comparison table

| Tool | License | Programmatic control | Multi-aspect export | Captions | Learning curve | Fit for this project |
|---|---|---|---|---|---|---|
| **ffmpeg (scripted)** | LGPL/GPL depending on build | Full — filtergraphs (`xstack`, `overlay`, `hstack`), `drawtext`, `subtitles`/`ass` filters | One command per aspect ratio, or `split` + parallel filter chains to emit all three from one pass ([ffmpeg-engineering-handbook](https://github.com/endcycles/ffmpeg-engineering-handbook/blob/main/docs/operations/scaling.md)) | `drawtext` for burned titles, `subtitles=file.srt` for burned captions, `-c:s mov_text` for toggleable soft subtitles ([FFmpegLab](https://www.ffmpeglab.com/articles/ffmpeg-add-text-subtitles-video.html)) | Steep initially, but scriptable/repeatable — the right choice for a recurring six-episode-per-thinker series | **Primary recommendation** |
| **Shotcut** | GPL-3.0, cross-platform incl. native macOS build | Has a "Rest API"-free but scriptable MLT XML project format; less automatable than raw ffmpeg | Manual export presets per aspect ratio | Built-in filters incl. text/timing | Low-moderate | **GUI backup** for manual review/trims before the automated ffmpeg pass |
| **Kdenlive** | GPL-3.0 (KDE) | MLT-based project XML, some CLI rendering via `melt` | Manual per-profile export | Native subtitle track editor, good caption support | Moderate — more powerful, steeper than Shotcut | Good alternative GUI if the team prefers KDE's more "traditional NLE" workflow; XML project files can be batch-rendered via `melt` for a semi-programmatic path ([opensourcelab.jp](https://opensourcelab.jp/articles/open-source-video-editing)) |
| **OpenShot** | GPL-3.0 | libopenshot has a Python API, so genuinely scriptable unlike Shotcut/Kdenlive | Presets exist but historically the least stable engine of the three GUI options | Basic caption support | Lowest learning curve | Weakest performance/stability track record of the GUI options; acceptable for quick manual edits only |
| **Olive** | GPL-3.0 | Still pre-1.0 maturity as of 2026; limited automation story | Manual | Basic | Low-moderate | Not mature enough to recommend for a recurring production pipeline |
| **Blender VSE** | GPL-3.0 | Fully scriptable via Python (`bpy`) — genuinely programmatic, can build round-table composites and render multiple aspect ratios from one script | Scriptable via `bpy.context.scene.render` per-aspect configs | Text strips are scriptable but caption workflow is clunkier than `drawtext`/SRT | Steep (whole-Blender learning curve) | Interesting for teams already inside Blender for the pencil-sketch/portrait art pipeline, but adds unnecessary complexity next to ffmpeg for pure video assembly |
| **DaVinci Resolve (free tier)** | Proprietary, free-of-charge | Python/Lua scripting API is powerful but the software itself is closed-source | Excellent multi-format export presets, best color-grading in class | Best-in-class caption/subtitle tooling, incl. auto-transcription in paid tier | Moderate | Good **optional** GUI polish step (grading the pencil-sketch aesthetic, adding stingers) for final review, but excluded from the "open-source" core stack per the brief's framing; free tier has no watermark and is a reasonable non-open addition to keep in mind for finishing touches only |

### Recommended round-table layout + multi-aspect ffmpeg pattern

For a "round table" of two to six animated portraits, use `xstack`/`overlay` to arrange faces in a grid or circle-substitute grid, `drawtext`/`subtitles` for lower-third names and captions, then branch the same composite into three aspect ratios in one pass using `split`:

```bash
# 1. Composite N talking-head clips into a 2x2 (or NxM) round-table grid at a master 1920x1080 canvas
ffmpeg \
  -i renders/gramsci.mp4 -i renders/kropotkin.mp4 \
  -i renders/graeber.mp4 -i renders/bakunin.mp4 \
  -filter_complex "\
    [0:v]scale=960:540,drawtext=text='GRAMSCI':fontsize=28:fontcolor=white:x=20:y=H-th-20:box=1:boxcolor=black@0.5[a]; \
    [1:v]scale=960:540,drawtext=text='KROPOTKIN':fontsize=28:fontcolor=white:x=20:y=H-th-20:box=1:boxcolor=black@0.5[b]; \
    [2:v]scale=960:540,drawtext=text='GRAEBER':fontsize=28:fontcolor=white:x=20:y=H-th-20:box=1:boxcolor=black@0.5[c]; \
    [3:v]scale=960:540,drawtext=text='BAKUNIN':fontsize=28:fontcolor=white:x=20:y=H-th-20:box=1:boxcolor=black@0.5[d]; \
    [a][b][c][d]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[grid]; \
    [grid]subtitles=captions/ep01.srt:force_style='FontName=Special Elite,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=40'[master]" \
  -map "[master]" -map 0:a -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k \
  renders/master_16x9.mp4

# 2. Fan the master 16:9 out to 9:16 (crop-focused) and 1:1 in a single subsequent pass
ffmpeg -i renders/master_16x9.mp4 -filter_complex "\
  [0:v]split=2[v916][v11]; \
  [v916]crop=ih*9/16:ih,scale=1080:1920,setsar=1[out916]; \
  [v11]crop=ih:ih,scale=1080:1080,setsar=1[out11]" \
  -map "[out916]" -map 0:a -c:v libx264 -crf 20 -c:a aac renders/ep01_9x16.mp4 \
  -map "[out11]" -map 0:a -c:v libx264 -crf 20 -c:a aac renders/ep01_1x1.mp4
```

This pattern (`scale` + `pad`/`crop` + `force_original_aspect_ratio` for platform-safe framing, `xstack` for grid composition, `subtitles`/`drawtext` for captions) is the standard documented approach for social multi-format delivery ([32blog ffmpeg guide](https://32blog.com/en/ffmpeg/ffmpeg-social-media-video-format), [ffmpeg-engineering-handbook](https://github.com/endcycles/ffmpeg-engineering-handbook/blob/main/docs/operations/scaling.md)).

**Recommendation: ffmpeg scripts as the primary, versionable pipeline (checked into the repo as `render.sh`); Shotcut as the GUI backup** for manual review, quick trims, or when a human editor without CLI comfort needs to touch a cut.

---

## 4. Open-Source Video Hosting / Distribution

### PeerTube: self-host vs. shared instance

| Factor | Self-hosted | Shared/joined instance |
|---|---|---|
| License | AGPL-3.0 ([European Purpose review](https://europeanpurpose.com/tool/peertube)) | Same software, someone else's server |
| Cost | VPS from ~€5-20/month (2 CPU, 2GB RAM minimum) ([European Purpose](https://europeanpurpose.com/tool/peertube), [Libre Self-hosted](https://libreselfhosted.com/project/peertube/)) | Free, but subject to that instance's storage quotas/moderation policy |
| Control | Full control over moderation, branding, federation policy, custom client markup ([PeerTube docs](https://docs.joinpeertube.org/api/custom-client-markup)) | Content sits under someone else's rules; de-platforming risk is instance-operator risk, not "Big Tech" risk |
| De-risking political content | Best option — publisher owns the server, cannot be demonetised/suspended by a platform | Choose an instance explicitly aligned with left/education content (many Fediverse/BreadTube-adjacent PeerTube instances exist; verify each instance's federation/moderation policy before uploading) |
| Setup friction | Moderate — YunoHost one-click installs exist, or Docker Compose | None beyond account creation |
| Reach | Grows via ActivityPub federation (P2P/BitTorrent-in-browser distributes bandwidth cost across viewers) ([Dion Moult](https://thinkmoult.com/embed-peertube-video-on-your-website.html)) | Same federation benefit, piggybacking on the host instance's existing followers |

A caveat worth noting for a politically-labelled project: PeerTube's decentralised nature means **no single moderation authority** exists across the network — a 2022-23 ISD report on PeerTube's use by right-wing extremist milieus documents this structural reality ([ISD report](https://www.isdglobal.org/isd-publications/the-hydra-on-the-web-challenges-associated-with-extremist-use-of-the-fediverse-a-case-study-of-peertube/)). This is not a reason to avoid PeerTube (the same openness benefits socialist education content that mainstream platforms might flag or demonetise), but it does mean **The Kiwi Dialectic should run its own instance rather than depend on a shared instance's continued goodwill**, and can optionally install the community-maintained `peertube-isolation` blocklist plugin to avoid inadvertent federation with objectionable instances ([JoinPeerTube statement](https://joinpeertube.org/news/isd-study)).

**Recommendation: self-host PeerTube** on a small Hetzner/OVH/DigitalOcean VPS via the official production guide or a YunoHost one-click install, embedding via the standard iframe pattern:

```html
<iframe
  title="Six Thinkers: Dialogues — Episode 1"
  width="100%" height="100%" frameborder="0"
  sandbox="allow-same-origin allow-scripts allow-popups"
  src="https://tube.kiwidialectic.nz/videos/embed/EPISODE_UUID">
</iframe>
```

### Owncast (live)

**Owncast** is a free, self-hosted, single-user live streaming + chat server ([owncast.online](https://owncast.online), [GitHub](https://github.com/owncast/owncast)) — useful if The Kiwi Dialectic ever wants to livestream a "thinkers' roundtable" reading/Q&A alongside the pre-rendered dialogue series. It needs only `ffmpeg` + a small VPS (same class as PeerTube), takes an RTMP feed from OBS, and can be run alongside PeerTube on the same box. Not essential for the core dialogue-video series but a natural companion for live discussion events.

### Programmatic multi-platform publishing

| Tool | License | Networks | Self-host complexity | Notes |
|---|---|---|---|---|
| **Postiz** | AGPL-3.0, cloud or self-host ([postiz.com](https://postiz.com)) | 13+ networks incl. YouTube Shorts, TikTok, Instagram Reels, X/Twitter, LinkedIn, Threads, Bluesky ([BulkPublish comparison](https://bulkpublish.com/compare/mixpost-vs-postiz)) | Docker Compose stack (Next.js + worker); moderate | Widest network coverage of the OSS options; genuinely no dual-licensing/enterprise paywall ([Postiz YouTube walkthrough](https://www.youtube.com/watch?v=s37vcN1-Ebc)) |
| **Mixpost** | Self-hosted, one-time license (Lite tier free) ([mixpost.app](https://mixpost.app)) | 11 networks | Laravel-based; moderate | Slightly higher G2/Capterra rating in some comparisons; "Lite" free tier is genuinely open ([Mixpost blog](https://mixpost.app/blog/why-open-source-social-media-management-tools-are-perfect-for-startups)) |
| Ayrshare-style hosted alternatives | Proprietary SaaS | Wide | None (SaaS) | Excluded — brief asks for open-source multi-poster tools specifically |

**Recommendation for a solo creator: Postiz**, self-hosted on the same or a sibling VPS to PeerTube/Owncast, connected to YouTube, TikTok, Instagram, and X via their respective developer APIs (each platform requires its own app-approval process — budget a few days of lead time per platform before the first automated post).

**Cost/complexity summary for a solo creator:** one VPS (~NZ$10-30/month) can comfortably run PeerTube + Owncast + Postiz together; all three are Docker-deployable, and total hands-on maintenance is roughly a few hours a month once configured.

---

## 5. Course/Catalogue Node Architecture

### Recommended static site generator: **plain HTML + Python `build.py` (existing convention)**

The Kiwi Dialectic already runs `six-thinkers` as a plain-HTML GitHub Pages hub built by a Python `build.py` script that inlines lesson bodies from `bodies/<slug>-lesson-NN.html`, with `thinkers-mapper` as a separate rhizome-map repo reading `courses.json` live from `raw.githubusercontent.com` with a jsDelivr fallback (per the publisher's own project notes). **The lowest-friction, most interoperable choice is to extend this exact pattern rather than introduce a new framework.**

If/when the catalogue outgrows hand-rolled Python templating, the natural escalation path (in order of fit) is:

1. **Eleventy** — "no framework" philosophy, zero client JS by default, accepts Markdown/JSON/Liquid/Nunjucks side by side, and deploys to GitHub Pages exactly like the current setup ([2026 SSG comparison](https://gautamkhorana.com/blog/static-site-generators-2026-astro-eleventy-hugo-jekyll-gatsby/)). This is the best-fit *framework* if the team ever wants templating without adopting a component model.
2. **Hugo** — only worth the Go-templating learning curve if the catalogue grows past several thousand lesson pages and CI build time becomes a real cost ([SSG comparisons](https://trybuildpilot.com/508-astro-vs-hugo-vs-eleventy-2026)).
3. **Astro** — the 2026 "default" for new content sites with islands architecture, but its component model is overkill for a project whose convention is deliberately plain HTML; only worth adopting if the site needs interactive UI (e.g. an in-browser dialogue "chooser").

### `dialogues.json` schema (extends `courses.json` conventions)

```json
{
  "$schema": "https://kiwidialectic.nz/schema/dialogues.schema.json",
  "series": "six-thinkers-dialogues",
  "parentCourse": "six-thinkers",
  "dialogues": [
    {
      "id": "dialogue-01-hegemony-vs-mutual-aid",
      "title": "On Hegemony and Mutual Aid",
      "thinkers": ["gramsci", "kropotkin"],
      "screenplay": "screenplays/dialogue-01.md",
      "parentLessons": {
        "gramsci": "gramsci-lesson-03",
        "kropotkin": "kropotkin-lesson-02"
      },
      "video": {
        "peertubeUuid": "EPISODE_UUID_1",
        "peertubeInstance": "https://tube.kiwidialectic.nz",
        "youtubeFallbackId": null,
        "html5Fallback": "media/dialogue-01_16x9.mp4",
        "aspectVariants": {
          "16x9": "media/dialogue-01_16x9.mp4",
          "9x16": "media/dialogue-01_9x16.mp4",
          "1x1": "media/dialogue-01_1x1.mp4"
        }
      },
      "voices": {
        "gramsci": { "engine": "chatterbox-multilingual", "accent": "it", "referenceClip": "voices/gramsci_ref.wav" },
        "kropotkin": { "engine": "chatterbox-multilingual", "accent": "ru", "referenceClip": "voices/kropotkin_ref.wav" }
      },
      "portraits": {
        "gramsci": "portraits/gramsci_sketch.png",
        "kropotkin": "portraits/kropotkin_sketch.png"
      },
      "license": "CC-BY-SA-4.0",
      "publishedAt": "2026-08-01",
      "captionsSrt": "captions/dialogue-01.srt"
    }
  ]
}
```

### Embedding strategy: PeerTube iframe vs. HTML5 vs. YouTube fallback

Recommended **tiered fallback**, mirroring how `six-thinkers` already treats paywalled/unpublished lesson bodies gracefully:

1. **First choice — PeerTube `<iframe>` embed** (owns the primary, ideologically-aligned distribution channel, no ads/tracking).
2. **Second choice — native HTML5 `<video>` tag** pointing at a self-hosted MP4 (`aspectVariants["16x9"]`) for resilience if the PeerTube instance is temporarily down, and for users who block third-party iframes.
3. **Third choice — YouTube fallback embed** (`youtubeFallbackId`) purely for reach/discoverability on a platform most casual viewers already use, clearly presented as a mirror rather than the canonical copy.

```html
<div class="dialogue-player" data-fallback-order="peertube,html5,youtube">
  <!-- rendered by build.py from dialogues.json; JS below only swaps on load error -->
  <iframe class="pt-embed" src="https://tube.kiwidialectic.nz/videos/embed/EPISODE_UUID_1" loading="lazy"></iframe>
  <video class="html5-fallback" controls preload="none" poster="portraits/dialogue-01_poster.jpg" hidden>
    <source src="media/dialogue-01_16x9.mp4" type="video/mp4">
    <track kind="captions" src="captions/dialogue-01.vtt" srclang="en" default>
  </video>
</div>
```

### Interoperability with `thinkers-mapper`

`thinkers-mapper` already reads `courses.json` from `raw.githubusercontent.com` (with jsDelivr fallback) to build its rhizome map of course → lessons → access status ([thinkers-mapper project notes]). To slot dialogues into that map **without forking the mapper's data model**:

- Add a `"dialogues"` array field to each relevant course entry in `courses.json` (e.g. the Gramsci course entry gains `"dialogues": ["dialogue-01-hegemony-vs-mutual-aid"]`), pointing by `id` into the new `dialogues.json`.
- Publish `dialogues.json` at a stable raw GitHub URL alongside `courses.json` (same repo or a sibling repo), so `thinkers-mapper` can optionally fetch it with the same jsDelivr-fallback fetch pattern it already uses for `courses.json`, with zero change to its core rendering logic beyond a new node type ("dialogue" nodes linking two or more "thinker" nodes rather than one).
- Keep `parentCourse` and `parentLessons` fields in `dialogues.json` so the mapper (or the `six-thinkers` `build.py`) can cross-link "watch the dialogue" CTAs directly from the relevant lesson page, matching the existing Substack Chat/badge-claim CTA pattern already used elsewhere in the hub.

---

## 6. Licensing + Attribution

### CC BY-SA 4.0 compatibility across the pipeline

| Asset type | Recommended output license | Compatibility notes |
|---|---|---|
| **Screenplays / dialogue scripts** | CC BY-SA 4.0 | Fully compatible — this is the publisher's stated convention; text is wholly authored by The Kiwi Dialectic, no upstream restriction. |
| **Portrait sketches** | CC BY-SA 4.0 (if originals are the publisher's own artwork) | Compatible only if the sketches are original works or are themselves under a CC-BY-SA-compatible license; if referencing existing public-domain photographs of the thinkers as a drawing basis, the *drawing* is a new copyrightable work the publisher controls, but crediting the photographic reference is good practice. |
| **Generated voice audio (Chatterbox output)** | Chatterbox is **MIT** on both code and model weights, so generated audio carries no separate model-license restriction — the publisher can apply CC BY-SA 4.0 to the *audio output* freely ([GitHub license](https://github.com/resemble-ai/chatterbox)). |
| **Generated voice audio (XTTS-v2 fallback)** | **Not CC-BY-SA compatible for public release** — CPML restricts commercial use and, per Coqui's own model card, personal/hobby/research use only; a shutdown company means no path to buy a commercial license ([PromptQuorum](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)). Use XTTS-v2 outputs only for internal drafts/testing, not final published episodes, unless retrained on clean data. |
| **Generated video (SadTalker/LivePortrait output)** | SadTalker is Apache-2.0 (commercial-safe); **LivePortrait's weights are Apache-2.0 but its InsightFace `buffalo_l` face-detection dependency is non-commercial-licensed**, which technically taints a "fully commercial" claim for LivePortrait-based renders — a caveat worth flagging in the repo's LICENSE notes even though The Kiwi Dialectic is a non-commercial educational publisher ([Replicate license note](https://replicate.com/fofr/live-portrait)). |
| **StyleTTS2 pretrained weights (if ever used)** | Carries an explicit ethics covenant requiring disclosure that any synthesized voice is AI-generated and that only consenting voices are cloned ([StyleTTS2 TERMS.md](https://github.com/yl4579/StyleTTS2/blob/main/TERMS.md)) — this obligation is a *useful floor*, not a blocker, and is good practice to adopt project-wide regardless of which TTS engine is actually used. |

**Practical rule of thumb:** license the *finished episode* (video + audio + screenplay bundle) as CC BY-SA 4.0, but keep an internal `LICENSES.md` tracking each underlying model's license so that if a future re-edit swaps in XTTS-v2/Fish Speech/LivePortrait-with-InsightFace outputs, the publisher knows exactly which components carry non-commercial or attribution obligations that don't fully wash through to CC BY-SA (Creative Commons licenses on the *output* do not retroactively relicense the *tools* used to make it — the CC BY-SA 4.0 legal code governs the licensed work itself, not upstream model weights ([CC BY-SA 4.0 legal code](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en))).

### Voice-cloning ethics for deceased historical figures

All six thinkers (Gramsci, d.1937; Kropotkin, d.1921; Bakunin, d.1876; Deleuze, d.1995; Freire, d.1997; Graeber, d.2020) are deceased, so **no living-person consent can be obtained**, and Graeber's death is recent enough that his estate/family and living collaborators have a direct interest. Cross-referencing the current ethics literature:

- **No historical persons can grant consent, so the operative safeguard is transparency, not permission.** A consent hierarchy proposed for synthetic media places "historical/deceased public figures used for education" in a **medium/low-risk** band *if clearly disclosed*, contrasted with private individuals or living public figures used deceptively ([Tendril ethics guide](https://tendril.neural-forge.io/learn/creators/creative-ethics-synthetic-media-creators)).
- **Recommended concrete practices for The Kiwi Dialectic:**
  1. **Disclose prominently** on every episode (on-screen title card + written description) that voices and animation are AI-generated dramatisations for educational purposes, not archival recordings.
  2. **Do not claim vocal accuracy** to a real historical recording where none exists (e.g., there is no known recording of Bakunin's actual voice) — frame the voice as an interpretive/illustrative choice, not a forensic reconstruction.
  3. **Contact Graeber's estate/literary executors** as a courtesy given his recent death and his family's/collaborators' active public presence, even though strict legal consent requirements for the deceased are unsettled in most jurisdictions (recent California legislation extends performer-likeness protections to the deceased, and this is a fast-moving area of law worth monitoring) ([WebProNews](https://www.webpronews.com/deepfakes-revive-the-dead-ethical-concerns-and-regulatory-gaps/), [Mishcon de Reya](https://www.mishcon.com/news/deepfakes-of-the-deceased-ethical-dilemmas-and-implications-on-legacy-and-reputation)).
  4. **Use watermarking where available** — Chatterbox's built-in PerTh watermark provides a technical provenance signal for free; enable it rather than stripping it ([Resemble AI v3 post](https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages)).
  5. **Favor educational framing over "griefbot"/impersonation framing** — the ethics literature draws a sharper line around *educational tools* than around commercial personality resurrection ([Tech Policy Press](https://www.techpolicy.press/deepfakes-and-beyond-mapping-the-ethics-and-risks-of-digital-duplicates/)), which aligns naturally with The Kiwi Dialectic's stated socialist-political-education mission — lean into that framing explicitly in episode descriptions and the catalogue metadata (`"purpose": "educational-dramatization"` field on each `dialogues.json` entry is a low-cost way to encode this).
  6. **Avoid the appearance of forged primary-source material** — never present a Six Thinkers dialogue clip without the pencil-sketch stylisation and disclosure, since photorealistic treatment would raise the deepfake-of-the-dead risk profile the literature specifically flags ([The Conversation](https://theconversation.com/ai-reanimations-making-facsimiles-of-the-dead-raises-ethical-quandaries-256771)).

---

## Appendix: Full Pipeline Command Sketch (end-to-end for one dialogue line)

```bash
#!/usr/bin/env bash
set -euo pipefail

THINKER=gramsci
LINE_ID=ep01_line03
TEXT="L'egemonia culturale si conquista nelle scuole, non solo nelle fabbriche."
REF_VOICE="voices/${THINKER}_ref.wav"
PORTRAIT="portraits/${THINKER}_sketch.png"

# 1. TTS (Chatterbox Multilingual)
python tts_chatterbox.py \
  --text "$TEXT" --lang it \
  --ref "$REF_VOICE" \
  --out "audio/${LINE_ID}.wav"

# 2. Portrait animation (SadTalker)
python SadTalker/inference.py \
  --driven_audio "audio/${LINE_ID}.wav" \
  --source_image "$PORTRAIT" \
  --result_dir "renders/${LINE_ID}" \
  --still --preprocess full

# 3. Compositing into round table + multi-aspect export (see §3 scripts above)
./render.sh "renders/${LINE_ID}/result.mp4" "captions/${LINE_ID}.srt" "renders/${LINE_ID}_final"

# 4. Publish to PeerTube via CLI
npx @peertube/peertube-cli upload \
  --url https://tube.kiwidialectic.nz \
  --file "renders/${LINE_ID}_final_16x9.mp4" \
  --video-name "Six Thinkers: Dialogues — ${LINE_ID}"

# 5. Fan out via Postiz (self-hosted API) to YouTube/TikTok/IG/X — see Postiz API docs
curl -X POST https://postiz.kiwidialectic.nz/api/posts \
  -H "Authorization: Bearer $POSTIZ_TOKEN" \
  -F "video=@renders/${LINE_ID}_final_9x16.mp4" \
  -F "channels=youtube,tiktok,instagram,x"
```

**Sources consulted are cited inline throughout this report next to each specific claim.**
