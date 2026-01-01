import re
from typing import Dict, List, Any, Optional


class CircuitParser:
    """Parser for zkSNARK/ZK circuit verification (circom, noir, halo2, plonk)"""
    
    @staticmethod
    def detect_circuit_framework(source_code: str) -> str:
        """Detect which circuit framework is used"""
        if "pragma circom" in source_code:
            return "circom"
        elif "fn main(" in source_code and "pub" in source_code and "struct" in source_code:
            return "noir"
        elif "use halo2" in source_code or "halo2::plonk" in source_code:
            return "halo2"
        elif "plonk" in source_code.lower():
            return "plonk"
        else:
            return "unknown"
    
    @staticmethod
    def extract_circom_constraints(source_code: str) -> Dict[str, Any]:
        """Extract Circom circuit structure"""
        analysis = {
            "templates": [],
            "constraints": 0,
            "signals": {
                "input": [],
                "output": [],
                "intermediate": []
            },
            "components": [],
            "public_inputs": []
        }
        
        # Extract templates
        template_pattern = r"template\s+(\w+)\s*$$([^)]*)$$\s*{([^}]+)}"
        templates = re.finditer(template_pattern, source_code)
        for match in templates:
            analysis["templates"].append({
                "name": match.group(1),
                "params": match.group(2),
                "body": match.group(3)
            })
        
        # Count constraints (=== operations)
        analysis["constraints"] = len(re.findall(r"===", source_code))
        
        # Extract signals
        input_signals = re.findall(r"signal\s+input\s+(\w+)", source_code)
        output_signals = re.findall(r"signal\s+output\s+(\w+)", source_code)
        intermediate_signals = re.findall(r"signal\s+(\w+)(?!.*input|output)", source_code)
        
        analysis["signals"]["input"] = input_signals
        analysis["signals"]["output"] = output_signals
        analysis["signals"]["intermediate"] = intermediate_signals
        
        # Count public inputs
        if "public_inputs" in source_code or "input" in source_code:
            analysis["public_inputs"] = input_signals
        
        return analysis
    
    @staticmethod
    def extract_noir_circuit(source_code: str) -> Dict[str, Any]:
        """Extract Noir circuit structure"""
        analysis = {
            "functions": [],
            "public_functions": [],
            "constraints": [],
            "assert_statements": 0,
            "field_operations": []
        }
        
        # Extract functions
        func_pattern = r"(?:fn|pub fn)\s+(\w+)\s*$$([^)]*)$$\s*(?:->[\w\[\]]+)?\s*{([^}]+)}"
        functions = re.finditer(func_pattern, source_code)
        for match in functions:
            is_public = "pub fn" in match.group(0)
            analysis["functions"].append({
                "name": match.group(1),
                "params": match.group(2),
                "is_public": is_public
            })
            if is_public:
                analysis["public_functions"].append(match.group(1))
        
        # Count assert statements
        analysis["assert_statements"] = len(re.findall(r"assert\s+\(", source_code))
        
        # Detect field operations
        if "modular" in source_code:
            analysis["field_operations"].append("Modular arithmetic")
        if "field::" in source_code:
            analysis["field_operations"].append("Direct field operations")
        
        return analysis
    
    @staticmethod
    def extract_halo2_circuit(source_code: str) -> Dict[str, Any]:
        """Extract Halo2 circuit structure"""
        analysis = {
            "config": None,
            "column_types": [],
            "gates": [],
            "lookups": 0,
            "permutation_columns": 0
        }
        
        # Detect column types
        columns = re.findall(r"(Advice|Fixed|Instance|Selector)Column", source_code)
        analysis["column_types"] = list(set(columns))
        
        # Count custom gates
        analysis["gates"] = len(re.findall(r"create_gate", source_code))
        
        # Count lookups
        analysis["lookups"] = len(re.findall(r"lookup", source_code))
        
        # Detect permutation usage
        if "permutation" in source_code:
            analysis["permutation_columns"] = len(re.findall(r"enable_equality", source_code))
        
        return analysis
    
    @staticmethod
    def detect_soundness_issues(source_code: str, framework: str) -> Dict[str, List[str]]:
        """Detect potential soundness issues"""
        issues = {
            "soundness_warnings": [],
            "completeness_concerns": [],
            "efficiency_issues": []
        }
        
        if framework == "circom":
            # Check for unconstrained signals
            if re.search(r"signal\s+\w+(?!.*===)", source_code):
                issues["soundness_warnings"].append("Potentially unconstrained signals detected")
            
            # Check for division by zero risks
            if "/" in source_code and "assert" not in source_code:
                issues["soundness_warnings"].append("Division operations without zero checks")
            
        elif framework == "noir":
            # Check for missing asserts
            if "let mut" in source_code and "assert" not in source_code:
                issues["completeness_concerns"].append("Mutable variables without assertions")
            
            # Check for unchecked casts
            if "as u" in source_code or "as Field" in source_code:
                issues["soundness_warnings"].append("Type casting without validation")
        
        elif framework == "halo2":
            # Check for polynomial degree issues
            if re.search(r"create_gate.*degree\s*>\s*3", source_code):
                issues["efficiency_issues"].append("High polynomial degree detected")
            
            # Check for excessive lookups
            lookups = len(re.findall(r"lookup", source_code))
            if lookups > 5:
                issues["efficiency_issues"].append(f"{lookups} lookups may impact performance")
        
        return issues
    
    @staticmethod
    def extract_witness_generation(source_code: str) -> Dict[str, Any]:
        """Extract witness generation patterns"""
        analysis = {
            "witness_functions": [],
            "public_inputs_generation": [],
            "randomness_usage": False,
            "hash_operations": []
        }
        
        # Detect witness functions
        witness_funcs = re.findall(r"fn\s+(\w*witness\w*)\s*\(", source_code, re.IGNORECASE)
        analysis["witness_functions"] = witness_funcs
        
        # Check for randomness
        if "random" in source_code.lower() or "rand" in source_code.lower():
            analysis["randomness_usage"] = True
        
        # Detect hash operations
        hashes = re.findall(r"(keccak|sha256|poseidon|blake2|mimc)", source_code, re.IGNORECASE)
        analysis["hash_operations"] = list(set(hashes))
        
        return analysis


