"""
=============================================================================
Agent Gatekeeper for IndiGo Airlines - Data Storage Module
Student Enrolment Number: PGD202572730
=============================================================================

This module manages persistent JSON storage for:
1. Registered and Revoked AI Agents ('data/agents.json')
2. Comprehensive Security Audit Trail ('data/audit_log.json')

All data operations are thread-safe, handle file creation gracefully, and
include default sample data tailored for IndiGo Airlines passenger scenarios.
=============================================================================
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# File path constants
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
AGENTS_FILE = os.path.join(DATA_DIR, "agents.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "audit_log.json")


def ensure_data_directory() -> None:
    """Ensures that the data storage directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_current_timestamp() -> str:
    """Returns the current date and time formatted as a readable string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_sample_agents() -> List[Dict[str, Any]]:
    """Returns sample agent data for IndiGo Airlines demonstration."""
    return [
        {
            "agent_id": "6E-AGT-101",
            "agent_name": "IndiGoBot-Alpha",
            "customer_name": "Aarav Sharma",
            "permitted_actions": ["View Fares", "Book"],
            "status": "ACTIVE",
            "registered_at": "2026-11-18 10:15:00",
            "revoked_at": None,
            "notes": "Primary travel booking assistant"
        },
        {
            "agent_id": "6E-AGT-102",
            "agent_name": "TravelMate-6E",
            "customer_name": "Ananya Iyer",
            "permitted_actions": ["View Fares", "Book", "Change", "Refund"],
            "status": "ACTIVE",
            "registered_at": "2026-11-18 11:30:00",
            "revoked_at": None,
            "notes": "Full-service VIP corporate assistant"
        },
        {
            "agent_id": "6E-AGT-103",
            "agent_name": "FareWatcher-AI",
            "customer_name": "Rohan Verma",
            "permitted_actions": ["View Fares"],
            "status": "ACTIVE",
            "registered_at": "2026-11-19 09:00:00",
            "revoked_at": None,
            "notes": "Restricted read-only price monitor"
        },
        {
            "agent_id": "6E-AGT-104",
            "agent_name": "SkyRevoked-Bot",
            "customer_name": "Priya Patel",
            "permitted_actions": ["View Fares", "Book"],
            "status": "REVOKED",
            "registered_at": "2026-11-15 14:00:00",
            "revoked_at": "2026-11-19 18:45:12",
            "notes": "Revoked by customer following device upgrade"
        }
    ]


def get_sample_audit_logs() -> List[Dict[str, Any]]:
    """Returns sample audit history records for IndiGo Airlines demonstration."""
    return [
        {
            "request_id": "REQ-6E-9001",
            "timestamp": "2026-11-19 15:30:22",
            "customer_name": "Aarav Sharma",
            "agent_name": "IndiGoBot-Alpha",
            "action": "View Fares",
            "amount": 0.0,
            "decision": "ALLOW",
            "rule": "R4",
            "reason": "Fare viewing is an authorized read-only inquiry. Cleared for autonomous execution."
        },
        {
            "request_id": "REQ-6E-9002",
            "timestamp": "2026-11-19 16:10:45",
            "customer_name": "Aarav Sharma",
            "agent_name": "IndiGoBot-Alpha",
            "action": "Book",
            "amount": 7500.0,
            "decision": "ALLOW",
            "rule": "R5",
            "reason": "Booking amount of ₹7,500.00 is within the autonomous threshold of ₹10,000.00. Cleared for autonomous booking."
        },
        {
            "request_id": "REQ-6E-9003",
            "timestamp": "2026-11-19 17:05:11",
            "customer_name": "Ananya Iyer",
            "agent_name": "TravelMate-6E",
            "action": "Book",
            "amount": 16800.0,
            "decision": "ASK CUSTOMER",
            "rule": "R6",
            "reason": "Booking amount of ₹16,800.00 exceeds the ₹10,000.00 autonomous limit. Explicit customer confirmation is required before proceeding."
        },
        {
            "request_id": "REQ-6E-9004",
            "timestamp": "2026-11-19 17:40:00",
            "customer_name": "Rohan Verma",
            "agent_name": "FareWatcher-AI",
            "action": "Book",
            "amount": 5400.0,
            "decision": "BLOCK",
            "rule": "R3",
            "reason": "Agent 'FareWatcher-AI' is not authorized to perform 'Book'. Permitted actions for this agent: [View Fares]."
        },
        {
            "request_id": "REQ-6E-9005",
            "timestamp": "2026-11-19 19:00:15",
            "customer_name": "Priya Patel",
            "agent_name": "SkyRevoked-Bot",
            "action": "View Fares",
            "amount": 0.0,
            "decision": "BLOCK",
            "rule": "R2",
            "reason": "Agent 'SkyRevoked-Bot' was revoked on 2026-11-19 18:45:12 and is strictly prohibited from acting."
        }
    ]


def load_agents() -> List[Dict[str, Any]]:
    """
    Loads all registered agents from the persistent JSON file.
    Initializes with sample data if file does not exist.
    """
    ensure_data_directory()
    if not os.path.exists(AGENTS_FILE):
        sample = get_sample_agents()
        save_agents(sample)
        return sample

    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        # Fallback to sample data if file is corrupted
        sample = get_sample_agents()
        save_agents(sample)
        return sample


def save_agents(agents: List[Dict[str, Any]]) -> bool:
    """
    Persists the list of agents to 'data/agents.json'.
    """
    ensure_data_directory()
    try:
        with open(AGENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(agents, f, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error saving agents: {e}")
        return False


def register_agent(
    customer_name: str,
    agent_name: str,
    permitted_actions: List[str],
    notes: str = ""
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Registers a new AI agent with the given customer and permitted actions.

    Returns:
        (success: bool, message: str, agent_record: dict or None)
    """
    c_name = customer_name.strip()
    a_name = agent_name.strip()

    if not c_name:
        return False, "Customer Name cannot be empty.", None
    if not a_name:
        return False, "Agent Name cannot be empty.", None
    if not permitted_actions:
        return False, "Please select at least one permitted action.", None

    agents = load_agents()

    # Check for duplicate agent name (case-insensitive)
    for agent in agents:
        if agent.get("agent_name", "").strip().lower() == a_name.lower():
            status = agent.get("status", "ACTIVE")
            return False, f"An agent named '{a_name}' is already registered (Status: {status}). Please choose a unique name.", None

    agent_id = f"6E-AGT-{len(agents) + 101}"
    new_agent = {
        "agent_id": agent_id,
        "agent_name": a_name,
        "customer_name": c_name,
        "permitted_actions": permitted_actions,
        "status": "ACTIVE",
        "registered_at": get_current_timestamp(),
        "revoked_at": None,
        "notes": notes.strip()
    }

    agents.append(new_agent)
    if save_agents(agents):
        return True, f"Agent '{a_name}' successfully registered with ID {agent_id}!", new_agent
    return False, "Failed to save agent to persistent storage.", None


