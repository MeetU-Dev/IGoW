"""
IGoW (Image-Generated Proof-of-Work) - Image Hash Generator

This module provides cryptographic image generation for blockchain consensus.
Each block generates a deterministic pixel array from its data and nonce,
creating a unique visual fingerprint that can be verified by all nodes.
"""

import hashlib
import numpy as np


def generate_image_hash(data: str, nonce: int, width: int = 10, height: int = 10) -> np.ndarray:
    """
    Generate a deterministic pixel array from data and nonce.
    
    This function is core to IGoW consensus. Determinism is critical because:
    - All network nodes must independently generate IDENTICAL images for the same block
    - Any variation would break consensus and invalidate the block
    - The SHA-256 hash ensures the slightest change in data/nonce produces completely different pixels
    - This creates the Proof-of-Work: the difficulty is in finding data+nonce combinations
      that produce images meeting certain criteria (e.g., patterns, hash thresholds)
    
    Args:
        data: Block data string (e.g., "IGOW_BLOCK_0")
        nonce: Integer nonce for PoW iteration
        width: Pixel array width (default 10)
        height: Pixel array height (default 10)
    
    Returns:
        np.ndarray: Array of shape (height, width, 3) with uint8 RGB values (0-255)
    """
    # Combine data and nonce into a single string
    combined = f"{data}:{nonce}"
    
    # Compute SHA-256 hash
    hash_object = hashlib.sha256(combined.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hex digest to integer for RNG seed
    seed_value = int(hash_hex, 16)
    
    # Create RNG with the deterministic seed
    rng = np.random.default_rng(seed_value)
    
    # Generate pixel array: (height, width, 3) RGB image with uint8 values
    pixel_array = rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)
    
    return pixel_array


def image_to_hex(pixels: np.ndarray) -> str:
    """
    Convert pixel array to compact hex string fingerprint.
    
    This hex fingerprint serves as the on-chain representation of the image.
    Instead of storing the full pixel array on-chain (expensive), we store this
    compressed hex representation. Nodes can verify by regenerating the image
    and computing its hex fingerprint independently.
    
    Args:
        pixels: np.ndarray of shape (height, width, 3) with uint8 values
    
    Returns:
        str: Hexadecimal string representation of the pixel array
    """
    # Convert array to bytes and return as hex string
    pixel_bytes = pixels.astype(np.uint8).tobytes()
    hex_string = pixel_bytes.hex()
    
    return hex_string


def verify_determinism(data: str, nonce: int) -> bool:
    """
    Verify that image generation is deterministic.
    
    Determinism is the foundation of blockchain consensus. This function
    validates that the same data+nonce always produces identical pixel arrays.
    If non-determinism is detected, it signals a critical bug that would
    break network consensus.
    
    Args:
        data: Block data string
        nonce: Integer nonce
    
    Returns:
        bool: True if both generations are identical, False otherwise
    """
    # Generate image twice with identical inputs
    image1 = generate_image_hash(data, nonce)
    image2 = generate_image_hash(data, nonce)
    
    # Compare arrays element-wise
    is_deterministic = np.array_equal(image1, image2)
    
    # Print result
    if is_deterministic:
        print("DETERMINISM CHECK: PASSED")
    else:
        print("DETERMINISM CHECK: FAILED")
    
    return is_deterministic


def check_difficulty(pixels: np.ndarray, difficulty: int) -> bool:
    """
    Check if a pixel array meets the difficulty threshold.
    
    In IGoW PoW, miners must find data+nonce combinations that produce images
    where the first N pixels have red channel values < 50. This is analogous
    to Bitcoin's target threshold but operates in pixel space instead of hash space.
    
    Difficulty scaling:
    - difficulty=1: Trivial, ~19% chance any image passes
    - difficulty=5: Moderate, ~0.7% chance of passing
    - difficulty=10: Hard, on a 10x10 image all top-row pixels must qualify
    
    Args:
        pixels: np.ndarray of shape (height, width, 3) with uint8 RGB values
        difficulty: Number of leading pixels that must have red < 50
    
    Returns:
        bool: True if first `difficulty` pixels all have red < 50, False otherwise
    """
    # Extract red channel (index 2 in RGB, which is the last axis)
    red_channel = pixels[:, :, 2]
    
    # Flatten to 1D array
    red_flat = red_channel.flatten()
    
    # Check first `difficulty` pixels - all must have red < 50
    for i in range(difficulty):
        if red_flat[i] >= 50:
            return False
    
    return True


