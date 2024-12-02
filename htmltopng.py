import imgkit


def html_to_png(html_input, output_path):
    options = {
        'format': 'png',
        'quality': '50',
        'width': 1024
    }
    try:
        imgkit.from_string(html_input, output_path, options=options)
        print(f"PNG успешно сохранен в: {output_path}")
    except Exception as e:
        print(f"Ошибка при конвертации HTML в PNG: {e}")