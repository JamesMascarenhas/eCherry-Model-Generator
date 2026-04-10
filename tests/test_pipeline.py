import pytest

from src.parser.parser import parse
from src.transform.transformer import transform
from src.validator import validate
from src.generator.generator import generate
from src.metamodel.metamodel import (
    ReactorModel, GeometryParams, OperatingConditions,
    Electrode, Separator, Electrolyte, FlowChannel,
)

DSL_FILE = "dsl/example_awe.reactor"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_model(**overrides) -> ReactorModel:
    """Return a valid ReactorModel with defaults, applying any overrides."""
    defaults = dict(
        name="Test",
        geometry=GeometryParams(),
        conditions=OperatingConditions(voltage=-2.5),
        anode=Electrode(reaction="OERdummy", kappa=75.0),
        cathode=Electrode(reaction="HERdummy", kappa=85.0),
        separator=Separator(),
        electrolyte=Electrolyte(
            species=["O2", "H2", "Hp", "OHm", "H2O"],
            c0=[0.0, 1.45e-12, 1e-4, 6000.0, 55e3],
        ),
        flow_channel=FlowChannel(),
    )
    defaults.update(overrides)
    return ReactorModel(**defaults)


# ---------------------------------------------------------------------------
# Full pipeline happy path
# ---------------------------------------------------------------------------

def test_full_pipeline_produces_output_files(tmp_path):
    model = parse(DSL_FILE)
    ctx = transform(model)
    generate(ctx, str(tmp_path))

    name = ctx["name"]
    assert (tmp_path / f"{name}_UserInput.mo").exists()
    assert (tmp_path / f"{name}_Model.mo").exists()


def test_full_pipeline_output_files_nonempty(tmp_path):
    model = parse(DSL_FILE)
    ctx = transform(model)
    generate(ctx, str(tmp_path))

    name = ctx["name"]
    assert (tmp_path / f"{name}_UserInput.mo").stat().st_size > 0
    assert (tmp_path / f"{name}_Model.mo").stat().st_size > 0


# ---------------------------------------------------------------------------
# Validator — rejection cases
# ---------------------------------------------------------------------------

def test_validator_rejects_positive_voltage():
    model = _minimal_model(conditions=OperatingConditions(voltage=1.0))
    with pytest.raises(ValueError, match="voltage must be negative"):
        validate(model)


def test_validator_rejects_mismatched_c0_length():
    model = _minimal_model(
        electrolyte=Electrolyte(
            species=["O2", "H2", "Hp", "OHm", "H2O"],
            c0=[0.0, 1e-12, 1e-4],          # only 3 values for 5 species
        )
    )
    with pytest.raises(ValueError, match="concentrations length"):
        validate(model)


def test_validator_rejects_unknown_species():
    model = _minimal_model(
        electrolyte=Electrolyte(
            species=["O2", "H2", "Xenon"],
            c0=[0.0, 0.0, 0.0],
        )
    )
    with pytest.raises(ValueError, match="unrecognized species"):
        validate(model)


def test_validator_rejects_invalid_electrolyte_mode():
    model = _minimal_model(
        electrolyte=Electrolyte(
            species=["O2", "H2", "Hp", "OHm", "H2O"],
            c0=[0.0, 1.45e-12, 1e-4, 6000.0, 55e3],
            mode="PEM",
        )
    )
    with pytest.raises(ValueError, match="electrolyte_mode"):
        validate(model)


def test_validator_rejects_wrong_setup():
    model = _minimal_model(setup="batch_mode")
    with pytest.raises(ValueError, match="setup"):
        validate(model)


# ---------------------------------------------------------------------------
# Parser — field population
# ---------------------------------------------------------------------------

def test_parser_populates_name():
    model = parse(DSL_FILE)
    assert model.name == "MyAWE"


def test_parser_populates_voltage():
    model = parse(DSL_FILE)
    assert model.conditions.voltage == pytest.approx(-2.5)


def test_parser_populates_species():
    model = parse(DSL_FILE)
    assert model.electrolyte.species == ["O2", "H2", "Hp", "OHm", "H2O"]


def test_parser_populates_electrolyte_mode():
    model = parse(DSL_FILE)
    assert model.electrolyte.mode == "simple"


def test_parser_populates_anode_reaction():
    model = parse(DSL_FILE)
    assert model.anode.reaction == "OERdummy"


def test_parser_populates_cathode_reaction():
    model = parse(DSL_FILE)
    assert model.cathode.reaction == "HERdummy"


def test_parser_populates_separator_kappa():
    model = parse(DSL_FILE)
    assert model.separator.kappa == pytest.approx(38.0)


# ---------------------------------------------------------------------------
# Transformer — output keys and values
# ---------------------------------------------------------------------------

def test_transformer_sets_user_input_record_name():
    model = parse(DSL_FILE)
    ctx = transform(model)
    assert ctx["user_input_record_name"] == "MyAWE_UserInput"


def test_transformer_resolves_species_fqns():
    model = parse(DSL_FILE)
    ctx = transform(model)
    fqns = ctx["species_fqns"]
    assert len(fqns) == 5
    assert "GaseousSpecies.O2" in fqns[0]
    assert "LiquidSpecies.H2O" in fqns[-1]


def test_transformer_simple_mode_not_koh():
    model = parse(DSL_FILE)
    ctx = transform(model)
    assert ctx["use_koh_conductivity"] is False


def test_transformer_koh_mode_sets_flag():
    model = _minimal_model(
        electrolyte=Electrolyte(
            species=["O2", "H2", "Hp", "OHm", "Kp", "H2O"],
            c0=[0.0, 1.45e-12, 1e-4, 6000.0, 6000.0, 55e3],
            mode="KOH",
        )
    )
    ctx = transform(model)
    assert ctx["use_koh_conductivity"] is True


def test_transformer_contains_expected_keys():
    model = parse(DSL_FILE)
    ctx = transform(model)
    required = {
        "name", "user_input_record_name", "electrolyte_mode",
        "species_fqns", "use_koh_conductivity",
        "anode_reaction_fqn", "cathode_reaction_fqn",
        "voltage", "kappa_anode", "kappa_cathode",
        "diaphragm_kappa", "sim_stop_time", "inflow_scale",
    }
    assert required <= ctx.keys()
