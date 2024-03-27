from openai import OpenAI


class ChatCompletion:
    def __init__(self, *args, **kwargs):
        self.client = OpenAI(*args, **kwargs)
        self.system_prompt = "You are a helpful assistant."
        self.chat_history = []

    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

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
        msgs = [{"role": "system", "content": system_prompt}]
        msgs.extend(self.chat_history)
        msgs.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model,
            messages=msgs,
            **kwargs,
        )

        return response.choices[0].message.content
