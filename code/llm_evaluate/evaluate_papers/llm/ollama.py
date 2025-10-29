#!/usr/bin/env python

import re
import tiktoken
from ollama import Client
from evaluate_papers.structured_output import StructuredOutput


class Ollama:

    def __init__(self, host, model, structured_output, temperature, top_p):
        self.host = host
        self.model = model
        self.structured_output = structured_output
        self.temperature = temperature
        self.top_p = top_p

        # Initialize the Ollama client
        self.client = Client(host=host)

        self.results_filename = "results/ollama/ollama_results_%s.json"
        self.errors_filename = "results/ollama/ollama_errors_%s.json"

    def evaluate_papers(self, paper_id, prompt, paper_text, questions):
        if self.structured_output:
            response_format = StructuredOutput.model_json_schema()
        else:
            response_format = "json"

        # Prepare options kwargs for the Ollama API call
        options_kwargs = {}

        if self.temperature != -1:
            options_kwargs["temperature"] = self.temperature
        if self.top_p != -1:
            options_kwargs["top_p"] = self.top_p

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "%s\n\n%s\n\n%s" % (prompt, paper_text, questions),
                },
            ],
            options=options_kwargs,
            format=response_format,
        )

        if self.structured_output:
            try:
                content_list = StructuredOutput.model_validate_json(
                    response.message.content
                )
                content_list = content_list.model_dump_json()
            except Exception as e:
                print(f"Error parsing structured output: {e}")
                print("Response content:", response.message.content)
                return None
        else:
            content_list = (
                response["message"]["content"]
                .replace("Here are the answers to your questions in JSON format:", "")
                .replace("\\", "")
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            pattern = r"Error: \d+"
            content_list = re.sub(pattern, "", content_list)

        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            input_tokens = len(encoding.encode(prompt + "\n" + paper_text + "\n" + questions))
            output_tokens = len(encoding.encode(content_list))
        except Exception as e:
            print(f"Error calculating tokens for paper {paper_id}: {e}")
            input_tokens = 0
            output_tokens = 0

        # Ollama does not provide thoughts tokens, so we set it to 0
        thoughts_tokens = 0

        return content_list, input_tokens, thoughts_tokens, output_tokens
