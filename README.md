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

## Installazione e primo avvio

Richiede Python 3.11–3.12 (vincolo delle wheel di MediaPipe). Il modo consigliato per installare le dipendenze è [uv](https://docs.astral.sh/uv/), che funziona anche su Windows.

### Windows (PowerShell)

Apri PowerShell e installa `uv` con il comando ufficiale:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Dopo l'installazione, chiudi e riapri **PowerShell**. Se usi il terminale integrato di VS Code, chiudi e riapri anche VS Code, così carica il `PATH` aggiornato. Verifica che il comando sia disponibile:

```powershell
uv --version
```

Se hai installato `uv` con lo script ufficiale ma PowerShell continua a non trovarlo, puoi verificarne l'installazione invocando direttamente l'eseguibile:

```powershell
& "$env:USERPROFILE\.local\bin\uv.exe" --version
```

Quando `uv --version` funziona, apri PowerShell nella cartella del progetto e lancia:

```bash
uv python install 3.12
uv sync
uv run anime-filter download-models
uv run anime-filter run
```

`uv sync` crea `.venv` e installa dipendenze e strumenti di sviluppo. Il download dei modelli richiede Internet e si fa una sola volta; se lo salti, l'app li scarica al primo avvio. Per uscire dall'app premi `q` o `ESC` nella finestra di anteprima.

### Altri sistemi

Gli stessi comandi `uv sync` e `uv run` funzionano su macOS e Linux. Se preferisci installare senza `uv`, con pip 25.1 o successivo:

Windows (PowerShell), senza bisogno di attivare l'ambiente virtuale:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e . --group dev
.\.venv\Scripts\anime-filter.exe download-models
.\.venv\Scripts\anime-filter.exe run
```

macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e . --group dev
anime-filter download-models
anime-filter run
```

Per eseguire i test di sviluppo: `uv run pytest`.

## Usare la webcam virtuale

### Windows: cosa fare dopo aver installato OBS

OBS Studio installa anche il dispositivo **OBS Virtual Camera**, che Anime Filter usa per pubblicare il video elaborato. Su Windows:

1. Installa OBS Studio (versione 26 o successiva).
2. Avvia Anime Filter con `uv run anime-filter run` dalla cartella del progetto. Si aprirà la finestra di anteprima.
3. In Teams, Discord, Meet o Zoom seleziona **OBS Virtual Camera** come videocamera.

Non devi creare scene in OBS né premere **Start Virtual Camera**: l'app invia i fotogrammi direttamente al dispositivo virtuale installato da OBS. Per questa modalità OBS può restare chiuso. Consenti ad app desktop di accedere alla fotocamera nelle impostazioni di privacy di Windows; se la webcam non si apre, chiudi le altre app che la stanno usando.

Anime Filter non passa attraverso una scena OBS: la webcam virtuale OBS è l'uscita diretta dell'app. Se vuoi invece comporre il risultato in una scena OBS e riutilizzare la sua webcam virtuale come uscita, il dispositivo OBS integrato non può fare entrambe le cose contemporaneamente.

### Prerequisiti per gli altri sistemi

| OS | Backend | Installazione |
|---|---|---|
| Windows | OBS Virtual Camera | Installa [OBS Studio](https://obsproject.com) ≥ 26; vedi i passaggi sopra |
| macOS | OBS Virtual Camera | Installa OBS ≥ 30, avvia **una volta** "Start Virtual Camera" da OBS per registrare la system extension, poi chiudi OBS. Concedi al terminale il permesso Fotocamera. |
| Linux | v4l2loopback | `sudo apt install v4l2loopback-dkms` poi `sudo modprobe v4l2loopback devices=1 exclusive_caps=1 card_label="AnimeFilter"` |

Su macOS e Linux, avvia l'app con `uv run anime-filter run`; nell'app di videoconferenza seleziona **OBS Virtual Camera** (o **AnimeFilter** su Linux).

## Comandi

| Tasto | Gesture | Azione |
|---|---|---|
| `b` | – | cattura lo sfondo (esci prima dall'inquadratura) |
| `v` | indice+medio sulla fronte | sparisci / riappari |
| `c` | – | filtro cartoon |
| `q` / `ESC` | – | esci |

I tasti funzionano con il focus sulla finestra di anteprima.
