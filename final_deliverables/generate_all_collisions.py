import subprocess
import os
import sys
import shutil

# --- Configuration: Paths are relative to the project root ---
# Assumes structure: PROJECT_ROOT -> {hashclash/, collisions/, final_deliverables/}
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("PROJECT_ROOT>>> " +PROJECT_ROOT)
HASHCLASH_BIN = os.path.join(PROJECT_ROOT, 'hashclash', 'bin')
print("HASHCLASH_BIN>>> " +HASHCLASH_BIN)
CORKAMI_COLLISIONS = os.path.join(PROJECT_ROOT, 'collisions')
print("CORKAMI_COLLISIONS>>> " +CORKAMI_COLLISIONS)
CORKAMI_SCRIPTS = os.path.join(PROJECT_ROOT, 'collisions', 'scripts')
print("CORKAMI_SCRIPTS>>> " +CORKAMI_SCRIPTS)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collision_artifacts')
print("OUTPUT_DIR>>> " + OUTPUT_DIR)

# --- File Definitions (Must be present in CORKAMI_COLLISIONS) ---
PDF_FILES = ['input_safe.pdf', 'input_malicious.pdf', 'dummy.pdf', 'pdf1.bin', 'pdf2.bin']
PNG_FILES = ['input_good.png', 'input_bad.png', 'png1.bin', 'png2.bin']


def check_inputs(file_list, base_dir):
    """Checks if all necessary input files exist."""
    missing = [f for f in file_list if not os.path.exists(os.path.join(base_dir, f))]
    if missing:
        print(f"\n[ERROR] Required files are missing in {base_dir}/:")
        for f in missing:
            print(f"  - {f}")
        print("Please acquire/create these files and rerun the script.")
        sys.exit(1)


