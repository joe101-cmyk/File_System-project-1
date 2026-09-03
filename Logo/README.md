# Company Cover Generator

This tkinter app generates 10 cm x 6 cm landscape stickers for the confirmed companies in `companies.py`. It never opens, reads, copies, renames, or modifies CV files. The `cv_type` field is metadata only.

## Structure

```text
Logo/
├── main.py
├── companies.py
├── config.py
├── requirements.txt
├── my_info/
├── logos/
└── output/
```

There are currently 20 confirmed companies in the provided Route Tech Summit plan. No extra names were invented to reach 40. Add confirmed companies to `companies.py` when they become available.

## Company configuration

Keep the order in `companies.py`. Each entry has a name, CV metadata, and an optional logo path:

```python
{
    "name": "IBM",
    "cv_type": "software_engineering",
    "logo": "logos/IBM.png",
}
```

Use only `backend` or `software_engineering` for `cv_type`. An empty `logo` displays as Missing in the GUI. You can select a missing logo with **Choose Logo**; that selection is kept in memory for the current run and the original logo is never copied or modified.

## QR configuration

`config.py` contains the one global QR destination:

```python
MY_INFO_URL = "https://joe101-cmyk.github.io/"
```

The master QR is created once at `output/QR_code.png` and reused inside every company sticker. There is only one QR image file.

## Install and run

```bash
python -m pip install -r requirements.txt
python main.py
```

Select one or more rows and use **Generate Selected**, or use **Generate All**. **Refresh** reloads the table from `companies.py` while retaining logo selections made during the current session.

Each successful company is written to:

```text
output/Company_Name/Company_Name.png
output/Company_Name/Company_Name.pdf
```

The PNG is 1181 x 709 pixels at 300 DPI. The PDF is exactly 10 cm x 6 cm. Logos are proportionally fitted into a maximum 4 cm x 2 cm area, and the QR code is approximately 2.35 cm square.
