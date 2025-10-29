#!/usr/bin/env python

import os
import json
import google.auth
from google.auth.transport.requests import Request
from openai import OpenAI
from pydantic import BaseModel

# Import the structured output schema for model responses
from evaluate_papers.structured_output import StructuredOutput

# =============================================================================
# Vertex AI MaaS LLM Client
# =============================================================================
# This module provides a wrapper class for interacting with Partner MaaS models
# on Vertex AI (e.g., zai-org/glm-4.7-maas, moonshotai/kimi-k2-thinking-maas).
# It uses the standard OpenAI Python SDK pointing to Google's OpenAPI endpoint.
# =============================================================================

class StructuredOutputList(BaseModel):
    """
    Wrapper class for OpenAI SDK.
    The beta.parse method requires a root-level BaseModel, so we wrap your 
    existing list of StructuredOutput objects here.
    """
    items: list[StructuredOutput]

class VertexMaaS:
    """
    Client for interacting with Vertex AI Partner Models via OpenAI-compatible endpoints.
    Handles Google Auth, API routing, and structured output parsing.
    """
    def __init__(self, project_id, region, model, structured_output, temperature, top_p):
        self.project_id = project_id
        self.region = region
        self.model = model
        self.structured_output = structured_output
        self.temperature = temperature
        self.top_p = top_p

        # Output file paths for results and errors
        safe_model_name = self.model.replace("/", "_")
        self.results_filename = f"results/vertex_maas/maas_text_results_{safe_model_name}_%s.json"
        self.errors_filename = f"results/vertex_maas/maas_text_errors_{safe_model_name}_%s.json"

        # 1. Authenticate using Google Cloud Default Credentials
        try:
            self.credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self.credentials.refresh(Request())
        except Exception as e:
            raise RuntimeError(f"Failed to load Google Cloud credentials: {e}")

        # 2. Configure the OpenAI client for Vertex AI
        # Handle the 'global' region endpoint prefix appropriately
        endpoint_prefix = "aiplatform.googleapis.com" if self.region == "global" else f"{self.region}-aiplatform.googleapis.com"
        
        base_url = f"https://{endpoint_prefix}/v1beta1/projects/{self.project_id}/locations/{self.region}/endpoints/openapi"
        
        self.client = OpenAI(
            base_url=base_url,
            api_key=self.credentials.token,
        )

    def evaluate_papers(self, paper_id, prompt, paper_text, questions):
        """
        Run the MaaS model on a paper and questions, returning the structured response.
        Input is text-only.
        """
        if not self.credentials.valid:
            try:
                # Request() comes from: from google.auth.transport.requests import Request
                self.credentials.refresh(Request())
                self.client.api_key = self.credentials.token
            except Exception as e:
                print(f"Error refreshing Google Cloud credentials: {e}")
                return None, 0, 0, 0

        # Build the message payload using the OpenAI schema
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Paper Content:\n{paper_text}\n\nQuestions:\n{questions}"}
        ]

        # Prepare generation arguments
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if self.temperature != -1:
            kwargs["temperature"] = self.temperature
        if self.top_p != -1:
            kwargs["top_p"] = self.top_p

        try:
            # Generate content using structured output beta parsing or standard generation
            if self.structured_output:
                response = self.client.beta.chat.completions.parse(
                    **kwargs,
                    response_format=StructuredOutputList,
                )
                
                # Extract the first item from the list to match the original Gemini behavior
                parsed_wrapper = response.choices[0].message.parsed
                if parsed_wrapper.items:
                    content_list = parsed_wrapper.items[0].model_dump_json()
                else:
                    content_list = "{}"
                
            else:
                response = self.client.chat.completions.create(**kwargs)
                content_list = response.choices[0].message.content
                
                # Fallback text parsing if structured output was disabled
                content_list = content_list.lower()
                start_idx = content_list.find("{")
                end_idx = content_list.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    content_list = content_list[start_idx : end_idx + 1]
                content_list = content_list.replace("\\n", "").replace("\\", "").replace("'", '"')

        except Exception as e:
            print(f"Error Processing MaaS Request: {e}")
            return None, 0, 0, 0

        # Extract Usage Metadata standard to the OpenAI schema
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        
        # Extract 'thoughts' tokens (reasoning tokens) for thinking models like Kimi-K2
        thoughts_tokens = 0
        if usage and hasattr(usage, "completion_tokens_details"):
            if usage.completion_tokens_details and hasattr(usage.completion_tokens_details, "reasoning_tokens"):
                thoughts_tokens = usage.completion_tokens_details.reasoning_tokens

        return content_list, input_tokens, thoughts_tokens, output_tokens

