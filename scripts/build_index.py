#!/usr/bin/env python3
"""Build metadata/index.csv by scanning the dataset subset folders under data/.

For each subset folder (e.g. data/realrec_acc, data/synrec_df_rv_std, ...), this
script:
  - scans its audio/ directory for *.wav files
  - reads each WAV header to count slices and total duration
  - counts non-empty transcript lines
  - merges with the author-provided metadata (set, voice, accent, tractor,
    province, cellphone, audio format, ...)
  - writes one row per subset to metadata/index.csv

Audio format fields (sample_rate_hz, channels, bit_depth) are author-specified
canonical values; slice counts, durations and transcript line counts are
measured from the actual files.

Re-run after any data change to regenerate the index.
"""
import csv
import os
import re
import wave
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

# Author-provided metadata keyed by exact folder name (under data/).
# Fields: set, voice_type, accent, tractor_model, operation_province,
#         cellphone, speaker_accent, n_commands, sample_rate_hz, channels,
#         bit_depth, notes
#
# NOTE on voice types (per the paper body text and the actual data):
#   The mixed recording sets (SynRec DF, SynRec KQ) share the SAME three voice
#   types: RV (STD) standard real voice, SV (STD) standard synthetic voice,
#   and SV (ACC) accent synthetic voice (Henan accent, iFLYTEK TTS).
#   SynRec DF and SynRec KQ differ ONLY in the background-noise source
#   (Dongfeng 2004-5A tractor vs Kubota M704-KQ tractor). There is no RV(ACC)
#   subset; the real-voice subsets in both sets are RV(STD) (unaccented).
#
# NOTE on operation provinces (corrected):
#   SynRec DF background noise was recorded in Songjiang, Shanghai.
#   SynRec KQ background noise was recorded in Suqian, Jiangsu.
PAPER_META = {
    "realrec_acc": dict(
        set="RealRec", voice_type="real", accent="ACC",
        tractor_model="Dongfeng 2004-5A (G4)",
        operation_province="Suqian, Jiangsu",
        cellphone="HUAWEI Pura 70", speaker_accent="Dongbei",
        n_commands=212, sample_rate_hz="48000", channels="1", bit_depth="16",
        notes="real recording with Dongbei accent; three real recordings from "
              "three cellphones (slice prefixes 2_/3_/4_)",
    ),
    "synrec_df_rv_std": dict(
        set="SynRec DF", voice_type="real", accent="STD",
        tractor_model="Dongfeng 2004-5A (G4)",
        operation_province="Songjiang, Shanghai",
        cellphone="HUAWEI Pura 70", speaker_accent="Unaccent",
        n_commands=100, sample_rate_hz="16000", channels="1", bit_depth="16",
        notes="mixed: standard real voice + Dongfeng-tractor background noise",
    ),
    "synrec_df_sv_acc": dict(
        set="SynRec DF", voice_type="synthetic", accent="ACC",
        tractor_model="Dongfeng 2004-5A (G4)",
        operation_province="Songjiang, Shanghai",
        cellphone="HUAWEI Pura 70", speaker_accent="Henan",
        n_commands=100, sample_rate_hz="16000", channels="1", bit_depth="16",
        notes="mixed: Henan-accent synthetic voice (iFLYTEK TTS) + Dongfeng noise",
    ),
    "synrec_df_sv_std": dict(
        set="SynRec DF", voice_type="synthetic", accent="STD",
        tractor_model="Dongfeng 2004-5A (G4)",
        operation_province="Songjiang, Shanghai",
        cellphone="HUAWEI Pura 70", speaker_accent="Unaccent",
        n_commands=100, sample_rate_hz="16000", channels="1", bit_depth="16",
        notes="mixed: unaccented synthetic voice (iFLYTEK TTS) + Dongfeng noise",
    ),
    "synrec_kq_rv_std": dict(
        set="SynRec KQ", voice_type="real", accent="STD",
        tractor_model="Kubota M704-KQ (G4)",
        operation_province="Suqian, Jiangsu",
        cellphone="iPhone 14 Pro Max", speaker_accent="Unaccent",
        n_commands=100, sample_rate_hz="16000", channels="1", bit_depth="16",
        notes="mixed: standard real voice + Kubota-tractor background noise. "
              "Same voice type as synrec_df_rv_std; differs only in noise source",
    ),
    "synrec_kq_sv_acc": dict(
        set="SynRec KQ", voice_type="synthetic", accent="ACC",
        tractor_model="Kubota M704-KQ (G4)",
        operation_province="Suqian, Jiangsu",
        cellphone="iPhone 14 Pro Max", speaker_accent="Henan",
        n_commands=100, sample_rate_hz="16000", channels="1", bit_depth="16",
        notes="mixed: Henan-accent synthetic voice (iFLYTEK TTS) + Kubota noise",
    ),
    "synrec_kq_sv_std": dict(
        set="SynRec KQ", voice_type="synthetic", accent="STD",
        tractor_model="Kubota M704-KQ (G4)",
        operation_province="Suqian, Jiangsu",
        cellphone="iPhone 14 Pro Max", speaker_accent="Unaccent",
        n_commands=100, sample_rate_hz="16000", channels="1", bit_depth="16",
        notes="mixed: unaccented synthetic voice (iFLYTEK TTS) + Kubota noise",
    ),
}


