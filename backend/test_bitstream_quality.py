"""
Test and compare bitstream quality metrics

This script analyzes the quality of bitstreams generated from hyperchaotic systems
using different methods (single-variable vs multi-variable XOR).
"""

import numpy as np
from chaotic_crypto import RosslerHyperchaos, ChenHyperchaos, LorenzHyperchaos


def calculate_run_lengths(bits):
    """
    Calculate run lengths (consecutive 0s or 1s)

    Args:
        bits: Binary array

    Returns:
        dict: Statistics including max_run, mean_run, std_run, and list of all runs
    """
    runs = []
    current_run = 1

    for i in range(1, len(bits)):
        if bits[i] == bits[i-1]:
            current_run += 1
        else:
            runs.append(current_run)
            current_run = 1
    runs.append(current_run)

    return {
        'max_run': np.max(runs),
        'mean_run': np.mean(runs),
        'std_run': np.std(runs),
        'median_run': np.median(runs),
        'runs': runs
    }


def calculate_autocorrelation(bits, max_lag=100):
    """
    Calculate autocorrelation at various lags

    Args:
        bits: Binary array
        max_lag: Maximum lag to calculate

    Returns:
        np.ndarray: Autocorrelation values for lags 0 to max_lag
    """
    n = len(bits)
    bits_centered = bits - np.mean(bits)
    autocorr = np.correlate(bits_centered, bits_centered, mode='full')
    autocorr = autocorr[n-1:n+max_lag] / autocorr[n-1]  # Normalize

    return autocorr


def calculate_entropy(bits, block_size=1):
    """
    Calculate Shannon entropy of bitstream

    Args:
        bits: Binary array
        block_size: Size of blocks to analyze (1 for bit-level, 8 for byte-level)

    Returns:
        float: Entropy in bits
    """
    if block_size == 1:
        # Bit-level entropy
        p1 = np.mean(bits)
        p0 = 1 - p1
        if p0 == 0 or p1 == 0:
            return 0
        return -p0 * np.log2(p0) - p1 * np.log2(p1)
    else:
        # Block-level entropy
        n_blocks = len(bits) // block_size
        blocks = bits[:n_blocks * block_size].reshape(n_blocks, block_size)
        block_values = [''.join(map(str, block)) for block in blocks]
        unique, counts = np.unique(block_values, return_counts=True)
        probs = counts / len(block_values)
        return -np.sum(probs * np.log2(probs))


def analyze_bitstream(bits, name="Bitstream"):
    """
    Perform comprehensive analysis on a bitstream

    Args:
        bits: Binary array
        name: Name for display purposes

    Returns:
        dict: Analysis results
    """
    # Run length analysis
    runs = calculate_run_lengths(bits)

    # Autocorrelation
    autocorr = calculate_autocorrelation(bits, max_lag=100)

    # Entropy
    entropy_bit = calculate_entropy(bits, block_size=1)
    entropy_byte = calculate_entropy(bits, block_size=8)

    # Balance
    p1 = np.mean(bits)

    results = {
        'name': name,
        'length': len(bits),
        'max_run': runs['max_run'],
        'mean_run': runs['mean_run'],
        'std_run': runs['std_run'],
        'median_run': runs['median_run'],
        'autocorr_lag1': autocorr[1],
        'autocorr_lag10': autocorr[10],
        'entropy_bit': entropy_bit,
        'entropy_byte': entropy_byte,
        'p1': p1,
        'balance_score': abs(0.5 - p1),  # Lower is better
    }

    return results


def print_analysis(results):
    """Print analysis results in a formatted way"""
    print(f"\n{results['name']}:")
    print(f"  Length: {results['length']:,} bits")
    print(f"  Run Lengths - Max: {results['max_run']}, Mean: {results['mean_run']:.2f}, Median: {results['median_run']:.1f}, Std: {results['std_run']:.2f}")
    print(f"  Autocorrelation - Lag 1: {results['autocorr_lag1']:.6f}, Lag 10: {results['autocorr_lag10']:.6f}")
    print(f"  Entropy - Bit: {results['entropy_bit']:.6f} (ideal: 1.0), Byte: {results['entropy_byte']:.4f} (ideal: 8.0)")
    print(f"  Balance - P(1): {results['p1']:.6f} (ideal: 0.5000), Deviation: {results['balance_score']:.6f}")


