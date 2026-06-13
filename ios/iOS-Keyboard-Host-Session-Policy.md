# iOS Keyboard / Host Session Policy

## Goal

This document defines the shared session rules between:

- the iOS host app
- the custom keyboard extension
- the shared App Group snapshot / command bridge

The main purpose is to keep both sides aligned on:

- phase semantics
- ownership semantics
- command authorization
- zombie cleanup
- final transcript fillback
- UI capability / presentation rules

## Shared Source Of Truth

The shared protocol layer currently lives in:

- `Sources/Shared/Services/KeyboardSharedBridge.swift`

The key shared types are:

- `KeyboardSessionState`
- `KeyboardSessionPolicy`
- `KeyboardSessionPresentation`
- `KeyboardSyncSnapshot`

## Session Phases

| Phase | Meaning | Active | Terminal | Keeps owner |
| --- | --- | --- | --- | --- |
| `idle` | Host is not holding warm mic | no | no | no |
| `armed` | Warm mic is active, but no dictation task is running | no | no | no |
| `starting` | Start command accepted, waiting for recording to fully begin | yes | no | yes |
| `recording` | Dictation is actively recording | yes | no | yes |
| `stopping` | Stop command accepted, recording is winding down | yes | no | yes |
| `finalizing` | Recording ended, transcription / polishing still in progress | yes | no | yes |
| `completed` | Final result is ready | no | yes | no active owner, but completed owner is published |
| `error` | Session ended with an error | no | yes | no active owner, but completed owner is published |

Shared helpers:

- `KeyboardSessionState.isActivePhase`
- `KeyboardSessionState.isInteractiveProcessingPhase`
- `KeyboardSessionState.isTerminalPhase`
- `KeyboardSessionState.isIdleLikePhase`
- `KeyboardSessionState.keepsOwnershipWhileActive`
- `KeyboardSessionState.publishesCompletedOwnership`

## Ownership Rules

Owner values:

- keyboard-owned session: `owningInstanceID == <keyboard instance id>`
- host-owned session: `owningInstanceID == "host"`
- no active owner: `nil`

Shared rules:

- `KeyboardSessionPolicy.snapshotOwner(for:ownerID:)`
- `KeyboardSessionPolicy.completedOwner(for:ownerID:)`
- `KeyboardSessionPolicy.isCommandAuthorized(ownerID:senderID:)`

Rules:

1. Active phases publish active ownership.
2. Terminal phases publish completed ownership.
3. Host-owned sessions cannot be controlled by keyboard commands.
4. Keyboard commands require strict sender match when an active keyboard owner exists.

## Final Transcript Rules

Shared rule:

- `KeyboardSessionPolicy.shouldPublishFinalTranscript(for:transcript:)`

Rules:

1. Final transcript is only published for terminal phases.
2. Empty / whitespace-only transcript does not produce a final transcript payload.
3. `finalTranscriptID` is used for idempotent fillback.

Host-side projection:

- `TranscriptionBridge_iOS.makeSnapshotProjection(from:)`

Keyboard-side consumption:

- `KeyboardSessionPolicy.shouldAttemptFillback(...)`
- `KeyboardDashboardModel.performFillback(...)`

## Keyboard Watch / Zombie Rules

Shared rules:

- `KeyboardSessionPolicy.shouldWatchKeyboardSession(state:isRecordingFromHost:ownerID:)`
- `KeyboardSessionPolicy.shouldAbortZombieSession(...)`

Rules:

1. Host only watchdogs keyboard-owned sessions.
2. Host watchdog is only active during `starting` / `recording`.
3. Keyboard zombie abort only happens when:
   - effective state is `recording`
   - host state is `recording`
   - there is no pending command ack
   - the active session id is neither `host` nor the current keyboard instance
4. Zombie cleanup must never preempt `stopping` / `finalizing`.

## Keyboard UI Capability Rules

Shared rules:

- `KeyboardSessionPolicy.canInteractWithRecordControl(isOccupied:state:)`
- `KeyboardSessionPolicy.shouldPollForCompletionFallback(isOccupied:ownsLocalSession:state:)`
- `KeyboardSessionPolicy.shouldShowSwipeHints(isOccupied:isRecordingState:state:showGhostHints:hasPipelineOptions:)`

Rules:

1. Record control is disabled during interactive processing phases.
2. Completion fallback polling only runs while:
   - host is occupied
   - keyboard still owns a local session
   - state is not idle-like
3. Swipe hints are hidden during recording / processing / ghost-hint overlay.

## Shared Presentation Rules

Shared presentation currently covers keyboard-facing text:

- `KeyboardSessionPresentation.statusText(...)`
- `KeyboardSessionPresentation.hintText(...)`

This keeps phase wording aligned with the shared phase model instead of duplicating
copy logic in the keyboard view layer.

## Host Runtime Structure

Host bridge layers:

- runtime container:
  - `TranscriptionBridge_iOS.HostRuntimeContext`
- session projection:
  - `TranscriptionBridge_iOS.HostSessionContext`
- snapshot projection:
  - `TranscriptionBridge_iOS.HostSnapshotProjection`
- command decisions:
  - `StartRecordingDecision`
  - `StopRecordingDecision`
  - `AbortRecordingDecision`

Runtime mutators:

- `setRuntimeOwnership(...)`
- `updateRuntimeTransientState(...)`
- `updateRuntimeFinalTranscriptID(...)`
- `resetKeyboardPulseTimestamp()`
- `markKeyboardPulseTimestamp()`

## Keyboard Runtime Structure

Keyboard layers:

- local pending command context:
  - `PendingKeyboardCommandContext`
- snapshot reducer:
  - `KeyboardSnapshotReduction`
- effect plan:
  - `KeyboardSnapshotEffects`
- fillback payload:
  - `KeyboardFillbackPayload`

The keyboard flow is now:

1. read snapshot
2. reduce snapshot into next state
3. derive effects
4. apply effects

## Current Mapping

Shared policy / phase:

- `Sources/Shared/Services/KeyboardSharedBridge.swift`

Host bridge:

- `Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS.swift`
- `Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS+SessionState.swift`
- `Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS+Snapshot.swift`
- `Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS+Commands.swift`
- `Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS+Watchdog.swift`
- `Sources/iOS/AppShell/Bridge/TranscriptionBridge_iOS+SyncSetup.swift`

Keyboard side:

- `Sources/iOS/Keyboard/KeyboardDashboardModel.swift`
- `Sources/iOS/Keyboard/KeyboardDashboardModel+Commands.swift`
- `Sources/iOS/Keyboard/KeyboardDashboardModel+StatusSync.swift`

## Remaining Direction

The next cleanup target should be to replace more keyboard model-specific wording /
capability derivations with shared policy outputs, then gradually reduce direct
`switch state` UI logic outside the shared layer.
