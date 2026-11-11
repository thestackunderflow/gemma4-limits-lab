# Data sources

| File | Source | Licence | sha256 | Fetched |
|---|---|---|---|---|
| `data/pg1342.txt` (not committed; fetched by `lab/fetch.py`) | Project Gutenberg eBook #1342, *Pride and Prejudice* (Jane Austen), https://www.gutenberg.org/cache/epub/1342/pg1342.txt | Public domain in the USA (Project Gutenberg licence; header kept in the file) | `3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75` | 2026-11-10 |

Lab-made: OCR screenshots, charts and two-image cards (`lab/images.py`, seed 42), the espeak-ng control clip.

| File | Source | Licence | sha256 | Fetched |
|---|---|---|---|---|
| `out/p15/audio/librivox.wav` (first 30 s, 16 kHz mono, cut with ffmpeg `-t 30`) | LibriVox, *Pride and Prejudice* (collection prideandprejudice_1005_librivox), chapter 1, https://archive.org/download/prideandprejudice_1005_librivox/prideandprejudice_01_austen_64kb.mp3 | Public Domain Mark 1.0 (archive.org licenseurl) | mp3 `aa7339960c90bed4c57ffe144c96b7a8ef4de482d6505d19906bb50248fe6f0c` | 2026-11-10 |

The LibriVox truth text in `lab/p15.py` is the standard LibriVox disclaimer plus the book's first sentence; the reader's
exact words were not checked by ear in the lab stage (WER against it is marked as such; transcript kept).
