# BTD Companion Simulation & Testing API

## Overview

The Simulation API enables comprehensive testing and analysis of smart contracts through transaction simulation, what-if scenario analysis, and failure path exploration. All simulations are powered by AI for intelligent insights.

## Features

### 1. Transaction Simulation API
Simulate contract calls with real calldata and state assumptions to understand execution behavior before deployment.

**Endpoint:** `POST /api/simulate/transaction`

**Request:**
```json
{
  "contract_id": 1,
  "calldata": "0xa9059cbb...",
  "state_assumptions": [
    {
      "address": "0x...",
      "balance": "1000000000000000000",
      "nonce": 5
    }
  ],
  "from_address": "0x...",
  "value": "0",
  "provider": "openai"
}
```

**Response:**
```json
{
  "simulation_id": 42,
  "status": "success",
  "gas_used": 21000,
  "execution_trace": {
    "status": "simulated",
    "steps": [...]
  },
  "findings": [
    {
      "type": "execution_failure",
      "severity": "high",
      "description": "Transaction would revert due to insufficient balance"
    }
  ],
  "ai_insights": "The transaction will fail because...",
  "execution_time_ms": 1250,
  "provider_used": "openai"
}
```

### 2. What-If Scenario Analysis
Analyze hypothetical state changes to understand contract behavior under different conditions.

**Endpoint:** `POST /api/simulate/what-if`

**Request:**
```json
{
  "contract_id": 1,
  "scenario_description": "What happens if owner changes the fee to 50%?",
  "function_to_test": "updateFee",
  "initial_state": {
    "owner": "0x123...",
    "feePercentage": 10
  },
  "modified_state": {
    "owner": "0x123...",
    "feePercentage": 50
  },
  "provider": "claude"
}
```

**Response:**
```json
{
  "scenarios": [
    {
      "scenario_name": "Fee Change to 50%",
      "description": "What happens if owner changes the fee to 50%?",
      "expected_behavior": "Fee updates and applies to future transactions",
      "actual_behavior": "Fee updates successfully, affecting swap calculations",
      "outcome": "success",
      "ai_analysis": "The fee change is valid and doesn't create edge cases..."
    }
  ],
  "summary": "The scenario analysis reveals potential impacts on contract behavior",
  "recommendations": [
    "Add fee cap validation",
    "Emit events for state changes",
    "Consider grandfather period for existing users"
  ],
  "execution_time_ms": 2100,
  "provider_used": "claude"
}
```

### 3. Failure Path Exploration
Identify worst-case scenarios, edge cases, and potential vulnerabilities.

**Endpoint:** `POST /api/simulate/failure-paths`

**Request:**
```json
{
  "contract_id": 1,
  "provider": "grok"
}
```

**Response:**
```json
{
  "contract_id": 1,
  "failure_paths": [
    {
      "path_description": "Reentrancy attack in withdraw function",
      "severity": "critical",
      "trigger_conditions": [
        "External call before state update",
        "Malicious contract in fallback"
      ],
      "consequences": [
        "Multiple withdrawals in single transaction",
        "Contract balance depletion"
      ],
      "mitigation_steps": [
        "Add mutex lock for critical sections",
        "Use checks-effects-interactions pattern",
        "Implement reentrancy guard"
      ],
      "ai_reasoning": "This path is exploitable because..."
    },
    {
      "path_description": "Integer overflow in balance tracking",
      "severity": "high",
      "trigger_conditions": ["Large deposit amounts"],
      "consequences": ["Balance counter wraps around"],
      "mitigation_steps": [
        "Use SafeMath library",
        "Add bounds validation"
      ],
      "ai_reasoning": "Solidity 0.8+ prevents this, but worth noting..."
    }
  ],
  "overall_risk_assessment": "High - Multiple critical vulnerabilities identified",
  "execution_time_ms": 3200,
  "provider_used": "grok"
}
```

## Endpoints

### List All Simulations
`GET /api/simulate/results?skip=0&limit=10`

Returns all simulation results for the authenticated user with pagination.

**Response:**
```json
{
  "count": 5,
  "simulations": [
    {
      "id": 42,
      "simulation_type": "transaction",
      "status": "success",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Simulation Details
`GET /api/simulate/results/{simulation_id}`

Retrieve full details of a specific simulation including findings and AI insights.

## Simulation Types

- **transaction**: Simulate contract function calls with specific calldata and state
- **scenario**: Analyze what-if scenarios with state modifications
- **failure_path**: Explore worst-case execution paths and vulnerabilities

## State Assumptions

Define realistic blockchain state for simulations:

```python
class SimulationStateAssumption:
    address: str              # Account address
    balance: Optional[str]    # ETH balance in wei
    storage_values: Optional[Dict]  # Contract storage state
    nonce: Optional[int]      # Transaction count
```

## Findings Format

Each simulation returns structured findings:

```python
class SimulationFinding:
    type: str        # execution_failure, unexpected_behavior, optimization_opportunity
    severity: str    # critical, high, medium, low
    description: str
    line_number: Optional[int]
```

## Integration with Contract Analysis

Simulations complement static analysis:

1. **Static Analysis** (Analysis API): Identifies potential issues in code
2. **Simulation** (Simulation API): Tests specific scenarios and behavior
3. **Failure Exploration** (Failure Paths): Reveals attack vectors and edge cases

## Error Handling

Common error responses:

- `400 Bad Request`: Missing required parameters
- `404 Not Found`: Contract or simulation result not found
- `500 Internal Server Error`: Simulation execution failed

## AI Providers

All simulations can use different AI providers for analysis:

- **openai**: GPT-4 for comprehensive analysis
- **claude**: Claude 3 for detailed reasoning
- **grok**: Grok for fast analysis

Specify provider in request or use default (OpenAI).

## Best Practices

1. **Start with transaction simulation** to understand basic behavior
2. **Use state assumptions** to model realistic conditions
3. **Explore failure paths** before deploying to mainnet
4. **Compare provider outputs** for critical contracts
5. **Save simulation results** for audit trails

## Examples

### Example 1: Testing ERC20 Transfer

```bash
curl -X POST http://localhost:8000/api/simulate/transaction \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_code": "contract ERC20 { ... }",
    "calldata": "0xa9059cbb0000....",
    "state_assumptions": [{
      "address": "0xSender",
      "balance": "1000000000000000000"
    }],
    "provider": "openai"
  }'
```

### Example 2: What-If Fee Change

```bash
curl -X POST http://localhost:8000/api/simulate/what-if \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": 1,
    "scenario_description": "What if governance changes slippage to 10%?",
    "function_to_test": "setSlippage",
    "initial_state": {"slippage": "50"},
    "modified_state": {"slippage": "10"},
    "provider": "claude"
  }'
```

### Example 3: Explore Vulnerabilities

```bash
curl -X POST http://localhost:8000/api/simulate/failure-paths \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": 1,
    "provider": "grok"
  }'
```

## Performance

- Transaction simulations: ~1-2 seconds
- What-if scenarios: ~2-3 seconds
- Failure path exploration: ~3-4 seconds

Times vary by contract complexity and AI provider response time.

## Data Persistence

All simulations are stored in the database with:

- Execution traces
- Findings and insights
- AI provider used
- Execution timestamps
- User attribution

Access historical simulations anytime through the list endpoint.
```

```python file="" isHidden
