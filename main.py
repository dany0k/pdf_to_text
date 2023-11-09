import os
import shutil
import pytesseract
from PIL import Image
import fitz
import argparse
import random
import string


def to_text(cur_pic):
    pytesseract.pytesseract.tesseract_cmd = 'D:/Tesseract/tesseract.exe'
    img = Image.open(cur_pic)
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 128 else 255, '1')
    img.save('preprocessed_image.png')
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string('preprocessed_image.png', lang='rus', config=custom_config)
    return text


def convert(path):
    pdf_document = path
    pdf = fitz.open(pdf_document)
    page_count = pdf.page_count
    for page_number in range(page_count):
        page = pdf[page_number]
        image_list = page.get_images(full=True)
        for img_index, img_info in enumerate(image_list):
            print(f"Converting {img_info[7]} from {page_count}")
            xref = img_info[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_file = f"img/raw/{page_number + 1}.png"
            with open(image_file, "wb") as img_out:
                img_out.write(image_bytes)
    pdf.close()
    return page_count


def divide_single_img(cur_pic):
    img = Image.open(f'img/raw/{cur_pic}.png')
    width, height = img.size
    if width < 2000:
        img.save(f'img/data/{cur_pic}_single.png')
        return
    half_width = width // 2
    left_half = img.crop((0, 0, half_width, height))
    right_half = img.crop((half_width, 0, width, height))
    left_half.save(f'img/data/{cur_pic}_left_half.png')
    right_half.save(f'img/data/{cur_pic}_right_half.png')


def divide_all(size):
    for i in range(1, size):
        perc = (i + 1) / size * 100
        print(f"Dividing twin pages: {perc:.2f}%")
        divide_single_img(i)
    return size * 2


def to_text_all(size):
    result = ''
    current_page = 1
    for i in range(1, size - 1):
        perc = (i + 1) / size * 100
        print(f'Current page: {i}\n{perc:.2f}%\n')
        try:
            result += f"\n======================================= {current_page} стр. =======================================\n"
            current_page += 1
            result += to_text(f'img/data/{i}_left_half.png')
            result += f"\n======================================= {current_page} стр. =======================================\n"
            current_page += 1
            result += to_text(f'img/data/{i}_right_half.png')
        except:
            result += f"\n======================================= {current_page} стр. =======================================\n"
            result += to_text(f'img/data/{i}_single.png')
            continue
    return result


def process(path):
    raw_size = convert(path)
    divide_all(raw_size)
    file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    with open(f'./out/{file_name}.txt', 'w') as text_file:
        text_file.write(to_text_all(raw_size))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDF to images')
    parser.add_argument('-f', help='Path to the PDF file')
    args = parser.parse_args()
    pdf_file_path = args.f
    try:
        shutil.rmtree('./img')
    except:
        print("Remove files")
    try:
        os.mkdir('./out')
    except:
        print()
    os.mkdir('./img')
    os.mkdir('./img/raw')
    os.mkdir('./img/data')
    process(pdf_file_path)
    os.remove('preprocessed_image.png')
