from pathlib import Path

DATA_DIR_PATH = Path('wat_data')
TIMETABLE_URL = 'https://planzajec.wcy.wat.edu.pl/pl/rozklad?grupa_id={group}'
CALENDAR_PDF_FP = (
    DATA_DIR_PATH
    / 'zal._nr_1_organizacja_zajec_w_roku_akademickim_2024_2025_na_studiach_stacjonarnych.pdf'
)
STRUCTURED_PDF_FP = DATA_DIR_PATH / 'informator_dla_studentow_1_roku_2024.pdf'
