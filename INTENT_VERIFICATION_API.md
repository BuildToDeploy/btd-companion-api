# Contract Intent Verification API

The Intent Verification API analyzes smart contracts to ensure their documented behavior matches actual on-chain implementation. It detects hidden logic, malicious patterns, and rug-pull/honeypot structures.

## Overview

Contract Intent Verification answers critical questions:
- **Does the code do what the README claims?**
- **Are there hidden functions or delayed execution logic?**
- **Does this contract have rug-pull or honeypot indicators?**
- **What's the overall trustworthiness of this contract?**

## Features

### 1. Intent vs Behavior Analysis
Compare documented intent (README, comments, NatSpec) with actual code implementation:
- Identify mismatches between claims and code
- Rate alignment score (0-100)
- Pinpoint specific discrepancies

### 2. Hidden Logic Detection
Discover code patterns that aren't immediately visible:
- **Dead Code**: Unreachable code paths that may indicate incomplete implementations
- **Delayed Execution**: Time-locks or logic triggered later (e.g., in next block)
- **Conditional Activation**: Admin-only features or hidden function switches not documented

### 3. Malicious Pattern Fingerprinting
Identify common exploit and scam patterns:
- **Rug-Pull Indicators**: Liquidity lock bypasses, ownership transfers, token burns
- **Honeypot Indicators**: Buy tax vs sell tax discrepancies, unfair buy limits, holder blocks
- **Common Exploits**: Reentrancy setup, delegatecall vulnerabilities, flash loan vectors

## API Endpoints

### Verify Contract Intent

**Endpoint**: `POST /api/verify/intent`

**Request**:
```json
{
  "contract_id": 1,
  "source_code": null,
  "contract_name": "MyToken",
  "readme_or_comments": "A fair trading token with no special features",
  "provider": "openai"
}
```

**Parameters**:
- `contract_id` (optional): ID of contract to verify (stored in DB)
- `source_code` (optional): Raw Solidity/Vyper code to analyze
- `contract_name` (optional): Name of contract for context
- `readme_or_comments` (optional): Documentation to compare against actual behavior
- `provider` (optional): AI provider to use - `openai`, `claude`, `grok` (default: `openai`)

**Response**:
```json
{
  "verification_id": 42,
  "contract_id": 1,
  "intent_analysis": {
    "documented_intent": "A fair trading token with no special features",
    "actual_behavior": "Token has hidden admin functions and transfer restrictions",
    "intent_match_score": 35,
    "mismatches": [
      "Undocumented transfer fee mechanism",
      "Hidden admin pause function",
      "Unequal tax on buy/sell transactions"
    ]
  },
  "hidden_logic_analysis": {
    "hidden_logic_detected": true,
    "dead_code_areas": [
      {
        "logic_type": "dead_code",
        "description": "Unreachable emergency withdrawal function",
        "location": "emergencyWithdraw()",
        "line_numbers": [145, 146, 147],
        "risk_level": "medium",
        "explanation": "Function cannot be called due to require condition that's never false"
      }
    ],
    "delayed_execution_logic": [
      {
        "logic_type": "delayed_execution",
        "description": "Tax rate increases after 100 blocks",
        "location": "_beforeTokenTransfer()",
        "line_numbers": [210, 211],
        "risk_level": "high",
        "explanation": "Initial tax is 0%, but increases 10x after 100 blocks"
      }
    ],
    "conditional_activation": [
      {
        "logic_type": "conditional",
        "description": "Admin-only pauser function not in docs",
        "location": "pause()",
        "line_numbers": [180],
        "risk_level": "high",
        "explanation": "Only owner can call, not documented in README"
      }
    ]
  },
  "malicious_pattern_analysis": {
    "malicious_patterns_found": true,
    "rug_pull_indicators": [
      {
        "pattern_type": "rug_pull",
        "pattern_name": "liquidity_lock_bypass",
        "description": "Owner can withdraw liquidity despite claimed lock",
        "indicators": ["emergencyWithdraw", "unchecked_balance", "no_time_lock"],
        "affected_functions": ["removeLiquidity", "emergencyWithdraw"],
        "severity": "critical",
        "ai_reasoning": "Function allows owner to extract LP tokens without time-lock restriction"
      }
    ],
    "honeypot_indicators": [
      {
        "pattern_type": "honeypot",
        "pattern_name": "unfair_tax",
        "description": "Different buy/sell tax rates designed to trap buyers",
        "indicators": ["50% sell tax", "0% buy tax", "dynamic tax"],
        "affected_functions": ["_transfer", "calculateTax"],
        "severity": "high",
        "ai_reasoning": "99% sell tax vs 0% buy tax indicates honeypot structure"
      }
    ],
    "malicious_risk_score": 92
  },
  "overall_trust_score": 8,
  "ai_recommendation": "DO NOT INTERACT. This contract exhibits multiple critical rug-pull indicators and honeypot patterns. The documented behavior does not match the actual implementation.",
  "execution_time_ms": 2341,
  "provider_used": "openai"
}
```

