import PyPDF2
reader = PyPDF2.PdfReader('catalyst_csv_bundle/a153cff8-2d99-401c-ac79-91ca6061b981.pdf')
out = ''
for p in reader.pages:
    out += p.extract_text() + '\n'
with open('c:/Users/Admin/OneDrive/Desktop/KSP/backend/pdf_text.txt', 'w', encoding='utf-8') as f:
    f.write(out)
