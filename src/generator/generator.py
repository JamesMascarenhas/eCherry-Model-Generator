from pathlib import Path
from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _monum(v) -> str:
    """Format a Python float/int for Modelica output (6 significant figures, no trailing zeros)."""
    if isinstance(v, int):
        return str(v)
    return f"{v:.6g}"


def _moarray(values) -> str:
    """Format a Python list as a Modelica array literal."""
    return "{" + ", ".join(_monum(v) for v in values) + "}"


def generate(ctx: dict, output_dir: str) -> None:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["monum"]   = _monum
    env.filters["moarray"] = _moarray

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ui_tmpl    = env.get_template("user_input.mo.j2")
    model_tmpl = env.get_template("top_model.mo.j2")

    (out / "UserInput.mo").write_text(ui_tmpl.render(ctx), encoding="utf-8")
    (out / "Model.mo").write_text(model_tmpl.render(ctx), encoding="utf-8")
