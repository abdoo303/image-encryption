"""
Image Analysis Module for Cryptographic Performance Evaluation
Implements various metrics to evaluate encryption quality
"""

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from scipy import stats
import io
import base64

class ImageAnalyzer:
    """Analyze encryption performance through various metrics"""

    def __init__(self):
        pass

    def calculate_histogram(self, image_array, channel_names=None):
        """
        Calculate histogram for each channel of the image

        Args:
            image_array: numpy array of shape (H, W, C)
            channel_names: list of channel names (default: ['R', 'G', 'B'])

        Returns:
            Dictionary with histogram data for each channel
        """
        if channel_names is None:
            if len(image_array.shape) == 3:
                channel_names = ['Red', 'Green', 'Blue']
            else:
                channel_names = ['Grayscale']

        histograms = {}

        if len(image_array.shape) == 3:
            # RGB image
            for i, channel_name in enumerate(channel_names):
                hist, bins = np.histogram(image_array[:, :, i], bins=256, range=(0, 256))
                histograms[channel_name] = {
                    'values': [int(x) for x in hist],
                    'bins': [float(x) for x in bins[:-1]]
                }
        else:
            # Grayscale
            hist, bins = np.histogram(image_array, bins=256, range=(0, 256))
            histograms[channel_names[0]] = {
                'values': [int(x) for x in hist],
                'bins': [float(x) for x in bins[:-1]]
            }

        return histograms

    def calculate_mse(self, image1, image2):
        """
        Calculate Mean Squared Error between two images

        Args:
            image1, image2: numpy arrays of same shape

        Returns:
            MSE value
        """
        if image1.shape != image2.shape:
            raise ValueError("Images must have the same shape")

        mse = np.mean((image1.astype(float) - image2.astype(float)) ** 2)
        return float(mse)

    def calculate_psnr(self, mse, max_pixel=255.0):
        """
        Calculate Peak Signal-to-Noise Ratio from MSE

        Args:
            mse: Mean squared error
            max_pixel: Maximum possible pixel value

        Returns:
            PSNR in dB
        """
        if mse == 0:
            return float('inf')

        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return float(psnr)

    def calculate_ssim(self, image1, image2):
        """
        Calculate Structural Similarity Index between two images

        Args:
            image1, image2: numpy arrays of same shape

        Returns:
            SSIM value (between -1 and 1, where 1 means identical)
        """
        if image1.shape != image2.shape:
            raise ValueError("Images must have the same shape")

        # Calculate SSIM for each channel if RGB
        if len(image1.shape) == 3:
            ssim_values = []
            for i in range(image1.shape[2]):
                ssim_val = ssim(image1[:, :, i], image2[:, :, i],
                               data_range=255)
                ssim_values.append(ssim_val)
            return float(np.mean(ssim_values))
        else:
            return float(ssim(image1, image2, data_range=255))

    def calculate_shannon_entropy(self, image_array):
        """
        Calculate Shannon entropy for image
        Higher entropy indicates more randomness (better encryption)

        Args:
            image_array: numpy array

        Returns:
            Entropy value and per-channel breakdown
        """
        entropies = {}

        if len(image_array.shape) == 3:
            # RGB image
            channel_names = ['Red', 'Green', 'Blue']
            for i, channel_name in enumerate(channel_names):
                channel_data = image_array[:, :, i].flatten()
                value, counts = np.unique(channel_data, return_counts=True)
                probabilities = counts / counts.sum()
                entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
                entropies[channel_name] = float(entropy)

            # Overall entropy
            all_data = image_array.flatten()
            value, counts = np.unique(all_data, return_counts=True)
            probabilities = counts / counts.sum()
            overall_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            entropies['Overall'] = float(overall_entropy)
        else:
            # Grayscale
            data = image_array.flatten()
            value, counts = np.unique(data, return_counts=True)
            probabilities = counts / counts.sum()
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            entropies['Overall'] = float(entropy)

        return entropies

    def add_salt_pepper_noise(self, image_array, salt_prob=0.01, pepper_prob=0.01):
        """
        Add salt and pepper noise to an image

        Args:
            image_array: numpy array
            salt_prob: probability of salt noise
            pepper_prob: probability of pepper noise

        Returns:
            Noisy image array
        """
        noisy = image_array.copy()

        # Salt noise (white pixels)
        salt_mask = np.random.random(image_array.shape) < salt_prob
        noisy[salt_mask] = 255

        # Pepper noise (black pixels)
        pepper_mask = np.random.random(image_array.shape) < pepper_prob
        noisy[pepper_mask] = 0

        return noisy

    def analyze_noise_resistance(self, original_image, encrypted_image,
                                  crypto_instance, original_shape, rounds=3,
                                  noise_levels=None):
        """
        Test decryption after adding noise to encrypted image

        Args:
            original_image: original image array
            encrypted_image: encrypted image array
            crypto_instance: ChaoticCrypto instance for decryption
            original_shape: shape to reshape decrypted image
            rounds: number of encryption rounds
            noise_levels: list of (salt_prob, pepper_prob) tuples

        Returns:
            Analysis results for different noise levels
        """
        if noise_levels is None:
            noise_levels = [
                (0.001, 0.001),  # 0.1%
                (0.005, 0.005),  # 0.5%
                (0.01, 0.01),    # 1%
                (0.02, 0.02),    # 2%
                (.05,.05)
            ]

        results = []

        for salt_prob, pepper_prob in noise_levels:
            # Add noise to encrypted image
            noisy_encrypted = self.add_salt_pepper_noise(
                encrypted_image, salt_prob, pepper_prob
            )

            # Decrypt noisy image
            try:
                decrypted = crypto_instance.decrypt_image(
                    noisy_encrypted, original_shape, rounds=rounds
                )

                # Calculate metrics
                mse = self.calculate_mse(original_image, decrypted)
                ssim_val = self.calculate_ssim(original_image, decrypted)
                psnr = self.calculate_psnr(mse)

                # Convert to base64 for display
                decrypted_img = Image.fromarray(decrypted.astype(np.uint8))
                buffer = io.BytesIO()
                decrypted_img.save(buffer, format='PNG')
                decrypted_base64 = base64.b64encode(buffer.getvalue()).decode()

                results.append({
                    'noise_level': f'{salt_prob*100:.1f}%',
                    'salt_prob': salt_prob,
                    'pepper_prob': pepper_prob,
                    'mse': mse,
                    'ssim': ssim_val,
                    'psnr': psnr,
                    'decrypted_image': f'data:image/png;base64,{decrypted_base64}'
                })
            except Exception as e:
                results.append({
                    'noise_level': f'{salt_prob*100:.1f}%',
                    'salt_prob': salt_prob,
                    'pepper_prob': pepper_prob,
                    'error': str(e)
                })

        return results

    def calculate_correlation_coefficient(self, image_array, direction='horizontal',
                                          sample_size=5000):
        """
        Calculate correlation coefficient of adjacent pixels

        Args:
            image_array: numpy array
            direction: 'horizontal', 'vertical', or 'diagonal'
            sample_size: number of pixel pairs to sample

        Returns:
            Correlation coefficient
        """
        if len(image_array.shape) == 3:
            # For RGB, calculate on grayscale version
            gray = np.mean(image_array, axis=2).astype(np.uint8)
        else:
            gray = image_array

        h, w = gray.shape

        # Randomly sample pixel pairs
        pairs_x = []
        pairs_y = []

        for _ in range(sample_size):
            if direction == 'horizontal':
                i = np.random.randint(0, h)
                j = np.random.randint(0, w - 1)
                pairs_x.append(gray[i, j])
                pairs_y.append(gray[i, j + 1])
            elif direction == 'vertical':
                i = np.random.randint(0, h - 1)
                j = np.random.randint(0, w)
                pairs_x.append(gray[i, j])
                pairs_y.append(gray[i + 1, j])
            elif direction == 'diagonal':
                i = np.random.randint(0, h - 1)
                j = np.random.randint(0, w - 1)
                pairs_x.append(gray[i, j])
                pairs_y.append(gray[i + 1, j + 1])

        # Calculate correlation
        correlation = np.corrcoef(pairs_x, pairs_y)[0, 1]

        return {
            'correlation': float(correlation),
            'pairs_x': [int(x) for x in pairs_x[:1000]],  # Return subset for visualization
            'pairs_y': [int(y) for y in pairs_y[:1000]]
        }

    def calculate_key_space(self, crypto_instance):
        """
        Calculate the key space of the cryptographic system

        For hyperchaotic systems, key space depends on:
        - Initial conditions (4 values per system × 3 systems = 12 values)
        - Parameters (various per system)
        - Computational precision

        Args:
            crypto_instance: ChaoticCrypto instance

        Returns:
            Key space information
        """
        # Assuming 10^-15 precision for floating point (double precision)
        precision = 15

        # Count total number of parameters
        num_initial_conditions = 12  # 4 per system × 3 systems

        # Parameters per system
        num_params_system1 = len(crypto_instance.system1.params)  # Rössler: 4
        num_params_system2 = len(crypto_instance.system2.params)  # Chen: 5
        num_params_system3 = len(crypto_instance.system3.params)  # Lorenz: 4

        total_params = num_params_system1 + num_params_system2 + num_params_system3

        # Total key space elements
        total_elements = num_initial_conditions + total_params

        # Key space = (10^precision)^total_elements
        # In bits: log2(10^precision)^total_elements = total_elements × precision × log2(10)
        key_space_bits = total_elements * precision * np.log2(10)

        # For comparison, AES-256 has 256-bit key space
        aes_256_bits = 256

        return {
            'total_parameters': total_elements,
            'initial_conditions': num_initial_conditions,
            'system_parameters': total_params,
            'precision_decimal': precision,
            'key_space_bits': float(key_space_bits),
            'key_space_decimal': f'10^{int(total_elements * precision)}',
            'comparison_aes256': float(key_space_bits / aes_256_bits),
            'systems_breakdown': {
                'Rössler': {
                    'initial_conditions': 4,
                    'parameters': num_params_system1
                },
                'Chen': {
                    'initial_conditions': 4,
                    'parameters': num_params_system2
                },
                'Lorenz': {
                    'initial_conditions': 4,
                    'parameters': num_params_system3
                }
            }
        }

    def comprehensive_analysis(self, original_image, encrypted_image,
                               decrypted_image, crypto_instance,
                               original_shape, rounds=3):
        """
        Perform comprehensive analysis on the encryption

        Returns:
            Complete analysis report
        """
        report = {}

        # 1. Histogram analysis
        print("Calculating histograms...")
        report['histograms'] = {
            'original': self.calculate_histogram(original_image),
            'encrypted': self.calculate_histogram(encrypted_image),
            'decrypted': self.calculate_histogram(decrypted_image)
        }

        # 2. MSE between plain and encrypted
        print("Calculating MSE (plain vs encrypted)...")
        mse_plain_encrypted = self.calculate_mse(original_image, encrypted_image)
        report['mse_plain_encrypted'] = mse_plain_encrypted

        # 3. MSE between plain and decrypted (should be 0 or very small)
        print("Calculating MSE (plain vs decrypted)...")
        mse_plain_decrypted = self.calculate_mse(original_image, decrypted_image)
        report['mse_plain_decrypted'] = mse_plain_decrypted

        # 4. SSIM between plain and encrypted
        print("Calculating SSIM (plain vs encrypted)...")
        ssim_plain_encrypted = self.calculate_ssim(original_image, encrypted_image)
        report['ssim_plain_encrypted'] = ssim_plain_encrypted

        # 5. SSIM between plain and decrypted
        print("Calculating SSIM (plain vs decrypted)...")
        ssim_plain_decrypted = self.calculate_ssim(original_image, decrypted_image)
        report['ssim_plain_decrypted'] = ssim_plain_decrypted

        # 6. Shannon entropy
        print("Calculating Shannon entropy...")
        report['entropy'] = {
            'original': self.calculate_shannon_entropy(original_image),
            'encrypted': self.calculate_shannon_entropy(encrypted_image),
            'decrypted': self.calculate_shannon_entropy(decrypted_image)
        }

        # 7. Correlation coefficients
        print("Calculating correlation coefficients...")
        report['correlation'] = {
            'original': {
                'horizontal': self.calculate_correlation_coefficient(original_image, 'horizontal'),
                'vertical': self.calculate_correlation_coefficient(original_image, 'vertical'),
                'diagonal': self.calculate_correlation_coefficient(original_image, 'diagonal')
            },
            'encrypted': {
                'horizontal': self.calculate_correlation_coefficient(encrypted_image, 'horizontal'),
                'vertical': self.calculate_correlation_coefficient(encrypted_image, 'vertical'),
                'diagonal': self.calculate_correlation_coefficient(encrypted_image, 'diagonal')
            }
        }

        # 8. Noise resistance analysis
        print("Testing noise resistance...")
        report['noise_resistance'] = self.analyze_noise_resistance(
            original_image, encrypted_image, crypto_instance,
            original_shape, rounds
        )

        # 9. Key space calculation
        print("Calculating key space...")
        report['key_space'] = self.calculate_key_space(crypto_instance)

        # 10. Statistical tests
        print("Running statistical tests...")
        report['statistics'] = {
            'original': self.calculate_image_statistics(original_image),
            'encrypted': self.calculate_image_statistics(encrypted_image),
            'decrypted': self.calculate_image_statistics(decrypted_image)
        }

        return report

    def calculate_image_statistics(self, image_array):
        """Calculate basic statistical properties of image"""
        flat = image_array.flatten()

        return {
            'mean': float(np.mean(flat)),
            'std': float(np.std(flat)),
            'min': int(np.min(flat)),
            'max': int(np.max(flat)),
            'median': float(np.median(flat)),
            'variance': float(np.var(flat))
        }
