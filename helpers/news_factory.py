import os
import random
import requests
from pathlib import Path
from faker import Faker
from PIL import Image, ImageDraw

def generate_image(
        width: int | None = 800,
        height: int | None = 600,
        folder: str | None = None,
) -> str:
    """
        Генерация изображения.

        Args:
            width (int): Ширина изображения. По умолчанию 800.
            height (int): Высота изображения. По умолчанию 600.
            folder (str): Папка для сохранения. Если не указать папку, в функции будет создана ссылка на папку temp в корне проекта.

        Returns:
            str: Путь, в который было сохранено изображение.
    """
    if folder is None:
        folder = Path(__file__).parent.parent / "temp"
        folder.mkdir(parents=True, exist_ok=True)


    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width - 1, height - 1], outline="black", width=2)

    save_path = os.path.join(folder, f"gen_{random.randint(0, 1000)}.png")
    img.save(save_path, "PNG")
    return save_path

def download_image(
        faker: Faker,
        width: int | None = 800,
        height: int | None = 600,
        folder: str | None = None,
    ) -> str:
    """
        Скачивание изображения из Faker

        Args:
            faker (Faker): Экземпляр библиотеки Faker для генерации данных. (Обязательный).
            width (int): Ширина изображения в пикселях. По умолчанию 800
            height (int): Высота изображения. По умолчанию 600
            folder (str): Папка для сохранения. Если не указать папку, в функции будет создана ссылка на папку temp в корне проекта.

        Returns:
            str: Путь, в который было сохранено изображение.

        Raises:
            Exception: возникает если Faker не нашёл изображение по тем или иным сетевым причинам.
    """
    if folder is None:
        folder = Path(__file__).parent.parent / "temp"
        folder.mkdir(parents=True, exist_ok=True)

    url = faker.image_url(width=width, height=height)

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to download image: {response.status_code}")

    filename = f"{faker.uuid4()}.jpg"
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as f:
        f.write(response.content)

    return os.path.abspath(filepath)

def generate_news(
        faker: Faker,
        words_title: int | None = 5,
        words_subtitle: int | None = 5,
        sentences_count: int | None = 3,
        tags_count: int | None = 5,
        img_width: int = 800,
        img_height: int = 600,
        exclude: tuple[str] | None = None
) -> dict:
    """
        Генерация новости.

        Args:
            faker (Faker): Экземпляр библиотеки Faker для генерации данных. (Обязательный).
            words_title (int): Количество слов в заголовке. По умолчанию 5.
            words_subtitle (int): Количество слов в подзаголовке. По умолчанию 5.
            sentences_count (int): Количество предложений в тексте новости. По умолчанию 3.
            tags_count (int): Количество тегов, которые необходимо сгенерировать. По умолчанию 5.
            img_widt (int): Ширина изображения в пикселях. По умолчанию 800.
            img_height (int): Высота изображения в пикселях. По умолчанию 600.
            exclude (tuple[str]): список параметров, которые необходимо исключить из возвращаемого словаря.

        Returns:
            dict: Словарь с данными для новости.
    """
    news = {
        "title": faker.sentence(nb_words=words_title),
        "subtitle": faker.sentence(nb_words=words_subtitle),
        "text": faker.paragraph(nb_sentences=sentences_count),
        "tags": ", ".join(faker.words(nb=tags_count)),
    }

    try:
        img_path = download_image(faker, width=img_width, height=img_height)
    except:
        img_path = generate_image(width=img_width, height=img_height)

    news["image"] = img_path

    if exclude:
        for word in exclude:
            news.pop(word, None)

    return news