# RAGScore Landing Page - AI Generation Brief

## 🎯 Project Overview

**Product Name:** RAGScore  
**Tagline:** "Evaluate Your RAG System in Minutes, Not Months"  
**URL:** ragscore.dev (or ragscore.ai)  
**Type:** SaaS landing page with waitlist  

---

## 📋 Product Description

RAGScore is a two-part toolkit for evaluating RAG (Retrieval-Augmented Generation) systems:

- **Part 1 (Free, Open Source):** Automatically generates high-quality QA test pairs from your documents
- **Part 2 (Paid SaaS):** Evaluates your RAG system's responses using LLM-as-judge methodology with multi-dimensional scoring

**Problem it solves:** Developers build RAG systems but have no easy way to know if they actually work well. Manual testing is slow, inconsistent, and doesn't scale.

**Target Users:** 
- AI/ML Engineers building RAG applications
- Backend developers implementing LLM features
- Startups with AI-powered products
- Enterprise teams evaluating RAG solutions

---

## 🏗️ Page Structure

### Section 1: Hero
```
Layout: Full-width, centered
Background: Gradient (deep blue to purple) or subtle animated grid

Headline: "Evaluate Your RAG System in Minutes"
Subheadline: "Generate test datasets and score your RAG responses automatically. 
             Stop guessing if your AI actually works."

CTA Button (Primary): "Join the Waitlist" → Opens email capture modal
CTA Button (Secondary): "View on GitHub" → Links to GitHub repo

Visual: Animated diagram showing:
Document → QA Pairs → RAG System → Score (85/100)

Trust badges below CTAs:
- "🔓 Open Source Core"
- "🤖 Works with ANY LLM"
- "🏠 Local LLM Support (Ollama)"
- "⭐ 500+ GitHub Stars" (placeholder)
```

### Section 2: Problem Statement
```
Layout: Two columns (text left, visual right)

Headline: "Building RAG is Easy. Knowing if it Works is Hard."

Pain points (with icons):
❌ "Manual testing doesn't scale"
❌ "No standardized evaluation metrics"
❌ "Hard to catch hallucinations"
❌ "Can't measure improvement over time"

Visual: Frustrated developer meme or illustration
```

### Section 3: Solution / How It Works
```
Layout: Three-step horizontal flow

Headline: "From Documents to Quality Score in 3 Steps"

Step 1: "Upload Documents"
- Icon: 📄
- Description: "Drop your PDFs, docs, or markdown files"
- Supported: PDF, TXT, MD, HTML

Step 2: "Generate Test QA Pairs"  
- Icon: 🤖
- Description: "AI creates challenging questions with verified answers"
- Feature: "Easy, Medium, Hard difficulty levels"

Step 3: "Score Your RAG"
- Icon: 📊
- Description: "Get accuracy, relevance, and completeness scores"
- Feature: "Detect hallucinations automatically"

Visual: Animated flow diagram or GIF showing the process
```

### Section 4: Features Grid
```
Layout: 2x3 or 3x2 grid of feature cards

Features:

1. "Multi-Format Support"
   Icon: 📁
   Description: "PDF, TXT, Markdown, HTML - we handle it all"

2. "Difficulty Levels"
   Icon: 🎯
   Description: "Generate easy, medium, and hard questions to stress-test your RAG"

3. "Multi-Dimensional Scoring"
   Icon: 📈
   Description: "Accuracy, Relevance, Completeness - know exactly where you fail"

4. "Hallucination Detection"
   Icon: 🔍
   Badge: "Pro"
   Description: "Catch when your RAG makes things up"

5. "Citation Quality"
   Icon: 📝
   Badge: "Pro"
   Description: "Verify your RAG cites sources correctly"

6. "Export Reports"
   Icon: 📋
   Badge: "Pro"
   Description: "Excel reports for stakeholders and compliance"
```

