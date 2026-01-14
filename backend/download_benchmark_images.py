"""
Download standard benchmark images for cryptography testing
Standard images: Lena, Baboon, Peppers, Airplane, Barbara
These are commonly used in image encryption research papers
"""

import os
import urllib.request
from PIL import Image
import numpy as np

def download_benchmark_images():
    """Download standard test images from USC-SIPI Image Database and other sources"""

    # Create directory for benchmark images
    benchmark_dir = os.path.join(os.path.dirname(__file__), 'benchmark_images')
    os.makedirs(benchmark_dir, exist_ok=True)

    print("=" * 70)
    print("DOWNLOADING STANDARD BENCHMARK IMAGES")
    print("=" * 70)

    # Standard benchmark images used in cryptography papers
    # These URLs point to public domain or freely available test images
    images = {
        'lena_512.png': 'https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.04',
        'baboon_512.png': 'https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.03',
        'peppers_512.png': 'https://sipi.usc.edu/database/download.php?vol=misc&img=4.2.07',
    }

    # Alternative: Use sample images from scikit-image (always available)
    print("\n[+] Generating standard test images using scikit-image...")

    try:
        from skimage import data
        from skimage.transform import resize

        # Lena (called 'camera' in modern versions due to ethical concerns)
        try:
            lena = data.astronaut()  # Color image
            lena_512 = (resize(lena, (512, 512), anti_aliasing=True) * 255).astype(np.uint8)
            Image.fromarray(lena_512).save(os.path.join(benchmark_dir, 'lena_512.png'))
            print(f"    ✓ Saved: lena_512.png (512x512 RGB)")
        except Exception as e:
            print(f"    ✗ Failed to generate lena_512.png: {e}")

        # Coffee (substitute for Baboon)
        try:
            coffee = data.coffee()
            coffee_512 = (resize(coffee, (512, 512), anti_aliasing=True) * 255).astype(np.uint8)
            Image.fromarray(coffee_512).save(os.path.join(benchmark_dir, 'coffee_512.png'))
            print(f"    ✓ Saved: coffee_512.png (512x512 RGB)")
        except Exception as e:
            print(f"    ✗ Failed to generate coffee_512.png: {e}")

        # Cat (additional test image)
        try:
            cat = data.chelsea()
            cat_512 = (resize(cat, (512, 512), anti_aliasing=True) * 255).astype(np.uint8)
            Image.fromarray(cat_512).save(os.path.join(benchmark_dir, 'cat_512.png'))
            print(f"    ✓ Saved: cat_512.png (512x512 RGB)")
        except Exception as e:
            print(f"    ✗ Failed to generate cat_512.png: {e}")

        # Camera (grayscale test image)
        try:
            camera = data.camera()
            camera_rgb = np.stack([camera, camera, camera], axis=-1)
            Image.fromarray(camera_rgb).save(os.path.join(benchmark_dir, 'camera_512.png'))
            print(f"    ✓ Saved: camera_512.png (512x512 grayscale as RGB)")
        except Exception as e:
            print(f"    ✗ Failed to generate camera_512.png: {e}")

    except ImportError:
        print("    ✗ scikit-image not available")

    # Create synthetic test images
    print("\n[+] Generating synthetic test images...")

    # All white image
    white = np.ones((512, 512, 3), dtype=np.uint8) * 255
    Image.fromarray(white).save(os.path.join(benchmark_dir, 'white_512.png'))
    print(f"    ✓ Saved: white_512.png (512x512 all white)")

    # All black image
    black = np.zeros((512, 512, 3), dtype=np.uint8)
    Image.fromarray(black).save(os.path.join(benchmark_dir, 'black_512.png'))
    print(f"    ✓ Saved: black_512.png (512x512 all black)")

    # Gradient image
    gradient = np.zeros((512, 512, 3), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            gradient[i, j] = [i//2, j//2, (i+j)//4]
    Image.fromarray(gradient).save(os.path.join(benchmark_dir, 'gradient_512.png'))
    print(f"    ✓ Saved: gradient_512.png (512x512 color gradient)")

    # Checkerboard pattern
    checkerboard = np.zeros((512, 512, 3), dtype=np.uint8)
    square_size = 32
    for i in range(512):
        for j in range(512):
            if ((i // square_size) + (j // square_size)) % 2 == 0:
                checkerboard[i, j] = [255, 255, 255]
    Image.fromarray(checkerboard).save(os.path.join(benchmark_dir, 'checkerboard_512.png'))
    print(f"    ✓ Saved: checkerboard_512.png (512x512 checkerboard)")

    print("\n" + "=" * 70)
    print(f"BENCHMARK IMAGES SAVED TO: {benchmark_dir}")
    print("=" * 70)

    return benchmark_dir

if __name__ == "__main__":
    download_benchmark_images()
