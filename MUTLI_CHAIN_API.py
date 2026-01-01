# Multi-Chain & Advanced Networks API

BTD Companion now supports analysis for multiple blockchain ecosystems and smart contract languages beyond Solidity/EVM.

## Supported Blockchains & Languages

### Move Language (Aptos & Sui)
- **Blockchain**: Aptos, Sui
- **Language**: Move
- **Endpoint**: `POST /api/multi-chain/contracts/move/analyze`
- **Analysis Focus**: Resource safety, capability patterns, Move-specific security issues

### CosmWasm (Cosmos Ecosystem)
- **Blockchain**: Cosmos, CosmWasm-enabled chains
- **Language**: Rust (CosmWasm-specific)
- **Endpoint**: `POST /api/multi-chain/contracts/cosmwasm/analyze`
- **Analysis Focus**: Message handling, state management, IBC integration, cross-chain risks

### TEAL/PyTeal (Algorand)
- **Blockchain**: Algorand
- **Languages**: TEAL, PyTeal
- **Endpoint**: `POST /api/multi-chain/contracts/teal/analyze`
- **Analysis Focus**: Stateful operations, transaction groups, stack depth, atomic transaction safety

### Circuit Analysis (Zero-Knowledge Proofs)
- **Frameworks**: Circom, Noir, Halo2, PLONK
- **Languages**: Circom, Rust (Noir/Halo2)
- **Endpoint**: `POST /api/multi-chain/contracts/circuit/analyze`
- **Analysis Focus**: Soundness, completeness, witness generation, proof system security

### EVM Chains (Already Supported)
- Ethereum, Polygon, Arbitrum, Base, xLayer
- Languages: Solidity, Vyper

---

## API Endpoints

### Analyze Move Contracts

```bash
POST /api/multi-chain/contracts/move/analyze
Content-Type: application/json

{
  "source_code": "module MyModule::Token { ... }",
  "contract_id": null,
  "provider": "openai"
}
```

**Response:**
```json
{
  "blockchain": "aptos",
  "language": "move",
  "modules_found": [
    {
      "name": "MyModule::Token",
      "abilities": ["key", "store"]
    }
  ],
  "resources": [
    {
      "name": "TokenStore",
      "abilities": ["key"],
      "fields": "..."
    }
  ],
  "patterns": {
    "signer_usage": ["Uses signer for authentication"],
    "capability_patterns": ["Uses capability-based security"],
    "storage_operations": ["Uses move_to", "Uses borrow_global"]
  },
  "safety_issues": {
    "potential_reentrancy": false,
    "resource_leaks": false,
    "unsafe_operations": [],
    "recommendations": []
  },
  "ai_insights": "Contract uses Move best practices with proper resource management...",
  "execution_time_ms": 2500
}
```

### Analyze CosmWasm Contracts

```bash
POST /api/multi-chain/contracts/cosmwasm/analyze
Content-Type: application/json

{
  "source_code": "#[entry_point]\npub fn execute(...) { ... }",
  "contract_id": null,
  "provider": "openai"
}
```

**Response:**
```json
{
  "blockchain": "cosmos",
  "language": "cosmwasm",
  "entry_points": {
    "instantiate": true,
    "execute": true,
    "query": true,
    "migrate": false,
    "reply": false
  },
  "messages": {
    "execute_msgs": ["ExecuteMsg"],
    "query_msgs": ["QueryMsg"],
    "cw_standards": ["CW20 (Token)"]
  },
  "state_structure": ["config", "balances", "allowances"],
  "ibc_integration": false,
  "ai_insights": "Standard CW20 implementation with proper access controls...",
  "execution_time_ms": 2300
}
```

### Analyze TEAL Contracts

```bash
POST /api/multi-chain/contracts/teal/analyze
Content-Type: application/json

{
  "source_code": "txn ApplicationID\ndup\n!",
  "contract_id": null,
  "provider": "openai"
}
```

**Response:**
```json
{
  "blockchain": "algorand",
  "language": "teal",
  "operations_count": 45,
  "state_schema": {
    "is_stateful": true,
    "global_state_ops": ["Uses global state"],
    "local_state_ops": ["Uses local state"],
    "abi_methods": ["Uses ABI routing"]
  },
  "security_issues": {
    "stack_depth_risks": [],
    "txn_group_risks": ["Uses transaction groups without proper validation"],
    "missing_checks": ["Arguments used without length validation"]
  },
  "ai_insights": "Contract validates transaction groups correctly but needs argument length checks...",
  "execution_time_ms": 1800
}
```

### Get Analysis Results

```bash
GET /api/multi-chain/contracts/analysis/123?analysis_type=move
```

---

## Circuit & ZK Analysis

### Supported Frameworks

1. **Circom** - JavaScript-based circuit language
   - Constraints, signals, templates
   - Soundness verification
   - Public input tracking

2. **Noir** - Rust-based ZK language
   - Function structure
   - Field operations
   - Assert statement analysis

3. **Halo2** - Rust ZK proving system
   - Column types (Advice, Fixed, Instance, Selector)
   - Custom gates
   - Lookup tables
   - Permutation analysis

4. **PLONK** - Permutation-based constraint system
   - Polynomial degree
   - Permutation tracking
   - Proof efficiency

### Circuit Analysis Example

```bash
POST /api/multi-chain/contracts/circuit/analyze
Content-Type: application/json

{
  "source_code": "template Example(n) { ... }",
  "framework": "circom",
  "provider": "openai"
}
```

**Response:**
```json
{
  "circuit_framework": "circom",
  "number_of_constraints": 42,
  "number_of_signals": 78,
  "number_of_public_inputs": 3,
  "soundness_issues": [
    "Potentially unconstrained signals detected"
  ],
  "witness_generation_safety": {
    "hash_operations": ["keccak256"],
    "randomness_usage": false
  },
  "proof_system_type": "groth16",
  "ai_insights": "Circuit has sound constraint structure but needs verification of signal constraints...",
  "execution_time_ms": 3100
}
```

---

## Supported Blockchains List

```bash
GET /api/multi-chain/supported-blockchains
```

**Response:**
```json
{
  "blockchains": [
    {
      "name": "Ethereum/EVM",
      "chains": ["ethereum", "polygon", "arbitrum", "base"],
      "languages": ["solidity", "vyper"]
    },
    {
      "name": "Aptos",
      "chains": ["aptos"],
      "languages": ["move"]
    },
    {
      "name": "Cosmos",
      "chains": ["cosmos"],
      "languages": ["cosmwasm"]
    },
    {
      "name": "Algorand",
      "chains": ["algorand"],
      "languages": ["teal", "pyteal"]
    }
  ]
}
```

---

## Key Features by Language

### Move
- Resource capability tracking
- Signer verification detection
- Storage operation analysis
- Abort condition mapping
- Move-specific security patterns

### CosmWasm
- Entry point validation
- CW-20/721 standard detection
- IBC integration analysis
- Cross-chain security concerns
- State consistency verification

### TEAL
- Stack depth analysis
- Transaction group validation
- ABI method extraction
- Inner transaction tracking
- Atomic transaction safety

### Circuits (ZK)
- Constraint counting
- Signal completeness verification
- Soundness issue detection
- Witness generation safety
- Proof system analysis
- Trusted setup requirements
