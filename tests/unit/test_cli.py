from pathlib import Path

from click.testing import CliRunner

# TODO: Migrate CLI properly to kindlemint package
import sys
from pathlib import Path

# Add scripts to path for now
scripts_path = Path(__file__).parent.parent.parent / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

import cli.main as cli_module
from cli.main import FORMATTERS, cli


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
