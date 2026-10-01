import time

from google import genai
from google.genai import errors

from app.config.settings import get_settings


class GeminiClient:
    """Application wrapper around the Gemini API."""

    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY_SECONDS = 2

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        if not settings.MODEL_NAME:
            raise RuntimeError(
                "MODEL_NAME is not configured."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

        self.model_name = settings.MODEL_NAME

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """
        Generate text using Gemini.

        Transient server errors are retried using bounded
        exponential backoff.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "prompt cannot be empty."
            )

        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = (
                    self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                    )
                )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return response.text

            except errors.ServerError as exc:
                last_error = exc

                if attempt >= self.MAX_RETRIES:
                    raise RuntimeError(
                        "Gemini is temporarily unavailable "
                        "after multiple retry attempts. "
                        "Please try again later."
                    ) from exc

                delay = (
                    self.INITIAL_RETRY_DELAY_SECONDS
                    * (2**attempt)
                )

                print(
                    f"Gemini server error "
                    f"(attempt {attempt + 1}/"
                    f"{self.MAX_RETRIES + 1}). "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)

            except errors.ClientError as exc:
                raise RuntimeError(
                    f"Gemini client error: {exc}"
                ) from exc

        raise RuntimeError(
            "Gemini request failed."
        ) from last_error