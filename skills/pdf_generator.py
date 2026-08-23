# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_weekly_pdf(report_data, output_path="weekly_report.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor('#1E293B'), spaceAfter=8)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#64748B'), spaceAfter=15)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=8)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    story.append(Paragraph("PROJECT OMEGA - WEEKLY PERFORMANCE REPORT", title_style))
    story.append(Paragraph(f"<b>Reporting Period:</b> {report_data['start_date']} to {report_data['end_date']} (Excludes Sat/Sun)", subtitle_style))
    story.append(Spacer(1, 10))

    metrics_data = [
        ["Total Trades", "Winning Trades", "Losing Trades", "Win Rate (%)", "Net Profit/Loss ($)"],
        [
            str(report_data['total_trades']),
            str(report_data['wins']),
            str(report_data['losses']),
            f"{report_data['win_rate']:.1f}%",
            f"${report_data['net_pnl']:+.2f}"
        ]
    ]
    
    t_metrics = Table(metrics_data, colWidths=[100, 100, 100, 100, 120])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Weekly Executions & Signal Predictions", section_style))
    
    trades_table_data = [["Symbol", "Action", "Predicted TP", "Actual Exit", "PnL ($)", "Status"]]
    for t in report_data['trades']:
        trades_table_data.append([
            t['symbol'],
            t['action'],
            f"${t['predicted_tp']:.2f}",
            f"${t['actual_exit']:.2f}",
            f"${t['pnl']:+.2f}",
            t['status']
        ])

    t_trades = Table(trades_table_data, colWidths=[80, 70, 110, 110, 90, 80])
    t_trades.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_trades)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Technical Remarks & Strategy Analysis", section_style))
    story.append(Paragraph(report_data['remarks'], body_style))

    doc.build(story)
    return output_path
