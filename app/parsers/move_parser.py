import re
from typing import Dict, List, Any, Optional
import json


class MoveParser:
    """Parser for Move language (Aptos/Sui)"""
    
    @staticmethod
    def parse_modules(source_code: str) -> List[Dict[str, Any]]:
        """Extract module definitions"""
        modules = []
        module_pattern = r"module\s+(\w+):(\w+)\s*{([^}]+)}"
        matches = re.finditer(module_pattern, source_code, re.MULTILINE)
        
        for match in matches:
            modules.append({
                "name": f"{match.group(1)}::{match.group(2)}",
                "content": match.group(3)
            })
        return modules
    
    @staticmethod
    def extract_resources(source_code: str) -> List[Dict[str, Any]]:
        """Extract resource definitions and capabilities"""
        resources = []
        resource_pattern = r"struct\s+(\w+)\s*(?:has\s+([^{]+))?\s*{([^}]+)}"
        
        matches = re.finditer(resource_pattern, source_code)
        for match in matches:
            abilities = match.group(2).strip().split(",") if match.group(2) else []
            resources.append({
                "name": match.group(1),
                "abilities": [a.strip() for a in abilities],
                "fields": match.group(3)
            })
        return resources
    
    @staticmethod
    def detect_resource_patterns(source_code: str) -> Dict[str, List[str]]:
        """Detect common Move security patterns"""
        patterns = {
            "signer_usage": [],
            "capability_patterns": [],
            "storage_operations": [],
            "abort_conditions": []
        }
        
        # Detect signer usage
        if "signer" in source_code:
            patterns["signer_usage"].append("Uses signer for authentication")
        
        # Detect capability patterns
        if re.search(r"struct\s+\w+Capability", source_code):
            patterns["capability_patterns"].append("Uses capability-based security")
        
        # Storage operations
        storage_ops = re.findall(r"move_to|borrow_global|exists", source_code)
        if storage_ops:
            patterns["storage_operations"].extend([f"Uses {op}" for op in set(storage_ops)])
        
        # Abort conditions
        abort_count = len(re.findall(r"abort\s+\d+", source_code))
        if abort_count > 0:
            patterns["abort_conditions"].append(f"Found {abort_count} abort conditions")
        
        return patterns
    
    @staticmethod
    def detect_safety_issues(source_code: str) -> Dict[str, Any]:
        """Detect Move-specific safety issues"""
        issues = {
            "potential_reentrancy": False,
            "resource_leaks": False,
            "unsafe_operations": [],
            "recommendations": []
        }
        
        # Check for nested mutable references
        if re.search(r"&mut.*&mut", source_code):
            issues["unsafe_operations"].append("Potential nested mutable references")
        
        # Check for unguarded global state access
        if "borrow_global_mut" in source_code and "signer" not in source_code:
            issues["resource_leaks"] = True
            issues["recommendations"].append("Ensure signer verification before mutable global access")
        
        # Check for infinite loops
        if "loop" in source_code and "break" not in source_code:
            issues["unsafe_operations"].append("Potential infinite loop detected")
        
        return issues


class TEALParser:
    """Parser for TEAL language (Algorand)"""
    
    @staticmethod
    def parse_teal_ops(source_code: str) -> List[Dict[str, str]]:
        """Extract TEAL operations"""
        ops = []
        lines = source_code.strip().split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("//") and not line.startswith("#"):
                parts = line.split()
                if parts:
                    ops.append({
                        "line": i + 1,
                        "operation": parts[0],
                        "args": parts[1:],
                        "full_line": line
                    })
        
        return ops
    
    @staticmethod
    def detect_state_schema(source_code: str) -> Dict[str, Any]:
        """Detect stateful contract structure"""
        schema = {
            "is_stateful": "byte" in source_code or "int" in source_code,
            "global_state_ops": [],
            "local_state_ops": [],
            "abi_methods": []
        }
        
        # Detect global state operations
        if "app_global_get" in source_code or "app_global_put" in source_code:
            schema["global_state_ops"] = ["Uses global state"]
        
        # Detect local state operations
        if "app_local_get" in source_code or "app_local_put" in source_code:
            schema["local_state_ops"] = ["Uses local state"]
        
        # Detect ABI methods
        if "@abi.method" in source_code or "abi_call" in source_code:
            schema["abi_methods"] = ["Uses ABI routing"]
        
        return schema
    
    @staticmethod
    def detect_security_issues(source_code: str) -> Dict[str, Any]:
        """Detect TEAL security issues"""
        issues = {
            "stack_depth_risks": [],
            "txn_group_risks": [],
            "missing_checks": []
        }
        
        # Stack depth analysis
        depth_count = 0
        for line in source_code.split("\n"):
            if line.strip() and not line.strip().startswith("//"):
                depth_count += 1
        
        if depth_count > 100:
            issues["stack_depth_risks"].append("High instruction count may cause stack issues")
        
        # Check for transaction group usage
        if "txn GroupIndex" in source_code and "txna" not in source_code:
            issues["txn_group_risks"].append("Uses transaction groups without proper validation")
        
        # Check for missing type checks
        if "arg" in source_code and "len" not in source_code:
            issues["missing_checks"].append("Arguments used without length validation")
        
        return issues
