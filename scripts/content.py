"""Everything the README says, in one place.

Edit this file, then run:

    python scripts/refresh.py    # live data: PRs, merges, logos, PyPI, new repos (needs a GitHub token)
    python scripts/build.py      # every SVG in assets/
    python scripts/readme.py     # README.md (keeps the live PR list)

House rules: only verified facts, first person, short lines, no emojis, no em or en dashes,
never mention an SIH 2024 finalist result (it is not true). Logo keys are listed in logos.py.
"""

NAME = ("Yashvardhan", "Thanvi.")
STATUS = ["Available for freelance work", "Jaipur, India · IST"]
# Hero paragraph: (text, emphasised?) runs.
INTRO = [
    ("Founder of ", False), ("LLMSlim", True), (", the open-source context layer for production AI agents, "
                                                 "backed by ", False), ("15 startup programs", True),
    (". I also run ", False), ("AMEYOR", True), (", my AI and software studio. Previously AI/ML research at ", False),
    ("DRDO", True), (".", False),
]

NAV = [("LLMSlim", "llmslim"), ("Work", "selected-work"), ("Open source", "open-source"),
       ("Recognition", "recognition"), ("Experience", "experience"), ("Stack", "stack"), ("Contact", "contact")]

EMAIL = "founder@llmslim.app"
CALL_URL = "https://calendly.com/yashvt9404/30min"
LINKS = [  # (href, asset name, label, icon, primary)
    (CALL_URL, "l-call", "Book a call", "calendar", True),
    ("https://www.yashvardhan.tech", "l-portfolio", "Portfolio", "globe", False),
    ("https://www.linkedin.com/in/yashvardhanthanvi", "l-linkedin", "LinkedIn", "linkedin", False),
    (f"mailto:{EMAIL}", "l-email", "Email", "mail", False),
    ("https://www.yashvardhan.tech/Yashvardhan-Thanvi-Resume.pdf", "l-resume", "Résumé", "file", False),
]

LLMSLIM = {
    "tagline": "The context layer for production AI agents.",
    "about": "Compress, plan and budget what the model sees, from prompts and chat history to RAG chunks, tool "
             "schemas and agent memory. It runs inside your own process: no API key, no network call.",
    "facts": "1,648 TESTS  ·  93% BRANCH COVERAGE  ·  MIT",
    "stats": [  # (big, label, source) exactly four
        ("212×", "lower cost than Mem0", "LongMemEval"),
        ("42×", "lower cost, same accuracy", "vs full history"),
        ("3×", "fewer tokens, same score", "LongBench v1"),
        ("+21", "points over LLMLingua-2", "NaturalQuestions"),
    ],
    "programs": ["openai", "anthropic", "mongodb", "sarvam", "zoho", "auth0", "zendesk", "mixpanel", "sentry",
                 "descope", "pulumi", "honeycomb", "exa", "neo4j", "cartesia"],
    "program_names": ["OpenAI", "Claude", "MongoDB", "Sarvam", "Zoho", "Auth0", "Zendesk", "Mixpanel", "Sentry",
                      "Descope", "Pulumi", "Honeycomb", "Exa", "Neo4j", "Cartesia"],
    "links": [
        ("Website", "https://www.llmslim.app"),
        ("Docs", "https://www.llmslim.app/docs/getting-started"),
        ("Benchmarks", "https://www.llmslim.app/benchmarks"),
        ("PyPI", "https://pypi.org/project/llmslim/"),
        ("Source", "https://github.com/Thanatos9404/llmslim"),
    ],
}

# Featured projects, two per row (keep an even count). shot = assets/shots/<shot>.jpg
PROJECTS = [
    {"repo": "Krishyak", "name": "Krishyak", "shot": "krishyak", "logo": "krishyak",
     "tag": "VBYLD 2026 · IETE 1ST PLACE", "line": "Farm decisions for Indian farmers, in all 22 Indian languages",
     "links": [("Live app", "https://krishyak.vercel.app")]},
    {"repo": "polygraph", "name": "Polygraph", "shot": "polygraph",
     "tag": "NEBIUS × NVIDIA HACKATHON", "line": "Checks every claim in a pull request by experiment",
     "links": [("Live demo", "https://yvt94-polygraph.static.hf.space"), ("Video", "https://youtu.be/VFzUl18uwP8")]},
    {"repo": "pratibimb", "name": "Pratibimb", "shot": "pratibimb",
     "tag": "DIGITAL TWIN CHALLENGE 2026", "line": "A physiology and ML digital twin for Type 2 diabetes",
     "links": [("Live console", "https://pratibimb-omega.vercel.app")]},
    {"repo": "canopyproof", "name": "CanopyProof", "shot": "canopyproof",
     "tag": "IEEE CLIMATECHAIN 2026", "line": "Satellite-verified integrity for forest carbon credits",
     "links": [("Video", "https://youtu.be/9FBv9KQ4Ag8")]},
    {"repo": "passerelle", "name": "Passerelle", "shot": "passerelle",
     "tag": "HACK APERTUS 2026", "line": "An air-gapped caseworker assistant on Apertus",
     "links": [("Video", "https://youtu.be/bjc88UYdgfE")]},
    {"repo": "hearthbeat", "name": "Hearthbeat", "shot": "hearthbeat",
     "tag": "AMAZON BUILD, SHIP, SHAPE", "line": "Privacy-first Alexa+ check-ins for older adults",
     "links": [("Video", "https://youtu.be/axVTrTiKaog")]},
]

