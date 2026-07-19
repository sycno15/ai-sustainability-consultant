import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import Dict, Any

class PDFService:
    @staticmethod
    def generate_pdf(report_json: Dict[str, Any], overall_score: float) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Define premium Forest/Emerald color theme
        primary_color = colors.HexColor("#065f46")   # Emerald-800
        secondary_color = colors.HexColor("#0f766e") # Teal-700
        text_color = colors.HexColor("#1e293b")      # Slate-800
        bg_light = colors.HexColor("#f8fafc")        # Slate-50
        border_color = colors.HexColor("#e2e8f0")    # Slate-200
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            name="DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=primary_color,
            spaceAfter=15
        )
        
        h1_style = ParagraphStyle(
            name="DocH1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=secondary_color,
            spaceBefore=15,
            spaceAfter=8,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            name="DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=text_color,
            spaceAfter=8
        )
        
        bold_body = ParagraphStyle(
            name="DocBoldBody",
            parent=body_style,
            fontName="Helvetica-Bold"
        )

        th_style = ParagraphStyle(
            name="TableHead",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.white
        )

        story = []
        
        # 1. Document Title & Score
        story.append(Paragraph("Sustainability Assessment Report", title_style))
        story.append(Paragraph(f"<b>Overall Strategy Confidence Score:</b> {overall_score:.1f}/100.0", body_style))
        story.append(Spacer(1, 10))
        
        # 2. Executive Summary
        story.append(Paragraph("1. Executive Summary", h1_style))
        summary_text = report_json.get("executive_summary", "No executive summary available.")
        story.append(Paragraph(summary_text, body_style))
        
        # 3. Carbon Analysis Summary
        story.append(Paragraph("2. Carbon Footprint Analysis", h1_style))
        carbon_text = report_json.get("carbon_analysis", "")
        if carbon_text:
            story.append(Paragraph(carbon_text, body_style))
            
        # 4. Recommendations Table
        story.append(Paragraph("3. Recommended Sustainability Measures", h1_style))
        recs = report_json.get("recommendations", [])
        
        if not recs:
            story.append(Paragraph("No specific recommendations generated.", body_style))
        else:
            # Build Table
            table_data = [[
                Paragraph("Measure Title", th_style),
                Paragraph("SDG Alignment", th_style)
            ]]
            for rec in recs:
                # Handle both string arrays and dict structures
                if isinstance(rec, dict):
                    title = rec.get("title", "")
                    sdgs = ", ".join(f"SDG {s}" for s in rec.get("sdg", []))
                else:
                    title = str(rec)
                    sdgs = "SDG 12, SDG 13"
                
                table_data.append([
                    Paragraph(title, body_style),
                    Paragraph(sdgs, body_style)
                ])
                
            rec_table = Table(table_data, colWidths=[380, 150])
            rec_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(rec_table)
            story.append(Spacer(1, 10))
            
        # 5. Financial Summary
        story.append(Paragraph("4. Financial Analysis & Payback Schedule", h1_style))
        fin_text = report_json.get("financial_summary", "No financial details available.")
        story.append(Paragraph(fin_text, body_style))
        
        # 6. Implementation roadmap
        story.append(Paragraph("5. Phased Implementation Roadmap", h1_style))
        roadmap_text = report_json.get("implementation_plan", "")
        if roadmap_text:
            story.append(Paragraph(roadmap_text, body_style))
            
        # 7. Next Steps Checklist
        story.append(Paragraph("6. Immediate Strategic Next Steps", h1_style))
        next_steps = report_json.get("next_steps", [])
        if not next_steps:
            story.append(Paragraph("- Engage stakeholders and request quotes.", body_style))
        else:
            for step in next_steps:
                story.append(Paragraph(f"• {step}", body_style))
                
        # Build document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