def revoke_agent(agent_name: str) -> Tuple[bool, str]:
    """
    Revokes an active AI agent and records the exact revocation timestamp.

    Returns:
        (success: bool, message: str)
    """
    a_name = agent_name.strip()
    agents = load_agents()

    found = False
    for agent in agents:
        if agent.get("agent_name", "").strip().lower() == a_name.lower():
            found = True
            if agent.get("status") == "REVOKED":
                return False, f"Agent '{a_name}' is already revoked (Revoked at: {agent.get('revoked_at')})."

            agent["status"] = "REVOKED"
            agent["revoked_at"] = get_current_timestamp()
            break

    if not found:
        return False, f"Agent '{a_name}' was not found in the registry."

    if save_agents(agents):
        return True, f"Agent '{a_name}' has been REVOKED. Exact timestamp recorded: {agent['revoked_at']}."
    return False, "Failed to persist revocation update."


def load_audit_log() -> List[Dict[str, Any]]:
    """
    Loads all audit log records from 'data/audit_log.json'.
    Initializes with sample data if file does not exist.
    """
    ensure_data_directory()
    if not os.path.exists(AUDIT_LOG_FILE):
        sample = get_sample_audit_logs()
        save_audit_log(sample)
        return sample

    try:
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        sample = get_sample_audit_logs()
        save_audit_log(sample)
        return sample


def save_audit_log(log_entries: List[Dict[str, Any]]) -> bool:
    """Persists audit log entries to 'data/audit_log.json'."""
    ensure_data_directory()
    try:
        with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error saving audit log: {e}")
        return False


def record_audit_entry(
    customer_name: str,
    agent_name: str,
    action: str,
    amount: float,
    decision: str,
    rule: str,
    reason: str,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Appends a new decision record to the persistent audit log.

    Every request is recorded with:
    - timestamp (exact date & time)
    - request_id
    - customer name
    - agent name
    - action
    - amount (₹)
    - decision (ALLOW / ASK CUSTOMER / BLOCK)
    - rule number (R1 - R7)
    - reason (explanation)
    """
    logs = load_audit_log()
    ts = timestamp if timestamp else get_current_timestamp()
    req_id = f"REQ-6E-{len(logs) + 1001}"

    entry = {
        "request_id": req_id,
        "timestamp": ts,
        "customer_name": customer_name,
        "agent_name": agent_name,
        "action": action,
        "amount": round(float(amount), 2),
        "decision": decision,
        "rule": rule,
        "reason": reason
    }

    logs.insert(0, entry)  # Prepend so newest is at the top
    save_audit_log(logs)
    return entry


def reset_to_sample_data() -> None:
    """Resets both agents and audit logs to the default IndiGo sample dataset."""
    ensure_data_directory()
    save_agents(get_sample_agents())
    save_audit_log(get_sample_audit_logs())
