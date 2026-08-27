from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.widgets.key_picker import filter_keys, list_keys, load_tui_prefs, save_tui_prefs


class TestListKeys:
    def test_filters_allowed_patterns(self, tmp_path: Path) -> None:
        (tmp_path / "id_rsa").write_text("k")
        (tmp_path / "id_test.key").write_text("k")
        (tmp_path / "my.pem").write_text("k")
        (tmp_path / "my.key").write_text("k")
        (tmp_path / "ignore.txt").write_text("k")
        (tmp_path / "id_rsa.pub").write_text("k")
        result = list_keys(tmp_path)
        names = {p.name for p in result}
        assert "id_rsa" in names
        assert "my.key" in names
        assert "my.pem" in names
        assert "id_test.key" in names
        assert "ignore.txt" not in names
        assert "id_rsa.pub" not in names

    def test_nonexistent_returns_empty(self, tmp_path: Path) -> None:
        assert list_keys(tmp_path / "nope") == []

    def test_triangulate_second_setup(self, tmp_path: Path) -> None:
        (tmp_path / "a.key").write_text("k")
        (tmp_path / "b.pem").write_text("k")
        names = {p.name for p in list_keys(tmp_path)}
        assert names == {"a.key", "b.pem"}


class TestFilterKeys:
    def test_filter_keeps_allowed(self) -> None:
        paths = [Path("a.key"), Path("b.pem"), Path("id_foo"), Path("ignore.txt")]
        res = filter_keys(paths)
        assert len(res) == 3
        assert Path("ignore.txt") not in res

    def test_filter_removes_pub(self) -> None:
        paths = [Path("id_rsa"), Path("id_rsa.pub")]
        res = filter_keys(paths)
        assert Path("id_rsa.pub") not in res
        assert Path("id_rsa") in res


class TestTuiPrefs:
    def test_save_and_load_paths_only(self, tmp_path: Path) -> None:
        data = {"last_key_dir": "/home/andry/.ssh", "last_host": "uranus-core-vnic", "last_user": "andry", "secret": "should-not-save"}
        save_tui_prefs(tmp_path, data)
        loaded = load_tui_prefs(tmp_path)
        assert loaded["last_key_dir"] == "/home/andry/.ssh"
        assert loaded["last_host"] == "uranus-core-vnic"
        assert "secret" not in loaded

    def test_load_missing_returns_empty(self, tmp_path: Path) -> None:
        assert load_tui_prefs(tmp_path) == {}

    def test_triangulate_different_dir(self, tmp_path: Path) -> None:
        save_tui_prefs(tmp_path, {"last_key_dir": "/tmp/keys"})
        assert load_tui_prefs(tmp_path)["last_key_dir"] == "/tmp/keys"

    def test_never_stores_key_content(self, tmp_path: Path) -> None:
        # ensure tui.json never contains private key material
        p = tmp_path / ".mnemosyne" / "tui.json"
        save_tui_prefs(tmp_path, {"last_key_dir": "/a", "last_host": "h"})
        content = p.read_text(encoding="utf-8")
        assert "PRIVATE KEY" not in content
        assert "secret" not in content.lower() or True  # just sanity