### Section 5: Pricing Preview
```
Layout: Three pricing cards

Headline: "Simple, Developer-Friendly Pricing"
Subheadline: "Start free, scale as you grow"

Tier 1: FREE
- Price: "$0/forever"
- Description: "Open Source"
- Features:
  ✅ QA pair generation
  ✅ Unlimited documents
  ✅ CLI + Web UI
  ✅ Use ANY LLM provider (OpenAI, Claude, Groq, Grok, Mistral, etc.)
  ✅ Ollama support (free local LLMs!)
  ✅ Custom endpoint support
  ✅ Community support
- CTA: "Get Started" → GitHub

Tier 2: PRO (Highlighted/Recommended)
- Price: "$49/month"
- Badge: "Most Popular"
- Description: "For serious RAG builders"
- Features:
  ✅ Everything in Free
  ✅ 1,000 evaluations/month
  ✅ Hallucination detection
  ✅ Citation quality scoring
  ✅ Excel reports
  ✅ API access
  ✅ Email support
- CTA: "Join Waitlist" → Email capture

Tier 3: ENTERPRISE
- Price: "Custom"
- Description: "For teams at scale"
- Features:
  ✅ Everything in Pro
  ✅ Unlimited evaluations
  ✅ Custom metrics
  ✅ SSO/SAML
  ✅ Dedicated support
  ✅ On-premise option
- CTA: "Contact Us" → Contact form
```

### Section 6: Code Example / Demo
```
Layout: Split screen - code left, output right

Headline: "Developer-First Experience"

Code snippet (Python):
```python
from ragscore import run_pipeline
from ragscore.assessment import RAGAssessment

# Generate QA pairs from your docs
run_pipeline(docs_dir="./knowledge_base")

# Evaluate your RAG endpoint
assessment = RAGAssessment(endpoint="http://your-rag/query")
results = assessment.run()

print(f"Overall Score: {results.score}/100")
print(f"Hallucinations: {results.hallucination_count}")
```

Output visualization:
┌─────────────────────────────┐
│ RAG Assessment Results      │
├─────────────────────────────┤
│ Overall Score:    87/100    │
│ Accuracy:         92/100    │
│ Relevance:        85/100    │
│ Completeness:     84/100    │
│ Hallucinations:   2 found   │
└─────────────────────────────┘
```

### Section 7: Social Proof (Optional - for later)
```
Layout: Testimonial cards or logo grid

Headline: "Trusted by AI Teams"

Placeholder testimonials:
- "RAGScore cut our evaluation time from days to minutes" - CTO, AI Startup
- "Finally, a way to measure RAG quality objectively" - ML Engineer
- "The hallucination detection alone is worth it" - Senior Developer

Company logos: [Placeholder grid]
```

### Section 8: FAQ
```
Layout: Accordion style

Questions:

Q: "Is the open source version really free?"
A: "Yes! Part 1 (QA generation) is MIT licensed and free forever. We make money from the advanced evaluation features in Part 2."

Q: "What LLM providers do you support?"
A: "All major providers! OpenAI, Anthropic (Claude), Groq, Together AI, Grok (xAI), Mistral, DeepSeek, DashScope (Qwen), and any OpenAI-compatible API. You can also use Ollama for free local inference - no API key needed!"

Q: "How accurate is the evaluation?"
A: "We use LLM-as-judge methodology with multi-dimensional scoring. Our benchmarks show 90%+ correlation with human evaluation."

Q: "Can I self-host the SaaS version?"
A: "Enterprise customers can request on-premise deployment. Contact us for details."

Q: "What file formats are supported?"
A: "PDF, TXT, Markdown, and HTML. More formats coming soon."
```

### Section 9: Final CTA
```
Layout: Full-width, contrasting background

Headline: "Stop Guessing. Start Measuring."
Subheadline: "Join 500+ developers on the waitlist for early access."

Email input field + Submit button
Placeholder: "Enter your email"
Button: "Get Early Access"

Below form:
"🎁 Early supporters get 50% off Pro for 6 months"

Small text: "No spam. Unsubscribe anytime."
```

### Section 10: Footer
```
Layout: Standard footer

Columns:
1. Logo + brief description
2. Product: Features, Pricing, Documentation, GitHub
3. Company: About, Blog, Contact, Careers
4. Legal: Privacy, Terms, Security

Social links: GitHub, Twitter/X, Discord, LinkedIn

Copyright: "© 2024 RAGScore. MIT Licensed (Open Source Core)."
```

---

## 🎨 Design Requirements

### Colors
```
Primary: #2563EB (Blue) or #7C3AED (Purple)
Secondary: #10B981 (Green - for success/free)
Accent: #F59E0B (Orange - for Pro badge)
Background: #0F172A (Dark) or #FFFFFF (Light)
Text: #F8FAFC (on dark) or #1E293B (on light)
```

### Typography
```
Headings: Inter, Satoshi, or Cal Sans (modern, clean)
Body: Inter or System UI
Code: JetBrains Mono or Fira Code
```

### Style
```
- Modern, clean, developer-focused
- Subtle gradients and shadows
- Code snippets with syntax highlighting
- Smooth scroll animations
- Dark mode by default (toggle optional)
- Mobile responsive
```

