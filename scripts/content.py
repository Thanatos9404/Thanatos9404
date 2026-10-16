"""Everything the README says, in one place.

Edit this file, then run:

    python scripts/build.py      # static SVGs
    python scripts/readme.py     # README.md (keeps the live PR list)
    python scripts/refresh.py    # live PR wall, skyline, PR list (needs a GitHub token)

House rules: only verified facts, first person, no em or en dashes, never mention
an SIH 2024 finalist result (it is not true).
"""

# Scrolling achievements strip at the bottom of the hero. Uppercase, short.
TICKER = [
    "VBYLD 2026 · RAJASTHAN RANK 1",
    "NASA SPACE APPS 2025 · GLOBAL NOMINEE",
    "DRDO · SAG RESEARCH INTERN",
    "IETE ENGINEERS' DAY 2026 · 1ST PLACE",
    "LLMSLIM · 14 STARTUP PROGRAMS",
    "PRODUCT HUNT · #11 OF THE DAY",
    "PRS MERGED AT NVIDIA, AWS LABS, IBM, OPENTELEMETRY",
    "AWS STUDENT BUILDER GROUP LEADER",
]

HERO_CHIPS = ["Python", "RAG + agents", "Open source", "BIT Mesra"]

# Plain-HTML intro paragraph under the link buttons.
INTRO = (
    "I'm a final-year BCA student at BIT Mesra, Jaipur, and the founder of "
    '<a href="https://www.llmslim.app"><b>LLMSlim</b></a>, open source context infrastructure for AI agents, '
    'built under my studio <a href="https://ameyor.in"><b>AMEYOR</b></a>. '
    "Most recently I was an AI/ML research intern at DRDO's Scientific Analysis Group. "
    "I also take on <b>freelance work</b>: Python backends, retrieval systems, AI features, and getting a "
    "prototype into someone's hands."
)

LINKS = [  # (href, asset name, label, arrow, primary)
    ("https://calendly.com/yashvt9404/30min", "l-call", "Book a call", "↗", True),
    ("https://www.yashvardhan.tech", "l-portfolio", "Portfolio", "↗", False),
    ("https://www.llmslim.app", "l-llmslim", "LLMSlim", "↗", False),
    ("https://www.linkedin.com/in/yashvardhanthanvi", "l-linkedin", "LinkedIn", "↗", False),
    ("mailto:yashvt9404@gmail.com", "l-email", "Email", "↗", False),
    ("https://www.yashvardhan.tech/Yashvardhan-Thanvi-Resume.pdf", "l-resume", "Résumé", "↓", False),
]

LLMSLIM = {
    "eyebrow": "OPEN SOURCE  ·  MIT  ·  V0.9",
    "facts": "678 TESTS  ·  90% BRANCH COVERAGE  ·  LANGCHAIN, LLAMAINDEX, HAYSTACK, MCP",
    "tokens_in": "114,006",
    "tokens_out": "7,985",
    "stats": [  # (big, line 1, line 2) exactly four
        ("62×", "lower cost per question", "LongMemEval, Haiku 5.5"),
        ("3×", "fewer tokens, same score", "LongBench v1"),
        ("+9.7", "points over LLMLingua-2", "NaturalQuestions, 300 cases"),
        ("0.1s", "per question vs 9.3s", "vs LongLLMLingua, same score"),
    ],
    "programs": ["OpenAI", "Claude", "MongoDB", "Sarvam", "Zoho", "Auth0", "Zendesk", "Mixpanel", "Sentry",
                 "Descope", "Pulumi", "Honeycomb", "Exa", "Neo4j"],
    "links": [
        ("Website", "https://www.llmslim.app"),
        ("Docs", "https://www.llmslim.app/docs/getting-started"),
        ("Benchmarks", "https://www.llmslim.app/benchmarks"),
        ("PyPI", "https://pypi.org/project/llmslim/"),
        ("Source", "https://github.com/Thanatos9404/llmslim"),
        ("Product Hunt", "https://www.producthunt.com/products/llmslim"),
    ],
}

