"""
=============================================================================
Automated Unit Tests for IndiGo Agent Gatekeeper
Student Enrolment Number: PGD202572730
=============================================================================

This test suite rigorously validates:
- The 7 Gatekeeper security rules (R1 to R7)
- Exact boundary conditions for autonomous booking thresholds (₹10,000)
- Revocation security: A revoked agent must never be permitted to act
- Storage persistence: Agent registration, revocation timestamp, and audit trail
=============================================================================
"""

import unittest
from datetime import datetime
import gatekeeper_engine
from gatekeeper_engine import evaluate_request
import storage


class TestGatekeeperEngine(unittest.TestCase):
    """Unit tests for the Agent Gatekeeper decision engine."""

    def setUp(self):
        """Prepare sample registry for testing."""
        self.sample_registry = [
            {
                "agent_id": "6E-AGT-101",
                "agent_name": "IndiGoBot-Alpha",
                "customer_name": "Aarav Sharma",
                "permitted_actions": ["View Fares", "Book"],
                "status": "ACTIVE",
                "registered_at": "2026-11-18 10:15:00",
                "revoked_at": None
            },
            {
                "agent_id": "6E-AGT-102",
                "agent_name": "TravelMate-6E",
                "customer_name": "Ananya Iyer",
                "permitted_actions": ["View Fares", "Book", "Change", "Refund"],
                "status": "ACTIVE",
                "registered_at": "2026-11-18 11:30:00",
                "revoked_at": None
            },
            {
                "agent_id": "6E-AGT-103",
                "agent_name": "FareWatcher-AI",
                "customer_name": "Rohan Verma",
                "permitted_actions": ["View Fares"],
                "status": "ACTIVE",
                "registered_at": "2026-11-19 09:00:00",
                "revoked_at": None
            },
            {
                "agent_id": "6E-AGT-104",
                "agent_name": "SkyRevoked-Bot",
                "customer_name": "Priya Patel",
                "permitted_actions": ["View Fares", "Book"],
                "status": "REVOKED",
                "registered_at": "2026-11-15 14:00:00",
                "revoked_at": "2026-11-19 18:45:12"
            }
        ]

    # -------------------------------------------------------------------------
    # TEST CASE 1: Unknown Agent -> BLOCKED (Rule R1)
    # -------------------------------------------------------------------------
    def test_tc1_unknown_agent_blocked_r1(self):
        """Test Case 1: Unregistered agent must be BLOCKED with Rule R1."""
        res = evaluate_request(
            customer_name="Vikram Malhotra",
            agent_name="GhostAgent-404",
            action="View Fares",
            amount=0.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule"], "R1")
        self.assertIn("not registered", res["reason"])

    # -------------------------------------------------------------------------
    # TEST CASE 1b: Customer Name Mismatch -> BLOCKED (Rule R1)
    # -------------------------------------------------------------------------
    def test_customer_mismatch_blocked_r1(self):
        """An agent used by an unauthorized customer must be BLOCKED with Rule R1."""
        res = evaluate_request(
            customer_name="Unauthorized Impersonator",
            agent_name="IndiGoBot-Alpha",  # Registered to Aarav Sharma
            action="View Fares",
            amount=0.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule"], "R1")
        self.assertIn("registered to customer 'Aarav Sharma'", res["reason"])

    # -------------------------------------------------------------------------
    # TEST CASE 2: Revoked Agent -> BLOCKED (Rule R2)
    # -------------------------------------------------------------------------
    def test_tc2_revoked_agent_blocked_r2(self):
        """Test Case 2: Revoked agent must be BLOCKED with Rule R2."""
        res = evaluate_request(
            customer_name="Priya Patel",
            agent_name="SkyRevoked-Bot",
            action="View Fares",
            amount=0.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule"], "R2")
        self.assertIn("revoked on 2026-11-19 18:45:12", res["reason"])

    # -------------------------------------------------------------------------
    # TEST CASE 3: Unauthorized Action -> BLOCKED (Rule R3)
    # -------------------------------------------------------------------------
    def test_tc3_unauthorized_action_blocked_r3(self):
        """Test Case 3: Action not in permitted list must be BLOCKED with Rule R3."""
        res = evaluate_request(
            customer_name="Rohan Verma",
            agent_name="FareWatcher-AI",  # Only has 'View Fares'
            action="Book",
            amount=4500.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule"], "R3")
        self.assertIn("not authorized to perform 'Book'", res["reason"])

    # -------------------------------------------------------------------------
    # TEST CASE 4: Authorized Fare Viewing -> ALLOWED (Rule R4)
    # -------------------------------------------------------------------------
    def test_tc4_authorized_fare_viewing_allowed_r4(self):
        """Test Case 4: Authorized View Fares query must be ALLOWED with Rule R4."""
        res = evaluate_request(
            customer_name="Aarav Sharma",
            agent_name="IndiGoBot-Alpha",
            action="View Fares",
            amount=0.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res["decision"], "ALLOW")
        self.assertEqual(res["rule"], "R4")
        self.assertIn("read-only inquiry", res["reason"])

    # -------------------------------------------------------------------------
    # TEST CASE 5: Authorized Booking <= ₹10,000 -> ALLOWED (Rule R5)
    # -------------------------------------------------------------------------
    def test_tc5_booking_under_or_equal_10k_allowed_r5(self):
        """Test Case 5: Authorized booking <= ₹10,000 must be ALLOWED with Rule R5."""
        # Test ₹7,500
        res = evaluate_request(
            customer_name="Aarav Sharma",
            agent_name="IndiGoBot-Alpha",
            action="Book",
            amount=7500.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res["decision"], "ALLOW")
        self.assertEqual(res["rule"], "R5")
        self.assertIn("within the autonomous threshold", res["reason"])

        # Test exact boundary at ₹10,000
        res_exact = evaluate_request(
            customer_name="Aarav Sharma",
            agent_name="IndiGoBot-Alpha",
            action="Book",
            amount=10000.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res_exact["decision"], "ALLOW")
        self.assertEqual(res_exact["rule"], "R5")

    # -------------------------------------------------------------------------
    # TEST CASE 6: Authorized Booking > ₹10,000 -> ASK CUSTOMER (Rule R6)
    # -------------------------------------------------------------------------
    def test_tc6_booking_over_10k_ask_customer_r6(self):
        """Test Case 6: Authorized booking > ₹10,000 requires ASK CUSTOMER with Rule R6."""
        # Test ₹10,001 (boundary + 1)
        res_boundary = evaluate_request(
            customer_name="Ananya Iyer",
            agent_name="TravelMate-6E",
            action="Book",
            amount=10001.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res_boundary["decision"], "ASK CUSTOMER")
        self.assertEqual(res_boundary["rule"], "R6")
        self.assertIn("exceeds the ₹10,000.00 autonomous limit", res_boundary["reason"])

        # Test ₹16,800
        res_high = evaluate_request(
            customer_name="Ananya Iyer",
            agent_name="TravelMate-6E",
            action="Book",
            amount=16800.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res_high["decision"], "ASK CUSTOMER")
        self.assertEqual(res_high["rule"], "R6")

    # -------------------------------------------------------------------------
    # BONUS TEST CASE 7: Authorized Changes and Refunds -> ASK CUSTOMER (Rule R7)
    # -------------------------------------------------------------------------
    def test_tc7_change_and_refund_ask_customer_r7(self):
        """Test Rule R7: Authorized Change and Refund actions require ASK CUSTOMER."""
        # Test Change
        res_change = evaluate_request(
            customer_name="Ananya Iyer",
            agent_name="TravelMate-6E",
            action="Change",
            amount=1200.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res_change["decision"], "ASK CUSTOMER")
        self.assertEqual(res_change["rule"], "R7")

        # Test Refund
        res_refund = evaluate_request(
            customer_name="Ananya Iyer",
            agent_name="TravelMate-6E",
            action="Refund",
            amount=5000.0,
            agents_registry=self.sample_registry
        )
        self.assertEqual(res_refund["decision"], "ASK CUSTOMER")
        self.assertEqual(res_refund["rule"], "R7")

    # -------------------------------------------------------------------------
    # REVOCATION INTEGRITY: Revoked agent cannot do ANY action
    # -------------------------------------------------------------------------
    def test_revoked_agent_cannot_do_any_action(self):
        """Verify that a revoked agent cannot View Fares, Book, Change, or Refund."""
        for act in ["View Fares", "Book", "Change", "Refund"]:
            res = evaluate_request(
                customer_name="Priya Patel",
                agent_name="SkyRevoked-Bot",
                action=act,
                amount=500.0,
                agents_registry=self.sample_registry
            )
            self.assertEqual(res["decision"], "BLOCK")
            self.assertEqual(res["rule"], "R2")


class TestStorageSystem(unittest.TestCase):
    """Unit tests for JSON storage operations."""

    def test_sample_agents_loading(self):
        """Ensure sample agents load properly."""
        agents = storage.load_agents()
        self.assertIsInstance(agents, list)
        self.assertGreaterEqual(len(agents), 1)

    def test_sample_audit_loading(self):
        """Ensure sample audit logs load properly."""
        logs = storage.load_audit_log()
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 1)

    def test_type_annotations_validity(self):
        """Verify that all type annotations in storage and gatekeeper_engine evaluate without NameError."""
        import inspect
        for mod in [storage, gatekeeper_engine]:
            for name, obj in inspect.getmembers(mod):
                if inspect.isfunction(obj):
                    # Should not raise NameError (e.g. 'Tuple')
                    hints = inspect.get_annotations(obj)
                    self.assertIsInstance(hints, dict)

    def test_register_and_revoke_agent_flow(self):
        """Test agent registration and revocation returning proper tuple structures."""
        test_agent_name = "UnitTestingBot-99"
        # Register agent
        success, msg, agent_rec = storage.register_agent(
            customer_name="Test Passenger",
            agent_name=test_agent_name,
            permitted_actions=["View Fares", "Book"]
        )
        self.assertTrue(success)
        self.assertIsNotNone(agent_rec)
        self.assertEqual(agent_rec["agent_name"], test_agent_name)
        self.assertEqual(agent_rec["status"], "ACTIVE")

        # Revoke agent
        rev_success, rev_msg = storage.revoke_agent(test_agent_name)
        self.assertTrue(rev_success)
        self.assertIn("REVOKED", rev_msg)

        # Cleanup test agent from storage so sample data remains pristine
        agents = storage.load_agents()
        agents = [a for a in agents if a.get("agent_name") != test_agent_name]
        storage.save_agents(agents)


if __name__ == "__main__":
    unittest.main()
