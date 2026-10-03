from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


time_window = load_module("time_window", "scripts/time_window.py")
source_registry = load_module("source_registry", "scripts/source_registry.py")
publication_history = load_module("publication_history", "scripts/publication_history.py")


class TimeWindowTests(unittest.TestCase):
    def test_daily_is_one_day(self):
        now = datetime.fromisoformat("2026-10-03T08:05:00-03:00")
        start, end = time_window.calculate("daily", now)
        self.assertEqual(end - start, timedelta(days=1))

    def test_weekly_is_seven_days(self):
        now = datetime.fromisoformat("2026-10-03T08:05:00-03:00")
        start, end = time_window.calculate("weekly", now)
        self.assertEqual(end - start, timedelta(days=7))


class SourceRegistryTests(unittest.TestCase):
    def test_add_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            state = td / "state.json"
            state.write_text(json.dumps({"version":1,"sources":[]}), encoding="utf-8")
            class A: pass
            a=A(); a.state=state; a.confirmed=False; a.approval_note=""; a.category="private_specialized"; a.url="https://example.com"; a.id=None; a.name="Exemplo"; a.approved_at="2026-10-03"; a.notes=""
            with self.assertRaisesRegex(ValueError, "USER_CONFIRMATION_REQUIRED"):
                source_registry.cmd_add(a)

    def test_add_confirmed_source(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            state = td / "state.json"
            state.write_text(json.dumps({"version":1,"sources":[]}), encoding="utf-8")
            class A: pass
            a=A(); a.state=state; a.confirmed=True; a.approval_note="confirmada pelo usuario"; a.category="private_specialized"; a.url="https://example.com/"; a.id="example"; a.name="Exemplo"; a.approved_at="2026-10-03"; a.notes=""
            result=source_registry.cmd_add(a)
            self.assertEqual(result["status"], "added")
            saved=json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["sources"]),1)


class HistoryTests(unittest.TestCase):
    def make_state(self, td):
        state = Path(td) / "history.json"
        state.write_text(json.dumps({"version":1,"items":[]}), encoding="utf-8")
        return state

    def args(self, state, **kw):
        class A: pass
        a=A(); a.state=state; a.url=kw.get("url","https://example.com/news?utm_source=x"); a.title=kw.get("title","Nova regra"); a.source_name=kw.get("source_name","Fonte"); a.published_at=kw.get("published_at","2026-10-02T10:00:00-03:00"); a.edition_at=kw.get("edition_at","2026-10-03T08:00:00-03:00"); a.new_fact_note=kw.get("new_fact_note","")
        return a

    def test_tracking_params_are_removed(self):
        norm = publication_history.normalize_url("https://Example.com/a?utm_source=x&x=1#frag")
        self.assertEqual(norm, "https://example.com/a?x=1")

    def test_duplicate_requires_new_fact(self):
        with tempfile.TemporaryDirectory() as td:
            state=self.make_state(td)
            a=self.args(state)
            publication_history.cmd_record(a)
            with self.assertRaisesRegex(ValueError, "DUPLICATE_REQUIRES_NEW_FACT_NOTE"):
                publication_history.cmd_record(a)

    def test_duplicate_with_new_fact_is_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            state=self.make_state(td)
            a=self.args(state)
            publication_history.cmd_record(a)
            b=self.args(state, new_fact_note="Novo ato oficial publicado")
            result=publication_history.cmd_record(b)
            self.assertTrue(result["item"]["supersedes"])


if __name__ == "__main__":
    unittest.main()
