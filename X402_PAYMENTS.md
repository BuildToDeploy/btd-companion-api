# x402 Solana Payment Integration

BTD Companion integrates with the x402 protocol to enable decentralized, pay-per-use access to premium features using Solana and other blockchain networks.

## Overview

The x402 protocol is a payment standard that allows creators to monetize API access. Users pay small amounts upfront to access premium features, with automatic refunds on testnet, making it perfect for trying before committing.

### Supported Networks

- **Solana Mainnet** - Production Solana payments
- **Solana Devnet** - Solana development environment
- **Base Mainnet** - Ethereum Layer 2
- **Base Sepolia** - Base testnet
- **Polygon Mainnet** - Production Polygon
- **Polygon Amoy** - Polygon testnet
- **xLayer Mainnet & Testnet** - OKX Layer 2
- **Peaq Mainnet** - Peaq blockchain
- **Sei Mainnet & Testnet** - Sei blockchain

## Subscription Tiers

### Free
- **Price**: Free
- **Features**: Basic analysis, limited simulations (100 API calls)
- **Use Case**: Trial and basic exploration

### Basic
- **Price**: 0.005 SOL (~$0.50 USD)
- **Features**: 
  - Contract analysis
  - Transaction simulations
  - Intent verification
- **API Calls**: 10,000/month
- **Use Case**: Regular developers

### Pro
- **Price**: 0.05 SOL (~$5.00 USD)
- **Features**: 
  - All basic features
  - Malicious pattern detection
  - Priority queue
  - Advanced analysis
- **API Calls**: 100,000/month
- **Priority Support**: Yes
- **Use Case**: Professional developers

### Enterprise
- **Price**: 0.5 SOL (~$50.00 USD)
- **Features**: 
  - All features unlocked
  - Custom analysis
  - Full API access
  - Dedicated support
  - Priority queue
- **API Calls**: 1,000,000/month
- **Use Case**: Teams and production systems

## API Endpoints

### Get Available Tiers
```bash
GET /api/x402/tiers
```

Returns all available subscription tiers with pricing and features.

**Response**:
```json
[
  {
    "tier": "free",
    "monthly_price_lamports": 0,
    "monthly_price_usd": 0,
    "features": ["basic_analysis", "limited_simulations"],
    "api_calls_limit": 100,
    "priority_support": false,
    "description": "Free tier with basic features"
  },
  {
    "tier": "basic",
    "monthly_price_lamports": 5000000,
    "monthly_price_usd": 0.50,
    "features": ["contract_analysis", "simulations", "intent_verification"],
    "api_calls_limit": 10000,
    "priority_support": false,
    "description": "Basic tier for regular users"
  }
  // ... more tiers
]
```

### Initiate Payment
```bash
POST /api/x402/payment/initiate
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "network": "solana",
  "tier": "pro",
  "amount_lamports": 50000000,
  "contract_id": 1
}
```

**Parameters**:
- `network` - Blockchain network (solana, base, polygon, etc.)
- `tier` - Subscription tier (free, basic, pro, enterprise)
- `amount_lamports` - Amount in Solana lamports (1 SOL = 1 billion lamports)
- `contract_id` - (Optional) Associated contract ID

**Response**:
```json
{
  "payment_id": 1,
  "network": "solana",
  "amount_lamports": 50000000,
  "tier": "pro",
  "x402_url": "https://api.x402.com/api/solana/paid-content",
  "message": "Redirect user to x402_url to complete payment"
}
```

### Verify Payment
```bash
POST /api/x402/payment/verify
Content-Type: application/json

{
  "transaction_hash": "5s6t7u8v9w0x1y2z...",
  "network": "solana"
}
```

**Response**:
```json
{
  "is_valid": true,
  "status": "confirmed",
  "confirmed_at": "2024-01-15T10:30:00",
  "tier": "pro",
  "access_level": 2,
  "message": "Payment verified and confirmed"
}
```

### Create Subscription
```bash
POST /api/x402/subscription/create
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "tier": "pro",
  "network": "solana",
  "auto_renew": true
}
```