def compare_methods():
    """Compare old vs. new bitstream methods"""

    print("=" * 80)
    print("BITSTREAM QUALITY COMPARISON")
    print("=" * 80)
    print("\nInitializing hyperchaotic systems...")

    # Initialize the three systems
    system1 = RosslerHyperchaos(
        initial_conditions=[0.1, 0.1, 0.1, 0.1],
        parameters=[0.25, 3.0, 0.5, 0.05]
    )

    system2 = ChenHyperchaos(
        initial_conditions=[1.0, 1.0, 1.0, 1.0],
        parameters=[36, 3, 28, -16, -0.7]
    )

    system3 = LorenzHyperchaos(
        initial_conditions=[1.0, 1.0, 1.0, 1.0],
        parameters=[10, 28, 8/3, -1]
    )

    print("Solving ODE systems...")
    system1.solve()
    system2.solve()
    system3.solve()

    print("\nGenerating bitstreams with different methods...")

    # Test all systems
    systems = [
        (system1, "Rössler Hyperchaos"),
        (system2, "Chen Hyperchaos"),
        (system3, "Lorenz Hyperchaos")
    ]

    all_results = []

    for system, system_name in systems:
        print(f"\n{'=' * 80}")
        print(f"{system_name}")
        print('=' * 80)

        # Generate bitstreams with all methods
        old_bits = system.to_bitstream(0)
        new_bits_full = system.to_bitstream_multivar(method='full_xor')
        new_bits_pairwise = system.to_bitstream_multivar(method='pairwise_xor')
        new_bits_selective = system.to_bitstream_multivar(method='selective_xor')

        # Analyze each method
        methods = [
            (old_bits, "Single Variable (old)"),
            (new_bits_full, "Full XOR"),
            (new_bits_pairwise, "Pairwise XOR (recommended)"),
            (new_bits_selective, "Selective XOR")
        ]

        for bits, name in methods:
            results = analyze_bitstream(bits, name)
            print_analysis(results)
            all_results.append(results)

    # Summary comparison
    print("\n" + "=" * 80)
    print("SUMMARY: Improvement Metrics")
    print("=" * 80)

    # Average across all three systems
    old_results = [r for r in all_results if "old" in r['name']]
    pairwise_results = [r for r in all_results if "Pairwise" in r['name']]

    print("\nAverage across all three systems:")
    print(f"\n  Single Variable (old):")
    print(f"    Max run: {np.mean([r['max_run'] for r in old_results]):.0f}")
    print(f"    Mean run: {np.mean([r['mean_run'] for r in old_results]):.2f}")
    print(f"    Autocorr (lag 1): {np.mean([r['autocorr_lag1'] for r in old_results]):.6f}")
    print(f"    Bit entropy: {np.mean([r['entropy_bit'] for r in old_results]):.6f}")

    print(f"\n  Pairwise XOR (new):")
    print(f"    Max run: {np.mean([r['max_run'] for r in pairwise_results]):.0f}")
    print(f"    Mean run: {np.mean([r['mean_run'] for r in pairwise_results]):.2f}")
    print(f"    Autocorr (lag 1): {np.mean([r['autocorr_lag1'] for r in pairwise_results]):.6f}")
    print(f"    Bit entropy: {np.mean([r['entropy_bit'] for r in pairwise_results]):.6f}")

    print(f"\n  Improvement:")
    old_max_run = np.mean([r['max_run'] for r in old_results])
    new_max_run = np.mean([r['max_run'] for r in pairwise_results])
    old_autocorr = np.mean([r['autocorr_lag1'] for r in old_results])
    new_autocorr = np.mean([r['autocorr_lag1'] for r in pairwise_results])
    old_entropy = np.mean([r['entropy_bit'] for r in old_results])
    new_entropy = np.mean([r['entropy_bit'] for r in pairwise_results])

    print(f"    Max run reduction: {(1 - new_max_run/old_max_run)*100:.1f}%")
    print(f"    Autocorrelation reduction: {(1 - new_autocorr/old_autocorr)*100:.1f}%")
    print(f"    Entropy improvement: {((new_entropy - old_entropy)/old_entropy)*100:.1f}%")

    print("\n" + "=" * 80)
    print("RECOMMENDATION: Use 'pairwise_xor' method for cryptographic applications")
    print("=" * 80)


if __name__ == "__main__":
    compare_methods()
