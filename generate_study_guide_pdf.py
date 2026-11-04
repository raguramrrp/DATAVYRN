import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 11 * 72 - 28, "AI MODEL TRAINER & TECHNICAL EVALUATION SPECIALIST — INTERVIEW CHEAT SHEET")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * 72 - 32, 8.5 * 72 - 36, 11 * 72 - 32)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 36, 20, page_text)
        self.drawString(36, 20, "CONFIDENTIAL & PREPARED FOR AI MODEL TRAINER CANDIDATES — 2026 EDITION")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 28, 8.5 * 72 - 36, 28)
        
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary = colors.HexColor("#1e3a8a")
    secondary = colors.HexColor("#0f766e")
    dark = colors.HexColor("#0f172a")
    slate = colors.HexColor("#334155")
    bg_blue = colors.HexColor("#eff6ff")
    bg_teal = colors.HexColor("#f0fdfa")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=secondary,
        textTransform='uppercase',
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SecH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.white,
        spaceBefore=10,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SecH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=dark,
        spaceAfter=4
    )

    bold_body = ParagraphStyle(
        'DocBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title Banner
    story.append(Paragraph("AI MODEL TRAINER & TECHNICAL EVALUATION SPECIALIST", title_style))
    story.append(Paragraph("Comprehensive Interview Cheat Sheet & Multi-Page Study Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary, spaceAfter=8))

    def make_section_header(title):
        t = Table([[Paragraph(f"<b>{title}</b>", h1_style)]], colWidths=[8.5*72 - 72])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), primary),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('CORNERPAD', (0, 0), (-1, -1), 3),
        ]))
        return t

    def make_callout(text, bg_color=bg_blue, border_color=primary, title="FORMULA CALLOUT"):
        content = [
            Paragraph(f"<b>{title}</b>", ParagraphStyle('CallTitle', parent=bold_body, textColor=border_color, fontSize=8)),
            Spacer(1, 2),
            Paragraph(text, body_style)
        ]
        t = Table([[content]], colWidths=[8.5*72 - 72])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        return t

    def make_problem_box(badge, title, question, solution_steps, answer):
        badge_color = colors.HexColor("#1e40af") if badge == "MODERATE" else colors.HexColor("#b91c1c")
        badge_bg = colors.HexColor("#dbeafe") if badge == "MODERATE" else colors.HexColor("#fee2e2")
        
        flowables = [
            Paragraph(f"<font color='{badge_color}'><b>[{badge}]</b></font> <b>{title}</b>", bold_body),
            Spacer(1, 2),
            Paragraph(f"<b>Problem:</b> {question}", body_style),
            Spacer(1, 2),
            Paragraph(f"<b>Step-by-Step Solution:</b><br/>{solution_steps}", body_style),
            Spacer(1, 2),
            Paragraph(f"<b>Key Answer:</b> <font color='#15803d'><b>{answer}</b></font>", bold_body)
        ]
        t = Table([[flowables]], colWidths=[8.5*72 - 72])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        return t

    # SECTION 1
    story.append(make_section_header("SECTION 1: QUANTITATIVE APTITUDE"))
    story.append(Spacer(1, 4))

    # 1.1
    story.append(Paragraph("1.1 Percentages, Profit & Loss, and Discount", h2_style))
    story.append(make_callout(
        "• Percentage Change: &Delta;% = [(New - Old) / Old] &times; 100 | Multiplying Factor: MF = 1 &plusmn; (x / 100)<br/>"
        "• Successive Change: E = a + b + (ab / 100)% | Selling Price: SP = CP(1 + P%) = CP(1 - L%)<br/>"
        "• Marked Price & Discount: SP = MP(1 - D%) | Fundamental Ratio: CP / MP = (100 - D%) / (100 + P%)<br/>"
        "• Invariance Rule: If A increases by x/y, B must decrease by x/(x+y) to keep product constant.<br/>"
        "• Dishonest Dealer Gain% = [(Claimed Weight - True Weight) / True Weight] &times; 100",
        bg_blue, primary, "CORE FORMULAS & SHORTCUTS"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "MODERATE", "Successive Discounts with Net Margin",
        "A trader marks an item 40% above CP and offers two successive discounts of 15% and 10%. Find net profit %.",
        "1. Let CP = 100 &rArr; MP = 140.<br/>"
        "2. Single equivalent discount D_eff = 15 + 10 - (15 &times; 10 / 100) = 25 - 1.5 = 23.5%.<br/>"
        "3. SP = 140 &times; (1 - 0.235) = 140 &times; 0.765 = 107.10.<br/>"
        "4. Profit = SP - CP = 107.10 - 100 = 7.10%.",
        "7.1% Net Profit"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "TRICKY", "Dishonest Merchant with Markup & Cash Discount",
        "A merchant marks goods 20% above CP, uses a faulty scale reading 1000g for every 800g actual weight, and gives a 10% cash discount. Find actual profit %.",
        "1. Let true cost of 1g = $1 &rArr; cost of 800g dispensed = $800.<br/>"
        "2. Nominal bill for 1000g at marked price = 1000 &times; 1.20 = $1200.<br/>"
        "3. Selling Price after 10% discount = 1200 &times; 0.90 = $1080.<br/>"
        "4. Net Profit % = [(1080 - 800) / 800] &times; 100 = (280 / 800) &times; 100 = 35%.",
        "35.0% Actual Profit"
    ))

    # 1.2
    story.append(Spacer(1, 6))
    story.append(Paragraph("1.2 Simple & Compound Interest (Rule of 72 & Shortcut Ratios)", h2_style))
    story.append(make_callout(
        "• SI = (P &times; R &times; T) / 100 | CI = P(1 + R/100)^T - P<br/>"
        "• Difference (2 Years): &Delta;2 = CI2 - SI2 = P(R / 100)^2<br/>"
        "• Difference (3 Years): &Delta;3 = P(R / 100)^2 &times; [(300 + R) / 100]<br/>"
        "• Pascal Ratio Method: 2 Yrs &rArr; 2:1 | 3 Yrs &rArr; 3:3:1 | 4 Yrs &rArr; 4:6:4:1<br/>"
        "• Doubling / Tripling Rules: Rule of 72 (Double &asymp; 72/R) | Rule of 114 (Triple &asymp; 114/R) | Rule of 144 (Quadruple &asymp; 144/R)",
        bg_teal, secondary, "INTEREST FORMULAS & MULTIPLIERS"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "MODERATE", "3-Year Difference Principal Determination",
        "The difference between CI and SI at 10% p.a. for 3 years is $620. Find the principal sum.",
        "1. &Delta;3 = P(R/100)^2 &times; [(300 + R)/100].<br/>"
        "2. 620 = P &times; (1/100) &times; (310/100) = P &times; (31/1000).<br/>"
        "3. P = (620 &times; 1000) / 31 = $20,000.",
        "$20,000 Principal"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "TRICKY", "Multi-Year Geometric Compounding",
        "A principal under CI grows to $8,000 after 3 years and to $12,000 after 6 years. Find the original principal.",
        "1. Equal intervals &Delta;t = 3 yrs &rArr; A3 = P &times; k^3 = 8000; A6 = P &times; k^6 = 12000.<br/>"
        "2. Ratio A6 / A3 = k^3 = 12000 / 8000 = 1.5 = 3/2.<br/>"
        "3. Substitute into A3: P &times; (3/2) = 8000 &rArr; P = (8000 &times; 2) / 3 = $5,333.33.",
        "$5,333.33 Original Principal"
    ))

    story.append(PageBreak())

    # 1.3
    story.append(Paragraph("1.3 Time, Speed, Distance & Relative Motion", h2_style))
    story.append(make_callout(
        "• Unit Conversion: 1 km/h = 5/18 m/s | 1 m/s = 18/5 km/h<br/>"
        "• Average Speed (Equal Distances): S_avg = 2xy / (x + y) | 3 Distances: 3xyz / (xy + yz + zx)<br/>"
        "• Relative Speed: Opposite Direction = S1 + S2 | Same Direction = |S1 - S2|<br/>"
        "• Boats & Streams: Downstream D = u + v, Upstream U = u - v &rArr; u = (D+U)/2, v = (D-U)/2<br/>"
        "• Post-Meeting Theorem: S1 / S2 = &radic;(t2 / t1)",
        bg_blue, primary, "TSD & RELATIVE MOTION"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "MODERATE", "Dual Train Overtake (Same Direction)",
        "Train A (180m, 72 km/h) overtakes Train B (120m, 36 km/h) in the same direction. How long to completely pass?",
        "1. Distance = 180 + 120 = 300m.<br/>"
        "2. Relative speed = 72 - 36 = 36 km/h = 36 &times; (5/18) = 10 m/s.<br/>"
        "3. Time = 300 / 10 = 30 seconds.",
        "30 seconds"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "TRICKY", "Post-Meeting Velocity Calculation",
        "Trains P and Q start simultaneously towards each other. After passing, P takes 4 hr 48 min to reach Y, and Q takes 3 hr 20 min to reach X. If S_P = 45 km/h, find S_Q.",
        "1. t_P = 4 + 48/60 = 24/5 hr; t_Q = 3 + 20/60 = 10/3 hr.<br/>"
        "2. S_P / S_Q = &radic;(t_Q / t_P) = &radic;((10/3) / (24/5)) = &radic;(50/72) = &radic;(25/36) = 5/6.<br/>"
        "3. 45 / S_Q = 5/6 &rArr; S_Q = (45 &times; 6) / 5 = 54 km/h.",
        "54 km/h"
    ))

    # 1.4, 1.5, 1.6
    story.append(Spacer(1, 6))
    story.append(Paragraph("1.4 Time & Work, 1.5 Mixtures, 1.6 Probability Shortcuts", h2_style))
    story.append(make_callout(
        "• Time & Work Efficiency: E = Work / Time | Work = LCM of times | MDH: (M1 D1 H1 E1)/W1 = (M2 D2 H2 E2)/W2<br/>"
        "• Alligation Rule: Q_cheaper / Q_dearer = (Cost_dearer - Cost_mean) / (Cost_mean - Cost_cheaper)<br/>"
        "• Repeated Dilution: Q_final = Q_initial &times; [1 - (y / x)]^n<br/>"
        "• Combinations & Probability: ^nC_r = n! / [r!(n-r)!] | Complement: P(At least 1) = 1 - P(None)",
        bg_teal, secondary, "WORK, ALLIGATION & PROBABILITY SHORTCUTS"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "MODERATE", "Alternate Days Rotation Work",
        "A finishes work in 12 days, B in 18 days. They work alternate days with A starting on Day 1. Total days taken?",
        "1. Total Work = LCM(12, 18) = 36 units. E_A = 3, E_B = 2 units/day.<br/>"
        "2. 2-day cycle = 3 + 2 = 5 units. 7 full cycles (14 days) = 35 units.<br/>"
        "3. Remaining = 1 unit. Day 15: A takes 1 / 3 day. Total = 14 1/3 days.",
        "14 1/3 days (14.33 days)"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "TRICKY", "Successive Dilution of Pure Liquid",
        "A barrel has 80L pure ethanol. 8L is drawn and replaced with water, repeated 2 more times (total 3 times). Final ethanol?",
        "1. Fraction remaining each step = 1 - 8/80 = 9/10 = 0.9.<br/>"
        "2. Q_final = 80 &times; (9/10)^3 = 80 &times; (729/1000) = 58.32 Liters.",
        "58.32 Liters Ethanol (21.68L Water)"
    ))

    story.append(PageBreak())

    # SECTION 2
    story.append(make_section_header("SECTION 2: LOGICAL REASONING"))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2.1 Syllogisms (Euler/Venn & 100-50 Rules, Either-Or Cases)", h2_style))
    story.append(make_callout(
        "• 100-50 Distribution: All (100-50), No (100-100), Some (50-50), Some Not (50-100)<br/>"
        "• Polarity Axioms: 2 Negative Premises = No Conclusion | 2 Particulars = No Conclusion<br/>"
        "• Either-Or Complementary Conditions: (1) Both conclusions uncertain, (2) Identical Subject & Predicate, (3) Pair is [Some + No] OR [Some + Some Not]. (Note: [All + No] is invalid).",
        bg_blue, primary, "SYLLOGISM DECISION RULES"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "TRICKY", "Either-Or with Possibility Conclusion",
        "Statements: (1) Some parameters are weights. (2) Some weights are biases. (3) No bias is an activation.<br/>Conclusions: I. Some parameters are activations. II. No parameter is an activation. III. All activations being weights is a possibility.",
        "1. Parameters and Activations share no transitive link &rArr; I and II are uncertain individually.<br/>"
        "2. Identical subject/predicate in [Some + No] form &rArr; <b>Either I or II follows</b>.<br/>"
        "3. Activations cannot overlap Biases, but Weights is broader; activations can reside in weights &rArr; <b>III follows</b>.",
        "Either I or II follows, AND III follows"
    ))

    story.append(Spacer(1, 6))
    story.append(Paragraph("2.2 Blood Relations, Seating & Critical Reasoning", h2_style))
    story.append(make_callout(
        "• Blood Relations: Gender elimination first (+/-), Generation Sum (&Sigma;&Delta;G): Parent=+1, Child=-1, Sibling=0.<br/>"
        "• Seating Arrangement: Anchor to fixed clues; maintain dual-branch diagrams; check facing orientations.<br/>"
        "• Critical Reasoning: Premise + Assumption = Conclusion. Use the <b>Negation Test</b> (if negated assumption destroys conclusion, it is mandatory).",
        bg_teal, secondary, "LOGICAL REASONING PROTOCOLS"
    ))
    story.append(Spacer(1, 4))
    story.append(make_problem_box(
        "MODERATE", "Critical Reasoning: Model Scaling Assumption",
        "An AI lab claims 10x parameter scaling will eliminate hallucinations, citing a 35% drop from 7B to 70B.<br/>Which assumption is required? (A) 7B models cannot be fine-tuned. (B) Hallucination reduction does not hit an asymptotic ceiling as parameters scale.",
        "1. Conclusion: 10x scaling will completely eliminate (reduce to 0) hallucinations.<br/>"
        "2. Negate (B): 'Hallucination reduction hits an asymptotic ceiling.' If true, hallucinations cannot reach 0.<br/>"
        "3. Thus, (B) is a necessary unstated assumption.",
        "Option (B)"
    ))

    story.append(PageBreak())

    # SECTION 3
    story.append(make_section_header("SECTION 3: VERBAL ABILITY & LANGUAGE SKILLS"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("3.1 Top 10 Recurring Error Spotting Patterns for AI Evaluators", h2_style))

    err_data = [
        ["Pattern", "Faulty Construct", "Correct Construction & Rule"],
        ["1. SVA Intervening Phrases", "The cluster of GPU nodes are hot.", "The cluster [of nodes] is hot. (Ignore prepositional phrase)"],
        ["2. Faulty Comparison", "Model A's speed is faster than Model B.", "Model A's speed is faster than that of Model B."],
        ["3. Mandative Subjunctive", "The lead insisted that he evaluates it.", "The lead insisted that he evaluate it. (Bare infinitive)"],
        ["4. Dangling Modifier", "Having finished the rubric, the data was sent.", "Having finished the rubric, the team sent the data."],
        ["5. Past Perfect Sequence", "When the job crashed, he saved weights.", "When the job crashed, he had saved weights."],
        ["6. Redundant Phrases", "Revert back; repeat again; reason because.", "Revert; repeat; the reason is that. (Tautology elimination)"],
        ["7. Countable/Uncountable", "The response has less hallucinations.", "The response has fewer hallucinations. (Countable = fewer)"],
        ["8. Parallelism", "Excels at coding, to write, and design.", "Excels at coding, writing, and designing."],
        ["9. Correlative Placement", "Failed either due to memory or weights.", "Failed due to either memory or weights."],
        ["10. Hypothetical 'If...would'", "If he would have checked, he knew.", "If he had checked, he would have known. (No 'would' in if-clause)"]
    ]

    t_err = Table(err_data, colWidths=[1.8*72, 2.5*72, 3.2*72])
    t_err.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('LEADING', (0, 0), (-1, -1), 9.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_err)

    story.append(Spacer(1, 6))
    story.append(make_problem_box(
        "MODERATE", "Sentence Correction: Parallelism & Verb Agreement",
        "Sentence: 'Unlike legacy architectures, modern diffusion models are characterized by sharp details, high coherence, and they display realistic textures.'<br/>"
        "(A) ...and they display realistic textures. | (B) ...and realistic textures. | (C) is characterized by sharp details... | (D) characterized by sharp details...",
        "• (A) violates parallelism by joining nouns with an independent clause.<br/>"
        "• (B) is CORRECT: balances 3 parallel noun phrases (details, coherence, textures) with plural 'are'.<br/>"
        "• (C) creates SVA error (plural models + singular is).<br/>"
        "• (D) creates a sentence fragment by omitting 'are'.",
        "Option (B)"
    ))

    story.append(PageBreak())

    # SECTION 4
    story.append(make_section_header("SECTION 4: ESSENTIAL CODING (AI & DATA FOCUS - PYTHON)"))
    story.append(Spacer(1, 4))
    story.append(Paragraph("4.1 RegEx, Token Normalization & JSONL Data Streaming", h2_style))

    code_snippet_1 = """# Clean and normalize raw model outputs for evaluation
import re, unicodedata, json

def clean_and_extract(text: str) -> dict:
    norm = unicodedata.normalize("NFKC", text)
    cleaned = re.sub(r'[\\u200B-\\u200D\\uFEFF]', '', norm)  # remove zero-width
    cleaned = re.sub(r'[ \\t]+', ' ', cleaned)
    code_blocks = re.findall(r'```([a-zA-Z0-9_-]*)\\n([\\s\\S]*?)```', cleaned)
    reasoning = re.findall(r'<(?:think|reasoning)>([\\s\\S]*?)</(?:think|reasoning)>', cleaned)
    return {"text": cleaned.strip(), "code": code_blocks, "reasoning": reasoning}

def stream_jsonl(filepath: str):  # O(1) Memory streaming generator
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip(): yield json.loads(line)"""

    t_code1 = Table([[Paragraph(f"<pre>{code_snippet_1}</pre>", code_style)]], colWidths=[8.5*72 - 72])
    t_code1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_code1)

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.2 Top Algorithmic Interview Question: Top-K Frequent Words (Heapq)", h2_style))
    
    code_snippet_2 = """import heapq
from collections import Counter

def top_k_frequent(words: list[str], k: int) -> list[str]:
    # Time: O(N + M log K) | Space: O(M)
    counts = Counter(words)
    class Node:
        def __init__(self, count, word): self.count, self.word = count, word
        def __lt__(self, o):
            return self.word > o.word if self.count == o.count else self.count < o.count
    heap = []
    for w, c in counts.items():
        heapq.heappush(heap, Node(c, w))
        if len(heap) > k: heapq.heappop(heap)
    return [heapq.heappop(heap).word for _ in range(len(heap))][::-1]"""

    t_code2 = Table([[Paragraph(f"<pre>{code_snippet_2}</pre>", code_style)]], colWidths=[8.5*72 - 72])
    t_code2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_code2)

    story.append(PageBreak())

    # SECTION 5
    story.append(make_section_header("SECTION 5: AI MODEL TRAINER SPECIALIZED SKILLS"))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.1 Annotation Taxonomy, Cohen's Kappa & RLHF Framework", h2_style))
    story.append(make_callout(
        "• <b>Cohen's Kappa (&kappa;):</b> &kappa; = (p_o - p_e) / (1 - p_e) | Target for SFT/RLHF: &kappa; &ge; 0.65-0.80.<br/>"
        "• <b>Bradley-Terry Preference Probability:</b> P(y_w &succ; y_l | x) = &sigma;(r(x, y_w) - r(x, y_l)) = 1 / [1 + e^(-(r_w - r_l))]<br/>"
        "• <b>Preference Hierarchy:</b> Safety Veto > Factual Truthfulness > Hard Constraint Compliance > Conciseness/Style.",
        bg_blue, primary, "RLHF & EVALUATION FORMULAS"
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.2 Prompt Strategies & Adversarial Red-Teaming Taxonomy", h2_style))
    story.append(make_callout(
        "• <b>Prompting Types:</b> Zero-Shot (baseline) | Few-Shot (format anchors) | Chain-of-Thought (logic/math) | Tree-of-Thoughts (search).<br/>"
        "• <b>Red-Teaming Vectors:</b> Roleplay/DAN Jailbreaks | Base64/Rot13 Obfuscation | Hypothetical/Fictional Framing | Multi-turn Linguistic Slicing (splitting malicious script across turns) | Indirect Prompt Injection (via ingested files).",
        bg_teal, secondary, "RED-TEAMING TAXONOMY"
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.3 Top Behavioral & Scenario Questions for AI Model Trainers", h2_style))

    scenarios = [
        ("Q1: Contradictory Guidelines", "Triage by user prompt intent. Explicit prompt constraints override general defaults. If ambiguous, check precedent in the edge-case log. Escalate an inquiry with both proposed ratings to the Lead Taxonomist to update the team rubric."),
        ("Q2: Articulate Hallucination vs Dry Correctness", "Dry, 100% correct response wins decisively. Truthfulness is non-negotiable in RLHF. Eloquent hallucinations are actively dangerous as articulate prose induces unjustified user trust. Severe penalty under Factuality."),
        ("Q3: Disagreement with Senior Annotator", "Ground debate in the written Safety Policy, not personal opinion. Cite the exact trigger phrase and policy clause (e.g. dual-use reconnaissance). If disagreement persists, escalate the sample to the Policy Author for binding calibration."),
        ("Q4: Systematic Red-Teaming for Code Exploits", "Deploy a 5-tier matrix: (1) Direct baseline request, (2) Dual-use admin/pen-testing framing, (3) Syntactic obfuscation, (4) Multi-turn linguistic slicing (split payload from listener), (5) Counterfactual/CTF narrative framing."),
        ("Q5: Tight Deadline with Ambiguous Guidelines", "(1) Triage the 20% of rules driving 80% of data quality (safety, factuality, core format). (2) Establish a real-time living FAQ channel. (3) Batch tasks by prompt category. (4) Run hourly 5% spot-checks to detect drift early.")
    ]

    for q_title, q_ans in scenarios:
        story.append(Paragraph(f"<b>{q_title}:</b> {q_ans}", body_style))
        story.append(Spacer(1, 2))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at: {filename}")

if __name__ == "__main__":
    out_pdf = Path(r"c:\Users\ragur\Downloads\ai model project\storage\exports\AI_Model_Trainer_Interview_Study_Guide.pdf")
    build_pdf(str(out_pdf))