# Featured project cards, shown two per row (keep an even count, 6 is ideal).
# glyph: field | trace | twin | merkle | bridge | pulse
PROJECTS = [
    {
        "key": "krishyak", "repo": "Krishyak", "name": "Krishyak", "tag": "VBYLD 2026 · IETE 2026 1ST",
        "desc": "Farm decisions for Indian farmers: crop photo disease checks, a Sentinel-2 view of the field, "
                "mandi prices, schemes and Monte Carlo planning, in all 22 Indian languages.",
        "stack": ["Next.js", "FastAPI", "PostGIS", "LiteRT"], "live": True, "glyph": "field",
        "links": [("live app", "https://krishyak.vercel.app")],
    },
    {
        "key": "polygraph", "repo": "polygraph", "name": "Polygraph", "tag": "NEBIUS × NVIDIA HACKATHON",
        "desc": "Every pull request makes claims. Polygraph checks them by experiment, running base and head side "
                "by side on NVIDIA Nemotron and proving undeclared changes with a pytest witness.",
        "stack": ["Python", "FastAPI", "Nemotron", "three.js"], "live": True, "glyph": "trace",
        "links": [("live demo", "https://yvt94-polygraph.static.hf.space"), ("video", "https://youtu.be/VFzUl18uwP8")],
    },
    {
        "key": "pratibimb", "repo": "pratibimb", "name": "Pratibimb", "tag": "DIGITAL TWIN CHALLENGE 2026",
        "desc": "A physiology + ML digital twin for Type 2 diabetes in India. An EnKF-synced glucose model warns "
                "of hypos an hour ahead (AUROC 0.986) and a What-If Lab lets clinicians test plans.",
        "stack": ["Python", "FastAPI", "LightGBM", "Next.js"], "live": True, "glyph": "twin",
        "links": [("live console", "https://pratibimb-omega.vercel.app")],
    },
    {
        "key": "canopyproof", "repo": "canopyproof", "name": "CanopyProof", "tag": "IEEE CLIMATECHAIN 2026",
        "desc": "Satellite-verified integrity for forest carbon credits. Sentinel-2 change detection, signed "
                "observations anchored as Merkle roots on-chain, and an oracle that holds or retires credits.",
        "stack": ["Python", "Solidity", "Hardhat", "React"], "live": False, "glyph": "merkle",
        "links": [("video", "https://youtu.be/9FBv9KQ4Ag8")],
    },
    {
        "key": "passerelle", "repo": "passerelle", "name": "Passerelle", "tag": "HACK APERTUS 2026 · TRACK 2B",
        "desc": "An air-gapped caseworker assistant on Apertus. It explains Swiss official letters in the "
                "client's own language, with a fact lock and a back-translation gate.",
        "stack": ["FastAPI", "Next.js", "llama.cpp"], "live": False, "glyph": "bridge",
        "links": [("video", "https://youtu.be/bjc88UYdgfE")],
    },
    {
        "key": "hearthbeat", "repo": "hearthbeat", "name": "Hearthbeat", "tag": "AMAZON BUILD, SHIP, SHAPE 2026",
        "desc": "Privacy-first check-ins for older adults who live alone. Home events (never video) learn a daily "
                "rhythm, and Alexa+ checks in by voice through a self-hosted MCP server.",
        "stack": ["Python", "MCP", "SQLite", "React"], "live": False, "glyph": "pulse",
        "links": [("video", "https://youtu.be/axVTrTiKaog")],
    },
]

# One-line mentions under the cards: (name, href, short description)
ALSO = [
    ("Leash", "https://github.com/Thanatos9404/leash", "spending mandates for AI shopping agents"),
    ("StudyTwin", "https://github.com/Thanatos9404/StudyTwin", "a tutor that cites your course material"),
    ("RuleDost", "https://ruledost.vercel.app", "hackathon rules decoded"),
    ("dayrhythm", "https://github.com/Thanatos9404/dayrhythm", "a routine-learning library"),
    ("Intuix", "https://github.com/Thanatos9404/Intuix-NASA", "exoplanet detection for NASA Space Apps"),
]

