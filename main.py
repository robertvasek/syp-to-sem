import os
from datetime import datetime, timedelta
import pandas as pd
import qrcode
from fpdf import FPDF
from fpdf.enums import XPos, YPos  # ADDED: Required for new syntax
from dotenv import load_dotenv

load_dotenv()

# --- DESIGN CONFIGURATION (Modern Palette) ---
COLOR_PRIMARY = (41, 58, 74)  # Deep Navy (Header/Text)
COLOR_ACCENT = (52, 152, 219)  # Bright Blue (Highlights)
COLOR_TEXT_MUTED = (149, 165, 166)  # Concrete Gray (Labels)
COLOR_DIVIDER = (236, 240, 241)  # Light Gray (Lines)
COLOR_BG_LIGHT = (250, 251, 252)  # Off-white (Backgrounds)


class ModernInvoicePDF(FPDF):
    def __init__(self, font_path='DejaVuSans.ttf'):
        super().__init__()
        self.font_path = font_path
        self.font_family = 'DejaVu'

        # Check if font exists
        if not os.path.exists(self.font_path):
            print(f"⚠️  WARNING: Font file '{self.font_path}' not found!")
            self.font_family = 'Arial'
        else:
            self.add_font(self.font_family, '', self.font_path)

    def header(self):
        # We will draw the header manually in the create_invoice function
        # to allow for a full-width banner effect on the first page.
        pass

    def footer(self):
        self.set_y(-25)
        self.set_font(self.font_family, '', 8)
        self.set_text_color(*COLOR_TEXT_MUTED)

        # Elegant footer line
        self.set_draw_color(*COLOR_DIVIDER)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

        repo_url = "https://github.com/robertvasek/syp-to-sem"
        # Changed ln=1 to new_x/new_y
        self.cell(0, 5, f'Generováno automaticky | {repo_url}', 0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=repo_url)
        # Changed ln=0 to new_x/new_y
        self.cell(0, 5, f'Strana {self.page_no()}', 0, align='C', new_x=XPos.RIGHT, new_y=YPos.TOP)

    def draw_label_value(self, label, value, w=45, new_line=False):
        """Helper to draw a small gray label and a larger value below it."""
        current_x = self.get_x()
        current_y = self.get_y()

        self.set_font(self.font_family, '', 7)
        self.set_text_color(*COLOR_TEXT_MUTED)
        # Changed ln=2 to new_x=XPos.LEFT, new_y=YPos.NEXT
        self.cell(w, 4, label.upper(), 0, align='L', new_x=XPos.LEFT, new_y=YPos.NEXT)

        self.set_font(self.font_family, '', 10)
        self.set_text_color(*COLOR_PRIMARY)
        # Changed ln=0 to new_x=XPos.RIGHT, new_y=YPos.TOP
        self.cell(w, 6, str(value), 0, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)

        if new_line:
            self.ln(12)  # Move down for next row
        else:
            self.set_xy(current_x + w, current_y)


def generate_qr_string(iban, bic, amount, vs, message="Faktura"):
    clean_iban = iban.replace(" ", "").upper()
    amount_str = f"{amount:.2f}"
    acc_str = clean_iban
    if bic and len(bic) > 3:
        acc_str += f"+{bic.upper()}"
    return f"SPD*1.0*ACC:{acc_str}*AM:{amount_str}*CC:CZK*X-VS:{vs}*MSG:{message}"


