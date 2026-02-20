"""Intent-Parser: kNN -> LLM -> Confirm -> Correct. Merge-Logik."""
from __future__ import annotations

from typing import Callable

from .schema import Intent, Slots
from .knn_store import KNNStore
from .rules import normalize_intent


class IntentParser:
    """Vereint kNN, LLM-Fallback und Korrektur-Lernen."""

    def __init__(
        self,
        knn_store: KNNStore,
        llm_generate: Callable[[str, str], str],
        extract_json: Callable[[str], dict | None],
        knn_auto: float = 0.85,
        knn_suggest: float = 0.65,
        llm_auto_conf: float = 0.8,
    ):
        self.knn_store = knn_store
        self.llm_generate = llm_generate
        self.extract_json = extract_json
        self.knn_auto = knn_auto
        self.knn_suggest = knn_suggest
        self.llm_auto_conf = llm_auto_conf

    def parse(self, phrase: str) -> tuple[Intent, str]:
        """
        Parst Phrase zu Intent.
        Returns (Intent, method) mit method in: knn_auto, knn_suggest, llm_auto, llm_suggest, unknown.
        """
        phrase = phrase.strip()
        if not phrase:
            return Intent(intent="UNKNOWN", slots={}, confidence=0.0), "unknown"

        # 1. kNN
        knn_results = self.knn_store.search(phrase, k=1)
        if knn_results:
            sim, intent_name, _, slots = knn_results[0]
            if sim >= self.knn_auto:
                return normalize_intent(Intent(intent=intent_name, slots=slots, confidence=float(sim))), "knn_auto"
            if sim >= self.knn_suggest:
                return normalize_intent(Intent(intent=intent_name, slots=slots, confidence=float(sim))), "knn_suggest"

        # 2. LLM Fallback
        from svc.llm.prompts import INTENT_SYSTEM_PROMPT, build_intent_prompt
        raw = self.llm_generate(INTENT_SYSTEM_PROMPT, build_intent_prompt(phrase))
        data = self.extract_json(raw)
        if data:
            intent = Intent(
                intent=str(data.get("intent", "UNKNOWN")),
                slots=data.get("slots") or {},
                confidence=float(data.get("confidence", 0.5)),
            )
            intent = normalize_intent(intent)
            if intent.confidence >= self.llm_auto_conf:
                return intent, "llm_auto"
            return intent, "llm_suggest"

        # Retry mit strengerer Anweisung
        retry_prompt = "Antworte NUR mit einem JSON-Objekt, kein anderer Text. " + build_intent_prompt(phrase)
        raw2 = self.llm_generate(INTENT_SYSTEM_PROMPT, retry_prompt)
        data2 = self.extract_json(raw2)
        if data2:
            intent = Intent(
                intent=str(data2.get("intent", "UNKNOWN")),
                slots=data2.get("slots") or {},
                confidence=float(data2.get("confidence", 0.5)),
            )
            return normalize_intent(intent), "llm_suggest"

        return Intent(intent="UNKNOWN", slots={}, confidence=0.0), "unknown"

    def learn_correction(self, original_phrase: str, corrected_intent: str, corrected_slots: dict) -> None:
        """Speichert ursprüngliche Phrase als Example für korrigierten Intent."""
        self.knn_store.add(original_phrase, corrected_intent, corrected_slots)
