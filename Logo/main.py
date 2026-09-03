"""Batch company sticker generator with a tkinter interface."""

from __future__ import annotations

import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import qrcode
from PIL import Image, ImageChops, ImageDraw, ImageFont

from companies import COMPANIES
from config import MY_INFO_URL

STICKER_WIDTH_CM = 10
STICKER_HEIGHT_CM = 6
DPI = 300
CM_TO_PX = DPI / 2.54
STICKER_WIDTH_PX = round(STICKER_WIDTH_CM * CM_TO_PX)
STICKER_HEIGHT_PX = round(STICKER_HEIGHT_CM * CM_TO_PX)
STICKER_WIDTH_PT = STICKER_WIDTH_CM / 2.54 * 72
STICKER_HEIGHT_PT = STICKER_HEIGHT_CM / 2.54 * 72
STICKER_PAGE_SIZE = (STICKER_WIDTH_PT, STICKER_HEIGHT_PT)
LOGO_BOX_SIZE = (round(4 * CM_TO_PX), round(2 * CM_TO_PX))
QR_SIZE_PX = round(2.35 * CM_TO_PX)
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MASTER_QR_NAME = "QR_code.png"
VALID_CV_TYPES = {"backend", "software_engineering"}


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return cleaned or "company"


def create_qr_code(url: str, destination: Path) -> None:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").convert("RGB").save(destination, "PNG")


