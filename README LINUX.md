
Here is the simple review:

app/inputfeed_to_text/mic_audio_source.py
Added Linux microphone support using sounddevice. Windows still keeps the old WasapiMicAudioSource.

app/inputfeed_to_text/inputfeed_to_text_service.py
Now it asks a helper to choose the correct mic source. Windows gets Windows audio, Linux gets Linux audio.

app/inputfeed_to_text/inputfeed_settings.py
Default input backend is now smart: Windows = windows_wasapi_mic, Linux = sounddevice_mic.

scripts/start_main_stack.py
Can now find running app processes on Linux using /proc, not only Windows wmic.

scripts/stop_main_stack.py
Can now stop Linux processes with SIGTERM, while Windows still uses taskkill.

app/ui_local/app.py
UI buttons now work better on Linux. Process check uses Linux-safe logic, and clear chat has Python cleanup if PowerShell is not available.

app/settings/audio_settings.py
Linux no longer uses your Windows mic/speaker names by default. It uses default audio devices.

app/ui_local/library_ui/workspace/services_workspace.py
Fixed path matching so Linux paths like /home/user/file.txt do not get changed into Windows paths.

app/web_tools/config.py
On Linux servers without a screen, browser automation starts headless automatically.

app/requirements-linux.txt
New Linux install list. It removes PyAudioWPatch, because that is Windows-specific.

Important detail: Linux should now be much closer, but real mic/screenshot testing still must happen on a Linux machine.