def create_invoice():
    # 1. Load Data
    try:
        my_name = os.getenv("MY_NAME")
        my_street = os.getenv("MY_STREET")
        my_city = os.getenv("MY_CITY")
        my_ico = os.getenv("MY_ICO")
        my_iban = os.getenv("MY_IBAN")
        my_acc_no = os.getenv("MY_ACC_NUMBER_DISPLAY", my_iban)
        my_swift = os.getenv("MY_SWIFT", "")
        my_bank = os.getenv("MY_BANK_NAME")
        my_reg = os.getenv("MY_REGISTRATION")

        client_name = os.getenv("CLIENT_NAME")
        client_street = os.getenv("CLIENT_STREET")
        client_city = os.getenv("CLIENT_CITY")
        client_ico = os.getenv("CLIENT_ICO")
        client_dic = os.getenv("CLIENT_DIC")

        invoice_prefix = os.getenv("INVOICE_PREFIX", datetime.now().year)
        due_days = int(os.getenv("DUE_DAYS", "14"))

        df = pd.read_csv('items.csv')
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Calculations
    now = datetime.now()
    invoice_number = f"{invoice_prefix}{now.strftime('%m%d')}"
    date_issue = now.strftime("%d. %m. %Y")
    date_due = (now + timedelta(days=due_days)).strftime("%d. %m. %Y")

    df['total'] = df['quantity'] * df['price_per_unit']
    grand_total = df['total'].sum()

    # QR Code
    qr_data = generate_qr_string(my_iban, my_swift, grand_total, invoice_number, f"Faktura {invoice_number}")
    qr_img = qrcode.make(qr_data)
    qr_filename = "temp_qr.png"
    qr_img.save(qr_filename)

    # 2. PDF Generation
    pdf = ModernInvoicePDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # --- TOP BANNER ---
    pdf.set_fill_color(*COLOR_PRIMARY)
    pdf.rect(0, 0, 210, 45, 'F')

    pdf.set_y(15)
    pdf.set_text_color(255, 255, 255)

    # Title Left
    pdf.set_font(pdf.font_family, '', 26)
    # Changed ln=0
    pdf.cell(100, 10, "FAKTURA", 0, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)

    # Invoice Number Right
    pdf.set_font(pdf.font_family, '', 14)
    # Changed ln=1
    pdf.cell(90, 10, f"Č. {invoice_number}", 0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(25)  # Spacing after banner

    # --- ADDRESS SECTION (Grid Layout) ---
    y_addresses = pdf.get_y()

    # Column 1: DODAVATEL (Left)
    pdf.set_font(pdf.font_family, '', 8)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    # Changed ln=1
    pdf.cell(90, 5, "DODAVATEL", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font(pdf.font_family, '', 11)
    pdf.set_text_color(*COLOR_PRIMARY)
    # Changed ln=1
    pdf.cell(90, 6, my_name, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font(pdf.font_family, '', 10)
    pdf.set_text_color(60, 60, 60)
    # Changed ln=1
    pdf.cell(90, 5, my_street, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Changed ln=1
    pdf.cell(90, 5, my_city, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.set_font(pdf.font_family, '', 9)
    # Changed ln=1
    pdf.cell(90, 5, f"IČ: {my_ico}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    y_left_bottom = pdf.get_y()

    # Column 2: ODBĚRATEL (Right)
    pdf.set_xy(110, y_addresses)
    pdf.set_font(pdf.font_family, '', 8)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    # Changed ln=1
    pdf.cell(90, 5, "ODBĚRATEL", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Fix: Force X back to 110 after each new line
    pdf.set_x(110)
    pdf.set_font(pdf.font_family, '', 11)
    pdf.set_text_color(0)
    # Changed ln=1
    pdf.cell(90, 6, client_name, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(110)
    pdf.set_font(pdf.font_family, '', 10)
    pdf.set_text_color(60, 60, 60)
    # Changed ln=1
    pdf.cell(90, 5, client_street, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(110)
    # Changed ln=1
    pdf.cell(90, 5, client_city, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)

    pdf.set_x(110)
    pdf.set_font(pdf.font_family, '', 9)
    # Changed ln=1
    pdf.cell(90, 5, f"IČ: {client_ico}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if client_dic:
        pdf.set_x(110)
        # Changed ln=1
        pdf.cell(90, 5, f"DIČ: {client_dic}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Re-align below longest column
    pdf.set_y(max(y_left_bottom, pdf.get_y()) + 15)

    # --- KEY DATES & BANK STRIP ---
    # Draw a rounded-look background (simulated)
    pdf.set_fill_color(*COLOR_BG_LIGHT)
    pdf.rect(10, pdf.get_y(), 190, 22, 'F')

    pdf.set_y(pdf.get_y() + 5)
    start_x = 15
    pdf.set_x(start_x)

    # Use helper to draw label/value pairs horizontally
    pdf.draw_label_value("DATUM VYSTAVENÍ", date_issue, w=40)
    pdf.draw_label_value("DATUM SPLATNOSTI", date_due, w=40)
    pdf.draw_label_value("BANKA", my_bank, w=50)
    pdf.draw_label_value("ČÍSLO ÚČTU", my_acc_no, w=60)  # IBAN is long

    pdf.ln(25)

    # --- TABLE ---
    # Header
    pdf.set_font(pdf.font_family, '', 8)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    # Changed ln=0
    pdf.cell(90, 8, "POPIS POLOŽKY", "B", align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
    # Changed ln=0
    pdf.cell(30, 8, "MNOŽSTVÍ", "B", align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
    # Changed ln=0
    pdf.cell(35, 8, "CENA/J.", "B", align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
    # Changed ln=1
    pdf.cell(35, 8, "CELKEM", "B", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Rows
    pdf.set_font(pdf.font_family, '', 10)
    pdf.set_text_color(*COLOR_PRIMARY)

    for index, row in df.iterrows():
        # Padding top
        pdf.ln(2)

        desc = str(row['description'])
        qty = f"{row['quantity']} {row['unit']}"
        price = f"{row['price_per_unit']:.0f} Kč"
        total = f"{row['total']:.0f} Kč"

        # Changed ln=0
        pdf.cell(90, 8, desc, 0, align='L', new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Changed ln=0
        pdf.cell(30, 8, qty, 0, align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Changed ln=0
        pdf.cell(35, 8, price, 0, align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        # Changed ln=1
        pdf.cell(35, 8, total, 0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Divider line
        y_line = pdf.get_y()
        pdf.set_draw_color(245, 245, 245)
        pdf.line(10, y_line, 200, y_line)

    pdf.ln(10)

    # --- FOOTER SECTION (Totals & QR) ---
    y_footer = pdf.get_y()

    # Left: QR Code + Reg Info
    if y_footer + 50 > 270:  # Check for page break
        pdf.add_page()
        y_footer = pdf.get_y()

    pdf.image(qr_filename, x=10, y=y_footer, w=40)

    # Registration info next to QR (small)
    pdf.set_xy(55, y_footer)
    pdf.set_font(pdf.font_family, '', 7)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    pdf.multi_cell(60, 3, my_reg + "\n\nNejsem plátce DPH.")

    # Right: Total Amount
    pdf.set_xy(120, y_footer)
    pdf.set_font(pdf.font_family, '', 10)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    # Changed ln=1
    pdf.cell(80, 8, "CELKEM K ÚHRADĚ", 0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(120)
    pdf.set_font(pdf.font_family, '', 24)
    pdf.set_text_color(*COLOR_PRIMARY)
    total_str = f"{grand_total:,.2f} Kč".replace(",", " ").replace(".", ",")
    # Changed ln=1
    pdf.cell(80, 12, total_str, 0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Variable symbol below total
    pdf.set_x(120)
    pdf.set_font(pdf.font_family, '', 9)
    pdf.set_text_color(*COLOR_TEXT_MUTED)
    # Changed ln=1
    pdf.cell(80, 6, f"Var. symbol: {invoice_number}", 0, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Cleanup
    try:
        os.remove(qr_filename)
    except:
        pass

    output_filename = f"faktura_{invoice_number}.pdf"
    pdf.output(output_filename)
    print(f"✅ Modern Invoice generated: {output_filename}")


if __name__ == "__main__":
    create_invoice()