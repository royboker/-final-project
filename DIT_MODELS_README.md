# DiT Model Weights — Download Instructions

The 6 DiT (Document Image Transformer) model weights are **not included in git** because each file is ~329 MB, exceeding GitHub's 100 MB hard limit. Download them from Google Drive and place them in the locations listed below.

## Google Drive

Folder: https://drive.google.com/drive/folders/1miR59JG3T531GdpBVp8-AHc9UyuxOpuS?usp=sharing

## Files & Destinations

Each model must be copied to **two locations** — `models/final_models/` (canonical) and the corresponding `notebooks/*/production/` directory (used by training/eval notebooks).

| # | Drive filename | Destinations |
|---|---|---|
| 1 | `dit_drivers_license_binary_15k.pth` | `models/final_models/dit_drivers_license_binary_15k.pth`<br>`notebooks/drivers_license_forgery/production/dit_binary_15k.pth` |
| 2 | `dit_drivers_license_fraud_type_15k.pth` | `models/final_models/dit_drivers_license_fraud_type_15k.pth`<br>`notebooks/drivers_license_forgery/production/dit_fraud_type_15k.pth` |
| 3 | `dit_id_card_binary_20k.pth` | `models/final_models/dit_id_card_binary_20k.pth`<br>`notebooks/id_card_forgery/production/dit_binary_20k.pth` |
| 4 | `dit_id_card_fraud_type_20k.pth` | `models/final_models/dit_id_card_fraud_type_20k.pth`<br>`notebooks/id_card_forgery/production/dit_fraud_type_20k.pth` |
| 5 | `dit_passport_binary_20k.pth` | `models/final_models/dit_passport_binary_20k.pth`<br>`notebooks/passport_forgery/production/dit_binary_20k.pth` |
| 6 | `dit_passport_fraud_type_20k.pth` | `models/final_models/dit_passport_fraud_type_20k.pth`<br>`notebooks/passport_forgery/production/dit_fraud_type_20k.pth` |

## Notes

- File size: ~329 MB each (~2 GB total).
- Note the filename difference: Drive files are prefixed `dit_<doctype>_...`; notebook copies drop the doctype (e.g. `dit_binary_15k.pth`).
- These paths are listed in `.gitignore` so they will never be committed accidentally.