class CosmWasmParser:
    """Parser for CosmWasm contracts"""
    
    @staticmethod
    def extract_entry_points(source_code: str) -> Dict[str, bool]:
        """Extract entry points from CosmWasm contract"""
        return {
            "instantiate": "#[entry_point]" in source_code and "fn instantiate(" in source_code,
            "execute": "#[entry_point]" in source_code and "fn execute(" in source_code,
            "query": "#[entry_point]" in source_code and "fn query(" in source_code,
            "migrate": "fn migrate(" in source_code,
            "reply": "fn reply(" in source_code
        }
    
    @staticmethod
    def extract_messages(source_code: str) -> Dict[str, List[str]]:
        """Extract message types from CosmWasm contract"""
        messages = {
            "execute_msgs": [],
            "query_msgs": [],
            "cw_standards": []
        }
        
        # Extract message enums
        msg_pattern = r"pub\s+enum\s+(\w*Msg)\s*{([^}]+)}"
        for match in re.finditer(msg_pattern, source_code):
            msg_name = match.group(1)
            if "Execute" in msg_name:
                messages["execute_msgs"].append(msg_name)
            elif "Query" in msg_name:
                messages["query_msgs"].append(msg_name)
        
        # Detect CW standards
        if "cw20" in source_code.lower():
            messages["cw_standards"].append("CW20 (Token)")
        if "cw721" in source_code.lower():
            messages["cw_standards"].append("CW721 (NFT)")
        if "cw1155" in source_code.lower():
            messages["cw_standards"].append("CW1155 (Multi-token)")
        
        return messages
    
    @staticmethod
    def extract_state_structure(source_code: str) -> List[str]:
        """Extract state structure from CosmWasm contract"""
        state_items = []
        
        # Find state storage items
        state_pattern = r"pub\s+(const|static|struct)\s+(\w+)"
        for match in re.finditer(state_pattern, source_code):
            state_items.append(match.group(2))
        
        return state_items
    
    @staticmethod
    def detect_ibc_integration(source_code: str) -> bool:
        """Detect IBC integration in CosmWasm contract"""
        return "ibc" in source_code.lower() or "IBC" in source_code