RECOGNITION = {
    "feature": {
        "eyebrow": "VBYLD 2026  ·  BHARAT MANDAPAM, NEW DELHI",
        "title": [("Rajasthan ", "serif"), ("Rank 1", "serif-i")],
        "body": "National finalist at the Viksit Bharat Young Leaders Dialogue. I presented Krishyak to the Union "
                "Agriculture Minister and the DG of ICAR, and was later invited to the Chief Minister's Residence, "
                "where the CM cited my idea by name.",
        "foot": "TOP 0.0005% OF 50.49 LAKH PARTICIPANTS",
    },
    "side": {"eyebrow": "NASA SPACE APPS 2025", "title": "Global Finalist", "body": "Nominee · exoplanet detection"},
    # (big, title, detail) three per row, newest or biggest first
    "tiles": [
        ("1st", "IETE Engineers' Day 2026", "Student project competition, with Krishyak"),
        ("1st", "IETE Student's Day 2025", "Design competition, IETE Bhawan, Jaipur"),
        ("#11", "Product Hunt", "LLMSlim on its launch day"),
        ("Top 10", "HackLoop 2025", "Finalist from 1,600+ entrants, at Thoughtworks"),
        ("Final", "Polaris Fellowship 2026", "Final round, top 100 applicants"),
        ("SIH '26", "BIT Jaipur internal round", "Nominated for the next round, Krishyak"),
    ],
}

WORK = [  # (org, role, when, note)
    ("DRDO · Scientific Analysis Group", "AI/ML and software research intern", "MAY TO JUL 2026",
     "Offline RAG, policy-compliant configuration and signal analysis in air-gapped labs."),
    ("AMEYOR", "Founder", "2026 TO NOW",
     "My Jaipur studio behind LLMSlim and Krishyak. Websites, AI systems and custom software."),
    ("Olinp Technologies", "AI/ML engineering intern", "APR TO JUN 2025",
     "Preprocessing and feature engineering across 3+ production modules."),
]

LEAD = [  # (org, role, when) up to 7 rows fit
    ("AWS", "Student Builder Group Leader, BIT Jaipur", "NOW"),
    ("GeeksforGeeks", "Campus Mantri", "2026 TO NOW"),
    ("IIC, BIT Jaipur", "Head, Innovation Subcommittee", "NOW"),
    ("GDG on Campus", "Coordinator, BIT Jaipur", "2025 TO 2026"),
    ("Google", "Gemini Student Ambassador", "2025"),
    ("OnePlus", "Student Ambassador", "PAST"),
    ("GSSoC '25 · OSCI", "Open source contributor", "2025"),
]

EDUCATION = {
    "school": "BIT Mesra, Jaipur",
    "degree": "BCA in Computer Science, minor in Artificial Intelligence",
    "score": "9.35", "score_label": "CGPA", "years": "2024 TO 2027",
}

TOOLS = [  # three marquee rows
    ["Python", "TypeScript", "SQL", "C", "FastAPI", "Flask", "Next.js", "React", "Tailwind", "Node.js"],
    ["PyTorch", "TensorFlow", "scikit-learn", "Hugging Face", "LangChain", "LlamaIndex", "Haystack",
     "Ollama", "OpenAI Agents SDK", "MCP", "LightGBM"],
    ["PostgreSQL", "PostGIS", "MongoDB", "Redis", "FAISS", "Docker", "Vercel", "AWS", "Google Cloud",
     "Linux", "Git", "GitHub Actions"],
]
HOT_TOOLS = {"Python", "LangChain", "MCP", "Hugging Face"}

FOOTER_LINKS = [
    ("yashvt9404@gmail.com", "mailto:yashvt9404@gmail.com"),
    ("yashvardhan.tech", "https://www.yashvardhan.tech"),
    ("ameyor.in", "https://ameyor.in"),
    ("LinkedIn", "https://www.linkedin.com/in/yashvardhanthanvi"),
    ("Instagram", "https://www.instagram.com/yashvardhan.thanvi/"),
]
CALL_URL = "https://calendly.com/yashvt9404/30min"
