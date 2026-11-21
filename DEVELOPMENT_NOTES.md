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
Testing Notes

The application was tested using seven live test scenarios.

Results:
- Unknown agent: BLOCK
- Revoked agent: BLOCK
- Unauthorized action: BLOCK
- Authorized fare viewing: ALLOW
- Booking within limit: ALLOW
- Booking above limit: ASK CUSTOMER
- Refund request: ASK CUSTOMER

All seven displayed test scenarios passed.
