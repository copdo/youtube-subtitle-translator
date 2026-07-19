#!/usr/bin/env python3
"""Minimal local Gemini TTS bridge. Run with GEMINI_API_KEY set."""
import base64, json, os, struct
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")
KEY = os.environ.get("GEMINI_API_KEY", "")

def wav(pcm, rate=24000):
    data = struct.pack('<4sI4s4sIHHIIHH4sI', b'RIFF', 36+len(pcm), b'WAVE', b'fmt ', 16, 1, 1, rate, rate*2, 2, 16, b'data', len(pcm))
    return data + pcm

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin', '*'); self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS'); self.send_header('Access-Control-Allow-Headers', 'Content-Type'); self.end_headers()

    def do_POST(self):
        if self.path != '/tts': self.send_error(404); return
        if not KEY: self.send_error(503, 'GEMINI_API_KEY is not configured'); return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
            text = str(body.get('text', '')).strip()
            if not text or len(text) > 2000: raise ValueError('text must be 1..2000 chars')
            payload = {"contents":[{"parts":[{"text":"Read aloud naturally in Vietnamese:\n" + text}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":body.get('voice','Kore')}}}}}
            req = Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json','x-goog-api-key':KEY})
            with urlopen(req, timeout=30) as r: result = json.load(r)
            pcm = base64.b64decode(result['candidates'][0]['content']['parts'][0]['inlineData']['data'])
            audio = wav(pcm)
            self.send_response(200); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Content-Type','audio/wav'); self.send_header('Content-Length',str(len(audio))); self.end_headers(); self.wfile.write(audio)
        except HTTPError as e:
            detail = e.read().decode(errors='replace')
            self.send_error(502, f'Gemini API {e.code}: {detail[:500]}')
        except Exception as e: self.send_error(502, str(e))
    def log_message(self, *_): pass

if __name__ == '__main__':
    print('Gemini TTS listening on http://127.0.0.1:8765/tts')
    HTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