**Response**:
```json
{
  "subscription_id": 1,
  "tier": "pro",
  "status": "active",
  "next_billing_date": "2024-02-15T10:30:00",
  "monthly_price_lamports": 50000000,
  "monthly_price_usd": 5.00,
  "features": [
    "contract_analysis",
    "simulations",
    "intent_verification",
    "malicious_detection",
    "priority_queue"
  ],
  "api_calls_limit": 100000,
  "monthly_calls_used": 0,
  "created_at": "2024-01-15T10:30:00"
}
```

### Get Current Subscription
```bash
GET /api/x402/subscription/current
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
{
  "subscription_id": 1,
  "tier": "pro",
  "status": "active",
  "next_billing_date": "2024-02-15T10:30:00",
  "monthly_price_lamports": 50000000,
  "monthly_price_usd": 5.00,
  "features": [...],
  "api_calls_limit": 100000,
  "monthly_calls_used": 2450
}
```

### Log Access
```bash
POST /api/x402/access/log
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "payment_id": 1,
  "endpoint": "/api/verify/intent",
  "feature": "intent_verification",
  "tokens_used": 1250,
  "execution_time_ms": 2340
}
```

### Get Access History
```bash
GET /api/x402/access/history?limit=50
Authorization: Bearer YOUR_API_KEY
```

**Response**:
```json
[
  {
    "access_id": 1,
    "endpoint": "/api/verify/intent",
    "feature_accessed": "intent_verification",
    "tokens_used": 1250,
    "execution_time_ms": 2340,
    "success": true,
    "created_at": "2024-01-15T10:32:15"
  },
  {
    "access_id": 2,
    "endpoint": "/api/simulate/transaction",
    "feature_accessed": "transaction_simulation",
    "tokens_used": 850,
    "execution_time_ms": 1560,
    "success": true,
    "created_at": "2024-01-15T10:35:42"
  }
]
```

## Payment Flow

1. **User selects tier** - Browse available tiers and pricing
2. **Initiate payment** - Call `/api/x402/payment/initiate` to get x402 URL
3. **Redirect to x402** - Direct user to returned x402_url
4. **Complete payment** - User signs transaction in wallet
5. **Verify payment** - Call `/api/x402/payment/verify` with transaction hash
6. **Access unlocked** - User gains access to selected features
7. **Track usage** - Endpoints log access for quota management

## Usage Tracking

All premium feature access is logged and tracked:

- **Endpoint tracking** - Which API endpoints are called
- **Feature tracking** - Which features are used
- **Token counting** - AI token usage is counted
- **Execution time** - Performance metrics are recorded
- **Success/Error** - Request success status and errors

View access history via `/api/x402/access/history` to monitor usage and quota status.

## Environment Configuration

Add these to your `.env` file:

```env
# x402 Payment Configuration
X402_ENABLED=True
X402_TESTNET=True  # Set to False for mainnet
X402_RECEIVER_ADDRESS=your_solana_wallet_address
```

## Implementation Example

### React/TypeScript Frontend

```typescript
// Get subscription tiers
const tiers = await fetch('/api/x402/tiers').then(r => r.json());

// Initiate payment
const payment = await fetch('/api/x402/payment/initiate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`
  },
  body: JSON.stringify({
    network: 'solana',
    tier: 'pro',
    amount_lamports: 50000000
  })
});

const { x402_url, payment_id } = await payment.json();

// Redirect user to x402 to complete payment
window.location.href = x402_url;

// After user completes payment, verify
const verification = await fetch('/api/x402/payment/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    transaction_hash: user_transaction_hash,
    network: 'solana'
  })
});

const result = await verification.json();
if (result.is_valid) {
  // Grant access to premium features
}
```

## Testing on Devnet/Testnet

When using testnet networks (solana-devnet, base-sepolia, etc.):

1. Test payments are automatically refunded
2. No real funds are charged
3. Perfect for development and testing
4. Switch to mainnet for production

## Support

For issues or questions about x402 integration:
- x402 Protocol Docs: https://x402.com/docs
- GitHub Issues: Report integration problems
- Email: support@btdcompanion.dev
