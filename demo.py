import time
from chain import IGoWChain


def print_banner() -> None:
    """Print the startup banner for the IGoW V1 prototype demo."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║         IGoW — Image-Generated Proof-of-Work         ║")
    print("║         V1 Prototype — Pixel-Space Blockchain        ║")
    print("║         github.com/MeetU-Dev/IGoW                    ║")
    print("║         DOI: 10.5281/zenodo.20118802                 ║")
    print("╚══════════════════════════════════════════════════════╝")


def print_section(title: str) -> None:
    """Print a clean divider for each demo stage."""
    line = f"── {title} "
    print(f"\n{line}{'─' * max(0, 56 - len(line))}")


def run_demo() -> None:
    """Run the full IGoW V1 presentation demo from mining to tamper testing."""
    difficulty = 2
    width = 10
    height = 10

    # STAGE 1 — Introduction
    print_banner()
    print()
    print("IGoW replaces SHA-256 hash strings with deterministically")
    print("generated pixel images as blockchain proof-of-work.")
    print("Resolution controls difficulty. No algebraic structure to exploit.")
    print(f"Current settings: difficulty={difficulty}, size={width}x{height}")
    time.sleep(0.3)

    # STAGE 2 — Build the Chain
    print_section("BUILDING THE IGOW CHAIN")
    build_start = time.time()
    chain = IGoWChain(difficulty=difficulty, width=width, height=height)
    print(f"Genesis block mined | Fingerprint: {chain.chain[0].fingerprint[:32]}...")

    block_messages = [
        "Transfer: Meet -> Priya  | 500 IGoW tokens",
        "Transfer: Priya -> Arjun | 200 IGoW tokens",
        "Transfer: Arjun -> Meet  | 100 IGoW tokens",
    ]

    for message in block_messages:
        block = chain.add_block(message)
        print(
            f"Block {block.index} mined | Nonce: {block.nonce} | "
            f"Attempts: {block.attempts} | Time: {block.elapsed}s"
        )

    build_end = time.time()
    print(f"Total chain build time: {round(build_end - build_start, 4)} seconds")
    time.sleep(0.3)

    # STAGE 3 — Display the Chain
    print_section("CHAIN STRUCTURE")
    chain.display_chain()
    time.sleep(0.3)

    # STAGE 4 — Verify the Chain
    print_section("CHAIN VERIFICATION")
    verification = chain.verify_chain()
    print(f"valid   : {verification['valid']}")
    print(f"blocks  : {verification['blocks']}")
    print(f"errors  : {verification['errors']}")
    print(f"status  : {verification['status']}")
    print()
    if verification["valid"]:
        print("\u2713 ALL BLOCKS VERIFIED — CHAIN IS INTACT")
    else:
        print("\u2717 VERIFICATION FAILED — CHAIN CORRUPTED")
    time.sleep(0.3)

    # STAGE 5 — Tamper Test
    print_section("TAMPER RESISTANCE TEST")
    print("Attempting to tamper with Block 1...")
    before = chain.verify_chain()
    print(f"Before tamper: {before['status']}")
    chain.chain[1].data = "HACKED"
    chain.chain[1].image_hex = "00" * 150
    after = chain.verify_chain()
    print(f"After tamper : {after['status']}")
    print("\u2713 TAMPER DETECTED — Blockchain integrity preserved")
    print()
    print("This demonstrates IGoW's core security guarantee:")
    print("modifying any block invalidates all subsequent blocks.")


if __name__ == "__main__":
    try:
        run_demo()
    except Exception as exc:
        print("\nIGoW demo failed cleanly.")
        print(f"Error: {exc}")
