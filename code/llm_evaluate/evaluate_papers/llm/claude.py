#!/usr/bin/env python

import anthropic
from anthropic import AnthropicBedrock


class Claude:

    def __init__(
        self,
        model,
        temperature,
        top_p,
        api_key="",
        aws_access_key="",
        aws_secret_key="",
        aws_region="",
    ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p

    def evaluate_papers(self, paper_id, prompt, paper_text, questions):

        # Prepare kwargs for Anthropic API call
        message_kwargs = {
            "model": self.model,
            "max_tokens": 1000,
            "system": prompt,
            "messages": [
                {
                    "role": "user",
                    "content": paper_text,
                },
                {
                    "role": "assistant",
                    "content": "Okay",
                },
                {
                    "role": "user",
                    "content": questions,
                },
            ],
        }

        if self.temperature != -1:
            message_kwargs["temperature"] = self.temperature
        if self.top_p != -1:
            message_kwargs["top_p"] = self.top_p

        try:
            response = self.client.messages.create(**message_kwargs)

        except anthropic.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
            return None
        except anthropic.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
            return None
        except anthropic.APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)
            return None

        return response.content[0].text


class ClaudeAnthropic(Claude):

    def __init__(self, api_key, model, temperature, top_p):
        super().__init__(model, temperature, top_p, api_key=api_key)

        # Initialize the client
        self.client = anthropic.Anthropic(
            api_key=api_key,
        )

        self.results_filename = "results/claude/claude_results_%s.json"
        self.errors_filename = "results/claude/claude_errors_%s.json"


class ClaudeAWS(Claude):

    def __init__(
        self, aws_access_key, aws_secret_key, aws_region, model, temperature, top_p
    ):
        super().__init__(
            model,
            temperature,
            top_p,
            aws_access_key=aws_access_key,
            aws_secret_key=aws_secret_key,
            aws_region=aws_region,
        )

        # Initialize the client
        self.client = AnthropicBedrock(
            aws_access_key=aws_access_key,
            aws_secret_key=aws_secret_key,
            aws_region=aws_region,
        )

        self.results_filename = "results/aws/claude_results_%s.json"
        self.errors_filename = "results/aws/claude_errors_%s.json"
