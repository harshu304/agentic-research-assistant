import re


# ==========================================
# SECTION HEADER PATTERNS
# ==========================================
SECTION_HEADERS = {

    # ==========================================
    # ABSTRACT
    # ==========================================
    "abstract": [
        r"^\s*abstract\b"
    ],

    # ==========================================
    # INTRODUCTION
    # ==========================================
    "introduction": [
        r"^\s*(i|1)\.?\s*introduction\b"
    ],

    # ==========================================
    # RELATED WORK
    # ==========================================
    "related_work": [
        r"^\s*(ii|2)\.?\s*related work\b",
        r"^\s*(ii|2)\.?\s*background\b",
        r"^\s*literature review\b"
    ],

    # ==========================================
    # METHODOLOGY
    # ==========================================
    "methodology": [

        # Generic
        r"^\s*methodology\b",
        r"^\s*methods\b",
        r"^\s*system model\b",
        r"^\s*problem formulation\b",
        r"^\s*proposed method\b",
        r"^\s*proposed framework\b",

        # IEEE Roman numeral sections
        r"^\s*(iii|iv|3|4)\.?\s*system model\b",
        r"^\s*(iii|iv|3|4)\.?\s*proposed\b",
        r"^\s*(iii|iv|3|4)\.?\s*resource allocation\b",
        r"^\s*(iii|iv|3|4)\.?\s*llm[- ]based\b",

        # Subsections
        r"^\s*a\.\s*principle of llm\b",
        r"^\s*b\.\s*conventional resource allocation\b",
        r"^\s*c\.\s*resource allocation using llm\b",

        # Additional common research sections
        r"^\s*network architecture\b",
        r"^\s*framework overview\b",
        r"^\s*optimization framework\b",
        r"^\s*proposed architecture\b"
    ],

    # ==========================================
    # EXPERIMENTS
    # ==========================================
    "experiments": [
        r"^\s*experiments\b",
        r"^\s*experimental setup\b",
        r"^\s*simulation setup\b",
        r"^\s*benchmark setup\b",
        r"^\s*evaluation setup\b"
    ],

    # ==========================================
    # RESULTS
    # ==========================================
    "results": [

        # Generic
        r"^\s*results\b",
        r"^\s*simulation results\b",
        r"^\s*performance evaluation\b",
        r"^\s*numerical results\b",

        # IEEE style
        r"^\s*(v|5)\.?\s*performance evaluation\b",
        r"^\s*(v|5)\.?\s*results\b"
    ],

    # ==========================================
    # CHALLENGES
    # ==========================================
    "challenges": [
        r"^\s*(vi|6)\.?\s*research challenges\b",
        r"^\s*latency and computation time\b",
        r"^\s*optimized llm architecture\b",
        r"^\s*training methodology\b",
        r"^\s*interpretability and explainability\b",
        r"^\s*limitations\b"
    ],

    # ==========================================
    # CONCLUSION
    # ==========================================
    "conclusion": [
        r"^\s*(vii|7)\.?\s*conclusion\b",
        r"^\s*future work\b",
        r"^\s*concluding remarks\b"
    ],

    # ==========================================
    # REFERENCES
    # ==========================================
    "references": [
        r"^\s*references\b"
    ]
}


# ==========================================
# CLEAN TEXT
# ==========================================
def clean_line(line):

    line = line.strip().lower()

    # normalize spaces
    line = re.sub(r"\s+", " ", line)

    return line


# ==========================================
# DETECT SECTION HEADER
# ==========================================
def detect_section_header(line):

    line = clean_line(line)

    # ==========================================
    # Ignore noisy PDF artifacts
    # ==========================================
    if line.startswith("figure"):
        return None

    if line.startswith("fig."):
        return None

    if line.startswith("table"):
        return None

    if line.startswith("copyright"):
        return None

    if line.startswith("received"):
        return None

    # Very long lines are usually paragraph text
    if len(line) > 120:
        return None

    # ==========================================
    # Detect section
    # ==========================================
    for section, patterns in SECTION_HEADERS.items():

        for pattern in patterns:

            if re.search(pattern, line):

                return section

    return None


# ==========================================
# PARSE DOCUMENT INTO SECTIONS
# ==========================================
def parse_sections(pages):

    parsed_content = []

    current_section = "unknown"

    last_detected = None

    for page in pages:

        page_number = page["page"]

        lines = page["text"].split("\n")

        for line in lines:

            clean = clean_line(line)

            if not clean:
                continue

            # ==========================================
            # Detect section
            # ==========================================
            detected = detect_section_header(clean)

            # ==========================================
            # Update active section
            # ==========================================
            if detected:

                # avoid repetitive logs
                if detected != last_detected:

                    current_section = detected

                    last_detected = detected

                    print(
                        f"\n📚 DETECTED SECTION: "
                        f"{current_section}"
                    )

            # ==========================================
            # Store parsed line
            # ==========================================
            parsed_content.append({

                "page": page_number,

                "section": current_section,

                "text": clean
            })

    return parsed_content