def get_difficulty_stats(difficulty: int) -> dict:
    """
    Calculate probability and expected work for a given difficulty level.
    
    This function mirrors Bitcoin's difficulty adjustment but in pixel probability space.
    Each pixel independently has a 50/256 ≈ 19.5% chance of satisfying the
    red-channel-less-than-50 condition. As difficulty increases, the probability
    compounds multiplicatively, exponentially increasing the expected attempts.
    
    Args:
        difficulty: The difficulty level (number of pixels required to pass)
    
    Returns:
        dict with keys:
            - "difficulty": The input difficulty value
            - "probability": Probability that `difficulty` pixels all satisfy condition
            - "expected_attempts": Average number of nonces needed to find one valid image
    """
    # Probability that a single pixel has red < 50
    single_pixel_probability = 50 / 256
    
    # Probability that all `difficulty` pixels satisfy the condition
    combined_probability = single_pixel_probability ** difficulty
    
    # Expected attempts (reciprocal of probability)
    expected_attempts = int(1 / combined_probability)
    
    return {
        "difficulty": difficulty,
        "probability": combined_probability,
        "expected_attempts": expected_attempts
    }


def visualize_difficulty() -> None:
    """
    Display a formatted table of difficulty levels and their corresponding statistics.
    
    This helps users understand the exponential growth in work required as difficulty
    increases. The table shows how quickly the expected attempts scale with difficulty.
    """
    print("\nDifficulty Analysis Table:")
    print("-" * 70)
    print(f"{'Difficulty':<12} {'Probability':<25} {'Expected Attempts':<20}")
    print("-" * 70)
    
    for difficulty in range(1, 7):
        stats = get_difficulty_stats(difficulty)
        prob = stats["probability"]
        attempts = stats["expected_attempts"]
        
        # Format with comma separators for readability
        attempts_str = f"{attempts:,}"
        print(f"{difficulty:<12} {prob:<25.2e} {attempts_str:<20}")
    
    print("-" * 70)


if __name__ == "__main__":
    # Test with sample block data
    print("=" * 50)
    print("IGoW Image Hash Generator - Test Run")
    print("=" * 50)
    
    # Verify determinism
    result = verify_determinism(data="IGOW_BLOCK_0", nonce=42)
    
    # Generate and display image properties
    print()
    image = generate_image_hash(data="IGOW_BLOCK_0", nonce=42)
    
    # Print hex fingerprint
    hex_fp = image_to_hex(image)
    print(f"Image Hex Fingerprint: {hex_fp[:64]}...")  # Print first 64 chars
    
    # Print array shape
    print(f"Pixel Array Shape: {image.shape}")
    
    print("=" * 50)
    
    # ============================================================
    # DIFFICULTY SYSTEM TEST
    # ============================================================
    print("\n" + "=" * 50)
    print("DIFFICULTY SYSTEM TEST")
    print("=" * 50)
    
    # Show difficulty analysis table
    visualize_difficulty()
    
    # Test generated image against different difficulty levels
    print("\nTesting image (IGOW_BLOCK_0, nonce=42) against difficulty levels:")
    test_difficulties = [1, 2, 3]
    
    for diff in test_difficulties:
        result = check_difficulty(image, diff)
        status = "PASS" if result else "FAIL"
        print(f"Difficulty {diff}: {status}")
    
    print("=" * 50)
