from openai import OpenAI


class Chatbot:

    def __init__(self) -> None:
        self._chat_id_generator = 0
        self._historys = {}
        self._openai = OpenAI()

    def CreateChatID(self):
        self._chat_id_generator += 1
        return self._chat_id_generator

    def GetHistoryMessages(self, chatid):
        return self._historys.get(chatid, [])

    def EditHistoryMessagesContent(self, chatid, idx, new_content):
        try:
            self._historys[chatid][idx]["content"] = new_content
        except Exception as e:
            print("EditHistoryMessagesContent Error:", e)

    def DelHistoryMessages(self, chatid, idx):
        try:
            self._historys[chatid].pop(idx)
        except Exception as e:
            print("DelHistoryMessages Error:", e)

    def Chat(self, message, chatid=None, **kwargs):
        history_messages = self._historys.setdefault(chatid,
                                                     []) if chatid else None
        completion = self.GetCompletion(message,
                                        history_messages=history_messages,
                                        **kwargs)
        msg = completion.choices[0].message
        if chatid:
            history_messages.append({"role": "user", "content": message})
            history_messages.append({"role": msg.role, "content": msg.content})
        return msg.content

    def GetCompletion(
            self,
            prompt,
            model="gpt-3.5-turbo-0125",
            system_prompt="You are ChatGPT, a large language model trained by OpenAI.",
            history_messages: list | None = None,
            **kwargs):
        messages = [{"role": "system", "content": system_prompt}]
        if history_messages and len(history_messages) > 0:
            messages += history_messages
        messages.append({"role": "user", "content": prompt})

        return self._openai.chat.completions.create(model=model,
                                                    messages=messages,
                                                    **kwargs)
