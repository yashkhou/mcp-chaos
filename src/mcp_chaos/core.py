from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Callable


class DroppedResponse(RuntimeError):
    pass


@dataclass(frozen=True)
class FaultRule:
    action: str
    every: int = 1
    method: str = "*"
    start: int = 1

    def __post_init__(self) -> None:
        if self.action not in {"drop", "retryable", "malformed", "truncate"}:
            raise ValueError(f"unsupported chaos action: {self.action}")
        if self.every < 1 or self.start < 1:
            raise ValueError("every and start must be positive")


@dataclass(frozen=True)
class Profile:
    drop_every: int = 0
    malformed_every: int = 0
    truncate_every: int = 0
    retryable_every: int = 0
    latency_ms: int = 0
    rules: tuple[FaultRule, ...] = ()


@dataclass(frozen=True)
class ChaosEvent:
    call: int
    method: str
    method_call: int
    action: str


class ChaosProxy:
    def __init__(self, handler: Callable[[dict], object], profile: Profile):
        self.handler = handler
        self.profile = profile
        self.calls = 0
        self.method_calls: Counter[str] = Counter()
        self.events: list[ChaosEvent] = []

    def _planned_action(self, method: str, method_call: int) -> str | None:
        for rule in self.profile.rules:
            if fnmatch(method, rule.method) and method_call >= rule.start and method_call % rule.every == 0:
                return rule.action
        global_rules = (
            ("drop", self.profile.drop_every),
            ("retryable", self.profile.retryable_every),
            ("malformed", self.profile.malformed_every),
            ("truncate", self.profile.truncate_every),
        )
        for action, every in global_rules:
            if every and self.calls % every == 0:
                return action
        return None

    def __call__(self, req: dict):
        self.calls += 1
        method = str(req.get("method", ""))
        self.method_calls[method] += 1
        method_call = self.method_calls[method]
        if self.profile.latency_ms:
            time.sleep(self.profile.latency_ms / 1000)
        action = self._planned_action(method, method_call)
        if action:
            self.events.append(ChaosEvent(self.calls, method, method_call, action))
        if action == "drop":
            raise DroppedResponse(f"dropped call {self.calls} ({method})")
        if action == "retryable":
            return {
                "jsonrpc": "2.0",
                "id": req.get("id"),
                "error": {"code": -32001, "message": "temporary chaos fault", "retryable": True},
            }
        result = self.handler(req)
        wire = json.dumps(result, separators=(",", ":"))
        if action == "malformed":
            return wire[:-1] + ",BROKEN}"
        if action == "truncate":
            return wire[: max(1, len(wire) // 2)]
        return result


def wrap(handler: Callable[[dict], object], profile: Profile) -> ChaosProxy:
    return ChaosProxy(handler, profile)


def echo_handler(req: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req.get("id"), "result": {"echo": req.get("params")}}