def run_command(cmd, cwd=None, is_fastcoll=False):
    """Helper function to run shell commands and handle errors."""
    if not is_fastcoll:
        print(f"  > Executing: {' '.join(cmd)}")
    try:
        # Fastcoll is noisy; suppress output unless check=True throws an error
        subprocess.run(cmd, check=True, cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed in directory: {cwd or os.getcwd()}")
        print(f"Command: {e.cmd}")
        print(f"Stdout (partial): {e.stdout[:500]}")
        print(f"Stderr (partial): {e.stderr[:500]}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n[ERROR] Required binary not found. Check if '{cmd[0]}' is installed or in the PATH.")
        sys.exit(1)


def clean_local_files(cwd, files_to_clean):
    """Removes temporary files from the current working directory (cwd)."""
    for f in files_to_clean:
        file_path = os.path.join(cwd, f)
        if os.path.exists(file_path):
            os.remove(file_path)


# --- Main Execution ---

print("--- Starting MD5 Collision Generation ---")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------
# 1. Identical Prefix Collision (Generic File)
# -----------------------------------------------------------
print("\n[1/3] Generating Generic Identical Prefix Collision (md5_fastcoll)...")

PREFIX_FILE = os.path.join(OUTPUT_DIR, 'temp_prefix.txt')
if os.path.exists(PREFIX_FILE): os.remove(PREFIX_FILE)

# Create the prefix file directly in the output directory
with open(PREFIX_FILE, 'w') as f:
    f.write("MD5 Collision Project - Generic Identical Prefix Test")

# Run md5_fastcoll. It outputs temp_prefix_msg1.txt and temp_prefix_msg2.txt to its CWD.
# We run it from $OUTPUT_DIR to simplify path handling.
run_command([os.path.join(HASHCLASH_BIN, 'md5_fastcoll'), '-p', PREFIX_FILE], cwd=OUTPUT_DIR, is_fastcoll=True)

# Rename the generated files to the final names
OUTPUT_A = os.path.join(OUTPUT_DIR, 'file_A_generic_coll.bin')
OUTPUT_B = os.path.join(OUTPUT_DIR, 'file_B_generic_coll.bin')
run_command(['mv', os.path.join(OUTPUT_DIR, 'temp_prefix_msg1.txt'), OUTPUT_A])
run_command(['mv', os.path.join(OUTPUT_DIR, 'temp_prefix_msg2.txt'), OUTPUT_B])
os.remove(PREFIX_FILE)
print(f"  > Created: {os.path.basename(OUTPUT_A)} and {os.path.basename(OUTPUT_B)}")

# -----------------------------------------------------------
# 2. Reusable/Formatting Trick Collision (PDF Files)
# -----------------------------------------------------------
print("\n[2/3] Generating Reusable PDF Collision (pdf.py)...")

check_inputs(PDF_FILES, CORKAMI_COLLISIONS)
PDF_TEMP_FILES = ['collision1.pdf', 'collision2.pdf', 'first.pdf', 'second.pdf', 'merged.pdf', 'hacked.pdf',
                  'cleaned.pdf']

# Copy inputs locally to the script's execution directory
for f in PDF_FILES:
    shutil.copy(os.path.join(CORKAMI_COLLISIONS, f), CORKAMI_SCRIPTS)

# Run the PDF collision script
# NOTE: The execution directory must be CORKAMI_SCRIPTS
run_command(['python3', 'pdf.py', os.path.basename(PDF_FILES[0]), os.path.basename(PDF_FILES[1])], cwd=CORKAMI_SCRIPTS)

# Move and Rename Collision Files
PDF_OUT_A = os.path.join(OUTPUT_DIR, 'doc_A_safe_view.pdf')
PDF_OUT_B = os.path.join(OUTPUT_DIR, 'doc_B_malicious_view.pdf')
run_command(['mv', os.path.join(CORKAMI_SCRIPTS, 'collision1.pdf'), PDF_OUT_A])
run_command(['mv', os.path.join(CORKAMI_SCRIPTS, 'collision2.pdf'), PDF_OUT_B])
print(f"  > Created: {os.path.basename(PDF_OUT_A)} and {os.path.basename(PDF_OUT_B)}")

# Clean up local copies and intermediate files
clean_local_files(CORKAMI_SCRIPTS, PDF_FILES + PDF_TEMP_FILES)

# -----------------------------------------------------------
# 3. Reusable/Formatting Trick Collision (PNG Files)
# -----------------------------------------------------------
print("\n[3/3] Generating Reusable PNG Collision (png.py)...")

check_inputs(PNG_FILES, CORKAMI_COLLISIONS)
PNG_TEMP_FILES = ['collision1.png', 'collision2.png', 'collision-crc1.png', 'collision-crc2.png', 'collision-sync1.png',
                  'collision-sync2.png']

# Copy inputs locally to the script's execution directory
for f in PNG_FILES:
    shutil.copy(os.path.join(CORKAMI_COLLISIONS, f), CORKAMI_SCRIPTS)

# Run the PNG collision script
run_command(['python3', 'png.py', os.path.basename(PNG_FILES[0]), os.path.basename(PNG_FILES[1])], cwd=CORKAMI_SCRIPTS)

# Move and Rename the simplest collision pair
PNG_OUT_A = os.path.join(OUTPUT_DIR, 'img_A_good_view.png')
PNG_OUT_B = os.path.join(OUTPUT_DIR, 'img_B_bad_view.png')
run_command(['mv', os.path.join(CORKAMI_SCRIPTS, 'collision1.png'), PNG_OUT_A])
run_command(['mv', os.path.join(CORKAMI_SCRIPTS, 'collision2.png'), PNG_OUT_B])
print(f"  > Created: {os.path.basename(PNG_OUT_A)} and {os.path.basename(PNG_OUT_B)}")

# Clean up local copies and intermediate files
clean_local_files(CORKAMI_SCRIPTS, PNG_FILES + PNG_TEMP_FILES)

# -----------------------------------------------------------
# Final Verification
# -----------------------------------------------------------
print("\n--- Generation Complete. Final MD5 Verification: ---")

# Run md5sum on all generated artifacts
artifact_files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)]
if artifact_files:
    subprocess.run(['md5sum'] + artifact_files, check=True)
else:
    print("No collision artifacts found. Check previous error logs.")

print("\nSUCCESS! All three collision types generated.")
print("You can find all artifacts in the 'final_deliverables/collision_artifacts' folder.")
