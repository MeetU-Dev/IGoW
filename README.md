# IGoW

**IGoW** (Image-Generated Proof-of-Work) is a prototype that explores a different way
to think about blockchain proof-of-work: not as a single hash puzzle, but as a
deterministic image-generation process driven by block data and a nonce.

This is a research prototype, not a claim that image-based PoW should replace
SHA-256. The goal is to explore the design space, show the logic clearly, and
create a clean demo that can be explained and reviewed by security and blockchain
people.

## Why I built this

I started from a cybersecurity mindset: question the default, understand why it
works, then ask whether there are meaningful alternatives. SHA-256 is proven and
widely used, but I wanted to explore whether a blockchain-style PoW could be
expressed in a different form without losing determinism.

The main idea here is simple:

- the block data and nonce are hashed into a deterministic seed
- that seed generates a pixel array
- difficulty is checked in pixel space
- the resulting image is compressed into a hex string fingerprint
- blocks chain together by fingerprint linkage

That makes the system visually demo-friendly while still preserving the core
blockchain property: changing one block breaks the chain unless you rebuild the
entire dependent history.

## What the project does

IGoW currently provides:

- deterministic image generation from `data + nonce`
- a brute-force mining loop with adjustable difficulty
- a `Block` abstraction that mines and verifies itself
- an `IGoWChain` abstraction that links blocks and verifies integrity
- persistence through JSON save/load and timestamped snapshots
- a small CLI and a presentation-style demo
- a benchmark script for comparing different worker counts
- signature and checkpoint support for stronger tamper-evidence in the prototype

## High-level flow

```mermaid
flowchart TD
		A[Block data + nonce] --> B[SHA-256 digest]
		B --> C[Deterministic RNG seed]
		C --> D[Pixel array generation]
		D --> E[Difficulty check]
		E -->|Pass| F[Image hex fingerprint]
		F --> G[Block fingerprint = SHA-256(image_hex)]
		G --> H[Chain link to previous fingerprint]
		H --> I[Chain verification / tamper detection]
```

## Core logic

### 1) Image generation

The function `generate_image_hash(data, nonce, width, height)` does three things:

1. concatenates the block data and nonce
2. hashes that string with SHA-256
3. uses the resulting integer as a seed for NumPy's RNG

That gives a deterministic pixel matrix:

$$
seed = \mathrm{int}(\mathrm{SHA256}(data:nonce), 16)
$$

$$
pixels = \mathrm{RNG}(seed).\mathrm{integers}(0, 256, shape=(height, width, 3))
$$

The important property is determinism. The same input always produces the same
image.

### 2) Difficulty rule

The current difficulty rule checks the first `d` pixels and requires the red
channel to stay below 50.

If a single pixel has probability

$$
p_1 = \frac{50}{256}
$$

then the approximate probability of passing difficulty `d` is:

$$
p(d) = \left(\frac{50}{256}\right)^d
$$

and the expected attempts are:

$$
E[attempts] = \frac{1}{p(d)}
$$

This is why difficulty is powerful as a tuning knob: each extra step grows the
work exponentially rather than linearly.

### 3) Fingerprint creation

After mining, the pixel array is converted to a hex string:

$$
image\_hex = \mathrm{hex}(pixels)
$$

Then the compact block identifier is computed as:

$$
fingerprint = \mathrm{SHA256}(image\_hex)
$$

This is used for chain linking. It is not the image itself; it is the hash of the
image representation.

### 4) Chain verification

Every block is checked with four rules:

- the image proof still validates
- the stored fingerprint matches the recomputed fingerprint
- the `previous_fingerprint` matches the prior block's fingerprint
- the index matches its position in the chain

If any one of those fails, the chain is marked corrupted.

## Math perspective

The project is built around a deterministic pipeline, but the mining outcome is
probabilistic because the nonce search is brute force.

### Expected attempts by difficulty

The table below uses the current rule `p(d) = (50/256)^d`.

| Difficulty `d` | Pass probability `p(d)` | Expected attempts `E[attempts]` |
|---:|---:|---:|
| 1 | 1.953125e-01 | 5.1 |
| 2 | 3.814697e-02 | 26.2 |
| 3 | 7.450581e-03 | 134.2 |
| 4 | 1.455192e-03 | 687.2 |
| 5 | 2.842171e-04 | 3,519.5 |
| 6 | 5.551115e-05 | 18,046.0 |
| 7 | 1.084202e-05 | 92,390.3 |