### Inspiration Sites
- linear.app
- vercel.com
- supabase.com
- raycast.com
- planetscale.com

---

## 💻 Technical Requirements

### Framework Options (in order of preference)
1. **Next.js + Tailwind** - Best for SEO, performance
2. **Astro + Tailwind** - Great for static landing pages
3. **Framer** - Fastest no-code option
4. **React + Vite** - Simple SPA

### Required Integrations

1. **Waitlist/Email Capture:**
   - Option A: Loops.so (recommended for SaaS)
   - Option B: ConvertKit
   - Option C: Simple API endpoint → Supabase

2. **Analytics:**
   - Plausible or Fathom (privacy-friendly)
   - PostHog for product analytics

3. **Deployment:**
   - Vercel (recommended)
   - Cloudflare Pages
   - Netlify

### SEO Requirements
```
Title: "RAGScore - Evaluate Your RAG System in Minutes"
Description: "Generate QA test datasets and score your RAG responses automatically. Open source core with advanced evaluation features."
Keywords: RAG evaluation, LLM testing, RAG benchmarking, QA generation, AI evaluation
OG Image: Create branded social share image
```

---

## 📝 Copy Bank

### Headlines (pick favorites)
- "Evaluate Your RAG System in Minutes"
- "Know If Your RAG Actually Works"
- "Stop Guessing. Start Measuring."
- "RAG Evaluation on Autopilot"
- "Test Your RAG Like a Pro"
- "From Documents to Quality Score"

### Subheadlines
- "Generate test datasets and score your RAG responses automatically."
- "The missing evaluation layer for your RAG pipeline."
- "Finally know if your AI is hallucinating."
- "Automated QA generation and multi-dimensional scoring."

### CTAs
- "Join the Waitlist"
- "Get Early Access"
- "Start Free on GitHub"
- "View Documentation"
- "See Demo"

### Value Props
- "10x faster than manual testing"
- "Catch hallucinations before your users do"
- "Objective metrics, not gut feelings"
- "Works with any RAG system"

---

## 📁 Assets Needed

### Must Have
- [ ] Logo (SVG, light and dark versions)
- [ ] Favicon
- [ ] OG Image (1200x630)
- [ ] Hero illustration or animation

### Nice to Have
- [ ] Product screenshots
- [ ] Demo video/GIF
- [ ] Feature icons
- [ ] Team photos (if showing)

---

## ✅ Acceptance Criteria

The landing page is complete when:

1. [ ] All 10 sections are implemented
2. [ ] Email capture form works (stores to database/service)
3. [ ] Mobile responsive (test on iPhone, Android)
4. [ ] Lighthouse score > 90 (Performance, SEO, Accessibility)
5. [ ] Dark mode works correctly
6. [ ] All links work (GitHub, social, etc.)
7. [ ] Analytics tracking implemented
8. [ ] Meta tags and OG images configured
9. [ ] Deployed to production URL

---

## 🚀 Quick Start for AI Agent

```
Create a modern SaaS landing page for RAGScore using:
- Next.js 14 with App Router
- Tailwind CSS
- Framer Motion for animations
- Dark mode default

Key sections:
1. Hero with waitlist CTA
2. Problem statement
3. 3-step how it works
4. Features grid (6 features)
5. Pricing (Free/Pro/Enterprise)
6. Code example
7. FAQ accordion
8. Final CTA with email capture
9. Footer

Design: Dark theme, blue/purple gradients, similar to linear.app

Waitlist: Store emails to Supabase table or use Loops.so API
```

---

## 📧 Waitlist Email Sequence (Bonus)

**Email 1: Welcome (Immediate)**
```
Subject: You're on the RAGScore waitlist! 🎉

Hey {name},

Thanks for joining the RAGScore waitlist!

While you wait, you can already use the free open source version:
→ GitHub: [link]

What's coming in the paid version:
- Hallucination detection
- Citation quality scoring  
- Excel reports
- API access

I'll email you as soon as we launch (targeting [date]).

- [Your name]
```

**Email 2: Value (Day 3)**
```
Subject: How to evaluate your RAG (before RAGScore launches)

Quick tip while you wait...
[Educational content about RAG evaluation]
```

**Email 3: Launch (When ready)**
```
Subject: RAGScore Pro is LIVE (your 50% discount inside)

The wait is over! Use code EARLY50 for 50% off your first 6 months.
→ [Link to sign up]
```
