from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from datetime import datetime
import os

from repositories.customer_repository import CustomerRepository


def export_account_statement(
    account,
    customer,
    date_from=None,
    date_to=None,
    directory="exports"
):
    """
    account     : Account objektum
    customer    : Customer objektum
    date_from   : datetime vagy None
    date_to     : datetime vagy None
    directory   : mentési könyvtár
    """

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = f"bank_kivonat_{account.account_number}.pdf"
    file_path = os.path.join(directory, filename)

    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []
    styles = getSampleStyleSheet()

    # ===== FEJLÉC =====
    elements.append(Paragraph("<b>BANKI SZÁMLAKIVONAT</b>", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Ügyfél neve: {customer.name}", styles["Normal"]))
    elements.append(Paragraph(f"Anyja neve: {customer.mothers_maiden_name}", styles["Normal"]))
    elements.append(Paragraph(f"Lakcím: {customer.address["post_code"]}. {customer.address["city"]}, {customer.address["street"]} {customer.address["house_number"]}. {customer.address["floor"]}/{customer.address["door_number"]}.", styles["Normal"]))
    elements.append(Paragraph(f"Számlaszám: {account.account_number}", styles["Normal"]))

    if date_from and date_to:
        elements.append(
            Paragraph(
                f"Időszak: {date_from.strftime('%Y-%m-%d')} - {date_to.strftime('%Y-%m-%d')}",
                styles["Normal"]
            )
        )
    else:
        elements.append(
            Paragraph(
                f"Kivonat dátuma: {datetime.now().strftime('%Y-%m-%d')}",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.3 * inch))

    # ===== SZŰRÉS =====
    transactions = account.transactions

    if date_from and date_to:
        filtered = []
        for t in transactions:
            t_date = datetime.strptime(t.timestamp, "%Y-%m-%d %H:%M:%S")
            if date_from <= t_date <= date_to:
                filtered.append(t)
        transactions = filtered

    # ===== TÁBLA =====
    data = [["Dátum", "Típus", "Partner neve", "Számlaszám", "Összeg (Ft)"]]

    total_income = 0
    total_expense = 0

    sorted_transactions = sorted(
        transactions,
        key=lambda x: x.timestamp
    )

    for t in sorted_transactions:

        # 🔹 Partner név lookup ID alapján
        partner = CustomerRepository.find_by_id(t.name)
        partner_name = partner.name if partner else "Ismeretlen"

        amount_str = f"{t.amount:,.0f}".replace(",", ".")

        data.append([
            t.timestamp,
            t.type,
            partner_name,
            t.account_number,
            amount_str
        ])

        if t.amount >= 0:
            total_income += t.amount
        else:
            total_expense += t.amount

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (3, 1), (3, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # ===== ÖSSZESÍTÉS =====
    summary_data = [
        ["Bevételek összesen:",
         f"{total_income:,.0f}".replace(",", ".") + " Ft"],
        ["Kiadások összesen:",
         f"{total_expense:,.0f}".replace(",", ".") + " Ft"],
        ["Záró egyenleg:",
         f"{account.balance:,.0f}".replace(",", ".") + " Ft"]
    ]

    summary_table = Table(summary_data, colWidths=[300, 150])

    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))

    elements.append(summary_table)

    doc.build(elements)

    return file_path
