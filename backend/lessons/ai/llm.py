from openai import OpenAI
from pydantic import BaseModel
from django.conf import settings
import json 

api_key= settings.OPENAI_API_KEY
base_url= settings.OPENAI_BASE_URL

from pydantic import BaseModel
class TranslateResponse(BaseModel):
    start_time: str
    end_time: str
    text: str
    fa_text: str

class ListTranslateResponse(BaseModel):
    transcript : list[TranslateResponse]


client = OpenAI(base_url=base_url, 
                api_key=api_key)



def llm_clean_text(text: str, model: str = "gpt-4o-mini") -> str:
    try:
        response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert editor. Clean and format the text with proper paragraphs."},
            {"role": "user", "content": text}
        ],
        temperature=0.25,
    )
        # ✅ Access via attribute
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"

def extract_important_notes(text: str, model: str = "gpt-4o-mini") -> str:
    """
    Use LLM to extract important grammar rules and vocabulary notes from text.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert English teacher that helps students learn English effectively and improve their language skills to C1 level."
                        "you imagine my level B1 or lower."
                        "From the given text, extract all important grammar rules or  phrases; and vocabulary notes. "
                        "IMPORTANT : Translate at least ten words."
                        "Organize the output clearly in JSON format exactly as specified. "
                        "Do not include any text outside the JSON object. "
                        "\n\nJSON format example:\n"
                        "{\n"
                        '  "grammar": ["rule1", "rule2", ...],\n'
                        '  "vocabulary": [\n'
                        "    {\n"
                        '      "word": "example_word",\n'
                        '      "definition": "short definition",\n'
                        '      "simple_example": "example sentence using the word",\n'
                        '      "translate_fa": "Persian translation"\n'
                        "    },\n"
                        "    ...\n"
                        "  ]\n"
                        "}\n"
                        "Ensure all fields are filled. If there is no vocabulary or grammar, return an empty list for that field."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {e}"




def translate_text(transcript_dict: list[dict], model: str = "gpt-4o-mini") -> ListTranslateResponse:
    try:
        response = client.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the text into Persian."},
                {"role": "user", "content": "The transcript is a list of dictionaries with the following keys: start_time, end_time, text, fa_text. \
                    Translate the text into Persian. and add the fa_text key to the dictionary. \
                        be careful to not change the start_time and end_time keys. and text_fa should be the translated text and meaningful."},
                {"role": "user", "content": f"transcript: {transcript_dict}"}
            ],
            response_format=ListTranslateResponse,
        )
        data = json.loads(response.choices[0].message.content)
        obj = ListTranslateResponse(**data)
        return obj.model_dump()["transcript"]
    except Exception as e:
        raise e 


