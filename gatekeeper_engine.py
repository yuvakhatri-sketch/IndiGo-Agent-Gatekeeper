"""
=============================================================================
Agent Gatekeeper for IndiGo Airlines - Decision Engine
Student Enrolment Number: PGD202572730
=============================================================================

This module implements the core Gatekeeper Decision Engine for AI agents
acting on behalf of IndiGo Airlines passengers.

The engine evaluates incoming customer requests against seven strict security
and business rules:
    - R1: Unknown agents are BLOCKED.
    - R2: Revoked agents are BLOCKED.
    - R3: Unauthorized actions are BLOCKED.
    - R4: Authorized fare viewing is ALLOWED.
    - R5: Authorized bookings of ₹10,000 or less are ALLOWED.
    - R6: Authorized bookings above ₹10,000 require ASK CUSTOMER.
    - R7: Authorized changes and refunds require ASK CUSTOMER.

CRITICAL SECURITY PRINCIPLES:
1. Always check whether an agent is registered and revoked before evaluating
   any action-specific permissions.
2. A revoked agent must NEVER be allowed to perform any action.
3. 'ASK CUSTOMER' means customer confirmation is required; the transaction
   is held in review and NEVER executed automatically.
=============================================================================
"""

from typing import Dict, Any, List, Optional, Tuple

# Supported actions across the IndiGo Agent Gatekeeper system
VALID_ACTIONS = ["View Fares", "Book", "Change", "Refund"]

# Autonomous booking threshold in Indian Rupees (₹)
AUTONOMOUS_BOOKING_THRESHOLD = 10000.0


