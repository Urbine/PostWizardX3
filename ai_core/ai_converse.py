from pathlib import Path
from typing import Optional

# Third Party Libraries
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from PIL import Image

# Local implementations
from ai_core.config.ai_config import get_ollama_load_config
from ai_core.ai_workflows import get_captions_list
from integrations import google_search
from ml_engine import classify_title, classify_description, classify_tags


OLLAMA_CONFIG = get_ollama_load_config()

ollama_llm = ChatOllama(
    model="llama2-uncensored:7b",
    temperature=OLLAMA_CONFIG.temperature,
    num_predict=OLLAMA_CONFIG.num_predict,
    num_thread=OLLAMA_CONFIG.num_thread,
    num_gpu=OLLAMA_CONFIG.num_gpu,
    num_ctx=OLLAMA_CONFIG.num_ctx,
    format="json",
)

prompt_example_1 = """ 
            You are a specialised and professional SEO expert in the adult industry
            and you will be processing outputs for SERP optimisation. You are concerned about analysing competition
            and giving each post a leg up to rank by using keywords and strategic thinking.
            You will be given strategic information that will help you make decisions
            
            Your task is to generate a set of attributes for a video post thumbnail that will be used as is and extracted:
            1. ALT Text
            2. Caption
            3. Description string to be extracted
            4. SEO Friendly slug for the image file and post
            5. Optimized tags for the post (based on what you see in the search results) without hyphens, example: "Some Tag"
            6. Pick from the list provided the most suitable category for the post.
            You will be given: 
            -> Title: ``{title}``
            -> Description: ``{description}`` 
            -> Image caption: ``{caption}`` 
            -> List of categories to choose from: ``{categories}``
            -> Google results: ``{google_results}`` 
            Use the Google search results to help you generate the details and use them to improve the description.
            Differentiate this posts from others you see in the results from Google Search, so that this post can rank.
            In case the description is `None`, you should generate a description based on the image caption and results in a creative tone.
            
            ``{format_instructions}``
            """


def ai_video_attrs(
    img: Path,
    title: str,
    description: Optional[str],
    tags: Optional[str],
    prompt_template_prompt: str,
):
    prompt_template = ChatPromptTemplate.from_template(prompt_template_prompt)

    alt_text_schema = ResponseSchema(
        name="alt_text",
        description="ALT text generated for accessibility and SEO optimization",
    )
    caption_schema = ResponseSchema(
        name="caption",
        description="Thumbnail caption adapted for this video entry",
    )
    description_schema = ResponseSchema(
        name="description",
        description="Adapted description for this post entry",
    )
    category_schema = ResponseSchema(
        name="category",
        description="One category recommendation picked based on how it semantically matches the video theme",
    )
    slug_schema = ResponseSchema(
        name="slug",
        description="Generated SEO friendly slug generated to allow for a correct balance between optimization and content cohesion",
    )
    tags_schema = ResponseSchema(
        name="tags",
        description="Optimized comma-separated content tags following the 'Some Tag,...' format based on alternative competitor keywords",
    )

    response_schemas = [
        alt_text_schema,
        caption_schema,
        description_schema,
        category_schema,
        slug_schema,
        tags_schema,
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    image_file = Image.open(img)
    caption = get_captions_list(image_file)
    google = google_search.GoogleImage()

    classifiers = [
        classify_title(title),
        classify_description(description) if description else "",
        classify_tags(tags) if tags else "",
    ]

    categories = {categ for categs in classifiers for categ in categs if categ}
    google_results = google.get_serp_items(title)

    prompt_message = prompt_template.format_messages(
        title=title,
        caption=caption,
        description=description,
        categories=categories,
        google_results=google_results,
        format_instructions=format_instructions,
    )

    chat_messages = [  # noqa: F841
        (
            "system",
            "You are a specialised and professional SEO expert in the adult industry \
            and you will be processing outputs for SERP optimisation. You are concerned about analysing competition \
              and giving each post a leg up to rank by using keywords and strategic thinking. \
              You will be given strategic information that will help you make decisions",
        ),
        ("human", prompt_message),
    ]

    response = ollama_llm.invoke(prompt_message)
    output_parsed = output_parser.parse(response.content)
    return output_parsed


if __name__ == "__main__":
    # Testing code
    from core import get_duration
    import time

    time_start = time.time()
    ai_act = ai_video_attrs(Path(""), "", "", "", prompt_example_1)
    print(ai_act)
    time_end = time.time()
    h, mins, secs = get_duration(time_end - time_start)
    print("This process took: ", "hours:", h, "mins:", mins, "secs:", secs)
