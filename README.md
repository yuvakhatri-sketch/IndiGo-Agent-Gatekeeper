# ✈️ Agent Gatekeeper for IndiGo Airlines

**Student Enrolment Number:** `PGD202572730`  
**Project Title:** Agent Gatekeeper for IndiGo Airlines  
**Technology Stack:** Python 3, Streamlit, JSON  

---

## 📌 Project Overview

**Agent Gatekeeper for IndiGo Airlines** is a cybersecurity and autonomous AI governance system designed to evaluate and regulate actions attempted by AI travel agents acting on behalf of IndiGo Airlines passengers.

Before an AI agent can view fares, make bookings, modify flights, or process refunds, it must pass through the **IndiGo Agent Gatekeeper Decision Engine**. The engine strictly enforces seven security and business rules to safeguard passengers against unauthorized actions, unintended financial charges, and unauthorized itinerary changes.

> **Important Security Principles:**
> 1. **Order of Evaluation:** Always check whether an agent is registered and revoked before evaluating any other permissions.
> 2. **Revocation Immutability:** A revoked agent must **never** be allowed to perform any action.
> 3. **Human-in-the-Loop (`ASK CUSTOMER`):** `ASK CUSTOMER` means explicit customer confirmation is required; the transaction is held in review and **never** executed automatically.
> 4. **Safe Sandbox:** Uses sample data only; does **not** connect to live IndiGo booking, PNR, or payment systems.

---

## 🏛️ The Seven Security Rules

| Rule | Condition | Decision | Explanation |
| :--- | :--- | :---: | :--- |
| **R1** | Unknown agent or customer mismatch | `BLOCK` | Unregistered agents or unauthorized customer associations are blocked immediately. |
| **R2** | Revoked agent | `BLOCK` | Agents revoked by customers can never act again. Exact revocation timestamp is preserved. |
| **R3** | Unauthorized action | `BLOCK` | If the requested action is not in the agent's permitted actions, the request is rejected. |
| **R4** | Authorized fare viewing | `ALLOW` | "View Fares" is a safe, read-only operational query cleared for autonomous execution. |
| **R5** | Authorized booking $\le$ ₹10,000 | `ALLOW` | Routine bookings within the ₹10,000 threshold are autonomously approved. |
| **R6** | Authorized booking $>$ ₹10,000 | `ASK CUSTOMER` | High-value transactions exceed the autonomous limit and require passenger approval. |
| **R7** | Authorized change or refund | `ASK CUSTOMER` | Modifications and cancellations directly impact travel itineraries and require passenger consent. |

---

## 📁 Project Directory Structure

```text
AgentGatekeeper/
├── app.py                  # Main Streamlit web application with IndiGo UI
├── gatekeeper_engine.py    # Core 7-rule decision engine
├── storage.py              # Persistent JSON storage for agents and audit logs
├── test_gatekeeper.py      # Automated unit test suite (11 unit tests)
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation and guide
└── data/
    ├── agents.json         # Persistent JSON registry of active & revoked agents
    └── audit_log.json      # Persistent JSON audit trail of all evaluated requests
```

---

## 🚀 How to Run the Application

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Set Up a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Web Application

```bash
streamlit run app.py
```

The web dashboard will automatically open in your default browser at:  
👉 **`http://localhost:8501`**

---

## 🧪 Automated Testing

To run the automated unit test suite covering all seven rules, edge cases, revocation immutability, and boundary conditions:

```bash
python3 -m unittest test_gatekeeper.py -v
```

All 11 automated test cases pass with 0 errors.

---

## 📋 The Six Official College Test Cases

The application includes an interactive test runner in the **"🧪 Test Cases & Verification"** tab:

