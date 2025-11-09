# Applied Cryptography Project: Practical MD5 Collision Attacks

This project empirically demonstrates the **practical feasibility of MD5 hash collisions** via three attacks on generic binaries, PDF documents, and PNG images.

The entire workflow (generation ➜ verification ➜ summaries) is automated by:
```
final_deliverables/generate_all_collisions.py
```

---

## 1. Compilation and Installation

**Tested environment:** Ubuntu 24.04.2 LTS (VM).

### Dependencies

| Dependency | Purpose | Install |
|---|---|---|
| Python 3 + `venv` | Runtime & isolation | preinstalled / `apt` |
| `mupdf-tools` (mutool) | PDF parsing/merging helper | `sudo apt install mupdf-tools` |
| `radare2` (`radiff2`) | Binary diff/visual check | `sudo apt install radare2` |
| `pycryptodome` | Lib used by Corkami helpers | `pip install pycryptodome` |
| HashClash / Corkami | Collision primitives & scripts | clone via `git` |

### Setup

```bash
# 1) Base packages
sudo apt update
sudo apt install -y build-essential git mupdf-tools radare2 python3-venv

# 2) Project root
cd ~/md5-collision-project   # adjust if different

# 3) Virtual environment
python3 -m venv venv
source venv/bin/activate

# 4) Python deps
pip install pycryptodome


### 5) Build HashClash

cd md5-collision-project/
cd hashclash/

# required build tools and libraries
sudo apt-get install -y autoconf automake libtool
sudo apt-get install -y zlib1g-dev libbz2-dev

# build HashClash (automatically handles Boost if missing)
chmod +x build.sh
./build.sh

# verify build
find . -type f -name md5_fastcoll -perm -111

# return to final_deliverables
cd ..
cd final_deliverables/

```

---

## 2. Running the Test Cases

The master script creates **six artifacts** under:
```
final_deliverables/collision_artifacts/
```

```bash
# from project root
source venv/bin/activate
python3 final_deliverables/generate_all_collisions.py
```

---

## 3. Output Interpretation

The script prints `md5sum` lines and stores all outputs in `collision_artifacts/`.

| Artifacts (pair) | Attack type | Verification | Expected result |
|---|---|---|---|
| `file_A_generic_coll.bin` / `file_B_generic_coll.bin` | **Identical-Prefix** (generic binaries) | `md5sum`, `radiff2` | Same MD5, but `radiff2` shows byte differences |
| `doc_A_safe_view.pdf` / `doc_B_malicious_view.pdf` | **Reusable** (PDF) | `md5sum`, open both in any PDF viewer | Same MD5, **visually different** documents |
| `img_A_good_view.png` / `img_B_bad_view.png` | **Reusable** (PNG) | `md5sum`, open in image viewer | Same MD5, **visually different** images |

### Manual checks

```bash
# Check all hashes (pairs should match)
md5sum collision_artifacts/*

# Check all SHA-256 hashes (every file should have a unique hash)
sha256sum collision_artifacts/*

# Prove binary non-equality on the generic pair
radiff2 -x collision_artifacts/file_A_generic_coll.bin            collision_artifacts/file_B_generic_coll.bin
```

`radiff2` should highlight differing bytes, proving the files are distinct despite equal MD5.

---

## 4. Implementation Overview

`generate_all_collisions.py` orchestrates three pipelines:

1) **Identical-Prefix (generic .bin)**  
   Uses Corkami’s MD5 collision blocks to craft two different binaries whose first block is identical and overall MD5 collides.

2) **Reusable Collision for PDF**  
   Leverages `mutool` plus Corkami `pdf.py` helpers to embed colliding blocks into two PDFs that render different visible content while preserving the same MD5 digest.

3) **Reusable Collision for PNG**  
   Adapts colliding payloads to PNG structure (headers/IDAT placement) to produce two images with different appearance but identical MD5.

4) **Verification & logging**  
   After generation, the script runs `md5sum` and (for the generic pair) `radiff2`, printing results to stdout and saving artifacts under `collision_artifacts/`.

---

## 5. Results Summary

- MD5 collisions were reliably produced for **three file types**.  
- In all cases, pairs **share the same MD5 hash** while being **binary or visually different**.  
- This demonstrates why MD5 is **unsuitable for integrity, signing, or security-critical deduplication**.

---

## 6. Project Structure (excerpt)

```
md5-collision-project/
├─ final_deliverables/
│  ├─ generate_all_collisions.py
│  └─ collision_artifacts/
│     ├─ file_A_generic_coll.bin
│     ├─ file_B_generic_coll.bin
│     ├─ doc_A_safe_view.pdf
│     ├─ doc_B_malicious_view.pdf
│     ├─ img_A_good_view.png
│     └─ img_B_bad_view.png
├─ collisions/        # Corkami (external)
└─ hashclash/         # HashClash (external)
```

---

## 7. References & Acknowledgements

- Corkami “collisions” framework — https://github.com/corkami/collisions  
- HashClash (Marc Stevens et al.) — https://github.com/cr-marcstevens/hashclash  
- DTU 02232 *Applied Cryptography* (Fall 2025) materials on collision attacks.
---

**Course:** 02232 Applied Cryptography — Technical University of Denmark  
**Authors:** Group 09  
---
**If you have any questions or need help with installation, please feel free to contact me at [s242513@dtu.dk].**
