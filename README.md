# anime-filter

Legge la webcam, applica filtri attivati da **gesture** o **tastiera** e pubblica il risultato
come **webcam virtuale** utilizzabile da Teams, Discord, Meet, Zoom, OBS…
Funziona su macOS, Linux e Windows.

Esempio: indice e medio uniti sulla fronte (teletrasporto di Goku) → sparisci dall'inquadratura.

## Architettura

```
Webcam (OpenCV) ─► Perception (MediaPipe) ─► Gesture ─┐
                                    ▲                 ├─► Command ─► FilterChain ─► VirtualCamera (pyvirtualcam)
                    Tastiera (preview) ───────────────┘                         └─► Preview (OpenCV)
```

```
src/anime_filter/
├── cli.py              # entry point `anime-filter`
├── app.py              # loop principale e dispatch dei comandi
├── config.py           # Settings (default → TOML → CLI)
├── commands.py         # Command enum, comune a tastiera e gesture
├── capture/            # acquisizione webcam
├── perception/         # MediaPipe: mani, volto, segmentazione persona
├── gestures/           # riconoscitori (HeldGesture + InstantTransmission)
├── filters/            # Filter, FilterChain, VanishFilter, CartoonFilter
├── controls/           # mappatura tasti → Command
└── output/             # webcam virtuale + finestra di anteprima
```

Per aggiungere un filtro: sottoclasse di `Filter` in `filters/`, registrala in `App`.
Per aggiungere una gesture: sottoclasse di `HeldGesture` che implementa `matches()`.

## Setup sviluppo

Richiede Python 3.11–3.12 (vincolo delle wheel di MediaPipe). Consigliato [uv](https://docs.astral.sh/uv/):

```bash
uv sync                       # crea .venv e installa dipendenze + gruppo dev
uv run anime-filter download-models
uv run anime-filter run
uv run pytest
```

Con pip standard (pip ≥ 25.1 per `--group`):

```bash
python3.12 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e . --group dev
```

## Webcam virtuale: prerequisiti per OS

| OS | Backend | Installazione |
|---|---|---|
| Windows | OBS Virtual Camera | Installa [OBS Studio](https://obsproject.com) ≥ 26 |
| macOS | OBS Virtual Camera | Installa OBS ≥ 30, avvia **una volta** "Start Virtual Camera" da OBS per registrare la system extension, poi chiudi OBS. Concedi al terminale il permesso Fotocamera. |
| Linux | v4l2loopback | `sudo apt install v4l2loopback-dkms` poi `sudo modprobe v4l2loopback devices=1 exclusive_caps=1 card_label="AnimeFilter"` |

Nell'app di videoconferenza seleziona la camera "OBS Virtual Camera" (o "AnimeFilter" su Linux).

## Comandi

| Tasto | Gesture | Azione |
|---|---|---|
| `b` | – | cattura lo sfondo (esci prima dall'inquadratura) |
| `v` | indice+medio sulla fronte | sparisci / riappari |
| `c` | – | filtro cartoon |
| `q` / `ESC` | – | esci |

I tasti funzionano con il focus sulla finestra di anteprima.