### Retrieve Previous Verification

**Endpoint**: `GET /api/verify/intent/{verification_id}`

**Response**:
Returns the full verification result from above.

## Risk Levels

### Intent Match Score (0-100)
- **90-100**: Excellent match between docs and code
- **70-89**: Good match with minor undocumented features
- **50-69**: Moderate discrepancies, investigate further
- **30-49**: Major mismatches, high risk
- **0-29**: Critical mismatches, do not interact

### Hidden Logic Risk
- **Critical**: Severe security implications or clear exploit vectors
- **High**: Significant undocumented functionality
- **Medium**: Minor discrepancies or low-impact hidden code
- **Low**: Negligible impact on security/usability
- **Informational**: Minor findings for awareness

### Malicious Risk Score (0-100)
- **90-100**: Critical indicators, likely malicious
- **70-89**: Multiple concerning patterns detected
- **50-69**: Some suspicious indicators, use caution
- **30-49**: Minor red flags
- **0-29**: Low risk indicators

### Overall Trust Score (0-100)
- **80-100**: Highly trustworthy, proceed with confidence
- **60-79**: Generally safe, verify key functions
- **40-59**: Caution advised, detailed review recommended
- **20-39**: High risk, expert review needed
- **0-19**: Critical risk, avoid interaction

## Common Patterns Detected

### Rug-Pull Indicators
- **Liquidity Lock Bypass**: Owner can withdraw locked liquidity early
- **Hidden Ownership Transfer**: Multiple addresses can claim ownership
- **Token Burn Trap**: Tokens sent to dead address with no recovery
- **Unfair Allocation**: Team tokens allocated but immediately dumped
- **No Time Locks**: Critical functions lack time-lock safeguards

### Honeypot Indicators
- **Tax Imbalance**: Different buy vs sell taxes (e.g., 0% buy / 99% sell)
- **Holder Blocks**: Specific addresses cannot sell tokens
- **Buy Limits**: Buyers limited to small amounts while insiders dump
- **Dynamic Tax**: Tax increases over time to trap early buyers
- **Blacklist**: Contract can blacklist addresses from trading

### Hidden Logic
- **Dead Code**: Functions that can never execute
- **Delayed Activation**: Features that activate after X blocks
- **Conditional Gates**: Functions behind undocumented conditions
- **Version Mismatches**: Proxy pointing to different implementation
- **Init Hooks**: Initialization code that modifies behavior

## Examples

### Detecting a Honeypot Token

```bash
curl -X POST http://localhost:8000/api/verify/intent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "source_code": "pragma solidity ^0.8.0; contract HoneypotToken { uint256 buyTax = 0; uint256 sellTax = 99; }",
    "readme_or_comments": "Fair trading token with equal fees",
    "provider": "claude"
  }'
```

### Verifying Stored Contract

```bash
curl -X POST http://localhost:8000/api/verify/intent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "contract_id": 5,
    "provider": "openai"
  }'
```

## Best Practices

1. **Always Verify Before Interacting**: Run intent verification before trading or providing liquidity
2. **Check Multiple Aspects**: Review all three analysis sections
3. **Trust Score Matters**: Focus on overall trust score first
4. **Review Specific Findings**: Examine hidden logic and malicious patterns in detail
5. **Use for Due Diligence**: Combine with traditional code review and audits
6. **Monitor Over Time**: Reverify contracts if they update their implementation

## Error Handling

The API returns standard HTTP status codes:
- `200 OK`: Verification completed successfully
- `400 Bad Request`: Missing required parameters
- `404 Not Found`: Contract or verification not found
- `500 Internal Server Error`: Backend processing error

Errors include detailed messages for debugging.

## Rate Limits

Verification requests consume AI provider tokens. Implement rate limiting for production use:
- Community: 10 verifications/day
- Professional: 100 verifications/day
- Enterprise: Unlimited with SLA

## See Also

- [SIMULATION_API.md](./SIMULATION_API.md) - Transaction simulation
- [README.md](./README.md) - Main documentation
