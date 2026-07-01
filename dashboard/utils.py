import io
import datetime
from django.db.models import Sum, Avg
from disturbance.models import DisturbanceArea
from risk_prediction.models import RiskArea

def generate_monthly_report_pdf(year, month):
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
            self.saveState()
            self.setFont("Times-Roman", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            
            # Header
            self.drawString(54, 750, f"FOREST-AI Monthly Deforestation Monitoring Report - {year}/{month:02d}")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
            # Footer
            self.line(54, 60, 558, 60)
            self.drawString(54, 45, "Confidential - Department of Wildlife Conservation")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 45, page_text)
            self.restoreState()

    # Query Data
    disturbances = DisturbanceArea.objects.filter(detection_date__year=year, detection_date__month=month).order_by('-detection_date')
    risks = RiskArea.objects.filter(risk_score__gt=0.7).order_by('-risk_score')
    
    # Calculate stats
    total_alerts = disturbances.count()
    total_area_m2 = disturbances.aggregate(Sum('area_m2'))['area_m2__sum'] or 0
    total_area_ha = round(total_area_m2 / 10000.0, 2)
    avg_confidence = disturbances.aggregate(Avg('confidence'))['confidence__avg'] or 0
    avg_confidence = round(avg_confidence * 100, 1)

    month_name = datetime.date(year, month, 1).strftime("%B %Y")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles (Times New Roman based)
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#15803d"),
        spaceAfter=10
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []
    
    # Header block
    story.append(Paragraph("FOREST-AI CONSERVATION SYSTEM", ParagraphStyle('Sub', fontName='Times-Bold', fontSize=10, textColor=colors.HexColor("#64748b"), spaceAfter=5)))
    story.append(Paragraph(f"Monthly Monitoring Report: {month_name}", title_style))
    story.append(Paragraph(f"Generated on {datetime.date.today().strftime('%B %d, %Y')}", ParagraphStyle('Date', fontName='Times-Roman', fontSize=10, spaceAfter=20)))
    
    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    summary_text = (
        f"During the month of {month_name}, the FOREST-AI system processed satellite telemetries for the Wilpattu Forest Reserve. "
        f"A total of <b>{total_alerts} deforestation disturbances</b> were detected and cataloged. "
        f"The cumulative forest cover affected stands at <b>{total_area_ha} hectares</b>, "
        f"with a neural verification confidence score averaging <b>{avg_confidence}%</b>. "
        f"Additionally, <b>{risks.count()} high-vulnerability corridors</b> were flagged for preventative patrolling."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))
    
    # Stats table
    stats_data = [
        [Paragraph("<b>Metric</b>", table_header_style), Paragraph("<b>Value</b>", table_header_style)],
        [Paragraph("Target Period", table_body_style), Paragraph(month_name, table_body_style)],
        [Paragraph("Total Deforestation Detections", table_body_style), Paragraph(str(total_alerts), table_body_style)],
        [Paragraph("Total Canopy Area Cleared", table_body_style), Paragraph(f"{total_area_ha} ha", table_body_style)],
        [Paragraph("Average Detection Confidence", table_body_style), Paragraph(f"{avg_confidence}%", table_body_style)],
        [Paragraph("High-Risk Vulnerability Areas", table_body_style), Paragraph(str(risks.count()), table_body_style)],
    ]
    stats_table = Table(stats_data, colWidths=[250, 150])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#15803d")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 15))
    
    # Section 2: Detailed Disturbance Logs
    story.append(Paragraph("2. Verified Disturbance Detections", h1_style))
    if total_alerts > 0:
        dist_data = [
            [
                Paragraph("<b>Area ID</b>", table_header_style),
                Paragraph("<b>Date</b>", table_header_style),
                Paragraph("<b>NDVI Change</b>", table_header_style),
                Paragraph("<b>Area affected</b>", table_header_style),
                Paragraph("<b>Severity</b>", table_header_style),
            ]
        ]
        for dist in disturbances[:25]:  # Limit to top 25 records to keep report concise
            dist_data.append([
                Paragraph(dist.area_id, table_body_style),
                Paragraph(dist.detection_date.strftime("%Y-%m-%d"), table_body_style),
                Paragraph(str(dist.ndvi_change), table_body_style),
                Paragraph(f"{round(dist.area_m2 / 10000.0, 3)} ha", table_body_style),
                Paragraph(dist.severity.upper(), table_body_style),
            ])
        
        dist_table = Table(dist_data, colWidths=[80, 80, 80, 80, 80])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(dist_table)
    else:
        story.append(Paragraph("No disturbances logged for this month.", body_style))
        
    story.append(PageBreak())
    
    # Section 3: High Risk Predictive Anomalies
    story.append(Paragraph("3. High-Risk Predictive Corridors", h1_style))
    if risks.exists():
        risk_data = [
            [
                Paragraph("<b>Area ID</b>", table_header_style),
                Paragraph("<b>Threat Score</b>", table_header_style),
                Paragraph("<b>Road Proximity</b>", table_header_style),
                Paragraph("<b>Village Proximity</b>", table_header_style),
                Paragraph("<b>Protected Area</b>", table_header_style),
            ]
        ]
        for r in risks[:20]:
            risk_data.append([
                Paragraph(r.area_id, table_body_style),
                Paragraph(str(r.risk_score), table_body_style),
                Paragraph(f"{round(r.road_distance_m)} m", table_body_style),
                Paragraph(f"{round(r.village_distance_m)} m", table_body_style),
                Paragraph("YES" if r.protected_area else "NO", table_body_style),
            ])
            
        risk_table = Table(risk_data, colWidths=[80, 80, 80, 80, 80])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(risk_table)
    else:
        story.append(Paragraph("No predictive risk threats flagged in this period.", body_style))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
