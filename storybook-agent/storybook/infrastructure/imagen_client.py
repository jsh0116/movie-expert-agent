from google import genai
from google.genai import types


def generate_image(prompt: str) -> bytes:
    client = genai.Client()
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="4:3",
        ),
    )
    return response.generated_images[0].image.image_bytes
