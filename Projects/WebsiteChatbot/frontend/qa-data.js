/**
 * qa-data.js — Predefined Q&A content for Pradeep's website chatbot.
 *
 * To update: edit answers here and re-deploy the static files to cPanel.
 * No server restart, no LLM, no API calls needed.
 */

window.QA_DATA = {
  greeting: "Hi! I'm Pradeep's assistant. Tap a question below to learn about his background, work, and how to connect.",

  categories: [
    {
      label: "Background & Experience",
      questions: [
        {
          q: "Tell me about Pradeep's background",
          a: "Pradeep Nair is a Senior Product Manager at PayPal with 18+ years of experience in fintech and payments. He specialises in Alternative Payment Methods (LPM), BNPL, Digital Wallets, Banking infrastructure, and Credit Cards.\n\nHe has led cross-functional teams of engineers, designers, and compliance specialists delivering payment products at global scale — reducing settlement risk, improving conversion, and opening new international markets."
        },
        {
          q: "What companies has he worked at?",
          a: "Pradeep's career spans major financial institutions and tech companies:\n\n• PayPal (current) — Senior PM, Payments\n• JPMorgan Chase — Product leadership in payments\n• Fidelity Investments — Financial product management\n• USAA — Banking and payments products\n• H-E-B — Enterprise systems, Supply Chain, AR/AP (2006–2015)\n\nHe is based in Austin, TX."
        },
        {
          q: "What does he specialise in?",
          a: "Pradeep's core domain expertise:\n\n• Alternative Payment Methods (LPM) — Alipay, GrabPay, UPI, PIX, SEPA, iDEAL\n• BNPL — Klarna, Afterpay, Zip\n• Digital Wallets & Banking infrastructure\n• ACH processing (domestic & international, multi-rail)\n• Credit Card platforms — onboarding, conversion, issuing\n• AI product management & tooling\n• ISO 20022 / SWIFT cross-border payments\n• Compliance-ready product launches across global markets"
        }
      ]
    },
    {
      label: "Case Studies",
      questions: [
        {
          q: "Tell me about the ACH Global Launch",
          a: "Pradeep led the ACH Global Launch at PayPal — designing and shipping a multi-rail ACH processing engine for international payments.\n\nKey results:\n• Settlement success: 75% → 93% first-attempt\n• Operational incidents: ↓ 32%\n• Transaction volume: ↑ 40% in 6 months\n• Customer satisfaction: 97% score\n• $12M additional annual revenue\n• 4 new international markets entered\n• 99.97% platform uptime in first 6 months\n\nThe project was first-to-market with a multi-rail ACH solution and involved leading 15+ engineers, designers, and compliance specialists."
        },
        {
          q: "Tell me about the Credit Card Redesign",
          a: "Pradeep led a full redesign of the Credit Card application platform — focused on streamlining onboarding and improving conversion.\n\nKey results:\n• Application conversion: ↑ 28%\n• Abandonment rate: ↓ 60%\n• Application time: 18 min → 7 min\n• Mobile conversion: 25% → 68%\n• Customer satisfaction: ↑ 35%\n• Support ticket volume: ↓ 50%\n• $8.5M additional annual revenue\n• $1.2M annual cost savings\n• Mobile Lighthouse score: 95+"
        },
        {
          q: "Tell me about the APM Integration",
          a: "Pradeep led the Alternative Payment Methods (APM) Integration — expanding payment options across global regions through strategic partnerships.\n\nCoverage added:\n• Europe: SEPA, iDEAL, Sofort, Bancontact, Giropay\n• Asia-Pacific: Alipay, WeChat Pay, GrabPay, PayNow, UPI, FPX\n• Americas: PIX, OXXO, Boleto Bancário, PSE\n• BNPL: Klarna, Afterpay, Zip\n\nKey results:\n• Market reach: ↑ 45%\n• International transactions: ↑ 62%\n• Payment failure rates: ↓ 23%\n• Customer acquisition: ↑ 38% in target markets\n• $18.2M additional annual revenue\n• 150,000+ new international customers\n• 8 new markets entered"
        }
      ]
    },
    {
      label: "Skills & Expertise",
      questions: [
        {
          q: "What payment methods has he worked with?",
          a: "Pradeep has hands-on product experience across a wide range of payment rails:\n\n• Bank Transfers: ACH (US & international), SEPA, PIX, UPI, FPX, PayNow\n• Digital Wallets: Alipay, WeChat Pay, GrabPay, Apple Pay\n• Cards: Credit card platforms, card acquiring, card issuing\n• BNPL: Klarna, Afterpay, Zip\n• Cash & Vouchers: OXXO, Boleto Bancário\n• European LPMs: iDEAL, Sofort, Bancontact, Giropay, PSE\n• ISO 20022 / SWIFT cross-border rails"
        },
        {
          q: "Does he have AI product experience?",
          a: "Yes — Pradeep actively builds AI-powered tools alongside his day job:\n\n• PradOS — A personal AI operating system built with Claude Code for managing work, projects, and knowledge workflows\n• Career Bot — An AI agent that matches job descriptions against his resume and surfaces relevant news\n• DailyBrief — Automated news digest using Claude + Brave Search, delivered daily by email\n• This chatbot — Built for pradeepunair.me using static Q&A (no LLM cost!)\n\nHe holds a Generative AI certification and is exploring the Claude Agent SDK for multi-agent workflows."
        }
      ]
    },
    {
      label: "Get in Touch",
      questions: [
        {
          q: "How can I contact Pradeep?",
          a: "The best way to reach Pradeep is via email:\n\n📧 pradeepunair@gmail.com\n\nYou can also connect on:\n• LinkedIn: linkedin.com/in/pradeep-u-nair/\n• GitHub: github.com/pradeepunair\n\nHe's based in Austin, TX (US Central time) and typically responds within 24 hours."
        },
        {
          q: "Is he open to new opportunities?",
          a: "Yes! Pradeep is actively exploring Director and Senior PM roles in:\n\n• Fintech & Payments companies\n• AI-adjacent product roles\n• Finance, Banking & embedded finance platforms\n\nHe brings 18+ years in payments, a strong track record with quantified results across ACH, Credit Cards, and APM — and a passion for building scalable financial products at global scale.\n\nReach out at pradeepunair@gmail.com to start a conversation."
        }
      ]
    }
  ]
};
