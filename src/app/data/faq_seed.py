# src/app/data/faq_seed.py

from typing import List, Dict

FAQ_ENTRIES: List[Dict] = [
    # ========== Account & Registration ==========
    {
        "id": "acc-001",
        "category": "Account & Registration",
        "question": "How do I create a new account?",
        "answer": "Open the app or website, select Sign Up, enter your email, create a password, and verify your email via the code sent to your inbox."
    },
    {
        "id": "acc-002",
        "category": "Account & Registration",
        "question": "I didn’t receive a verification email. What should I do?",
        "answer": "Check spam/promotions folders, add our domain to your safe list, and request a new code from the login screen."
    },
    {
        "id": "acc-003",
        "category": "Account & Registration",
        "question": "Can I change my email after registering?",
        "answer": "Yes. Go to Settings → Account → Email, enter the new email, and confirm it with the verification link."
    },
    {
        "id": "acc-004",
        "category": "Account & Registration",
        "question": "How do I delete my account?",
        "answer": "Navigate to Settings → Privacy → Delete Account. You’ll receive a confirmation email. Deletion is permanent after 7 days."
    },

    # ========== Payments & Transactions ==========
    {
        "id": "pay-001",
        "category": "Payments & Transactions",
        "question": "Which payment methods are supported?",
        "answer": "We accept major credit/debit cards, Apple Pay/Google Pay (where available), and selected local wallets."
    },
    {
        "id": "pay-002",
        "category": "Payments & Transactions",
        "question": "My card was charged twice. How do I get a refund?",
        "answer": "Open a ticket in Help → Billing. Duplicate charges are auto-reversed within 3–5 business days after review."
    },
    {
        "id": "pay-003",
        "category": "Payments & Transactions",
        "question": "How can I download my invoices?",
        "answer": "Go to Settings → Billing → Invoices and select the month. You can download PDFs for your records."
    },
    {
        "id": "pay-004",
        "category": "Payments & Transactions",
        "question": "The payment failed. What should I try?",
        "answer": "Verify card details, ensure sufficient funds, enable international/online transactions, and try a different method if needed."
    },

    # ========== Security & Fraud Prevention ==========
    {
        "id": "sec-001",
        "category": "Security & Fraud Prevention",
        "question": "How do I enable two-factor authentication (2FA)?",
        "answer": "Go to Settings → Security → Two-Factor and pair an authenticator app or enable SMS codes."
    },
    {
        "id": "sec-002",
        "category": "Security & Fraud Prevention",
        "question": "I suspect unauthorized access. What should I do?",
        "answer": "Reset your password immediately, revoke active sessions (Settings → Security → Sessions), and enable 2FA."
    },
    {
        "id": "sec-003",
        "category": "Security & Fraud Prevention",
        "question": "What is your policy on phishing attempts?",
        "answer": "We never ask for passwords or 2FA codes. Report suspicious emails via Help → Report Phishing with full headers."
    },
    {
        "id": "sec-004",
        "category": "Security & Fraud Prevention",
        "question": "How are my data and payments protected?",
        "answer": "We use TLS 1.2+, encryption at rest, tokenized payments, and periodic third-party security audits."
    },

    # ========== Regulations & Compliance ==========
    {
        "id": "reg-001",
        "category": "Regulations & Compliance",
        "question": "How do you comply with GDPR/CCPA requests?",
        "answer": "Users can request data export/deletion via Settings → Privacy. We process verified requests within statutory timelines."
    },
    {
        "id": "reg-002",
        "category": "Regulations & Compliance",
        "question": "Where are your data centers located?",
        "answer": "We use regional cloud providers with data residency options. See Settings → Privacy → Data Residency for regions."
    },
    {
        "id": "reg-003",
        "category": "Regulations & Compliance",
        "question": "How long do you retain personal data?",
        "answer": "We keep data only as long as necessary for service and legal obligations. Retention varies by category and jurisdiction."
    },
    {
        "id": "reg-004",
        "category": "Regulations & Compliance",
        "question": "How can I obtain a Data Processing Agreement (DPA)?",
        "answer": "Business customers can request a signed DPA via Help → Legal → DPA Request."
    },

    # ========== Technical Support & Troubleshooting ==========
    {
        "id": "tech-001",
        "category": "Technical Support & Troubleshooting",
        "question": "The app won’t load. What are the first steps?",
        "answer": "Force-quit, clear cache, check connectivity/VPN, and ensure you’re on the latest version."
    },
    {
        "id": "tech-002",
        "category": "Technical Support & Troubleshooting",
        "question": "I’m getting frequent timeouts.",
        "answer": "Check network stability, disable aggressive firewalls, and try switching from mobile data to Wi-Fi (or vice-versa)."
    },
    {
        "id": "tech-003",
        "category": "Technical Support & Troubleshooting",
        "question": "How do I report a bug with logs?",
        "answer": "Go to Help → Report a Bug and enable diagnostic logs. Attach screenshots and exact steps to reproduce."
    },
    {
        "id": "tech-004",
        "category": "Technical Support & Troubleshooting",
        "question": "Push notifications aren’t arriving.",
        "answer": "Enable notifications for the app in OS settings, disable battery optimization, and ensure you’re logged in on one device."
    },
]
