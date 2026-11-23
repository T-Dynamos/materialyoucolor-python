import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)

# When testing an installed wheel (such as in cibuildwheel),
# remove repo_root so site-packages takes precedence.
while repo_root in sys.path:
    sys.path.remove(repo_root)

try:
    from materialyoucolor.scheme.scheme_cmf import SchemeCmf
    from materialyoucolor.quantize import QuantizeWsmeans
except (ImportError, AttributeError):
    # Not installed in site-packages (or outdated system install); use repo_root
    for mod in list(sys.modules.keys()):
        if mod == "materialyoucolor" or mod.startswith("materialyoucolor."):
            del sys.modules[mod]
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