def wav_duration(path):
    """Return duration in seconds, or None on failure."""
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return None


def fmt_duration(seconds):
    s = int(round(seconds))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    return f"{m}m{s:02d}s"


def scan_subset(folder):
    audio_dir = os.path.join(DATA_DIR, folder, "audio")
    wavs = sorted(f for f in os.listdir(audio_dir) if f.lower().endswith(".wav"))
    durations = []
    prefixes = Counter()
    bad = 0
    for f in wavs:
        d = wav_duration(os.path.join(audio_dir, f))
        if d is None:
            bad += 1
            continue
        durations.append(d)
        m = re.match(r"([A-Za-z0-9]+)[_\s]", f)
        if m:
            prefixes[m.group(1)] += 1
    tpath = os.path.join(DATA_DIR, folder, "transcript.txt")
    n_lines = 0
    if os.path.isfile(tpath):
        with open(tpath, encoding="utf-8") as fh:
            n_lines = sum(1 for line in fh if line.strip())
    return {
        "n_slices": len(wavs),
        "n_bad": bad,
        "total_duration": fmt_duration(sum(durations)),
        "slice_seconds": round(min(durations), 2) if durations else 0,
        "n_transcript_lines": n_lines,
    }


def main():
    rows = []
    for folder in sorted(PAPER_META.keys()):
        audio_dir = os.path.join(DATA_DIR, folder, "audio")
        if not os.path.isdir(audio_dir):
            print(f"[warn] missing audio dir: data/{folder}/audio")
            continue
        scan = scan_subset(folder)
        meta = PAPER_META[folder]
        rows.append({
            "subset_id": folder,
            "folder": folder,
            "set": meta["set"],
            "voice_type": meta["voice_type"],
            "accent": meta["accent"],
            "speaker_accent": meta["speaker_accent"],
            "tractor_model": meta["tractor_model"],
            "operation_province": meta["operation_province"],
            "cellphone": meta["cellphone"],
            "sample_rate_hz": meta["sample_rate_hz"],
            "channels": meta["channels"],
            "bit_depth": meta["bit_depth"],
            "slice_length_s": scan["slice_seconds"],
            "n_slices": scan["n_slices"],
            "total_duration": scan["total_duration"],
            "n_commands_paper": meta["n_commands"],
            "n_transcript_lines": scan["n_transcript_lines"],
            "audio_dir": f"data/{folder}/audio",
            "transcript_file": f"data/{folder}/transcript.txt",
            "notes": meta["notes"],
        })
        print(f"[ok] {folder}: {scan['n_slices']} slices, {scan['total_duration']}")

    out = os.path.join(ROOT, "metadata", "index.csv")
    fieldnames = list(rows[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\n[written] {out}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
