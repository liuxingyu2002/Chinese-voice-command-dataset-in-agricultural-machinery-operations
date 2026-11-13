# Chinese Voice Command Dataset for Agricultural Machinery Operations

A Chinese voice-command dataset designed for **long-audio automatic speech
recognition (ASR)** in agricultural machinery (tractor plowing) operating
environments. Each subset contains continuous long audio with tractor
background noise plus human-voice commands, together with the ordered command
transcript. This dataset accompanies the paper
_"Agricultural Machinery Voice Command Recognition Based on Customized Large
Models"_ (Under review, 2026).

> The ASR system studied in the paper takes the **long audio as input**;
> segmentation is performed by a downstream stage of the system. Therefore the
> audio in this repository is provided as **fixed-length 5-second slices**
> (consecutive, non-overlapping windows of the original long recording), and
> `transcript.txt` is the **ordered command list** for the full recording. The
> slices, concatenated in filename order, reconstruct the original long audio.

## Contents

- [Overview](#overview)
- [Statistics](#statistics)
- [Directory structure](#directory-structure)
- [Subset description](#subset-description)
- [Audio format](#audio-format)
- [Transcript format](#transcript-format)
- [Usage](#usage)
- [License](#license)
- [Citation](#citation)

## Overview

The dataset was constructed with a hybrid method (direct recording + synthesis)
to simulate different agricultural machinery operation scenarios. It contains
three recording sets:

| Recording set | Description | Tractor | Province |
|---|---|---|---|
| **RealRec** | Real recordings with accent real voice (ACC), captured on a cellphone mounted on the windshield during field operation | Dongfeng 2004-5A (G4) | Suqian, Jiangsu |
| **SynRec DF** | Mixed recordings: human-voice commands superimposed on a background-noise recording of a Dongfeng tractor | Dongfeng 2004-5A (G4) | Songjiang, Shanghai |
| **SynRec KQ** | Mixed recordings: human-voice commands superimposed on a background-noise recording of a Kubota tractor | Kubota M704-KQ (G4) | Suqian, Jiangsu |

Each of the two mixed recording sets (SynRec DF and SynRec KQ) contains the
**same three voice types**:

- **RV (STD)** — standard (unaccented) **real** human voice
- **SV (STD)** — standard (unaccented) **synthetic** voice (iFLYTEK TTS)
- **SV (ACC)** — accented **synthetic** voice (iFLYTEK TTS, Henan accent)

Recording devices are cellphones configured to **Mono-M4A, 48 kHz sample rate,
16-bit depth** at capture time. The provided WAV slices are the post-processed
waveform.

## Statistics

### Per recording set

| Item | RealRec (ACC) | SynRec DF | SynRec KQ |
|---|---|---|---|
| Total audio duration | 2h22m50s | 33m2s | 57m11s |
| Number of commands | 212 | 100 | 100 |
| Machinery model | Dongfeng 2004-5A (G4) | Dongfeng 2004-5A (G4) | Kubota M704-KQ (G4) |
| Cellphone | HUAWEI Pura 70 | HUAWEI Pura 70 | iPhone 14 Pro Max |
| Operation province | Suqian, Jiangsu | Songjiang, Shanghai | Suqian, Jiangsu |

### Per subset (5-second slices)

| Subset folder | Set | Voice / Accent | Slices | Total duration | Sample rate | Channels | Transcript lines |
|---|---|---|---|---|---|---|---|
| `data/realrec_acc` | RealRec | real / ACC (Dongbei) | 1712 | 2h22m40s | 48000 Hz | 1 | 215 |
| `data/synrec_df_rv_std` | SynRec DF | real / STD | 207 | 17m15s | 16000 Hz | 1 | 100 |
| `data/synrec_df_sv_acc` | SynRec DF | synth / ACC (Henan) | 201 | 16m45s | 16000 Hz | 1 | 100 |
| `data/synrec_df_sv_std` | SynRec DF | synth / STD | 200 | 16m40s | 16000 Hz | 1 | 100 |
| `data/synrec_kq_rv_std` | SynRec KQ | real / STD | 395 | 32m55s | 16000 Hz | 1 | 100 |
| `data/synrec_kq_sv_acc` | SynRec KQ | synth / ACC (Henan) | 396 | 33m00s | 16000 Hz | 1 | 100 |
| `data/synrec_kq_sv_std` | SynRec KQ | synth / STD | 395 | 32m55s | 16000 Hz | 1 | 100 |

## Directory structure

```
.
├── README.md
├── README_zh.md               # Chinese translation of this README
├── LICENSE
├── metadata/
│   └── index.csv              # one row per subset, machine-readable index
├── scripts/
│   └── build_index.py         # regenerate metadata/index.csv from data/
└── data/
    ├── realrec_acc/
    │   ├── audio/             # 1712 WAV slices (prefixes 2_/3_/4_ = 3 cellphones)
    │   └── transcript.txt     # 212 ordered commands (Dongbei accent)
    ├── synrec_df_rv_std/
    │   ├── audio/             # 207 WAV slices
    │   └── transcript.txt
    ├── synrec_df_sv_acc/
    │   ├── audio/
    │   └── transcript.txt
    ├── synrec_df_sv_std/
    │   ├── audio/
    │   └── transcript.txt
    ├── synrec_kq_rv_std/
    │   ├── audio/
    │   └── transcript.txt
    ├── synrec_kq_sv_acc/
    │   ├── audio/
    │   └── transcript.txt
    └── synrec_kq_sv_std/
        ├── audio/
        └── transcript.txt
```

## Subset description

- **RealRec (ACC)** — `data/realrec_acc/`. Three real recordings from three
  cellphones (slice filename prefixes `2_`, `3_`, `4_`) mounted on the
  windshield of a Dongfeng 2004-5A (G4) tractor during plowing in Suqian,
  Jiangsu. The operator speaks with a Dongbei accent. This is the only subset
  with real background noise captured in the field together with the commands.

- **Mixed recording with standard real voice (RV STD)** — `data/synrec_df_rv_std/`
  and `data/synrec_kq_rv_std/`. Real human-voice commands recorded in a quiet
  environment, mixed with a tractor background-noise recording. Natural voice,
  unaccented delivery. The two folders differ only in the background-noise
  source: Dongfeng tractor noise recorded in Songjiang, Shanghai (DF) vs
  Kubota tractor noise recorded in Suqian, Jiangsu (KQ).

- **Mixed recording with standard synthetic voice (SV STD)** —
  `data/synrec_df_sv_std/` and `data/synrec_kq_sv_std/`. Commands synthesized
  by iFLYTEK online TTS (unaccented setting), mixed with the background-noise
  recording of the respective tractor.

- **Mixed recording with accent synthetic voice (SV ACC)** —
  `data/synrec_df_sv_acc/` and `data/synrec_kq_sv_acc/`. Commands synthesized
  by iFLYTEK online TTS (Henan accent setting), mixed with the background-noise
  recording of the respective tractor.

## Audio format

- **Container:** WAV (PCM)
- **Slice length:** 5.00 s (consecutive, non-overlapping; the last slice of a
  recording may be shorter)
- **Sample rate:** 48000 Hz (RealRec) / 16000 Hz (SynRec subsets)
- **Channels:** mono (1)
- **Bit depth:** 16-bit

## Transcript format

Each subset has one `transcript.txt` containing the **ordered list of voice
commands** for the full recording, one command per line (UTF-8, `\n` line
endings). The line order corresponds to the order in which the commands appear
in the audio. There is no per-slice or timestamp alignment — alignment is
intentionally deferred to the downstream segmentation stage of the ASR system.

Example (`data/realrec_acc/transcript.txt`):

```
落犁
起犁
转弯
落犁
起犁
...
```

## Citation

If you use this dataset, please cite both the accompanying paper and this
repository.