| Test ID | Test Scenario | Inputs | Expected Decision | Expected Rule | Actual Result |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **TC-01** | Unknown Agent | Agent: `PhantomBot-99`, Action: `Book`, Amount: ₹5,000 | `BLOCK` | **R1** | PASS ✅ |
| **TC-02** | Revoked Agent | Agent: `SkyRevoked-Bot`, Action: `View Fares`, Amount: ₹0 | `BLOCK` | **R2** | PASS ✅ |
| **TC-03** | Unauthorized Action | Agent: `FareWatcher-AI`, Action: `Book`, Amount: ₹4,500 | `BLOCK` | **R3** | PASS ✅ |
| **TC-04** | Authorized Fare Viewing | Agent: `IndiGoBot-Alpha`, Action: `View Fares`, Amount: ₹0 | `ALLOW` | **R4** | PASS ✅ |
| **TC-05** | Authorized Booking ($\le$ ₹10,000) | Agent: `IndiGoBot-Alpha`, Action: `Book`, Amount: ₹7,500 | `ALLOW` | **R5** | PASS ✅ |
| **TC-06** | Authorized Booking ($>$ ₹10,000) | Agent: `TravelMate-6E`, Action: `Book`, Amount: ₹16,800 | `ASK CUSTOMER` | **R6** | PASS ✅ |
| **TC-07** | Authorized Change / Refund | Agent: `TravelMate-6E`, Action: `Refund`, Amount: ₹4,200 | `ASK CUSTOMER` | **R7** | PASS ✅ |

---

## 💡 Key Features of the Web Application

1. **Gatekeeper Evaluation Form:**
   - Quick-load buttons for all evaluation scenarios.
   - Clean, professional IndiGo 6E airline boarding pass style clearance card.
   - Distinct visual states: Green for `ALLOW`, Amber for `ASK CUSTOMER`, Red for `BLOCK`.
2. **AI Agent Registry:**
   - Register new agents with custom permitted actions (`View Fares`, `Book`, `Change`, `Refund`).
   - One-click immediate revocation with automatic timestamp stamping.
   - Live searchable tables of Active and Revoked agents.
3. **Security Audit Log:**
   - Real-time audit history of every transaction attempt.
   - Filterable by Decision, Rule Number, or Customer/Agent name.
   - One-click JSON download for reporting and compliance inspection.
4. **Interactive Test Runner:**
   - One-click **"Run All Test Cases Live"** button with automated verification and pass/fail badges.
5. **Prominent Student Identity:**
   - Student Enrolment Number **`PGD202572730`** displayed prominently in the top header, sidebar, and submission cards.

---

## 📜 Academic Integrity & Disclaimer
- This project was developed as a college assignment.
- All airline data, agent identifiers, and passenger records are simulated sample data.
- No live connections to IndiGo Airlines production APIs or real financial gateways are made.
- ---

## Security Rules and Decision Logic

The Gatekeeper follows seven rules:

| Rule | Condition | Decision |
|---|---|---|
| R1 | Unknown agent | BLOCK |
| R2 | Revoked agent | BLOCK |
| R3 | Unauthorized action | BLOCK |
| R4 | Authorized fare viewing | ALLOW |
| R5 | Booking up to ₹10,000 | ALLOW |
| R6 | Booking above ₹10,000 | ASK CUSTOMER |
| R7 | Authorized change or refund | ASK CUSTOMER |

### Spending Limit

The ₹10,000 threshold is an illustrative limit selected for this prototype. It allows routine lower-value bookings while requiring customer confirmation for higher-value transactions. It is not an official IndiGo policy.

### Prototype Limitation

All records and transactions use sample data. The prototype does not connect to live airline booking or payment systems.
---

## Customer Confirmation Process

When the system returns ASK CUSTOMER, the requested action is not automatically executed.

1. The customer is asked to review the requested action and amount.
2. The customer can approve or reject the request.
3. The decision must be recorded in the audit trail.
4. If the customer does not approve, the action remains unexecuted.

This human-in-the-loop process helps prevent unintended bookings, refunds, and financial transactions.
