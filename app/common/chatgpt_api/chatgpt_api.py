import logging
from openai import OpenAI


class ChatCompletion:
    def __init__(self, *args, **kwargs):
        self.client = OpenAI(*args, **kwargs)
        self.system_prompt = "You are a helpful assistant."
        self.chat_history = []

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def clear_history(self):
        self.chat_history = []

    def chat_nohistory(
        self,
        prompt: str,
        system_prompt="You are a helpful assistant.",
        model="gpt-3.5-turbo-16k",
        **kwargs,
    ):
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            **kwargs,
        )
        return response.choices[0].message.content

    def chat(
        self,
        prompt: str,
        system_prompt="You are a helpful assistant.",
        model="gpt-3.5-turbo-16k",
        **kwargs,
    ) -> str:
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": system_prompt})

        msgs = self.chat_history + [{"role": "user", "content": prompt}]

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=msgs,
                **kwargs,
            )

            res_message = response.choices[0].message
            self.chat_history.append(
                {"role": res_message.role, "content": res_message.content}
            )

            return res_message.content
        except Exception as e:
            logging.error(f"Failed to chat: {e}")
            return None
