"""
Visualize the three hyperchaotic attractors
"""

import matplotlib
matplotlib.use("Agg")   # must be BEFORE pyplot
import matplotlib.pyplot as plt
import numpy as np
from chaotic_crypto import ChaoticCrypto

def plot_attractors():
    """Create 3D plots of all three hyperchaotic attractors"""
    
    print("Generating hyperchaotic attractors...")
    crypto = ChaoticCrypto(seed="visualization_seed")
    
    fig = plt.figure(figsize=(18, 5))
    fig.patch.set_facecolor('#0a0a0a')
    
    systems = [
        (crypto.system1, "Rössler Hyperchaos", "#00ffff"),
        (crypto.system2, "Chen Hyperchaos", "#ff00ff"),
        (crypto.system3, "Lorenz Hyperchaos", "#ffff00")
    ]
    
    for idx, (system, name, color) in enumerate(systems, 1):
        ax = fig.add_subplot(1, 3, idx, projection='3d')
        ax.set_facecolor('#0a0a0a')
        
        # Plot trajectory (use every 10th point for performance)
        step = 10
        x = system.solution[::step, 0]
        y = system.solution[::step, 1]
        z = system.solution[::step, 2]
        
        ax.plot(x, y, z, color=color, linewidth=0.5, alpha=0.6)
        
        # Styling
        ax.set_title(name, color=color, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('X', color='white', fontsize=10)
        ax.set_ylabel('Y', color='white', fontsize=10)
        ax.set_zlabel('Z', color='white', fontsize=10)
        
        # Make grid subtle
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.grid(True, alpha=0.1)
        
        # Set tick colors
        ax.tick_params(colors='white', labelsize=8)
        ax.xaxis.pane.set_edgecolor('#333333')
        ax.yaxis.pane.set_edgecolor('#333333')
        ax.zaxis.pane.set_edgecolor('#333333')
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('/home/claude/hyperchaotic_attractors.png', 
                dpi=200, 
                facecolor='#0a0a0a',
                edgecolor='none',
                bbox_inches='tight')
    print("✓ Saved visualization to: hyperchaotic_attractors.png")
    
    plt.show()


def plot_phase_portraits():
    """Create 2D phase portraits for all systems"""
    
    print("Generating phase portraits...")
    crypto = ChaoticCrypto(seed="visualization_seed")
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    fig.patch.set_facecolor('#0a0a0a')
    
    systems = [
        (crypto.system1, "Rössler", "#00ffff"),
        (crypto.system2, "Chen", "#ff00ff"),
        (crypto.system3, "Lorenz", "#ffff00")
    ]
    
    projections = [
        (0, 1, "X-Y"),
        (0, 2, "X-Z"),
        (1, 2, "Y-Z")
    ]
    
    for row, (system, name, color) in enumerate(systems):
        for col, (i, j, label) in enumerate(projections):
            ax = axes[row, col]
            ax.set_facecolor('#0a0a0a')
            
            # Plot projection (use every 10th point)
            step = 10
            x = system.solution[::step, i]
            y = system.solution[::step, j]
            
            ax.plot(x, y, color=color, linewidth=0.3, alpha=0.6)
            
            # Styling
            title = f"{name} - {label} Plane"
            ax.set_title(title, color=color, fontsize=10, fontweight='bold')
            ax.tick_params(colors='white', labelsize=8)
            ax.grid(True, alpha=0.1, color='white')
            
            # Remove spines
            for spine in ax.spines.values():
                spine.set_edgecolor('#333333')
                spine.set_linewidth(0.5)
    
    plt.tight_layout()
    plt.savefig('/home/claude/phase_portraits.png', 
                dpi=200, 
                facecolor='#0a0a0a',
                edgecolor='none',
                bbox_inches='tight')
    print("✓ Saved phase portraits to: phase_portraits.png")
    
    plt.show()


def plot_bitstreams():
    """Visualize the bit-streams"""
    
    print("Generating bit-stream visualizations...")
    crypto = ChaoticCrypto(seed="visualization_seed")
    
    fig, axes = plt.subplots(3, 1, figsize=(15, 8))
    fig.patch.set_facecolor('#0a0a0a')
    
    bitstreams = [
        (crypto.bitstream1, "Rössler Bit-stream", "#00ffff"),
        (crypto.bitstream2, "Chen Bit-stream", "#ff00ff"),
        (crypto.bitstream3, "Lorenz Bit-stream", "#ffff00")
    ]
    
    for ax, (bitstream, name, color) in zip(axes, bitstreams):
        ax.set_facecolor('#0a0a0a')
        
        # Plot first 1000 bits
        bits = bitstream[:1000]
        ax.plot(bits, color=color, linewidth=0.5, alpha=0.8)
        ax.fill_between(range(len(bits)), bits, alpha=0.3, color=color)
        
        # Styling
        ax.set_title(name, color=color, fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('Bit Value', color='white', fontsize=10)
        ax.set_ylim(-0.1, 1.1)
        ax.tick_params(colors='white', labelsize=8)
        ax.grid(True, alpha=0.1, color='white')
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_edgecolor('#333333')
            spine.set_linewidth(0.5)
    
    axes[-1].set_xlabel('Time Step', color='white', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('/home/claude/bitstreams.png', 
                dpi=200, 
                facecolor='#0a0a0a',
                edgecolor='none',
                bbox_inches='tight')
    print("✓ Saved bit-streams to: bitstreams.png")
    
    plt.show()


def plot_bitstream_comparison():
    """Compare old vs new bitstream generation methods"""

    print("Generating bitstream comparison...")
    from chaotic_crypto import RosslerHyperchaos

    # Initialize system
    system = RosslerHyperchaos(
        initial_conditions=[0.1, 0.1, 0.1, 0.1],
        parameters=[0.25, 3.0, 0.5, 0.05]
    )
    system.solve()

    # Generate bitstreams
    old_bits = system.to_bitstream(0)
    new_bits_pairwise = system.to_bitstream_multivar(method='pairwise_xor')

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor('#0a0a0a')

    # Plot 1: Old method bitstream (first 1000 bits)
    ax = axes[0, 0]
    ax.set_facecolor('#0a0a0a')
    bits_sample = old_bits[:1000]
    ax.plot(bits_sample, color='#ff6b6b', linewidth=0.5, alpha=0.8)
    ax.fill_between(range(len(bits_sample)), bits_sample, alpha=0.3, color='#ff6b6b')
    ax.set_title('Single Variable Method (Old)', color='#ff6b6b', fontsize=12, fontweight='bold')
    ax.set_ylabel('Bit Value', color='white', fontsize=10)
    ax.set_ylim(-0.1, 1.1)
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, alpha=0.1, color='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

    # Plot 2: New method bitstream (first 1000 bits)
    ax = axes[0, 1]
    ax.set_facecolor('#0a0a0a')
    bits_sample = new_bits_pairwise[:1000]
    ax.plot(bits_sample, color='#51cf66', linewidth=0.5, alpha=0.8)
    ax.fill_between(range(len(bits_sample)), bits_sample, alpha=0.3, color='#51cf66')
    ax.set_title('Multi-Variable XOR Method (New)', color='#51cf66', fontsize=12, fontweight='bold')
    ax.set_ylabel('Bit Value', color='white', fontsize=10)
    ax.set_ylim(-0.1, 1.1)
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, alpha=0.1, color='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

    # Plot 3: Autocorrelation comparison
    ax = axes[1, 0]
    ax.set_facecolor('#0a0a0a')

    # Calculate autocorrelation
    def autocorr(bits, max_lag=100):
        n = len(bits)
        bits_centered = bits - np.mean(bits)
        corr = np.correlate(bits_centered, bits_centered, mode='full')
        corr = corr[n-1:n+max_lag] / corr[n-1]
        return corr

    old_autocorr = autocorr(old_bits)
    new_autocorr = autocorr(new_bits_pairwise)

    ax.plot(old_autocorr[:100], color='#ff6b6b', linewidth=2, alpha=0.8, label='Old Method')
    ax.plot(new_autocorr[:100], color='#51cf66', linewidth=2, alpha=0.8, label='New Method')
    ax.axhline(y=0, color='white', linestyle='--', alpha=0.3)
    ax.set_title('Autocorrelation Comparison', color='white', fontsize=12, fontweight='bold')
    ax.set_xlabel('Lag', color='white', fontsize=10)
    ax.set_ylabel('Autocorrelation', color='white', fontsize=10)
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, alpha=0.1, color='white')
    ax.legend(facecolor='#0a0a0a', edgecolor='#333333', labelcolor='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

    # Plot 4: Run length distribution
    ax = axes[1, 1]
    ax.set_facecolor('#0a0a0a')

    def get_run_lengths(bits):
        runs = []
        current_run = 1
        for i in range(1, len(bits)):
            if bits[i] == bits[i-1]:
                current_run += 1
            else:
                runs.append(current_run)
                current_run = 1
        runs.append(current_run)
        return runs

    old_runs = get_run_lengths(old_bits)
    new_runs = get_run_lengths(new_bits_pairwise)

    # Create histogram
    bins = np.logspace(0, np.log10(max(max(old_runs), max(new_runs))), 50)
    ax.hist(old_runs, bins=bins, alpha=0.5, color='#ff6b6b', label=f'Old (max: {max(old_runs)})', edgecolor='none')
    ax.hist(new_runs, bins=bins, alpha=0.5, color='#51cf66', label=f'New (max: {max(new_runs)})', edgecolor='none')
    ax.set_xscale('log')
    ax.set_title('Run Length Distribution', color='white', fontsize=12, fontweight='bold')
    ax.set_xlabel('Run Length (log scale)', color='white', fontsize=10)
    ax.set_ylabel('Frequency', color='white', fontsize=10)
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, alpha=0.1, color='white')
    ax.legend(facecolor='#0a0a0a', edgecolor='#333333', labelcolor='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')

    plt.tight_layout()
    plt.savefig('/home/claude/bitstream_comparison.png',
                dpi=200,
                facecolor='#0a0a0a',
                edgecolor='none',
                bbox_inches='tight')
    print("✓ Saved comparison to: bitstream_comparison.png")

    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("Hyperchaotic System Visualization")
    print("=" * 60)
    print()

    plot_attractors()
    print()
    plot_phase_portraits()
    print()
    plot_bitstreams()
    print()
    plot_bitstream_comparison()

    print()
    print("=" * 60)
    print("All visualizations complete!")
    print("=" * 60)
