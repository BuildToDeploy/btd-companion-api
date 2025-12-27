-- Create simulation_results table
CREATE TABLE IF NOT EXISTS simulation_results (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id),
    user_id INTEGER REFERENCES users(id) NOT NULL,
    request_id INTEGER REFERENCES ai_requests(id),
    simulation_type VARCHAR(50) NOT NULL,  -- transaction, scenario, failure_path
    calldata TEXT,
    state_assumptions JSONB,
    result_status VARCHAR(50) NOT NULL,  -- success, reverted, error, warning
    gas_used INTEGER,
    execution_trace JSONB,
    findings JSONB,
    ai_insights TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_simulation_user ON simulation_results(user_id);
CREATE INDEX idx_simulation_contract ON simulation_results(contract_id);
CREATE INDEX idx_simulation_type ON simulation_results(simulation_type);

-- Create simulation_scenarios table
CREATE TABLE IF NOT EXISTS simulation_scenarios (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulation_results(id),
    scenario_name VARCHAR(255) NOT NULL,
    description TEXT,
    initial_state JSONB,
    modified_state JSONB,
    expected_behavior TEXT,
    actual_behavior TEXT,
    outcome VARCHAR(50),  -- success, reverted, unexpected
    ai_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scenario_simulation ON simulation_scenarios(simulation_id);

-- Create failure_paths table
CREATE TABLE IF NOT EXISTS failure_paths (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulation_results(id),
    contract_id INTEGER REFERENCES contracts(id),
    path_description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- critical, high, medium, low
    trigger_conditions JSONB,
    consequences JSONB,
    mitigation_steps JSONB,
    ai_reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_failure_simulation ON failure_paths(simulation_id);
CREATE INDEX idx_failure_contract ON failure_paths(contract_id);
CREATE INDEX idx_failure_severity ON failure_paths(severity);
