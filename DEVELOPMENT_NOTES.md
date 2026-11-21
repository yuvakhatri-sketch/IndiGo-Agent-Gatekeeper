 Development Notes

Project
Agent Gatekeeper for IndiGo Airlines

Development Summary
The prototype was built using Python and Streamlit.
It evaluates requests made by registered AI agents
and returns ALLOW, ASK CUSTOMER, or BLOCK.

Security Decisions
- Unknown agents are blocked.
- Revoked agents are blocked.
- Unauthorized actions are blocked.
- Authorized fare viewing is allowed.
- Bookings above ₹10,000 require customer confirmation.
- Authorized changes and refunds require customer confirmation.

 Verification
The live application test runner displayed 7 out of 7
test cases passed.

The automated unit tests were also run during development.

Limitation
This is a demonstration prototype using sample data.
It does not connect to IndiGo's live booking or payment systems.
