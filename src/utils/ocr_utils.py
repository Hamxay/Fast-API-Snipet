import easyocr


def get_reader_lang(lang=("ar", "en")):
    reader = easyocr.Reader(list(lang))
    return reader


async def extract_imag_text(image, lang=("ar", "en")):
    reader = get_reader_lang(lang)
    result = reader.readtext(image, detail=0)
    return result