def ensure_master_qr(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    master_path = output_dir / MASTER_QR_NAME
    if not master_path.is_file():
        create_qr_code(MY_INFO_URL, master_path)
    return master_path


def create_company_folder(output_dir: Path, company_name: str) -> tuple[Path, str]:
    filename = safe_filename(company_name)
    company_dir = output_dir / filename
    company_dir.mkdir(parents=True, exist_ok=True)
    return company_dir, filename


def process_logo(logo_path: Path) -> Image.Image:
    with Image.open(logo_path) as source:
        rgba = source.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema()[0] < 255:
        bbox = alpha.getbbox()
    else:
        difference = ImageChops.difference(rgba.convert("RGB"), Image.new("RGB", rgba.size, "white"))
        bbox = difference.point(lambda value: 0 if value < 12 else 255).getbbox()
    logo = rgba.crop(bbox) if bbox else rgba
    logo.thumbnail(LOGO_BOX_SIZE, Image.Resampling.LANCZOS)
    return logo


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_png(company_name: str, logo_path: Path, qr_path: Path, destination: Path) -> None:
    sticker = Image.new("RGB", (STICKER_WIDTH_PX, STICKER_HEIGHT_PX), "white")
    logo = process_logo(logo_path)
    logo_left = round(0.7 * CM_TO_PX) + (LOGO_BOX_SIZE[0] - logo.width) // 2
    logo_top = round(0.65 * CM_TO_PX) + (LOGO_BOX_SIZE[1] - logo.height) // 2
    sticker.paste(logo, (logo_left, logo_top), logo)

    draw = ImageDraw.Draw(sticker)
    title_size = round(0.43 * CM_TO_PX)
    title_font = get_font(title_size, bold=True)
    max_title_width = round(5.4 * CM_TO_PX)
    while title_size > 18 and draw.textbbox((0, 0), company_name, font=title_font)[2] > max_title_width:
        title_size -= 2
        title_font = get_font(title_size, bold=True)
    draw.text((round(0.7 * CM_TO_PX), round(3.05 * CM_TO_PX)), company_name, fill="#1F2933", font=title_font)

    with Image.open(qr_path) as master_qr:
        qr = master_qr.convert("RGB")
        qr.thumbnail((QR_SIZE_PX, QR_SIZE_PX), Image.Resampling.NEAREST)
    qr_left = STICKER_WIDTH_PX - round(0.7 * CM_TO_PX) - qr.width
    sticker.paste(qr, (qr_left, round(0.75 * CM_TO_PX)))

    name = "Yousief Nassar Ahmed"
    name_font = get_font(round(0.3 * CM_TO_PX))
    name_width = draw.textbbox((0, 0), name, font=name_font)[2]
    name_left = max(round(0.7 * CM_TO_PX), STICKER_WIDTH_PX - round(0.7 * CM_TO_PX) - name_width)
    draw.text((name_left, round(5.25 * CM_TO_PX)), name, fill="#4B5563", font=name_font)
    sticker.save(destination, "PNG", dpi=(DPI, DPI))


def generate_pdf(image_path: Path, destination: Path) -> None:
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    page = canvas.Canvas(str(destination), pagesize=STICKER_PAGE_SIZE)
    page.drawImage(ImageReader(str(image_path)), 0, 0, width=STICKER_WIDTH_PT, height=STICKER_HEIGHT_PT)
    page.showPage()
    page.save()


def generate_cover(company: dict[str, str], logo_path: Path, output_dir: Path, master_qr: Path) -> tuple[Path, Path]:
    company_dir, filename = create_company_folder(output_dir, company["name"])
    png_path = company_dir / f"{filename}.png"
    pdf_path = company_dir / f"{filename}.pdf"
    temporary_png = company_dir / f".{filename}.png.tmp"
    temporary_pdf = company_dir / f".{filename}.pdf.tmp"
    try:
        generate_png(company["name"], logo_path, master_qr, temporary_png)
        generate_pdf(temporary_png, temporary_pdf)
        temporary_png.replace(png_path)
        temporary_pdf.replace(pdf_path)
    except Exception:
        for temporary_file in (temporary_png, temporary_pdf):
            if temporary_file.exists():
                temporary_file.unlink()
        raise
    return png_path, pdf_path


class CoverApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Company Cover Generator")
        self.root.geometry("700x620")
        self.logo_paths: dict[int, Path] = {}
        self.rows: list[dict[str, str]] = [dict(company) for company in COMPANIES]
        self.tree: ttk.Treeview
        self.progress = tk.DoubleVar()
        self.status = tk.StringVar(value=f"{len(self.rows)} confirmed companies loaded")
        self.build_ui()
        self.refresh()

    def build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Select companies, assign missing logos, then generate stickers.").pack(anchor="w", pady=(0, 10))
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)
        columns = ("company", "cv_type", "logo")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended", height=20)
        self.tree.heading("company", text="Company")
        self.tree.heading("cv_type", text="CV Type")
        self.tree.heading("logo", text="Logo Status")
        self.tree.column("company", width=280)
        self.tree.column("cv_type", width=170)
        self.tree.column("logo", width=150)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="Generate Selected", command=self.generate_selected).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Generate All", command=self.generate_all).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Choose Logo", command=self.choose_logo).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Progressbar(frame, variable=self.progress, maximum=100).pack(fill="x", pady=(16, 8))
        ttk.Label(frame, textvariable=self.status, wraplength=650).pack(anchor="w")

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, company in enumerate(self.rows):
            logo_path = self.logo_paths.get(index) or self.configured_logo(company)
            status = "✓ Selected" if logo_path and logo_path.is_file() else "Missing Logo"
            cv_label = "Backend" if company.get("cv_type") == "backend" else "Software Engineering"
            self.tree.insert("", "end", iid=str(index), values=(company["name"], cv_label, status))
        self.status.set(f"{len(self.rows)} confirmed companies loaded")

    def configured_logo(self, company: dict[str, str]) -> Path | None:
        value = company.get("logo", "").strip()
        if not value:
            return None
        path = Path(value)
        if not path.is_absolute():
            path = Path(__file__).resolve().parent / path
        return path

    def choose_logo(self) -> None:
        selection = self.tree.selection()
        if len(selection) != 1:
            messagebox.showerror("Choose one company", "Select exactly one company before choosing its logo.")
            return
        selected = filedialog.askopenfilename(title="Choose company logo", filetypes=[("Logo images", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")])
        if selected:
            index = int(selection[0])
            self.logo_paths[index] = Path(selected)
            self.refresh()
            self.tree.selection_set(str(index))

    def selected_indexes(self, all_companies: bool = False) -> list[int]:
        return list(range(len(self.rows))) if all_companies else [int(item) for item in self.tree.selection()]

    def generate_selected(self) -> None:
        indexes = self.selected_indexes()
        if not indexes:
            messagebox.showerror("No companies selected", "Select one or more companies first.")
            return
        self.generate_indexes(indexes)

    def generate_all(self) -> None:
        self.generate_indexes(self.selected_indexes(all_companies=True))

    def generate_indexes(self, indexes: list[int]) -> None:
        if not MY_INFO_URL.strip() or MY_INFO_URL == "PUT_MY_PUBLIC_MY_INFO_URL_HERE":
            messagebox.showerror("Missing My Info URL", "Set MY_INFO_URL in config.py before generating covers.")
            return
        output_dir = Path(__file__).resolve().parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        successful = 0
        failures: list[str] = []
        missing: list[str] = []
        self.progress.set(0)
        try:
            master_qr = ensure_master_qr(output_dir)
            for completed, index in enumerate(indexes, start=1):
                company = self.rows[index]
                logo_path = self.logo_paths.get(index) or self.configured_logo(company)
                if not logo_path or not logo_path.is_file() or logo_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    missing.append(company["name"])
                    self.progress.set(completed / len(indexes) * 100)
                    self.root.update_idletasks()
                    continue
                try:
                    generate_cover(company, logo_path, output_dir, master_qr)
                    successful += 1
                except Exception as error:
                    failures.append(f"{company['name']}: {error}")
                self.progress.set(completed / len(indexes) * 100)
                self.root.update_idletasks()
        except Exception as error:
            messagebox.showerror("Generation failed", str(error))
            return
        summary = ["Generation completed.", f"\nSuccessful: {successful}", f"Failed: {len(failures) + len(missing)}", f"Missing logos: {len(missing)}"]
        if missing:
            summary.append("\nMissing logos:\n- " + "\n- ".join(missing))
        if failures:
            summary.append("\nOther failures:\n- " + "\n- ".join(failures))
        self.status.set("".join(summary))
        messagebox.showinfo("Generation completed", "".join(summary))
        self.refresh()


def main() -> None:
    root = tk.Tk()
    CoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
