import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape
from typing import Dict, Any


class PDFService:
    @staticmethod
    def _to_text(value: Any, fallback: str = "") -> str:
        if value is None:
            return fallback
        if isinstance(value, dict):
            parts = []
            for key, item in value.items():
                parts.append(f"{key}: {PDFService._to_text(item)}")
            return "; ".join(parts) if parts else fallback
        if isinstance(value, list):
            return "; ".join(PDFService._to_text(item) for item in value if item is not None)
        # Helvetica cannot render ₹; normalize currency for PDF output
        return str(value).replace("₹", "Rs.").replace("Rs.Rs.", "Rs.")

    @staticmethod
    def _safe_paragraph(text: Any, style, fallback: str = "") -> Paragraph:
        raw = PDFService._to_text(text, fallback)
        # ReportLab Paragraph uses a mini-HTML subset; escape raw content first.
        safe = escape(raw).replace("\n", "<br/>")
        return Paragraph(safe, style)

    @staticmethod
    def generate_pdf(report_json: Dict[str, Any], overall_score: float) -> bytes:
        # Support both flat report payloads and nested {"report": {...}} shapes
        payload = report_json.get("report") if isinstance(report_json.get("report"), dict) else report_json
        if not isinstance(payload, dict):
            payload = {}

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
        story.append(Paragraph(
            f"<b>Overall Strategy Confidence Score:</b> {overall_score:.1f}/100.0",
            body_style
        ))
        story.append(Spacer(1, 10))
        
        # 2. Executive Summary
        story.append(Paragraph("1. Executive Summary", h1_style))
        story.append(PDFService._safe_paragraph(
            payload.get("executive_summary"),
            body_style,
            "No executive summary available."
        ))
        
        # 3. Carbon Analysis Summary
        story.append(Paragraph("2. Carbon Footprint Analysis", h1_style))
        carbon_text = payload.get("carbon_analysis", "")
        if carbon_text:
            story.append(PDFService._safe_paragraph(carbon_text, body_style))
            
        # 4. Recommendations Table
        story.append(Paragraph("3. Recommended Sustainability Measures", h1_style))
        recs = payload.get("recommendations", [])
        if not isinstance(recs, list):
            recs = [recs] if recs else []
        
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
                    sdg_values = rec.get("sdg", [])
                    if isinstance(sdg_values, list):
                        sdgs = ", ".join(f"SDG {s}" for s in sdg_values)
                    else:
                        sdgs = PDFService._to_text(sdg_values, "SDG 12, SDG 13")
                else:
                    title = str(rec)
                    sdgs = "SDG 12, SDG 13"
                
                table_data.append([
                    PDFService._safe_paragraph(title, body_style),
                    PDFService._safe_paragraph(sdgs, body_style),
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
        story.append(PDFService._safe_paragraph(
            payload.get("financial_summary"),
            body_style,
            "No financial details available."
        ))
        
        # 6. Implementation roadmap
        story.append(Paragraph("5. Phased Implementation Roadmap", h1_style))
        roadmap_text = payload.get("implementation_plan", "")
        if roadmap_text:
            story.append(PDFService._safe_paragraph(roadmap_text, body_style))
            
        # 7. Next Steps Checklist
        story.append(Paragraph("6. Immediate Strategic Next Steps", h1_style))
        next_steps = payload.get("next_steps", [])
        if not isinstance(next_steps, list):
            next_steps = [next_steps] if next_steps else []
        if not next_steps:
            story.append(Paragraph("- Engage stakeholders and request quotes.", body_style))
        else:
            for step in next_steps:
                story.append(PDFService._safe_paragraph(f"- {PDFService._to_text(step)}", body_style))
                
        # Build document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
