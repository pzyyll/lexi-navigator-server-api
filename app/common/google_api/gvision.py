from google.cloud import vision
import asyncio


class GoogleVision:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def text_from_image(self, image_path):
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        return self.text_from_image_content(content)

    def text_from_image_content(self, image_content):
        image = vision.Image(content=image_content)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        return texts[0].description if texts else None

    async def async_text_from_image_content(self, image_content):
        text = await asyncio.get_event_loop().run_in_executor(
            None, self.text_from_image_content, image_content
        )
        return text