That is the big practical advantage of a tunable difficulty: it gives you a very
clear experimental control for pacing, benchmarking, and demos.

## Pros and cons vs SHA-256 PoW

| Aspect | SHA-256 PoW | IGoW prototype |
|---|---|---|
| Determinism | Yes | Yes |
| Difficulty tuning | Well understood | Adjustable and visually demo-friendly |
| Hardware optimization | Extremely mature | Not optimized yet |
| Explainability | Abstract hash space | Easier to show in a terminal/video |
| Security model | Battle-tested | Experimental |
| Chain linking | Hash pointers | Fingerprint pointers |
| Tamper detection | Strong when used correctly | Strong inside the prototype, but still needs external trust anchors for real-world security |
| Research value | Standard baseline | New design space |

## Tamper model

This prototype is **tamper-evident**, not fully tamper-proof.

What it catches well:

- changing a block's data after mining
- changing the image hex after mining
- breaking the fingerprint chain
- reordering blocks

What it does not solve by itself:

- an attacker rewriting the entire stored chain history
- network-wide consensus across multiple nodes
- identity/authenticity without external trust anchors

That is why checkpoints and signatures were added: they make the prototype more
useful as an experiment, but they do not magically turn it into a production
blockchain.

## Security and research notes

- `Block.verify()` rebuilds the image from stored `block_data` and `nonce`.
- `IGoWChain.verify_chain()` recomputes fingerprints and checks chain linkage.
- `save_checkpoint()` can store an external anchor for the last fingerprint.
- `security.py` supports Ed25519 if `cryptography` is installed, otherwise a
	fallback HMAC demo path is used.
- The fallback is for prototype convenience only; Ed25519 is the proper public-key
	route.

## Project structure

| File | Purpose |
|---|---|
| `image_hash.py` | Core deterministic image generation, difficulty checks, and mining |
| `block.py` | Block model, mining on construction, verification, serialization |
| `chain.py` | Chain management, verification, persistence, checkpoints |
| `demo.py` | Presentation-style demo for recording and LinkedIn videos |
| `cli.py` | Small CLI for demo/save/load/snapshot |
| `benchmark.py` | Quick performance comparison script |
| `security.py` | Signature helper abstraction |
| `tests/test_igow.py` | Basic unit tests |

## How to run

### Demo

```bash
python3 demo.py
```

### CLI

```bash
python3 cli.py demo
python3 cli.py snapshot
python3 cli.py save chain.json
python3 cli.py load chain.json
```

### Tests

```bash
python3 tests/test_igow.py -v
```

### Benchmark

```bash
python3 benchmark.py
```

## What the demo shows

The demo runs a clean, presentation-style sequence:

1. banner and short introduction
2. chain building with a visible mining delay
3. chain structure output
4. verification summary
5. tamper-resistance test

For a video, this is enough to show the logic, the output, and the integrity
check in one continuous run.

## Useful output interpretation

| Output | Meaning |
|---|---|
| `BLOCK VERIFIED` | The block re-generated correctly and still meets difficulty |
| `CHAIN VALID` | Every block passed verification and linkage checks |
| `CHAIN CORRUPTED` | At least one block or link failed integrity checks |
| `TAMPER DETECTED` | The demo intentionally modified a block and the chain caught it |

## Practical advantages of this prototype

- It is easy to explain visually.
- Difficulty can be adjusted as an experimental dial.
- It gives a concrete path for discussion about alternative PoW shapes.
- It can be benchmarked and extended incrementally.
- It makes tamper detection very visible for demos and presentations.

## Limitations

- Not a production blockchain.
- Not a replacement for SHA-256 PoW.
- Not a distributed consensus system.
- Not optimized for real mining hardware.
- Fallback signatures are not public-key signatures.

## Links

- DOI: https://doi.org/10.5281/zenodo.20118802
- GitHub: https://github.com/MeetU-Dev/IGoW

## Closing thought

IGoW is about exploring possibilities, not claiming victory over established
cryptography. The value here is the question it asks:

**What else could proof-of-work look like if we treat the output as an image,
not just a hash string?**