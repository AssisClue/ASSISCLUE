$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "LIGHT CLEAN RUNTIME"
Write-Host "==================="
Write-Host ""

$projectRoot = "C:\AI\ASSISCLUE"
$runtimeRoot = Join-Path $projectRoot "runtime"

function Ensure-File($path) {
    $parent = Split-Path $path -Parent
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    if (-not (Test-Path $path)) {
        New-Item -ItemType File -Force -Path $path | Out-Null
    }
}

function Ensure-Dir($path) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    }
}

function Clear-File($path, $defaultContent = "") {
    Ensure-File $path
    Set-Content -Path $path -Value $defaultContent -Encoding UTF8 -NoNewline
    Write-Host "Cleared file: $path"
}

function Reset-Json($path, $jsonText = "{}") {
    Ensure-File $path
    Set-Content -Path $path -Value $jsonText -Encoding UTF8 -NoNewline
    Write-Host "Reset json: $path"
}

function Remove-All-Files-In($dir, $filter = "*") {
    if (-not (Test-Path $dir)) {
        return
    }
    Get-ChildItem -Path $dir -File -Filter $filter -Force | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "Deleted file: $($_.FullName)"
    }
}

# --------------------------------------------------
# PRESERVE ON PURPOSE (do NOT touch)
# --------------------------------------------------
# runtime/sacred/live_transcript_assembled.jsonl
# runtime/sacred/live_transcript_assembled_latest.json
# runtime/output/chat_history.jsonl
# runtime/memory/*
# runtime/sacred/live_moment_history.jsonl
# runtime/sacred/context_snapshot.json
# runtime/sacred/memory_snapshot.json
# runtime/sacred/world_state.json
# runtime/state/system_runtime.json
# runtime/state/llm_runtime_state.json

# Ensure sacred exists
Ensure-Dir (Join-Path $runtimeRoot "sacred")

# --------------------------------------------------
# 1) TRANSCRIPT LIVE / RAW / COMPAT OLD NAMES
# --------------------------------------------------
Clear-File (Join-Path $runtimeRoot "sacred\live_transcript_raw.jsonl")
Reset-Json (Join-Path $runtimeRoot "sacred\live_transcript_raw_latest.json") "{}"

# compat old names: keep empty so nothing replays accidentally
Clear-File (Join-Path $runtimeRoot "sacred\live_transcript_history.jsonl")
Reset-Json (Join-Path $runtimeRoot "sacred\live_transcript_latest.json") "{}"

# DO NOT TOUCH assembled transcript canonical files
# runtime/sacred/live_transcript_assembled.jsonl
# runtime/sacred/live_transcript_assembled_latest.json

# --------------------------------------------------
# 2) LISTENER / TRANSCRIPT STATUS + CURSORS (live only)
# --------------------------------------------------
Reset-Json (Join-Path $runtimeRoot "status\assembled_transcript_builder_status.json") "{}"
Reset-Json (Join-Path $runtimeRoot "status\inputfeed_to_text_status.json") "{}"
Reset-Json (Join-Path $runtimeRoot "status\primary_listener_status.json") "{}"
Reset-Json (Join-Path $runtimeRoot "status\raw_interrupt_listener_status.json") "{}"

Reset-Json (Join-Path $runtimeRoot "state\live_listeners\primary_listener_cursor.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\live_listeners\raw_interrupt_listener_cursor.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\live_listeners\administrative_listener_cursor.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\live_listeners\context_runner_cursor.json") "{}"

# --------------------------------------------------
# 3) ROUTER QUEUES / STATUS
# --------------------------------------------------
Clear-File (Join-Path $runtimeRoot "queues\router_dispatch\router_input_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "queues\router_dispatch\action_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "queues\router_dispatch\response_queue.jsonl")
Reset-Json (Join-Path $runtimeRoot "status\router_dispatch\router_status.json") "{}"

# --------------------------------------------------
# 4) DISPLAY / SPOKEN QUERY RESULTS
# --------------------------------------------------
Clear-File (Join-Path $runtimeRoot "display_actions\results\display_action_results.jsonl")
Reset-Json (Join-Path $runtimeRoot "display_actions\status\display_action_runner_status.json") "{}"

Clear-File (Join-Path $runtimeRoot "queues\spoken_queries\spoken_query_results.jsonl")
Reset-Json (Join-Path $runtimeRoot "status\spoken_queries\spoken_query_status.json") "{}"

# --------------------------------------------------
# 5) SPEECH OUT / PLAYBACK / AUDIO TEMP
# --------------------------------------------------
Clear-File (Join-Path $runtimeRoot "queues\speech_out\speech_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "queues\speech_out\spoken_history.jsonl")

Reset-Json (Join-Path $runtimeRoot "queues\speech_out\latest_tts.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\speech_out\playback_state.json") "{}"
Reset-Json (Join-Path $runtimeRoot "status\speech_out\speech_queue_writer_status.json") "{}"
Reset-Json (Join-Path $runtimeRoot "status\speech_out\speaker_status.json") "{}"

Remove-All-Files-In (Join-Path $runtimeRoot "queues\speech_out\audio") "*.wav"
Remove-All-Files-In (Join-Path $runtimeRoot "queues\speech_out\audio") "*.mp3"
Remove-All-Files-In (Join-Path $runtimeRoot "queues\speech_out\audio") "*.ogg"

# --------------------------------------------------
# 6) OUTPUT TEMP / LIVE UI CONFUSION
# --------------------------------------------------
Reset-Json (Join-Path $runtimeRoot "output\latest_response.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\session_snapshot.json") "{}"

# --------------------------------------------------
# 7) OPTIONAL LIVE TEMP AUDIO CHUNKS / INPUT TEMP
# --------------------------------------------------
Remove-All-Files-In (Join-Path $runtimeRoot "input\audio_chunks") "*.wav"
Remove-All-Files-In (Join-Path $runtimeRoot "input\audio_chunks") "*.json"
Remove-All-Files-In (Join-Path $runtimeRoot "input\audio_chunks") "*.txt"

Write-Host ""
Write-Host "LIGHT CLEAN COMPLETE"
Write-Host "Preserved:"
Write-Host " - runtime/sacred/live_transcript_assembled.jsonl"
Write-Host " - runtime/sacred/live_transcript_assembled_latest.json"
Write-Host " - runtime/output/chat_history.jsonl"
Write-Host " - runtime/memory/*"
Write-Host " - runtime/sacred/live_moment_history.jsonl"
Write-Host " - runtime/sacred/context_snapshot.json"
Write-Host " - runtime/sacred/memory_snapshot.json"
Write-Host " - runtime/sacred/world_state.json"
Write-Host " - runtime/state/system_runtime.json"
Write-Host " - runtime/state/llm_runtime_state.json"
Write-Host ""
