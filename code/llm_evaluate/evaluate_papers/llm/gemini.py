#!/usr/bin/env python

import os
import pathlib

# Import the Google GenAI SDK for interacting with Gemini models
# https://ai.google.dev/gemini-api/docs
# https://cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview
from google import genai

# Import the structured output schema for model responses
from evaluate_papers.structured_output import StructuredOutput

# =============================================================================
# Gemini LLM Client Classes
# =============================================================================
# This module provides wrapper classes for interacting with various Gemini LLM
# endpoints (public API, Vertex AI, text-only and multimodal variants).
# Each class manages configuration, authentication, and response handling.
# =============================================================================

class Gemini:
    """
    Base class for Gemini LLM clients.
    Handles configuration and evaluation logic shared by all Gemini endpoints.
    """
    def __init__(self, model, structured_output, temperature, top_p):
        # Store the model name or ID to use for generation
        self.model = model
        self.structured_output = structured_output
        self.temperature = temperature
        self.top_p = top_p

    def gemini_config(self):
        """
        Helper to build the generation config dictionary for Gemini models.
        Supports structured output, temperature, and top_p sampling.
        """
        gemini_config = {}

        if self.structured_output:
            # Request JSON output and provide schema for validation
            gemini_config["response_mime_type"] = "application/json"
            gemini_config["response_schema"] = list[StructuredOutput]

        if self.temperature != -1:
            gemini_config["temperature"] = self.temperature
        if self.top_p != -1:
            gemini_config["top_p"] = self.top_p

        return gemini_config

    def evaluate_papers(self, paper_id, prompt, paper_text, questions):
        """
        Run the Gemini model on a paper and questions, returning the structured response.
        Handles both text and PDF (multimodal) inputs depending on subclass.
        """
        subclass = self.__class__.__name__

        # For multimodal models, load the PDF file as input; otherwise use text
        if subclass == "GeminiMultimodal" or subclass == "GeminiVertexMultimodal":
            filepath = pathlib.Path(f"papers/pdf/{paper_id}.pdf")
            paper_text_input = genai.types.Part.from_bytes(
                data=filepath.read_bytes(), mime_type="application/pdf"
            )
        else:
            # For text-only models, paper_text is passed directly
            paper_text_input = paper_text

        try:
            # Generate content using the model and config
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, paper_text_input, questions],
                config=self.generation_config,
            )
        except Exception as e:
            print(f"Error Processing Gemini Request: {e}")
            return None

        # If structured output is requested, parse the response
        if self.structured_output:
            try:
                content_list = response.parsed[0].model_dump_json()
            except Exception as e:
                print(f"Error parsing structured output: {e}")
                print("Response content:", response.candidates[0].content)
                return None
        else:

            # Extract and clean up the response content
            content_list = str(response.candidates[0].content.parts[0])
            content_list = content_list.lower()
            content_list = content_list[content_list.find("{") :]
            content_list = content_list[: content_list.find("}") + 1]
            content_list = content_list.replace("\\n", "").replace("\\", "")
            content_list = content_list.replace("'", '"')

        input_tokens = response.usage_metadata.prompt_token_count
        thoughts_tokens = response.usage_metadata.thoughts_token_count
        output_tokens = response.usage_metadata.candidates_token_count

        if input_tokens is None:
            input_tokens = 0
        if thoughts_tokens is None:
            thoughts_tokens = 0
        if output_tokens is None:
            output_tokens = 0

        return content_list, input_tokens, thoughts_tokens, output_tokens


class GeminiText(Gemini):
    """
    Gemini client for public API (text-only).
    Handles API key authentication and configures output file paths.
    """
    def __init__(self, api_key, model, structured_output, temperature, top_p):
        super().__init__(model, structured_output, temperature, top_p)

        # Remove Vertex AI environment variables to ensure public API usage
        os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
        os.environ.pop("GOOGLE_CLOUD_LOCATION", None)
        os.environ.pop("GOOGLE_GENAI_USE_VERTEXAI", None)

        # Configure the public GenAI client with API key for AI Studio
        self.client = genai.Client(api_key=api_key)

        # Build and store the generation config object
        gemini_config_dict = self.gemini_config()
        self.generation_config = genai.types.GenerateContentConfig(**gemini_config_dict)

        # Output file paths for results and errors
        self.results_filename = "results/gemini/gemini_text_results_%s.json"
        self.errors_filename = "results/gemini/gemini_text_errors_%s.json"


class GeminiMultimodal(GeminiText):
    """
    Gemini client for public API (multimodal: PDF input).
    Inherits authentication and config from GeminiText.
    """
    def __init__(self, api_key, model, structured_output, temperature, top_p):
        super().__init__(api_key, model, structured_output, temperature, top_p)

        # Output file paths for multimodal results and errors
        self.results_filename = "results/gemini/gemini_multimodal_results_%s.json"
        self.errors_filename = "results/gemini/gemini_multimodal_errors_%s.json"


class GeminiVertexText(Gemini):
    """
    Gemini client for Vertex AI (text-only).
    Handles Vertex project/region configuration and authentication.
    """
    def __init__(
        self, project_id, region, model, structured_output, temperature, top_p
    ):
        super().__init__(model, structured_output, temperature, top_p)

        # Set environment variables for Vertex AI usage
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = region
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

        # Configure the GenAI client for Vertex AI endpoint
        self.client = genai.Client(
            http_options=genai.types.HttpOptions(api_version="v1")
        )

        # Build and store the generation config object
        gemini_config_dict = self.gemini_config()
        self.generation_config = genai.types.GenerateContentConfig(**gemini_config_dict)

        # Output file paths for results and errors
        self.results_filename = (
            "results/gemini_vertex/gemini_vertex_text_results_%s.json"
        )
        self.errors_filename = "results/gemini_vertex/gemini_vertex_text_errors_%s.json"


class GeminiVertexMultimodal(GeminiVertexText):
    """
    Gemini client for Vertex AI (multimodal: PDF input).
    Inherits authentication and config from GeminiVertexText.
    """
    def __init__(
        self, project_id, region, model, structured_output, temperature, top_p
    ):
        super().__init__(
            project_id, region, model, structured_output, temperature, top_p
        )

        # Output file paths for multimodal results and errors
        self.results_filename = (
            "results/gemini_vertex/gemini_vertex_multimodal_results_%s.json"
        )
        self.errors_filename = (
            "results/gemini_vertex/gemini_vertex_multimodal_errors_%s.json"
        )
