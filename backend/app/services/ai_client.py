import requests
from app.core.config import settings


def generate_embedding(image_base64: str):
    url = f"{settings.AI_SERVICE_URL}/embed"

    try:
        res = requests.post(
            url,
            json={"image_base64": image_base64},
            timeout=20
        )

        if res.status_code != 200:
            print("AI Service returned error:", res.text)
            return None

        data = res.json()
        return data.get("embedding")

    except Exception as e:
        print("AI Service error:", str(e))
        return None
