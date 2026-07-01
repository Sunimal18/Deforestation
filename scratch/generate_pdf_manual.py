import os
import sys

def build_pdf(filename="FOREST-AI_User_Manual.pdf"):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super(NumberedCanvas, self).__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            if self._pageNumber == 1:
                return  # Suppress headers/footers on cover page
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            
            # Header
            self.drawString(54, 750, "FOREST-AI: Conservation Monitoring System - User Manual")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            self.line(54, 60, 558, 60)
            self.drawString(54, 45, "Confidential - Forestry Department Internal Use Only")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 45, page_text)
            self.restoreState()

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#15803d"),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#475569"),
        spaceAfter=40
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=20,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=20,
        bulletIndent=8,
        spaceAfter=6
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 150))
    story.append(Paragraph("FOREST-AI", ParagraphStyle('GreenBrand', parent=title_style, fontSize=40, leading=46)))
    story.append(Paragraph("Conservation Monitoring System", title_style))
    story.append(Paragraph("A Comprehensive Guide for Conservation Officers and Field Administrators", subtitle_style))
    
    # Metadata Table
    meta_data = [
        [Paragraph("<b>Document:</b> User Manual", body_style), Paragraph("<b>Version:</b> 1.0", body_style)],
        [Paragraph("<b>Author:</b> Technical Team", body_style), Paragraph("<b>Date:</b> July 2026", body_style)],
        [Paragraph("<b>Target Site:</b> Wilpattu Forest Reserve", body_style), Paragraph("<b>Status:</b> Production", body_style)],
    ]
    t = Table(meta_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # ------------------ PAGE 2: TABLE OF CONTENTS & INTRODUCTION ------------------
    story.append(Paragraph("Table of Contents", h1_style))
    toc_data = [
        [Paragraph("1. System Overview", body_style), Paragraph("Page 2", body_style)],
        [Paragraph("2. User Authentication & Session Security", body_style), Paragraph("Page 2", body_style)],
        [Paragraph("3. Main Dashboard & Layer Controls", body_style), Paragraph("Page 3", body_style)],
        [Paragraph("4. Disturbance Detection (Vegetation Index Analysis)", body_style), Paragraph("Page 3", body_style)],
        [Paragraph("5. AI Risk Prediction & Explanations", body_style), Paragraph("Page 4", body_style)],
        [Paragraph("6. Reforestation Recommendations & Priority Matrix", body_style), Paragraph("Page 4", body_style)],
        [Paragraph("7. Monitoring Reports & PDF/CSV Exporter", body_style), Paragraph("Page 5", body_style)],
    ]
    toc_table = Table(toc_data, colWidths=[350, 50])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.HexColor("#f1f5f9")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("1. System Overview", h1_style))
    story.append(Paragraph(
        "FOREST-AI is a state-of-the-art conservation platform designed to monitor illegal deforestation, identify "
        "vulnerable areas, and optimize reforestation planning inside the Wilpattu Forest Reserve. By merging high-resolution "
        "Sentinel-2 satellite imagery composites with neural-network-driven analytics, the system supplies forest authorities "
        "with real-time, explainable telemetry to direct field patrols.",
        body_style
    ))
    
    story.append(Paragraph("2. User Authentication & Session Security", h1_style))
    story.append(Paragraph(
        "To safeguard sensitive geographical alerts, FOREST-AI implements strict user authorization and access controls:",
        body_style
    ))
    story.append(Paragraph("<b>&bull; Access Lock:</b> All application pages require an active login session. Unauthenticated attempts are redirected back to the login screen.", bullet_style))
    story.append(Paragraph("<b>&bull; Roles:</b> Administrators and Conservation Officers are supplied with unique profile descriptors (Username, Email, Role, Joined Date) that can be viewed by clicking the **Profile Dropdown** in the navbar.", bullet_style))
    story.append(Paragraph("<b>&bull; Logout:</b> Click the Profile dropdown and choose 'Logout' to end your session safely, which clears all session cookies.", bullet_style))
    
    story.append(PageBreak())
    
    # ------------------ PAGE 3: DASHBOARD & DISTURBANCE ------------------
    story.append(Paragraph("3. Main Dashboard & Layer Controls", h1_style))
    story.append(Paragraph(
        "The Dashboard serves as the central hub of the system, presenting a dynamic GIS map initialized on the Wilpattu boundary.",
        body_style
    ))
    story.append(Paragraph("<b>&bull; Map Layer Toggles:</b> The left sidebar contains checkboxes to overlay **Disturbances** (past canopy losses), **Risk Prediction** (modeled danger corridors), and **Reforestation** (ongoing replanting plots) on the map. You can combine layers to analyze spatial correlations.", bullet_style))
    story.append(Paragraph("<b>&bull; Time Range Selection:</b> Filter the visual markers by adjusting the 'Start Year' dropdown and the 'End Year' range slider. The timeline spans from 2019 to the current year, updating instantly upon release.", bullet_style))
    story.append(Paragraph("<b>&bull; Alert Center (Bell Icon):</b> Clicking the Bell in the top-right navbar expands a dropdown displaying the 4 most recent verified canopy losses. Each alert displays a colored severity level. Clicking any alert automatically pans the map and focuses on the target polygon.", bullet_style))
    
    story.append(Paragraph("4. Disturbance Detection (Vegetation Index Analysis)", h1_style))
    story.append(Paragraph(
        "The **Disturbance Detection** page lists and maps verified forest losses using automated pixel classification algorithms.",
        body_style
    ))
    story.append(Paragraph("<b>&bull; Disturbances Map:</b> Positioned above the table, this map highlights the precise boundaries of canopy loss. Hovering over a polygon shows its unique **Area ID** (e.g. Area 104) in a tooltip, and clicking reveals the affected extent and detection date.", bullet_style))
    story.append(Paragraph("<b>&bull; NDVI Change:</b> The Normalized Difference Vegetation Index measures foliage density. The system flags localized vegetation declines (negative value changes). A larger negative score suggests complete clearance.", bullet_style))
    story.append(Paragraph("<b>&bull; Confidence Scores:</b> Neural networks classify the likelihood that a detected anomaly represents actual deforestation. High confidence logs (&gt;85%) should be treated as confirmed encroachment.", bullet_style))
    
    story.append(PageBreak())
    
    # ------------------ PAGE 4: RISK & REFORESTATION ------------------
    story.append(Paragraph("5. AI Risk Prediction & Explanations", h1_style))
    story.append(Paragraph(
        "The **Risk Prediction** page flags areas vulnerable to future clearance, using proximity metrics to assess threat levels.",
        body_style
    ))
    story.append(Paragraph("<b>&bull; Landscape Indicators:</b> Threat scores are calculated by measuring spatial proximity to logging corridors: distance to roads, distance to waterways, and distance to agricultural borders.", bullet_style))
    story.append(Paragraph("<b>&bull; Explainable AI (XAI):</b> Every flagged risk area includes a human-readable explanation card. This explains what local factors contributed to the threat level (e.g. 'high risk due to a road corridor construction within 250m'), aiding resource allocation.", bullet_style))
    
    story.append(Paragraph("6. Reforestation Recommendations & Priority Matrix", h1_style))
    story.append(Paragraph(
        "The **Reforestation** module suggests optimal sites for canopy restoration, using a multi-criteria decision framework.",
        body_style
    ))
    story.append(Paragraph("<b>&bull; Suitability Index:</b> Classified as **Suitable**, **Moderately Suitable**, or **Unsuitable** by evaluating local water tables, soil moisture proxies, and past logging severity.", bullet_style))
    story.append(Paragraph("<b>&bull; Priority Rankings:</b> Classified into **High**, **Medium**, or **Low** priority. High-priority sites represent highly degraded buffer zones that require immediate soil prep and tree planting.", bullet_style))
    story.append(Paragraph("<b>&bull; Interactive Analytics:</b> The right sidebar renders live breakdown charts (Suitability Bar Chart and Priority Doughnut Chart) based on the latest field recommendations.", bullet_style))
    
    story.append(PageBreak())
    
    # ------------------ PAGE 5: MONITORING REPORTS ------------------
    story.append(Paragraph("7. Monitoring Reports & PDF/CSV Exporter", h1_style))
    story.append(Paragraph(
        "The **Reports** page allows administrators to search database records, export raw telemetry, and generate print-ready reports.",
        body_style
    ))
    story.append(Paragraph("<b>&bull; Custom Date Filters:</b> Query the entire alerts database by entering a custom start date (defaults to 2019-01-01) and end date.", bullet_style))
    story.append(Paragraph("<b>&bull; Generate Monthly Report:</b> Compiles a formal monthly conservation status document. This is optimized for A4 print sizes and removes screen-only UI elements when exported as a PDF.", bullet_style))
    story.append(Paragraph("<b>&bull; CSV Export:</b> Downloads tabular database views into spreadsheet-compatible format for offline GIS integration.", bullet_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == '__main__':
    # Use absolute path resolving relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, '..', 'static', 'docs', 'FOREST-AI_User_Manual.pdf')
    build_pdf(os.path.abspath(output_path))
    print(f"Successfully generated PDF manual at {output_path}")
