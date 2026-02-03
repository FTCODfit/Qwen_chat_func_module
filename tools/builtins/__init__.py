from importlib import import_module
from pathlib import Path

# __init__ 先註冊好工具，省得以後慢慢 import
TOOLS = []
for path in Path(__file__).parent.glob("*.py"):
    if path.name.startswith("_") or path.name == "__init__.py":
        continue

    module = import_module(f"{__package__}.{path.stem}")

    for obj in vars(module).values():
        schema = getattr(obj, "__tool_schema__", None)
        if schema:
            TOOLS.append(schema)
