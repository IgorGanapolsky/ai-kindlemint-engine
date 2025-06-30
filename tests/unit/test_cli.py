from pathlib import Path

from click.testing import CliRunner

import scripts.cli.main as cli_module
from scripts.cli.main import FORMATTERS, cli


class DummyFormatter:
        """  Init  """
def __init__(self, output_path=None):
        self.output_path = output_path

        """Create Pdf"""
def create_pdf(self):
        return Path("dummy_output.txt")


    """Test List Formatters"""
def test_list_formatters():
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    for name in FORMATTERS:
        assert name in result.output


    """Test Generate With Dummy Formatter"""
def test_generate_with_dummy_formatter(monkeypatch):
    # Add a dummy formatter for testing
    monkeypatch.setitem(cli_module.FORMATTERS, "dummy", DummyFormatter)
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--formatter", "dummy"])
    assert result.exit_code == 0
    assert "Generated: dummy_output.txt" in result.output
