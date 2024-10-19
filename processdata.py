import PyPDF2, pdfplumber

# extract text from pdf using pypdf 
def extract_text_from_pypdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# extract text from pdf using pdfplumber
def extract_text_from_pdfplumber(pdf_path):
    try: 
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            hyperlinks = ''
            for page in pdf.pages:
                if len(page.hyperlinks):
                    for link in page.hyperlinks:
                        hyperlinks += link['uri'] + ' '
                if hyperlinks:
                    text += ' ' + hyperlinks
                    pass
                text +=  ' ' + page.extract_text() + ' '
            return text
    except:
        print('The file {pdf_path} cant be processed'.format(pdf_path=pdf_path))
        return ''