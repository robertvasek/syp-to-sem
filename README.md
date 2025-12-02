# Modern Invoice Generator (CZ)

A Python-based tool that generates professional, modern PDF invoices with **Czech QR Payment** support (SPAD standard). It uses environment variables for configuration and a CSV file for line items, making it easy to automate billing.

## ✨ Features

- **QR Payment Ready:** Automatically generates a valid Czech QR code (SPAD format) for instant banking app payments.
- **Automated Math:** Calculates line item totals and grand totals automatically.
- **Configurable:** Uses `.env` for sender/recipient details (keeps your sensitive data out of the code).
- **Unicode Support:** Designed to handle Czech characters (requires `DejaVuSans.ttf` which is attached in repo - kudos to [DeJaVu](https://dejavu-fonts.github.io/)).

## 🛠️ Prerequisites

- **Python 3.10+**
- **Font File:** You need `DejaVuSans.ttf` in the project root to support Czech characters (č, ř, ž). You can download it [here](https://dejavu-fonts.github.io/).

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/robertvasek/syp-to-sem.git
   cd syp-to-sem
   ```

2. **Install dependencies:**
   *Note: This project uses modern FPDF features. Ensure you install `fpdf2`.*
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### 1. Environment Variables (`.env`)
Create a file named `.env` (just copy .env.example and rename it) and **fill in your actual details.**

### 2. Line Items (`items.csv`)
Create a file named `items.csv` in the root directory. This defines what you are billing for.

**Format:**
```csv
description,quantity,unit,price_per_unit
Konzultace a vývoj software,10,hod,1500
Správa serveru,1,ks,2000
Hosting roční poplatek,1,rok,1200
```

## 🚀 Usage

Run the script from your terminal:

```bash
python main.py
```
popř.
```bash
python3 main.py
```

**The script will:**
1. Read your configuration and CSV items.
2. Generate a unique QR code.
3. Create a PDF named `faktura_<PREFIX><MMDD>.pdf` (e.g., `faktura_20251202.pdf`).
4. Clean up temporary image files.

## 📂 Project Structure

```text
.
├── main.py            # The generator script
├── .env               # Your config (DO NOT commit this to git)
├── items.csv          # List of items to bill
├── DejaVuSans.ttf     # Font file (Required for CZ chars)
└── README.md          # This file
```

## ⚠️ Notes

- **VAT (DPH):** The script currently hardcodes the text "Nejsem plátce DPH" in the footer. If you are a VAT payer, update line 263 in `main.py`.
- **Variable Symbol:** The Variable Symbol (VS) is automatically generated based on the `INVOICE_PREFIX` + current `MMDD`.

## 📄 License

MIT