# Listed inside "More projects": (name, href, short description)
MORE = [
    ("RuleDost", "https://ruledost.vercel.app", "hackathon rules, decoded with receipts"),
    ("StudyTwin", "https://github.com/Thanatos9404/StudyTwin", "a tutor that cites your course material"),
    ("Leash", "https://github.com/Thanatos9404/leash", "spending mandates for AI shopping agents"),
    ("dayrhythm", "https://github.com/Thanatos9404/dayrhythm", "a routine-learning Python library"),
    ("Intuix", "https://github.com/Thanatos9404/Intuix-NASA", "exoplanet detection for NASA Space Apps"),
]

# (logo, title, detail, year) shown two per row
RECOGNITION = [
    ("mybharat", "Rajasthan Rank 1, VBYLD 2026",
     "National finalist, top 0.0005% of 50.49 lakh. Presented Krishyak to the Union Agriculture Minister.", "2026"),
    ("nasa", "Global Finalist Nominee", "NASA Space Apps Challenge, exoplanet detection.", "2025"),
    ("iete", "1st place, IETE Engineers' Day", "Student project competition, with Krishyak.", "2026"),
    ("producthunt", "#11 Product of the Day", "LLMSlim on its Product Hunt launch.", "2026"),
    ("polaris", "Polaris Fellowship, final round", "Top 100 applicants from across India.", "2026"),
    ("sih", "Smart India Hackathon 2026", "BIT Jaipur internal round, nominated for the next round.", "2026"),
    ("thoughtworks", "Top 10, HackLoop", "Finalist from 1,600+ entrants, finale at Thoughtworks.", "2025"),
    ("iete", "1st prize, IETE Student's Day", "Design competition, IETE Bhawan, Jaipur.", "2025"),
]

WORK = [  # (logo, org, role, when, note)
    ("drdo", "DRDO, Scientific Analysis Group", "AI/ML and software research intern", "MAY TO JUL 2026",
     "Offline RAG, policy-compliant configuration and signal analysis in air-gapped labs."),
    ("ameyor", "AMEYOR", "Founder", "2026 TO NOW",
     "My Jaipur studio behind LLMSlim and Krishyak: AI systems, websites and custom software."),
    ("olinp", "Olinp Technologies", "AI/ML engineering intern", "APR TO JUN 2025",
     "Preprocessing and feature engineering across three production modules."),
]
LEAD = [  # (logo, org, role, when) up to 7 rows
    ("aws", "Amazon Web Services", "Student Builder Group Leader", "NOW"),
    ("gfg", "GeeksforGeeks", "Campus Mantri", "2026"),
    ("iic", "Institution's Innovation Council", "Head, Innovation Subcommittee", "NOW"),
    ("gdg", "GDG on Campus, BIT Jaipur", "Coordinator", "2025"),
    ("google", "Google", "Gemini Student Ambassador", "2025"),
    ("oneplus", "OnePlus", "Student Ambassador", "PAST"),
    ("gssoc", "GirlScript Summer of Code", "Open source contributor", "2025"),
]
EDUCATION = ("bit", "BIT Mesra, Jaipur", "BCA in Computer Science, minor in Artificial Intelligence", "9.35",
             "CGPA", "2024 TO 2027")

# skill-icons names (MIT, github.com/tandpfun/skill-icons), two rows
STACK = [
    ["Python", "TypeScript", "JavaScript", "FastAPI", "Flask", "NextJS", "React", "TailwindCSS", "NodeJS", "Docker",
     "Linux", "Git"],
    ["PyTorch", "TensorFlow", "ScikitLearn", "OpenCV", "PostgreSQL", "MongoDB", "Redis", "SQLite", "AWS", "GCP",
     "Vercel", "GithubActions"],
]
STACK_ALSO = "LangChain, LlamaIndex, Haystack, Hugging Face, Ollama, MCP, OpenAI Agents SDK"

CONTACT = {
    "title": ("Have something in mind?", "Let's build it."),
    "body": "Freelance and contract work: Python backends, retrieval and RAG systems, AI features, and prototypes "
            "that reach real users.",
    "button": "Book a 30-min call",
}
FOOTER_LINKS = [
    (EMAIL, f"mailto:{EMAIL}"),
    ("yashvardhan.tech", "https://www.yashvardhan.tech"),
    ("ameyor.in", "https://ameyor.in"),
    ("llmslim.app", "https://www.llmslim.app"),
    ("LinkedIn", "https://www.linkedin.com/in/yashvardhanthanvi"),
]

# Public repos that the automatic "More projects" list should never pick up.
AUTO_EXCLUDE = {"Thanatos9404", "Thanatos9404.github.io", "StackUnderflow_BIT-Mesra-Jaipur", "Portfolio-Website",
                "SoapySDR", "todo-app", "hackathon-demo-videos"}
# Brand-new public repos (last 60 days, not featured above) are added to "More projects" automatically.
FRESH_MAX = 4
