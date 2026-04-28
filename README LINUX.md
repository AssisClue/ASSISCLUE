# ASSISCLUE Linux Setup

This is the beginner Linux install guide.

Linux support is close, but still needs real testing for microphone, speaker, screenshot, and browser automation.

## 1. Install System Packages

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip portaudio19-dev ffmpeg
```

## 2. Download The Project

```bash
mkdir -p ~/AI/ASSISCLUE  
cd ~/AI/ASSISCLUE
git clone https://github.com/AssisClue/ASSISCLUE.git
```

Replace `<YOUR_GITHUB_REPO_URL>` with the real GitHub repo URL.

## 3. Create Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-linux.txt
python -m playwright install --with-deps chromium
```

## 4. Start The App

```bash
python scripts/start_main_stack.py
python scripts/stop_main_stack.py
```
MAIN INTERFACE RUN FROM START

Open the main Web UI:

```text
http://127.0.0.1:8000
```

Start library Web UI only:

```bash
uvicorn app.ui_local.library_ui.appdocs:app --host 127.0.0.1 --port 8001 --reload
```

Open library Web UI:

```text
http://127.0.0.1:8001
```



## Common Commands

Run this first when you open a new terminal:

```bash
cd ~/AI/ASSISCLUE
source .venv/bin/activate
```

Start the full app:

```bash
python scripts/start_main_stack.py
```

Stop the full app:

```bash
python scripts/stop_main_stack.py
```


Light clean runtime files:
(this might need policy permissions
)
```bash
python scripts/clean_all_lightrun.py
```


## Optional Test Commands

```bash
python -m py_compile app/inputfeed_to_text/mic_audio_source.py
INPUTFEED_SOURCE_BACKEND=sounddevice_mic python -m app.inputfeed_to_text.inputfeed_to_text_service
```

## What Linux Changes

ASSISCLUE was first built around Windows.

Linux now has safer defaults for:

- microphone input
- process start / stop
- browser headless mode
- runtime cleaning

Default microphone backend:

- Windows: `windows_wasapi_mic`
- Linux: `sounddevice_mic`

## Known Linux Risks

These parts may still need fixes after real Linux testing:

- real microphone capture
- speaker / TTS playback
- screenshot capture with X11 or Wayland
- browser automation on desktop or server

## Common Problems

If install fails on audio packages, run:

```bash
sudo apt install -y portaudio19-dev ffmpeg
```

If Playwright browser is missing, run:

```bash
python -m playwright install --with-deps chromium
```

If the app does not open, check that the terminal still says the server is running, then open:

```text
http://127.0.0.1:8000
```
