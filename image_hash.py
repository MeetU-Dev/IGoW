"""
IGoW (Image-Generated Proof-of-Work) - Image Hash Generator

This module provides cryptographic image generation for blockchain consensus.
Each block generates a deterministic pixel array from its data and nonce,
creating a unique visual fingerprint that can be verified by all nodes.
"""

import hashlib
import time
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
    # Input validation
    if not isinstance(data, str):
        raise TypeError("data must be a string")
    if not isinstance(nonce, int) or nonce < 0:
        raise ValueError("nonce must be a non-negative integer")
    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("width and height must be integers")
    if width <= 0 or height <= 0 or width > 2000 or height > 2000:
        raise ValueError("width and height must be between 1 and 2000")

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
    # Input validation
    if not isinstance(pixels, np.ndarray):
        raise TypeError("pixels must be a numpy ndarray")
    if not isinstance(difficulty, int) or difficulty < 0:
        raise ValueError("difficulty must be a non-negative integer")

    # Extract red channel (index 0 in RGB, which is the first axis of color)
    red_channel = pixels[:, :, 0]
    
    # Flatten to 1D array
    red_flat = red_channel.flatten()
    
    total_pixels = red_flat.size
    if difficulty > total_pixels:
        # impossible to satisfy
        return False

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


def mine_block(data: str, difficulty: int, width: int = 10, height: int = 10, max_workers: int = 1) -> dict:
    """
    Mine a block by finding a nonce that produces an image meeting difficulty threshold.
    
    This is the core PoW computation for IGoW. The nonce search is intentionally brute force
    with no shortcuts — this is a fundamental security property. There is no way to predict
    which nonce will satisfy the difficulty without trying them sequentially. This ensures
    that the only way to create valid blocks is through computational work.
    
    Args:
        data: Block data string to mine
        difficulty: Required difficulty level (number of qualifying pixels)
        width: Pixel array width (default 10)
        height: Pixel array height (default 10)
    
    Returns:
        dict with keys:
            - "nonce": The winning nonce value
            - "attempts": Total attempts made (same as nonce)
            - "elapsed": Time taken in seconds (4 decimal places)
            - "hash_rate": Attempts per second (2 decimal places)
            - "pixels": The valid pixel array
            - "image_hex": Hex fingerprint of the pixels
            - "data": Original data string
            - "difficulty": Difficulty level used
    """
    # Input validation
    if not isinstance(difficulty, int) or difficulty < 0:
        raise ValueError("difficulty must be a non-negative integer")
    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("width and height must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")

    start_time = time.time()
    nonce = 0
    
    # Brute force search for valid nonce. If max_workers > 1, attempt parallel search.
    if max_workers is None or max_workers <= 1:
        # Sequential search
        while True:
            pixels = generate_image_hash(data, nonce, width, height)

            if check_difficulty(pixels, difficulty):
                end_time = time.time()
                elapsed = round(end_time - start_time, 4)
                # attempts should count how many nonces were tried (nonce starts at 0)
                attempts = nonce + 1
                hash_rate = round(attempts / elapsed, 2) if elapsed > 0 else 0

                return {
                    "nonce": nonce,
                    "attempts": attempts,
                    "elapsed": elapsed,
                    "hash_rate": hash_rate,
                    "pixels": pixels,
                    "image_hex": image_to_hex(pixels),
                    "data": data,
                    "difficulty": difficulty,
                }

            nonce += 1
    else:
        # Parallel search using threads. Each worker checks nonces starting from its id
        # stepping by `max_workers` to avoid overlap. This is a best-effort parallel
        # explorer; order of discovered nonce may differ from sequential search.
        import threading

        found = threading.Event()
        result = {}

        def worker(start_id: int):
            nonlocal result
            i = start_id
            while not found.is_set():
                pixels = generate_image_hash(data, i, width, height)
                if check_difficulty(pixels, difficulty):
                    end_time = time.time()
                    elapsed = round(end_time - start_time, 4)
                    attempts = i + 1
                    hash_rate = round(attempts / elapsed, 2) if elapsed > 0 else 0
                    result = {
                        "nonce": i,
                        "attempts": attempts,
                        "elapsed": elapsed,
                        "hash_rate": hash_rate,
                        "pixels": pixels,
                        "image_hex": image_to_hex(pixels),
                        "data": data,
                        "difficulty": difficulty,
                    }
                    found.set()
                    return
                i += max_workers

        threads = []
        for w in range(max_workers):
            t = threading.Thread(target=worker, args=(w,))
            t.daemon = True
            threads.append(t)
            t.start()

        # Wait for a worker to find a result
        found.wait()
        # Join threads briefly
        for t in threads:
            if t.is_alive():
                t.join(0.01)

        return result


def print_mining_result(result: dict) -> None:
    """
    Print a formatted mining result report.
    
    Displays the outcome of a successful mining operation with all relevant statistics
    in a clean, readable format.
    
    Args:
        result: Dict returned from mine_block()
    """
    print("\n" + "=" * 70)
    print("MINING RESULT")
    print("=" * 70)
    print(f"Data mined         : {result['data']}")
    print(f"Difficulty         : {result['difficulty']}")
    print(f"Winning nonce      : {result['nonce']}")
    print(f"Total attempts     : {result['attempts']:,}")
    print(f"Time taken         : {result['elapsed']} seconds")
    print(f"Hash rate          : {result['hash_rate']} attempts/sec")
    print(f"Image fingerprint  : {result['image_hex'][:64]}...")
    print("=" * 70)


def test_difficulty_scaling() -> None:
    """
    Mine blocks at increasing difficulty levels to demonstrate exponential scaling.
    
    This test shows the fundamental property of PoW: as difficulty increases,
    the work required grows exponentially. Each additional difficulty typically
    requires ~5x more attempts on average, since each pixel independently has
    a ~1/5 probability of satisfying the condition.
    """
    print("\nTesting difficulty scaling...")
    print("Mining 'IGOW_GENESIS' at difficulty levels 1, 2, and 3:\n")
    
    results = []
    
    # Use distinct, progressively harder test data per difficulty level
    data_map = {
        1: "IGOW_TEST_D1",
        2: "IGOW_TEST_D2",
        3: "IGOW_TEST_D3",
    }

    for difficulty in [1, 2, 3]:
        data = data_map[difficulty]
        result = mine_block(data, difficulty)
        print_mining_result(result)
        results.append(result)
    
    # Print scaling summary
    print("\n" + "=" * 70)
    print("DIFFICULTY SCALING SUMMARY")
    print("=" * 70)
    
    for i, result in enumerate(results):
        diff = result["difficulty"]
        attempts = result["attempts"]
        print(f"Difficulty {diff}: {attempts:>6,} attempts")
        
        if i > 0:
            prev_attempts = results[i - 1]["attempts"]
            scaling_factor = round(attempts / prev_attempts, 1)
            print(f"  → {scaling_factor}x harder than difficulty {diff - 1}")
    
    print("=" * 70)


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
    
    # ============================================================
    # MINING LOOP TEST
    # ============================================================
    print("\n" + "=" * 50)
    print("MINING LOOP TEST")
    print("=" * 50)
    
    test_difficulty_scaling()
    
    print("\nAll tests completed successfully!")
    print("=" * 50)
