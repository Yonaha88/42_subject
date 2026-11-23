"""生成: 言語モデルに答えを書かせる。torch を使うのはこのファイルだけ。"""

from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.augmentation import NO_CONTEXT_ANSWER, build_context, build_messages
from src.errors import RagError
from src.models import MinimalSource

MODEL_NAME = "Qwen/Qwen3-0.6B"
# 答えは数文で足りる。モデルが長々と書き続けるのも止める。
MAX_NEW_TOKENS = 200


class AnswerGenerator:
    """モデルは 1 回だけ読み込み、全部の質問で使い回す。"""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        """モデルとトークナイザを読み込む。

        Args:
            model_name: Hugging Face のモデル名。

        Raises:
            RagError: 読み込めないとき。
        """
        # 実際のクラスは実行時に決まるので、型は Any にしている。
        self.tokenizer: Any
        self.model: Any
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, dtype=torch.float32
            )
        except (OSError, ValueError) as error:
            raise RagError(
                f"cannot load the model {model_name}: {error}"
            ) from error

    def answer(
        self,
        question: str,
        sources: list[MinimalSource],
        max_context_tokens: int,
    ) -> str:
        """ソースをもとに、質問に答える。

        Args:
            question: 質問。
            sources: 検索で見つかったソース（良い順）。
            max_context_tokens: 文脈のトークン数の上限。

        Returns:
            回答。読めるソースがなければ、決まった文を返す。
        """
        context = build_context(
            sources, self.count_tokens, max_context_tokens
        )
        # ソースがないとモデルは答えを作り出してしまうので、呼ばない。
        if not context:
            return NO_CONTEXT_ANSWER
        return self.generate(build_messages(question, context))

    def count_tokens(self, text: str) -> int:
        """モデルのトークナイザで、トークン数を数える。"""
        return len(self.tokenizer.encode(text))

    def generate(self, messages: list[dict[str, str]]) -> str:
        """メッセージから、回答を 1 つ書く。

        Args:
            messages: システムメッセージとユーザーメッセージ。

        Returns:
            モデルが書いた回答。
        """
        # チャットテンプレートで、モデルが学習した書式に変換する。
        # Qwen3 の「思考」は、速く答えるために切っている。
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        prompt_length = inputs["input_ids"].shape[1]
        with torch.no_grad():
            # do_sample=False: 常に一番確率の高いトークンを選ぶ（毎回同じ答え）。
            output = self.model.generate(
                **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False
            )
        # 出力にはプロンプトも含まれるので、追加された部分だけ取り出す。
        new_tokens = output[0][prompt_length:]
        answer = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return str(answer).strip()
