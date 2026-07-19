#!/usr/bin/env bash
set -euo pipefail
BASE="$HOME/.local/share/youtube-subtitle-translator"
CFG="$HOME/.config/youtube-subtitle-translator"
mkdir -p "$BASE" "$CFG" "$HOME/.config/systemd/user"
cp "$(dirname "$0")/gemini_tts_server.py" "$BASE/gemini_tts_server.py"
if [[ ! -s "$CFG/env" ]]; then
  read -r -s -p 'Gemini API key: ' KEY; echo
  printf 'GEMINI_API_KEY=%s\n' "$KEY" > "$CFG/env"
  chmod 600 "$CFG/env"
fi
cat > "$HOME/.config/systemd/user/gemini-tts.service" <<EOF
[Unit]
Description=Gemini Vietnamese TTS bridge
After=network-online.target
[Service]
EnvironmentFile=%h/.config/youtube-subtitle-translator/env
ExecStart=/usr/bin/python3 %h/.local/share/youtube-subtitle-translator/gemini_tts_server.py
Restart=on-failure
[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now gemini-tts.service
echo 'Gemini TTS đã cài và chạy nền tại http://127.0.0.1:8765/tts'
