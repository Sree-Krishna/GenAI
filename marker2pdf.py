from marker.convert import convert_single_pdf
from marker.models import load_all_models

fpath = "data/das.pdf"
# fpath = "data/Sree_Krishna_Resume_Infosys.pdf"
model_lst = load_all_models()
full_text, images, out_meta = convert_single_pdf(fpath, model_lst, ocr_all_pages=False)
print(full_text)