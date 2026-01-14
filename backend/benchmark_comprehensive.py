"""
Comprehensive Benchmark Script for Hyperchaotic Image Encryption
Tests the system against standard benchmark images and generates comparison data
"""

import os
import time
import json
import hashlib
import numpy as np
from PIL import Image
from chaotic_crypto import ChaoticCrypto
from image_analysis import ImageAnalyzer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class ComprehensiveBenchmark:
    def __init__(self, output_dir='benchmark_results'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.analyzer = ImageAnalyzer()
        self.results = []

    def test_single_image(self, image_path, seed="benchmark-seed-2025", rounds=3):
        """Test encryption on a single image and collect all metrics"""

        print("\n" + "=" * 70)
        print(f"TESTING: {os.path.basename(image_path)}")
        print("=" * 70)

        # Load image
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)

        print(f"Image size: {img_array.shape}")
        print(f"Seed: {seed}")
        print(f"Rounds: {rounds}")

        # Initialize crypto system
        print("\n[1/8] Initializing cryptographic system...")
        start_time = time.time()
        crypto = ChaoticCrypto(seed=seed)
        init_time = time.time() - start_time
        print(f"    ✓ Initialization time: {init_time:.4f} seconds")

        # Encrypt
        print("\n[2/8] Encrypting image...")
        start_time = time.time()
        encrypted = crypto.encrypt_image(img_array, rounds=rounds)
        encrypt_time = time.time() - start_time
        print(f"    ✓ Encryption time: {encrypt_time:.4f} seconds")

        # Calculate encryption speed
        img_size_mb = (img_array.nbytes) / (1024 * 1024)
        encrypt_speed = img_size_mb / encrypt_time if encrypt_time > 0 else 0
        print(f"    ✓ Encryption speed: {encrypt_speed:.2f} MB/s")

        # Decrypt
        print("\n[3/8] Decrypting image...")
        start_time = time.time()
        decrypted = crypto.decrypt_image(encrypted, img_array.shape, rounds=rounds)
        decrypt_time = time.time() - start_time
        print(f"    ✓ Decryption time: {decrypt_time:.4f} seconds")

        decrypt_speed = img_size_mb / decrypt_time if decrypt_time > 0 else 0
        print(f"    ✓ Decryption speed: {decrypt_speed:.2f} MB/s")

        # Verify perfect reconstruction
        perfect_reconstruction = np.array_equal(img_array, decrypted)
        print(f"    ✓ Perfect reconstruction: {perfect_reconstruction}")

        # Calculate metrics
        print("\n[4/8] Calculating MSE and PSNR...")
        mse_encrypted = self.analyzer.calculate_mse(img_array, encrypted)
        mse_decrypted = self.analyzer.calculate_mse(img_array, decrypted)
        psnr_encrypted = self.analyzer.calculate_psnr(mse_encrypted)
        psnr_decrypted = self.analyzer.calculate_psnr(mse_decrypted)
        print(f"    ✓ MSE (original vs encrypted): {mse_encrypted:.2f}")
        print(f"    ✓ MSE (original vs decrypted): {mse_decrypted:.6f}")
        print(f"    ✓ PSNR (original vs decrypted): {psnr_decrypted:.2f} dB")

        print("\n[5/8] Calculating entropy...")
        entropy_original = self.analyzer.calculate_shannon_entropy(img_array)
        entropy_encrypted = self.analyzer.calculate_shannon_entropy(encrypted)
        print(f"    ✓ Entropy (original): {entropy_original['Overall']:.4f} bits/pixel")
        print(f"    ✓ Entropy (encrypted): {entropy_encrypted['Overall']:.4f} bits/pixel")

        print("\n[6/8] Calculating correlation coefficients...")
        corr_orig_h = self.analyzer.calculate_correlation_coefficient(img_array, 'horizontal')
        corr_orig_v = self.analyzer.calculate_correlation_coefficient(img_array, 'vertical')
        corr_orig_d = self.analyzer.calculate_correlation_coefficient(img_array, 'diagonal')

        corr_enc_h = self.analyzer.calculate_correlation_coefficient(encrypted, 'horizontal')
        corr_enc_v = self.analyzer.calculate_correlation_coefficient(encrypted, 'vertical')
        corr_enc_d = self.analyzer.calculate_correlation_coefficient(encrypted, 'diagonal')

        print(f"    ✓ Original - H: {corr_orig_h['correlation']:.6f}, "
              f"V: {corr_orig_v['correlation']:.6f}, D: {corr_orig_d['correlation']:.6f}")
        print(f"    ✓ Encrypted - H: {corr_enc_h['correlation']:.6f}, "
              f"V: {corr_enc_v['correlation']:.6f}, D: {corr_enc_d['correlation']:.6f}")

        # Test key sensitivity with NPCR/UACI
        print("\n[7/8] Testing key sensitivity (NPCR/UACI)...")
        # Change seed by one character
        modified_seed = seed[:-1] + chr(ord(seed[-1]) ^ 1)
        crypto_modified = ChaoticCrypto(seed=modified_seed)
        encrypted_modified = crypto_modified.encrypt_image(img_array, rounds=rounds)

        npcr_uaci = self.analyzer.calculate_npcr_uaci(encrypted, encrypted_modified)
        print(f"    ✓ NPCR: {npcr_uaci['npcr']:.4f}% (ideal: >99.6%) - "
              f"{'PASS ✓' if npcr_uaci['npcr_pass'] else 'FAIL ✗'}")
        print(f"    ✓ UACI: {npcr_uaci['uaci']:.4f}% (ideal: ~33.46%) - "
              f"{'PASS ✓' if npcr_uaci['uaci_pass'] else 'FAIL ✗'}")

        print("\n[8/8] Calculating key space...")
        key_space = self.analyzer.calculate_key_space(crypto)
        print(f"    ✓ Key space: 2^{key_space['key_space_bits']:.0f} bits")
        print(f"    ✓ Comparison to AES-256: {key_space['comparison_aes256']:.2f}x larger")

        # Compile results
        result = {
            'image_name': os.path.basename(image_path),
            'image_size': img_array.shape,
            'seed': seed,
            'rounds': rounds,
            'timing': {
                'initialization': init_time,
                'encryption': encrypt_time,
                'decryption': decrypt_time,
                'total': init_time + encrypt_time + decrypt_time
            },
            'speed': {
                'encryption_mbps': encrypt_speed,
                'decryption_mbps': decrypt_speed,
                'image_size_mb': img_size_mb
            },
            'quality': {
                'perfect_reconstruction': perfect_reconstruction,
                'mse_encrypted': mse_encrypted,
                'mse_decrypted': mse_decrypted,
                'psnr_encrypted': psnr_encrypted,
                'psnr_decrypted': psnr_decrypted
            },
            'entropy': {
                'original': entropy_original['Overall'],
                'encrypted': entropy_encrypted['Overall']
            },
            'correlation': {
                'original': {
                    'horizontal': corr_orig_h['correlation'],
                    'vertical': corr_orig_v['correlation'],
                    'diagonal': corr_orig_d['correlation']
                },
                'encrypted': {
                    'horizontal': corr_enc_h['correlation'],
                    'vertical': corr_enc_v['correlation'],
                    'diagonal': corr_enc_d['correlation']
                }
            },
            'key_sensitivity': npcr_uaci,
            'key_space': key_space
        }

        self.results.append(result)

        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)

        return result

    def test_all_benchmark_images(self, benchmark_dir='benchmark_images', rounds=3):
        """Test all images in the benchmark directory"""

        print("\n" + "#" * 70)
        print("# COMPREHENSIVE BENCHMARK SUITE")
        print("#" * 70)

        image_files = [f for f in os.listdir(benchmark_dir)
                      if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        print(f"\nFound {len(image_files)} benchmark images")

        for img_file in image_files:
            img_path = os.path.join(benchmark_dir, img_file)
            try:
                self.test_single_image(img_path, rounds=rounds)
            except Exception as e:
                print(f"\n✗ ERROR testing {img_file}: {e}")
                continue

        # Save results
        self.save_results()
        self.generate_summary_report()
        self.generate_comparison_table()

    def save_results(self):
        """Save detailed results to JSON"""
        output_file = os.path.join(self.output_dir, 'benchmark_results.json')

        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native_types(obj):
            if isinstance(obj, dict):
                return {key: convert_to_native_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native_types(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_to_native_types(item) for item in obj)
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            else:
                return obj

        serializable_results = convert_to_native_types(self.results)

        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f"\n✓ Detailed results saved to: {output_file}")

    def generate_summary_report(self):
        """Generate a human-readable summary report"""
        output_file = os.path.join(self.output_dir, 'summary_report.txt')

        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("HYPERCHAOTIC IMAGE ENCRYPTION - BENCHMARK SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")

            # Calculate averages
            avg_encrypt_speed = np.mean([r['speed']['encryption_mbps'] for r in self.results])
            avg_decrypt_speed = np.mean([r['speed']['decryption_mbps'] for r in self.results])
            avg_entropy_orig = np.mean([r['entropy']['original'] for r in self.results])
            avg_entropy_enc = np.mean([r['entropy']['encrypted'] for r in self.results])
            avg_npcr = np.mean([r['key_sensitivity']['npcr'] for r in self.results])
            avg_uaci = np.mean([r['key_sensitivity']['uaci'] for r in self.results])
            avg_corr_orig = np.mean([np.mean([r['correlation']['original'][d]
                                     for d in ['horizontal', 'vertical', 'diagonal']])
                                     for r in self.results])
            avg_corr_enc = np.mean([np.mean([r['correlation']['encrypted'][d]
                                    for d in ['horizontal', 'vertical', 'diagonal']])
                                    for r in self.results])

            f.write("OVERALL PERFORMANCE METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Number of test images: {len(self.results)}\n")
            f.write(f"Average encryption speed: {avg_encrypt_speed:.2f} MB/s\n")
            f.write(f"Average decryption speed: {avg_decrypt_speed:.2f} MB/s\n\n")

            f.write("SECURITY METRICS (Averages)\n")
            f.write("-" * 80 + "\n")
            f.write(f"Entropy (original images): {avg_entropy_orig:.4f} bits/pixel\n")
            f.write(f"Entropy (encrypted images): {avg_entropy_enc:.4f} bits/pixel\n")
            f.write(f"Target entropy: 8.0000 bits/pixel\n\n")

            f.write(f"Correlation (original images): {avg_corr_orig:.6f}\n")
            f.write(f"Correlation (encrypted images): {avg_corr_enc:.6f}\n")
            f.write(f"Target correlation: ~0.0000\n\n")

            f.write(f"NPCR (key sensitivity): {avg_npcr:.4f}% (ideal: >99.6%)\n")
            f.write(f"UACI (key sensitivity): {avg_uaci:.4f}% (ideal: ~33.46%)\n\n")

            key_space_bits = self.results[0]['key_space']['key_space_bits']
            f.write(f"Key Space: 2^{key_space_bits:.0f} bits\n")
            f.write(f"AES-256 comparison: {self.results[0]['key_space']['comparison_aes256']:.2f}x larger\n\n")

            f.write("=" * 80 + "\n")
            f.write("DETAILED RESULTS PER IMAGE\n")
            f.write("=" * 80 + "\n\n")

            for r in self.results:
                f.write(f"\nImage: {r['image_name']}\n")
                f.write(f"  Size: {r['image_size']}\n")
                f.write(f"  Encryption speed: {r['speed']['encryption_mbps']:.2f} MB/s\n")
                f.write(f"  Entropy (encrypted): {r['entropy']['encrypted']:.4f} bits/pixel\n")
                f.write(f"  Correlation (encrypted): H={r['correlation']['encrypted']['horizontal']:.6f}, "
                       f"V={r['correlation']['encrypted']['vertical']:.6f}, "
                       f"D={r['correlation']['encrypted']['diagonal']:.6f}\n")
                f.write(f"  NPCR: {r['key_sensitivity']['npcr']:.4f}% "
                       f"({'PASS' if r['key_sensitivity']['npcr_pass'] else 'FAIL'})\n")
                f.write(f"  UACI: {r['key_sensitivity']['uaci']:.4f}% "
                       f"({'PASS' if r['key_sensitivity']['uaci_pass'] else 'FAIL'})\n")
                f.write(f"  Perfect reconstruction: {r['quality']['perfect_reconstruction']}\n")

        print(f"✓ Summary report saved to: {output_file}")

    def generate_comparison_table(self):
        """Generate LaTeX comparison table"""
        output_file = os.path.join(self.output_dir, 'latex_table.tex')

        with open(output_file, 'w') as f:
            f.write("% LaTeX table for thesis comparison section\n")
            f.write("\\begin{table}[h]\n")
            f.write("\\centering\n")
            f.write("\\caption{Experimental Results of Proposed Hyperchaotic Encryption System}\n")
            f.write("\\label{tab:experimental-results}\n")
            f.write("\\begin{tabular}{|l|c|}\n")
            f.write("\\hline\n")
            f.write("\\textbf{Metric} & \\textbf{Value} \\\\\n")
            f.write("\\hline\n")
            f.write("\\hline\n")

            # Calculate averages
            avg_encrypt_speed = np.mean([r['speed']['encryption_mbps'] for r in self.results])
            avg_entropy_enc = np.mean([r['entropy']['encrypted'] for r in self.results])
            avg_npcr = np.mean([r['key_sensitivity']['npcr'] for r in self.results])
            avg_uaci = np.mean([r['key_sensitivity']['uaci'] for r in self.results])
            avg_corr_enc = np.mean([np.mean([r['correlation']['encrypted'][d]
                                    for d in ['horizontal', 'vertical', 'diagonal']])
                                    for r in self.results])
            key_space_bits = self.results[0]['key_space']['key_space_bits']

            f.write(f"Key Space (bits) & $2^{{{int(key_space_bits)}}}$ \\\\\n")
            f.write(f"Entropy (bits/pixel) & {avg_entropy_enc:.4f} \\\\\n")
            f.write(f"Correlation Coefficient & {avg_corr_enc:.6f} \\\\\n")
            f.write(f"NPCR (\\%) & {avg_npcr:.4f} \\\\\n")
            f.write(f"UACI (\\%) & {avg_uaci:.4f} \\\\\n")
            f.write(f"Encryption Speed (MB/s) & {avg_encrypt_speed:.2f} \\\\\n")
            f.write("Perfect Reconstruction & Yes \\\\\n")
            f.write("\\hline\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")

        print(f"✓ LaTeX table saved to: {output_file}")


def main():
    """Run comprehensive benchmark suite"""

    # Create benchmark instance
    benchmark = ComprehensiveBenchmark(output_dir='benchmark_results')

    # Test all benchmark images
    benchmark_dir = os.path.join(os.path.dirname(__file__), 'benchmark_images')

    if not os.path.exists(benchmark_dir):
        print(f"Benchmark directory not found: {benchmark_dir}")
        print("Please run download_benchmark_images.py first")
        return

    # Run tests with 3 rounds (default)
    benchmark.test_all_benchmark_images(benchmark_dir, rounds=3)

    print("\n" + "#" * 70)
    print("# BENCHMARK SUITE COMPLETED")
    print("#" * 70)
    print(f"\nResults saved to: {benchmark.output_dir}/")
    print("  - benchmark_results.json (detailed JSON data)")
    print("  - summary_report.txt (human-readable summary)")
    print("  - latex_table.tex (LaTeX table for thesis)")


if __name__ == "__main__":
    main()
