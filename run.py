import sys
from pathlib import Path

from src.parser.parser import parse
from src.transform.transformer import transform
from src.generator.generator import generate

OUTPUT_DIR = "results/generated"


def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py <path/to/file.reactor>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if input_path.suffix != ".reactor":
        print(f"Error: expected a .reactor file, got: {input_path}")
        sys.exit(1)

    if not input_path.exists():
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    try:
        model = parse(str(input_path))
        ctx   = transform(model)
        generate(ctx, OUTPUT_DIR)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    name = ctx["name"]
    out  = Path(OUTPUT_DIR)
    print("Generation successful")
    print(f"Input:  {input_path}")
    print(f"Output: {out / f'{name}_UserInput.mo'}")
    print(f"        {out / f'{name}_Model.mo'}")


if __name__ == "__main__":
    main()