def evaluate_request(
    customer_name: str,
    agent_name: str,
    action: str,
    amount: float,
    agents_registry: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates an agent action request against the 7 Gatekeeper security rules.

    Parameters:
        customer_name (str): Name of the passenger/customer.
        agent_name (str): Name or ID of the AI agent making the request.
        action (str): The requested action ('View Fares', 'Book', 'Change', 'Refund').
        amount (float): Monetary value in Indian Rupees (₹).
        agents_registry (list): List of registered agent records from storage.

    Returns:
        dict: A decision record containing:
            - 'decision': 'ALLOW', 'ASK CUSTOMER', or 'BLOCK'
            - 'rule': Rule identifier ('R1' through 'R7')
            - 'rule_name': Short descriptive title of the rule
            - 'reason': Human-readable explanation of why the decision was made
            - 'status_type': 'success', 'warning', or 'error' (for UI rendering)
            - 'customer_name': Normalized customer name
            - 'agent_name': Normalized agent name
            - 'action': Normalized action
            - 'amount': Amount formatted as float
    """
    # Clean input strings
    c_name_clean = customer_name.strip()
    a_name_clean = agent_name.strip()
    action_clean = action.strip()
    amount_val = float(amount) if amount is not None else 0.0

    # -------------------------------------------------------------------------
    # STEP 1: Search for the agent in the registry
    # -------------------------------------------------------------------------
    matched_agent: Optional[Dict[str, Any]] = None
    for entry in agents_registry:
        if entry.get("agent_name", "").strip().lower() == a_name_clean.lower():
            matched_agent = entry
            break

    # -------------------------------------------------------------------------
    # RULE R1: Unknown agents are BLOCKED
    # If the agent is not registered, or customer does not match registered owner
    # -------------------------------------------------------------------------
    if not matched_agent:
        return {
            "decision": "BLOCK",
            "rule": "R1",
            "rule_name": "Unknown Agent Policy",
            "reason": f"Agent '{a_name_clean}' is not registered in the IndiGo Agent Registry.",
            "status_type": "error",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # Verify that the agent belongs to the specified customer
    reg_customer = matched_agent.get("customer_name", "").strip()
    if reg_customer.lower() != c_name_clean.lower():
        return {
            "decision": "BLOCK",
            "rule": "R1",
            "rule_name": "Unknown Agent / Customer Mismatch",
            "reason": (
                f"Agent '{a_name_clean}' is registered to customer '{reg_customer}', "
                f"not '{c_name_clean}'. Unrecognized customer-agent relationship."
            ),
            "status_type": "error",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # RULE R2: Revoked agents are BLOCKED
    # A revoked agent must never be allowed to act.
    # -------------------------------------------------------------------------
    agent_status = matched_agent.get("status", "ACTIVE").upper()
    revocation_timestamp = matched_agent.get("revoked_at")

    if agent_status == "REVOKED" or revocation_timestamp is not None:
        time_str = f" on {revocation_timestamp}" if revocation_timestamp else ""
        return {
            "decision": "BLOCK",
            "rule": "R2",
            "rule_name": "Revoked Agent Policy",
            "reason": f"Agent '{a_name_clean}' was revoked{time_str} and is strictly prohibited from acting.",
            "status_type": "error",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # RULE R3: Unauthorized actions are BLOCKED
    # The requested action must be in the agent's permitted actions list.
    # -------------------------------------------------------------------------
    permitted_actions = matched_agent.get("permitted_actions", [])
    # Case-insensitive comparison for safety
    permitted_actions_clean = [p.strip() for p in permitted_actions]

    if action_clean not in permitted_actions_clean:
        allowed_list_str = ", ".join(permitted_actions_clean) if permitted_actions_clean else "None"
        return {
            "decision": "BLOCK",
            "rule": "R3",
            "rule_name": "Unauthorized Action Policy",
            "reason": (
                f"Agent '{a_name_clean}' is not authorized to perform '{action_clean}'. "
                f"Permitted actions for this agent: [{allowed_list_str}]."
            ),
            "status_type": "error",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # RULE R4: Authorized fare viewing is ALLOWED
    # Fare inquiry is a safe, read-only operational query.
    # -------------------------------------------------------------------------
    if action_clean == "View Fares":
        return {
            "decision": "ALLOW",
            "rule": "R4",
            "rule_name": "Authorized Fare Viewing",
            "reason": "Fare viewing is an authorized read-only inquiry. Cleared for autonomous execution.",
            "status_type": "success",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # RULE R5: Authorized bookings of ₹10,000 or less are ALLOWED
    # -------------------------------------------------------------------------
    if action_clean == "Book" and amount_val <= AUTONOMOUS_BOOKING_THRESHOLD:
        return {
            "decision": "ALLOW",
            "rule": "R5",
            "rule_name": "Low-Value Booking Autonomous Clearance",
            "reason": (
                f"Booking amount of ₹{amount_val:,.2f} is within the autonomous threshold "
                f"of ₹{AUTONOMOUS_BOOKING_THRESHOLD:,.2f}. Cleared for autonomous booking."
            ),
            "status_type": "success",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # RULE R6: Authorized bookings above ₹10,000 require ASK CUSTOMER
    # -------------------------------------------------------------------------
    if action_clean == "Book" and amount_val > AUTONOMOUS_BOOKING_THRESHOLD:
        return {
            "decision": "ASK CUSTOMER",
            "rule": "R6",
            "rule_name": "High-Value Booking Approval Required",
            "reason": (
                f"Booking amount of ₹{amount_val:,.2f} exceeds the ₹{AUTONOMOUS_BOOKING_THRESHOLD:,.2f} "
                "autonomous limit. Explicit customer confirmation is required before proceeding."
            ),
            "status_type": "warning",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # RULE R7: Authorized changes and refunds require ASK CUSTOMER
    # Modifications and refunds impact itineraries and require customer consent.
    # -------------------------------------------------------------------------
    if action_clean in ["Change", "Refund"]:
        return {
            "decision": "ASK CUSTOMER",
            "rule": "R7",
            "rule_name": "Itinerary Modification & Refund Policy",
            "reason": (
                f"Authorized '{action_clean}' action affects ticket itinerary / financial credit. "
                "Explicit customer confirmation is required."
            ),
            "status_type": "warning",
            "customer_name": c_name_clean,
            "agent_name": a_name_clean,
            "action": action_clean,
            "amount": amount_val
        }

    # -------------------------------------------------------------------------
    # Fallback default: If an unhandled action slips through, block securely
    # -------------------------------------------------------------------------
    return {
        "decision": "BLOCK",
        "rule": "R3",
        "rule_name": "Unrecognized Action Policy",
        "reason": f"Action '{action_clean}' is not recognized in the IndiGo security policy.",
        "status_type": "error",
        "customer_name": c_name_clean,
        "agent_name": a_name_clean,
        "action": action_clean,
        "amount": amount_val
    }
