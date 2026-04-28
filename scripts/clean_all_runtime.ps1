$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "CLEAN ALL RUNTIME"
Write-Host "================="
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

function Clear-File($path, $defaultContent = "") {
    Ensure-File $path
    Set-Content -Path $path -Value $defaultContent -Encoding UTF8 -NoNewline
    Write-Host "Cleared file: $path"
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

function Remove-All-Recursive($dir, $filter = "*") {
    if (-not (Test-Path $dir)) {
        return
    }
    Get-ChildItem -Path $dir -Recurse -File -Filter $filter -Force | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "Deleted file: $($_.FullName)"
    }
}

function Reset-Json($path, $jsonText) {
    Ensure-File $path
    Set-Content -Path $path -Value $jsonText -Encoding UTF8 -NoNewline
    Write-Host "Reset json: $path"
}

# -----------------------------
# 1) SACRED / STT / TRANSCRIPTS
# -----------------------------
Clear-File (Join-Path $runtimeRoot "sacred\live_transcript_history.jsonl")
Reset-Json (Join-Path $runtimeRoot "sacred\live_transcript_latest.json") "{}"

Clear-File (Join-Path $runtimeRoot "status\inputfeed_to_text_status.json")
Clear-File (Join-Path $runtimeRoot "status\primary_listener_status.json")

# -----------------------------
# 2) ROUTER QUEUES / STATUS
# -----------------------------
Clear-File (Join-Path $runtimeRoot "queues\router_dispatch\router_input_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "queues\router_dispatch\action_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "queues\router_dispatch\response_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "status\router_dispatch\router_status.json")

# -----------------------------
# 3) DISPLAY ACTIONS / SCREENSHOTS
# -----------------------------
Clear-File (Join-Path $runtimeRoot "display_actions\results\display_action_results.jsonl")
Clear-File (Join-Path $runtimeRoot "display_actions\status\display_action_runner_status.json")
Remove-All-Files-In (Join-Path $runtimeRoot "display_actions\screenshots") "*.png"
Remove-All-Files-In (Join-Path $runtimeRoot "display_actions\screenshots") "*.jpg"
Remove-All-Files-In (Join-Path $runtimeRoot "display_actions\screenshots") "*.jpeg"
Remove-All-Files-In (Join-Path $runtimeRoot "display_actions\screenshots") "*.webp"

# -----------------------------
# 4) SPOKEN QUERIES / RESULTS
# -----------------------------
Clear-File (Join-Path $runtimeRoot "queues\spoken_queries\spoken_query_results.jsonl")
Clear-File (Join-Path $runtimeRoot "status\spoken_queries\spoken_query_status.json")

# -----------------------------
# 5) SPEECH OUT / TTS / CHAT HISTORY
# -----------------------------
Clear-File (Join-Path $runtimeRoot "queues\speech_out\speech_queue.jsonl")
Clear-File (Join-Path $runtimeRoot "queues\speech_out\spoken_history.jsonl")
Reset-Json (Join-Path $runtimeRoot "queues\speech_out\latest_tts.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\speech_out\playback_state.json") "{}"
Clear-File (Join-Path $runtimeRoot "status\speech_out\speech_queue_writer_status.json")
Clear-File (Join-Path $runtimeRoot "status\speech_out\speaker_status.json")

Remove-All-Files-In (Join-Path $runtimeRoot "queues\speech_out\audio") "*.wav"
Remove-All-Files-In (Join-Path $runtimeRoot "queues\speech_out\audio") "*.mp3"
Remove-All-Files-In (Join-Path $runtimeRoot "queues\speech_out\audio") "*.ogg"

# -----------------------------
# 6) OUTPUT / RESPONSE / SESSION / STATE
# -----------------------------
Reset-Json (Join-Path $runtimeRoot "output\latest_response.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\session_snapshot.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\system_runtime.json") "{}"
Reset-Json (Join-Path $runtimeRoot "state\llm_runtime_state.json") "{}"

# -----------------------------
# 7) EXTRA TEMP / CHUNKS / LOG-LIKE FILES
# -----------------------------
Remove-All-Recursive (Join-Path $runtimeRoot "audio_chunks") "*"
Remove-All-Recursive (Join-Path $runtimeRoot "tmp") "*"
Remove-All-Recursive (Join-Path $runtimeRoot "temp") "*"

# Optional: clean loose runtime jsonl/log leftovers
if (Test-Path $runtimeRoot) {
    Get-ChildItem -Path $runtimeRoot -Recurse -File -Force |
    Where-Object {
        $_.Extension -in @(".jsonl", ".log", ".tmp", ".wav", ".mp3", ".ogg") -and
        $_.FullName -notlike "*\stt_archive\*" -and
        $_.FullName -notlike "*\archive\*" -and
        $_.FullName -notlike "*\screenshots\*" -and
        $_.FullName -notlike "*\queues\speech_out\audio\*"
    } | ForEach-Object {
        # already-cleared known files are harmless to clear again
        if ($_.Length -gt 0) {
            Set-Content -Path $_.FullName -Value "" -Encoding UTF8 -NoNewline
            Write-Host "Emptied leftover file: $($_.FullName)"
        }
    }
}

Write-Host ""
Write-Host "CLEAN COMPLETE"
Write-Host ""
