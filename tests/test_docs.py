import subprocess
from unittest.mock import Mock

from docs.scripts import manage, mkruleref
from xrlint.plugins.core import export_plugin


def test_rule_reference_preserves_metadata_and_avoids_rewrites(tmp_path, monkeypatch):
    plugin = export_plugin()
    monkeypatch.setattr(
        mkruleref, "plugins_from_entry_points", lambda: {plugin.meta.name: plugin}
    )
    page = tmp_path / "rule-ref.md"
    mkruleref.write_rule_ref_page(page)
    content = page.read_text(encoding="utf-8")
    assert "# Rule Reference" in content
    assert ":material-bug:" in content
    assert "config.md#configuring-rules" in content
    assert "Rule identifier: `access-latency`" in content
    assert "**Options schema**" in content
    assert '"exclusiveMinimum": 0' in content
    assert "`recommended`" in content
    modified = page.stat().st_mtime_ns
    mkruleref.write_rule_ref_page(page)
    assert page.stat().st_mtime_ns == modified
    assert not page.with_suffix(".md.tmp").exists()


def test_rule_source_snapshot_detects_additions_changes_and_removals(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(manage, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(manage, "GENERATOR", tmp_path / "mkruleref.py")
    source_dir = tmp_path / "xrlint"
    source_dir.mkdir()
    initial = manage.rule_sources()
    source = source_dir / "plugin.py"
    source.write_text("first", encoding="utf-8")
    added = manage.rule_sources()
    assert source in added
    assert added != initial
    source.write_text("changed metadata", encoding="utf-8")
    assert manage.rule_sources() != added
    source.unlink()
    assert manage.rule_sources() == initial


def test_preview_recovers_from_generation_errors(tmp_path, monkeypatch, capsys):
    source = tmp_path / "rule.py"
    snapshots = iter({source: (version, 1)} for version in range(4))
    monkeypatch.setattr(manage, "rule_sources", lambda: next(snapshots))
    generate = Mock(
        side_effect=[None, subprocess.CalledProcessError(1, []), None, None]
    )
    monkeypatch.setattr(manage, "generate_rule_reference", generate)
    monkeypatch.setattr(manage.time, "sleep", lambda _: None)
    process = Mock(returncode=0)
    process.poll.side_effect = [None, None, None, 0, 0]
    monkeypatch.setattr(manage.subprocess, "Popen", Mock(return_value=process))

    assert manage.serve([]) == 0
    assert generate.call_count == 4
    assert "fix the sources to retry" in capsys.readouterr().err
    process.wait.assert_called_once_with(timeout=5)
