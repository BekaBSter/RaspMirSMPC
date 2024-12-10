import imgkit
from Settings import out


def html_to_png(html_input, output_path):
    options = {
        'format': 'png',
        'quality': '50',
        'width': 1024
    }
    try:
        imgkit.from_string(html_input, output_path, options=options)
        out(f"Конвертация: PNG успешно сохранен в: {output_path}", "g")
    except Exception as e:
        out(f"Конвертация: Ошибка при конвертации HTML в PNG: {e}", "r")