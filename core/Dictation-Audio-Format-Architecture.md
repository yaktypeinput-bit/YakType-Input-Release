# Dictation Audio Format Architecture

## Purpose

This document defines the audio-format contract for the dictation pipeline.

The goal is to keep audio handling predictable across engines:

- recording capture stays engine-agnostic
- internal task storage stays normalized
- each dictation engine explicitly declares its preferred upload format
- transcoding happens in one shared place instead of being reimplemented per engine

## Current Three-Layer Model

### 1. Capture format

Runtime recording and realtime chunks are handled as:

- `16kHz`
- `mono`
- `Float32` samples

This is the in-memory working format used by the recording and segmentation pipeline.

### 2. Internal storage format

Recorded or imported audio is normalized into internal task storage as:

- `OGG/Opus`

This is the canonical persisted recording format for dictation tasks.

Current implications:

- imported audio should not be copied through based only on file extension
- imported audio must be transcoded into internal OGG before entering the task pipeline
- downstream components should treat task recordings as normalized internal assets, not raw source files

### 3. Engine upload format

Each `SpeechRecognitionEngine` declares:

- `preferredDictationAudioFormat`

This is the format the engine wants immediately before upload.

Current engine mapping:

- `Gemini`: `oggOpus`
- `Aliyun`: `oggOpus`
- `MiMo`: `wav16kMonoPcm16`
- default protocol fallback: `oggOpus`

## Responsibility Split

### `DictationAudioTranscoder`

Shared transcoding layer for:

- converting realtime float chunks into engine upload format
- converting segmented audio files into engine upload format
- normalizing imported audio into internal OGG
- decoding audio for components that should not assume the source is already OGG

This type is the only place that should know how to:

- encode `Float32` samples to `OGG`
- encode `Float32` samples to `WAV`
- decode OGG input
- decode non-OGG input through `AVFoundation`

### `SpeechRecognitionEngine`

Engines should:

- declare upload preference
- request transcoding through the shared layer
- focus on request construction, response parsing, and engine-specific retry/state logic

Engines should not:

- embed ad hoc audio format conversion logic
- assume all internal files are already in the upload format they need

### `TranscriptionSessionCoordinator`

Coordinator-level import handling should:

- write imported files into normalized internal recordings
- avoid raw file copy semantics for user-imported audio

### `AudioProcessor`

Audio segmentation should:

- operate on decoded float samples
- avoid assuming the input source must be OGG
- continue emitting normalized internal segment files

## Current End-to-End Flow

### Realtime dictation

1. audio is captured as `16k mono Float32`
2. chunk is passed to the active dictation engine
3. engine asks `DictationAudioTranscoder` for its preferred upload format
4. transcoded payload is uploaded

### Recorded file dictation

1. recording is persisted as internal `OGG`
2. `AudioProcessor` segments the recording if needed
3. engine requests each segment in its preferred upload format
4. transcoded payload is uploaded

### Imported file dictation

1. external audio file is imported
2. file is normalized into internal `OGG`
3. later segmentation and upload follow the same pipeline as regular recordings

## Why MiMo Needed This

MiMo accepts only a narrow MIME/type set for ASR uploads.

Observed constraint:

- `audio/ogg` requests can be rejected
- `audio/wav` is accepted

That means MiMo should be modeled as:

- a standalone dictation brand engine
- with an explicit upload preference of `wav16kMonoPcm16`

The important architectural conclusion is broader than MiMo:

- engine compatibility belongs to engine metadata
- transcoding belongs to shared infrastructure

## Rules For Future Engines

When adding a new dictation engine:

1. decide the engine's preferred upload format first
2. declare it on the engine type
3. reuse `DictationAudioTranscoder`
4. do not add local per-engine encoding helpers unless the shared transcoder truly cannot support the new format
5. keep internal task recordings normalized to the canonical storage format unless the whole product-level storage policy changes

## Open Follow-Ups

- Add more transcoder-focused tests around MIME and payload headers.
- If a future engine needs another upload format, extend `DictationAudioFormat` instead of adding one-off code paths.
- If import fidelity becomes important, document whether internal normalization is lossy-by-design and whether original source files should also be retained.
