#!/usr/bin/env python

import json
from openai import (
    OpenAI,
    AzureOpenAI,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
)
from evaluate_papers.structured_output import StructuredOutput


class ChatGPT:

    def __init__(
        self,
        api_key,
        model,
        structured_output,
        temperature,
        top_p,
        organization="",
        azure_endpoint="",
        base_url="",
    ):
        self.model = model
        self.structured_output = structured_output
        self.temperature = temperature
        self.top_p = top_p

    def evaluate_papers(self, paper_id, prompt, paper_text, questions):

        if self.structured_output:
            openai_chat_completions = self.client.beta.chat.completions.parse
            response_format = StructuredOutput
        else:
            openai_chat_completions = self.client.chat.completions.create
            response_format = {"type": "json_object"}

        # Prepare kwargs for ChatGPT API call
        completion_kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": paper_text},
                {"role": "user", "content": questions},
            ],
            "response_format": response_format,
        }
        if self.temperature != -1:
            completion_kwargs["temperature"] = self.temperature
        if self.top_p != -1:
            completion_kwargs["top_p"] = self.top_p

        try:
            response = openai_chat_completions(**completion_kwargs)

        except APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
            return None
        except RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
            return None

        except APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)
            print(e)
            return None

        if self.structured_output:
            content_list = json.dumps(response.choices[0].message.parsed.model_dump())
        else:
            content_list = response.choices[0].message.content

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # ChatGPT includes thoughts tokens in the output, so we set it to 0
        thoughts_tokens = 0

        return content_list, input_tokens, thoughts_tokens, output_tokens


class ChatGPTOpenAI(ChatGPT):

    def __init__(
        self,
        api_key,
        organization,
        model,
        structured_output,
        temperature,
        top_p,
    ):
        super().__init__(
            api_key,
            model,
            structured_output,
            temperature,
            top_p,
            organization=organization,
        )

        # Initialize the client
        self.client = OpenAI(
            api_key=api_key,
            organization=organization,
        )

        self.results_filename = "results/chatgpt/chatgpt_results_%s.json"
        self.errors_filename = "results/chatgpt/chatgpt_errors_%s.json"


class ChatGPTAzure(ChatGPT):

    def __init__(
        self, api_key, azure_endpoint, model, structured_output, temperature, top_p
    ):
        super().__init__(
            api_key,
            model,
            structured_output,
            temperature,
            top_p,
            azure_endpoint=azure_endpoint,
        )

        # Initialize the client
        self.client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=azure_endpoint,
            api_key=api_key,
        )

        self.results_filename = "results/azure/chatgpt_results_%s.json"
        self.errors_filename = "results/azure/chatgpt_errors_%s.json"

class ChatGPTCompatibleService(ChatGPT):

    def __init__(
        self, api_key, base_url, model, structured_output, temperature, top_p
    ):
        super().__init__(
            api_key,
            model,
            structured_output,
            temperature,
            top_p,
            base_url=base_url,
        )

        # Initialize the client
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self.results_filename = "results/chatgpt_compatible/chatgpt_results_%s.json"
        self.errors_filename = "results/chatgpt_compatible/chatgpt_errors_%s.json"