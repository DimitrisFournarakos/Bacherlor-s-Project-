# Comparative Performance Evaluation of Asymmetric Cryptographic Algorithms

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Academic%20%26%20Educational%20Use-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Academic%20Project-brightgreen.svg)]()

A pure-Python implementation and benchmarking framework for the comparative evaluation of asymmetric cryptographic algorithms.

The project implements and evaluates five cryptographic algorithms using realistic, standardized parameters:

* **RSA-2048**
* **Diffie–Hellman (RFC 3526 Group 14 / 2048-bit MODP)**
* **DSA-2048/256**
* **ECDSA using secp256k1**
* **Ed25519**

The main objective is to study the computational and structural characteristics of these algorithms through a common experimental framework, measuring execution time, input-size scalability, key size, signature size, and other relevant metrics.

> **Important:** This project is intended for academic and educational purposes. It is **not a production cryptographic library** and must not be used to protect sensitive information.

---

## Table of Contents

* [Overview](#overview)
* [Implemented Algorithms](#implemented-algorithms)
* [Key Features](#key-features)
* [Project Architecture](#project-architecture)
* [Installation](#installation)
* [Usage](#usage)
* [Benchmark Methodology](#benchmark-methodology)
* [Measured Metrics](#measured-metrics)
* [Generated Results](#generated-results)
* [Implementation Details](#implementation-details)
* [Limitations](#limitations)
* [Security Considerations](#security-considerations)
* [Reproducibility](#reproducibility)
* [Project Structure](#project-structure)
* [References](#references)
* [Academic Context](#academic-context)
* [License](#license)
* [Contributing](#contributing)

---

## Overview

The purpose of this project is to provide a controlled experimental environment for studying the performance characteristics of different asymmetric cryptographic primitives.

The original implementation used very small, toy cryptographic parameters. Although such parameters are useful for demonstrating mathematical concepts, they are not representative of real-world cryptographic systems and can produce misleading benchmark results.

The current implementation replaces those toy parameters with realistic parameter sets based on published cryptographic standards and specifications.

The benchmark evaluates the algorithms using the same input datasets and a common timing methodology while keeping algorithm-specific operations conceptually separate.

### Main objectives

The project focuses on:

1. Comparing the computational cost of different asymmetric cryptographic constructions.
2. Studying how execution time changes with increasing input size.
3. Comparing public-key and signature representations.
4. Examining key-generation, signing, verification, and key-exchange operations.
5. Demonstrating the impact of elliptic-curve coordinate systems on implementation performance.
6. Producing reproducible numerical results and visualizations suitable for academic analysis.

> **Important methodological note:** The algorithms do not all provide exactly the same estimated security strength. RSA-2048, DH-2048, and DSA-2048/256 are approximately in the 112-bit security class, while 256-bit elliptic-curve systems such as secp256k1 and Ed25519 are generally associated with approximately 128-bit security. Therefore, the benchmark should be interpreted as a comparison of standardized cryptographic constructions and their implementation characteristics, rather than as a strict equal-security comparison.

---

# Implemented Algorithms

| Algorithm          | Parameter Set                 | Primary Operation                   | Public Key Representation | Signature Size |
| ------------------ | ----------------------------- | ----------------------------------- | ------------------------: | -------------: |
| **RSA-2048**       | 2048-bit modulus, `e = 65537` | Digital signatures / RSA operations |          2048-bit modulus |      256 bytes |
| **Diffie–Hellman** | RFC 3526 Group 14             | Key exchange                        |            2048-bit group |            N/A |
| **DSA-2048/256**   | `L = 2048`, `N = 256`         | Digital signatures                  |           2048-bit domain |       64 bytes |
| **ECDSA**          | secp256k1                     | Digital signatures                  |  33-byte compressed point |       64 bytes |
| **Ed25519**        | RFC 8032                      | Digital signatures                  |                  32 bytes |       64 bytes |

---

## RSA-2048

The RSA implementation uses a 2048-bit modulus generated from two independently generated 1024-bit probable primes.

### Main characteristics

* 2048-bit RSA modulus
* Public exponent `e = 65537`
* Probable-prime generation using Miller–Rabin testing
* SHA-256 message hashing
* PKCS#1 v1.5 signature encoding
* 256-byte RSA signature
* Pure-Python modular arithmetic

RSA key generation is intentionally included in the benchmark because prime generation is a significant computational component of RSA key establishment.

> The implementation is intended for algorithmic experimentation. It does not implement the constant-time and side-channel protections expected from production RSA libraries.

---

## Diffie–Hellman

The project implements classical finite-field Diffie–Hellman using **RFC 3526 Group 14**, a standardized 2048-bit MODP group.

### Main characteristics

* 2048-bit MODP group
* Generator `g = 2`
* Random private exponents
* Modular exponentiation using Python's arbitrary-precision integers
* Shared-secret computation between two parties

Diffie–Hellman is fundamentally a **key-exchange mechanism**, not a digital-signature algorithm.

Therefore, its benchmark should be interpreted differently from RSA, DSA, ECDSA, and Ed25519. The relevant computational operation is modular exponentiation and shared-secret establishment.

---

## DSA-2048/256

The implementation uses a DSA parameter set with:

* `L = 2048`
* `N = 256`
* 2048-bit prime `p`
* 256-bit subgroup order `q`
* SHA-256 message hashing
* Deterministic nonce generation based on RFC 6979
* 64-byte `(r || s)` signature representation

The implementation includes both signature generation and verification.

---

## ECDSA — secp256k1

ECDSA is implemented over the **secp256k1** elliptic curve.

### Main characteristics

* 256-bit elliptic curve
* Standard secp256k1 domain parameters
* Jacobian projective coordinates
* Scalar multiplication without an inversion at every point operation
* Single conversion to affine coordinates at the end of scalar multiplication
* RFC 6979 deterministic nonce generation using HMAC-SHA256
* Cryptographically random private-key generation using Python's `secrets` module
* Compressed public-key representation
* 33-byte compressed public key
* 64-byte `(r, s)` signature
* Low-`S` normalization

The use of Jacobian coordinates is particularly important for the benchmark because affine point arithmetic requires modular inversion during point operations, while projective coordinates allow most intermediate operations to avoid such inversions.

---

## Ed25519

Ed25519 is implemented according to the EdDSA construction defined for the Ed25519 parameter set.

### Main characteristics

* 255-bit twisted Edwards curve
* 32-byte public keys
* 64-byte signatures
* SHA-512 based signing process
* Deterministic nonce generation derived from the private-key material and message
* Extended Edwards coordinates `(X, Y, Z, T)`
* Efficient scalar multiplication using projective coordinates
* One final modular inversion when converting the result to affine representation

The implementation avoids the inefficient approach of performing a modular inversion during every affine point operation.

---

# Key Features

* **Pure Python implementation**

  * No external cryptographic libraries such as `cryptography`, PyCryptodome, OpenSSL bindings, or libsodium are used for the cryptographic primitives.

* **Realistic cryptographic parameters**

  * The benchmark does not rely on the small toy parameters used in the original prototype.

* **Standards-based parameter selection**

  * Parameters are based on published RFCs and cryptographic specifications.

* **Elliptic-curve optimizations**

  * Jacobian coordinates for ECDSA.
  * Extended Edwards coordinates for Ed25519.

* **Deterministic signature nonces**

  * RFC 6979 is used for ECDSA and DSA.
  * Ed25519 follows its deterministic signing construction.

* **Common benchmark framework**

  * The same input datasets and timing infrastructure are used throughout the experiments.

* **Multiple input sizes**

  * 1 KB
  * 10 KB
  * 100 KB
  * 1 MB

* **Automated result generation**

  * Excel spreadsheet containing benchmark metrics.
  * Matplotlib visualizations.

* **Reproducible dataset generation**

  * Test datasets can be generated from a specified seed.

---

# Project Architecture

The project consists of three main layers:

### 1. Cryptographic Demonstrations

Each algorithm has a dedicated demonstration function showing its basic operation and intermediate results.

Examples include:

```text
demo_rsa()
demo_diffie_hellman()
demo_dsa()
demo_ecdsa()
demo_ed25519()
```

### 2. Benchmarking Layer

Dedicated measurement functions collect execution times for operations such as:

* Key generation
* Signing
* Verification
* Diffie–Hellman key exchange / modular exponentiation

High-resolution timing is performed using:

```python
time.perf_counter_ns()
```

### 3. Reporting Layer

The collected measurements are:

* stored in structured records,
* exported to Excel using `openpyxl`,
* visualized using `matplotlib`,
* and processed using `numpy` where required for plotting and aggregation.

---

# Installation

## Requirements

* Python **3.8 or newer**
* `numpy`
* `matplotlib`
* `openpyxl`

No external cryptographic package is required.

## Clone the Repository

```bash
git clone https://github.com/yourusername/crypto-benchmark.git
cd crypto-benchmark
```

## Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install numpy matplotlib openpyxl
```

Alternatively, if a `requirements.txt` file is included:

```bash
pip install -r requirements.txt
```

---

# Usage

## Run the Complete Benchmark

```bash
python performance.py
```

The benchmark will:

1. Generate the test datasets.
2. Execute the cryptographic demonstrations.
3. Measure the selected operations.
4. Collect key and signature size information.
5. Export the benchmark results to Excel.
6. Generate the visualization charts.

The primary output files are:

```text
cryptography_metrics_realistic.xlsx
plots/
```

---

## Dataset Generation

The benchmark uses four input sizes:

```text
1 KB
10 KB
100 KB
1 MB
```

The dataset generation mechanism can also be used independently when reproducible test data are required.

For example:

```python
dataset = generate_dataset(
    seed=42,
    sizes=[1000, 10000, 100000, 1000000]
)
```

---

## Running Individual Demonstrations

Because the main script contains a hyphen in its filename, it is not directly importable using standard Python module syntax.

For individual algorithm demonstrations, the recommended approach is to execute the main script and select/modify the corresponding demonstration function.

Alternatively, the file can be renamed to a valid Python module name, for example:

```text
performance.py
```

and then imported normally:

```python
from performance import demo_rsa
```

---

# Benchmark Methodology

The benchmark follows the general principle:

> **Realistic parameters → common datasets → consistent timing methodology → clearly defined metrics → transparent interpretation**

The goal is not to manipulate the measurements so that a particular algorithm appears faster. Instead, the benchmark uses realistic parameters and reports the behavior produced by the implementations.

## 1. Input Sizes

Each algorithm is evaluated using the same four message/data sizes:

| Dataset   |   Size |
| --------- | -----: |
| Dataset 1 |   1 KB |
| Dataset 2 |  10 KB |
| Dataset 3 | 100 KB |
| Dataset 4 |   1 MB |

This allows the effect of input size on processing time to be observed.

---

## 2. Timing Method

The benchmark uses:

```python
time.perf_counter_ns()
```

This provides a high-resolution monotonic timer suitable for measuring short-duration operations.

The main operations are measured independently rather than combining all cryptographic stages into one timing measurement.

---

## 3. Key Generation

Key-generation measurements include the computational work required to establish the cryptographic key material.

Examples:

* RSA: prime generation and RSA parameter construction
* ECDSA: private-key generation and public-key derivation
* Ed25519: private-key processing and public-key derivation
* DSA: private/public key generation
* DH: private exponent and public-value generation

---

## 4. Signing

For signature-based algorithms, signing latency measures the time required to produce a valid digital signature for the supplied input.

The evaluated signature algorithms are:

* RSA
* DSA
* ECDSA
* Ed25519

Diffie–Hellman is not a signature algorithm and therefore does not have a meaningful signing operation.

---

## 5. Verification

Verification latency measures the computational cost of validating a generated signature against the corresponding public key and message.

This applies to:

* RSA
* DSA
* ECDSA
* Ed25519

For Diffie–Hellman, the corresponding operation is key-exchange/shared-secret computation rather than signature verification.

---

## 6. Throughput

The benchmark also calculates an input-processing throughput based on the measured signing time:

```text
Throughput (MB/s) =
    Input Size (MB) / Signing Time (seconds)
```

This metric should be interpreted specifically as **benchmark throughput based on the signing measurement**.

It should not be interpreted as a universal measure of cryptographic system throughput, network throughput, or production-library performance.

---

# Measured Metrics

The generated Excel dataset contains measurements including:

| Metric                   | Description                                                          |
| ------------------------ | -------------------------------------------------------------------- |
| **Algorithm**            | Cryptographic algorithm                                              |
| **Input Size**           | Size of the processed dataset                                        |
| **Throughput**           | Input-processing rate derived from signing time                      |
| **Key Generation Speed** | Time required for key generation                                     |
| **Verification Latency** | Time required for signature verification                             |
| **Signing Latency**      | Time required for signature generation or corresponding DH operation |
| **Key Size**             | Reported public/key representation size                              |
| **Signature Size**       | Signature representation size                                        |

For Diffie–Hellman, the signature-related fields are not applicable and are represented accordingly.

---

# Generated Results

The benchmark generates an Excel file:

```text
cryptography_metrics_realistic.xlsx
```

The workbook can be used for:

* further statistical analysis,
* creation of custom charts,
* comparison of algorithms,
* inclusion of selected results in the thesis.

## Generated Visualizations

The project generates the following charts:

### 1. `latency_grouped_signing.png`

Grouped bar chart comparing signing latency across algorithms and input sizes.

### 2. `throughput_scalability.png`

Line chart showing how the measured input-processing throughput changes with increasing input size.

### 3. `latency_stacked_avg.png`

Visualization comparing average signing and verification latency.

### 4. `key_vs_signature_size.png`

Comparison of reported key and signature sizes.

### 5. `signature_size_bar.png`

Comparison of signature sizes across the evaluated signature algorithms.

---

# Interpreting the Results

The benchmark should be interpreted from several perspectives rather than using a single "fastest algorithm" metric.

## Computational Performance

Execution time provides information about the computational cost of the implemented algorithms under the specific Python environment used for the experiment.

## Scalability

The measurements across 1 KB to 1 MB datasets help illustrate how the message-processing component behaves as the input grows.

## Key and Signature Size

Elliptic-curve-based signature systems provide substantially smaller public-key and signature representations than traditional large-integer systems such as RSA and DSA.

This difference is particularly relevant in environments where:

* bandwidth is limited,
* storage is constrained,
* certificates or public keys are transmitted frequently,
* protocol overhead matters.

## Algorithmic Characteristics

Performance differences should not be attributed solely to the underlying mathematical algorithm. They are also affected by:

* Python interpreter overhead,
* implementation choices,
* modular arithmetic,
* coordinate representation,
* scalar multiplication strategy,
* big-integer operations,
* hashing,
* hardware,
* operating-system scheduling.

Consequently, the benchmark describes the behavior of **these particular pure-Python implementations**, rather than providing a universal ranking of cryptographic algorithms.

---

# Implementation Details

## Modular Arithmetic

The project uses Python's arbitrary-precision integer arithmetic for large-number cryptographic operations.

This allows RSA, DSA, and finite-field Diffie–Hellman to operate using realistic parameter sizes without external big-integer libraries.

---

## Miller–Rabin Primality Testing

RSA prime generation uses a probabilistic Miller–Rabin primality test.

The implementation performs multiple rounds of testing before accepting a candidate as a probable prime.

This is suitable for the educational benchmarking context of the project, but it should not be interpreted as a replacement for the carefully engineered prime-generation mechanisms of production cryptographic libraries.

---

## ECDSA Coordinate System

ECDSA uses Jacobian coordinates to avoid repeated modular inversions during point addition and doubling.

Instead of performing an inversion after every elliptic-curve operation, intermediate points remain in projective form and are converted to affine coordinates when required.

This provides a substantially more appropriate implementation strategy than the original affine-coordinate prototype.

---

## Ed25519 Coordinate System

Ed25519 uses extended Edwards coordinates:

```text
(X, Y, Z, T)
```

The implementation performs scalar multiplication in projective coordinates and converts to affine representation only when necessary.

This avoids the significant computational cost of repeatedly calculating modular inverses during scalar multiplication.

---

## Deterministic Nonces

ECDSA and DSA use deterministic nonce generation based on RFC 6979.

This avoids relying on a fresh external random value for every signature nonce while still generating message- and key-dependent nonce values.

Ed25519 uses its standardized deterministic signing procedure based on SHA-512 and private-key-derived secret material.

---

# Limitations

The results of this project should be interpreted within the scope of the experimental environment.

## 1. Pure-Python Implementations

The cryptographic primitives are implemented directly in Python rather than using optimized native libraries.

As a result, the measured execution times are expected to be substantially slower than implementations based on:

* OpenSSL
* LibreSSL
* libsodium
* hardware-optimized cryptographic libraries
* native C/C++ implementations

Therefore, the numerical timings should **not** be directly compared with published benchmarks of native cryptographic libraries.

---

## 2. Implementation-Specific Results

A benchmark measures both:

```text
Cryptographic algorithm
+
Implementation
+
Runtime environment
```

Therefore, differences between algorithms may partly reflect implementation decisions rather than only theoretical algorithmic complexity.

---

## 3. No Constant-Time Guarantees

The Python implementations are not designed to provide constant-time execution.

Operations involving:

* modular arithmetic,
* conditional branches,
* scalar multiplication,
* big integers,

may exhibit data-dependent execution behavior.

The implementation should therefore not be used in environments where resistance to timing or other side-channel attacks is required.

---

## 4. No Production Side-Channel Protections

The project does not attempt to reproduce all protections found in mature cryptographic libraries, including:

* constant-time arithmetic,
* RSA blinding,
* side-channel resistant implementations,
* fault-injection countermeasures,
* hardened memory handling,
* formal verification.

---

## 5. Limited Statistical Repetition

The current benchmark evaluates multiple input sizes but does not constitute a full statistical laboratory benchmark with large numbers of repeated trials, confidence intervals, or formal significance testing.

For more rigorous performance research, future versions could include:

* repeated measurements,
* mean and median execution time,
* standard deviation,
* confidence intervals,
* warm-up runs,
* outlier detection,
* system-load control,
* CPU affinity,
* independent benchmark repetitions.

---

## 6. Security-Level Differences

The selected parameter sets do not represent one perfectly uniform security level.

In particular:

```text
RSA-2048 / DH-2048 / DSA-2048
        ≈ 112-bit security class

secp256k1 / Ed25519
        ≈ 128-bit security class
```

Therefore, performance results should not be presented as a strict "same-security-level" comparison.

---

# Security Considerations

This project is an educational implementation and **must not be used for production cryptography**.

### The implementation does NOT provide:

* Constant-time execution
* Side-channel resistance
* RSA blinding
* Hardened key storage
* Secure memory zeroization
* Formal cryptographic verification
* Production-grade error handling
* Interoperability guarantees with all external cryptographic implementations

### The implementation DOES demonstrate:

* Standard cryptographic parameter selection
* Correct mathematical structures
* Standard signature/key-exchange procedures
* Realistic key and signature sizes
* Deterministic nonce generation where appropriate
* Practical elliptic-curve coordinate techniques
* Benchmarking and performance analysis

The distinction between **educational correctness** and **production security engineering** is fundamental to the purpose of this project.

---

# Reproducibility

The benchmark is designed to make the experimental process reproducible as far as the software environment permits.

The dataset generator accepts a seed, allowing the same input datasets to be regenerated.

Example:

```python
dataset = generate_dataset(
    seed=42,
    sizes=[1000, 10000, 100000, 1000000]
)
```

However, exact execution times are **not expected to be identical** across different machines or executions.

Performance depends on:

* CPU architecture
* CPU frequency
* Python version
* operating system
* system load
* memory subsystem
* background processes
* interpreter implementation

For meaningful comparisons, experiments should ideally be performed on the same machine under similar system conditions.

---

# Project Structure

```text
crypto-benchmark/
│
├── performance.py
│   └── Main cryptographic implementations and benchmark framework
│
├── README.md
│   └── Project documentation
│
├── LICENSE
│   └── MIT License
│
├── requirements.txt
│   └── Python dependencies
│
├── cryptography_metrics_realistic.xlsx
│   └── Generated benchmark results
│
└── plots/
    ├── latency_grouped_signing.png
    ├── throughput_scalability.png
    ├── latency_stacked_avg.png
    ├── key_vs_signature_size.png
    └── signature_size_bar.png
```

Generated output files may not be present until the benchmark has been executed.

---

# References

## Standards and Specifications

* **RFC 3526** — More Modular Exponential (MODP) Diffie-Hellman Groups for Internet Key Exchange (IKE)
* **RFC 6979** — Deterministic Usage of the Digital Signature Algorithm (DSA) and Elliptic Curve Digital Signature Algorithm (ECDSA)
* **RFC 8032** — Edwards-Curve Digital Signature Algorithm (EdDSA): Ed25519 and Ed448
* **FIPS 186-4** — Digital Signature Standard (DSS)
* **SEC 2** — Recommended Elliptic Curve Domain Parameters
* **PKCS #1 / RFC 8017** — RSA Cryptography Specifications

## Algorithms and Techniques

The implementation makes use of concepts including:

* RSA modular exponentiation
* Miller–Rabin primality testing
* Modular inverses
* Extended Euclidean algorithm
* Finite-field Diffie–Hellman
* DSA digital signatures
* ECDSA digital signatures
* Elliptic-curve scalar multiplication
* Jacobian projective coordinates
* Extended Edwards coordinates
* RFC 6979 HMAC-based deterministic nonce generation
* SHA-256 and SHA-512 hashing

---

# Academic Context

This project was developed as part of an academic thesis/project focusing on the **comparative performance evaluation of asymmetric cryptographic algorithms**.

The project combines:

* cryptographic theory,
* standards-based parameter selection,
* algorithm implementation,
* implementation optimization,
* experimental benchmarking,
* data analysis,
* visualization,
* and reproducible reporting.

The main academic objective is not to identify a universally "best" cryptographic algorithm, but to examine how different cryptographic constructions behave under a common experimental framework and to understand the factors that influence their computational and structural characteristics.

---

# Academic and Educational Use License

This project is licensed under the **ACADEMIC AND EDUCATIONAL USE LICENSE**.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

# Contributing

This repository is primarily an academic project, but suggestions, corrections, and technical improvements are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Document significant methodological or cryptographic changes.
5. Submit a pull request with a clear description of the modification.

For cryptographic changes, please include the relevant standard, RFC, or technical reference whenever possible.

---

# Disclaimer

This software is provided for **educational and research purposes only**.

It is not intended to replace established cryptographic libraries or to provide production-grade security.

**Do not use the implementations in this repository to protect real-world sensitive data, passwords, private keys, financial information, authentication credentials, or other security-critical assets.**

