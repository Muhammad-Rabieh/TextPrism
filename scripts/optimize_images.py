import os
import time
from datetime import timedelta
from PIL import Image

CLIPART_DIR = os.path.join(os.getcwd(), 'data', 'clipart')
MAX_SIZE = (128, 128)

def get_all_pngs():
    png_files = []
    for root, _, files in os.walk(CLIPART_DIR):
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append(os.path.join(root, file))
    return png_files

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

def optimize_images():
    print(f"Scanning {CLIPART_DIR} for PNG files...")
    start_time = time.time()
    
    png_files = get_all_pngs()
    total_files = len(png_files)
    print(f"Found {total_files} PNG files to process.")
    
    if total_files == 0:
        return

    count_optimized = 0
    count_skipped = 0
    count_errors = 0
    
    for idx, file_path in enumerate(png_files):
        # Progress and ETA reporting every 100 images
        if idx > 0 and idx % 100 == 0:
            elapsed = time.time() - start_time
            rate = idx / elapsed
            remaining_files = total_files - idx
            eta_seconds = remaining_files / rate if rate > 0 else 0
            
            print(f"Progress: {idx}/{total_files} ({(idx/total_files)*100:.1f}%) | "
                  f"Optimized: {count_optimized} | Skipped: {count_skipped} | "
                  f"Speed: {rate:.1f} it/s | ETA: {format_time(eta_seconds)}")
        
        try:
            with Image.open(file_path) as img:
                if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
                    img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                    img.save(file_path, optimize=True)
                    count_optimized += 1
                else:
                    count_skipped += 1
        except Exception as e:
            # We don't want to spam the console with a single bad file error, just track it
            count_errors += 1
                    
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print("--- 🚀 Optimization Complete ---")
    print(f"Total time elapsed: {format_time(total_time)}")
    print(f"Images optimized and resized: {count_optimized}")
    print(f"Images skipped (already <= 128px): {count_skipped}")
    print(f"Errors computing files: {count_errors}")
    print("="*50)

if __name__ == "__main__":
    optimize_images()
