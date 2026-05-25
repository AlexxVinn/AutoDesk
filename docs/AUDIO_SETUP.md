# Audio device setup

The assistant matches Windows playback device **names** to aliases in `config/audio.json`.

## 1. List your devices

With the backend running:

```
GET http://127.0.0.1:9477/audio/devices
```

Or in PowerShell after installing `pycaw`:

```powershell
python -c "from pycaw.pycaw import AudioUtilities; [print(d.FriendlyName) for d in AudioUtilities.GetAllDevices() if getattr(d,'flow',1)==1]"
```

## 2. Edit `config/audio.json`

Update `match` patterns so they appear in your device name:

```json
"earbuds": {
  "match": ["Galaxy Buds", "Your Earbud Name Here"]
}
```

## 3. Voice commands

- `set volume to 40`
- `volume up` / `volume down`
- `mute` / `unmute`
- `switch audio to earbuds`
- `use headsets`

Device switching uses `scripts/switch-audio-device.ps1` on Windows.
