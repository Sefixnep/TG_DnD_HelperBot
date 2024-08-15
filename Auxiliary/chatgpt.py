# Libs
import openai
import requests
from Auxiliary.config import api_gpt

# Configure the OpenAI library with the API key
openai.api_key = api_gpt


class Chat:
    def __init__(self, model_name="gpt-4o-mini", image_size="256x256"):
        self.model_name = model_name
        self.hist = list()
        self.image_size = image_size  # Доступные размеры: 256x256, 512x512, 1024x1024

    def new_chat(self):
        self.hist.clear()

    def message(self, text, system=False, answer=True, save=True, max_tokens=1000):
        if save:
            self.hist.append({"role": "user" if not system else "system", "content": text})
        if answer:
            response = openai.ChatCompletion.create(
                model=self.model_name,  # or another model name
                messages=self.hist,
                max_tokens=max_tokens
            )
            if save:
                self.hist.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
            return response['choices'][0]['message']['content']

    def print(self):
        print('\n\n'.join(map(lambda dct: f'{dct["role"]}: {dct["content"]}', self.hist)))

    def create_image(self, text):
        # Генерация изображения по текстовому описанию
        response = openai.Image.create(
            prompt=text,
            n=1,
            size=self.image_size
        )

        # Извлечение URL сгенерированного изображения
        image_url = response['data'][0]['url']

        # Скачивание изображения и сохранение его в файл
        return requests.get(image_url).content
