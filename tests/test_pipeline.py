import pytest

from src.parser.parser import parse
from src.transform.transformer import transform
from src.validator import validate
from src.generator.generator import generate
from src.metamodel.metamodel import (
    ReactorModel, GeometryParams, OperatingConditions,
    Electrode, Separator, Electrolyte, FlowChannel,
)

CONTI_SIMPLE_DSL = "dsl/example_conti_simple.reactor"
CONTI_KOH_DSL    = "dsl/example_conti_koh.reactor"
BATCH_SIMPLE_DSL = "dsl/example_batch_simple.reactor"
BATCH_KOH_DSL    = "dsl/example_batch_koh.reactor"


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


# ===========================================================================
# VALIDATOR — rejection cases
# ===========================================================================

class TestValidator:

    def test_rejects_positive_voltage(self):
        model = _minimal_model(conditions=OperatingConditions(voltage=1.0))
        with pytest.raises(ValueError, match="voltage must be negative"):
            validate(model)

    def test_rejects_mismatched_c0_length(self):
        model = _minimal_model(
            electrolyte=Electrolyte(
                species=["O2", "H2", "Hp", "OHm", "H2O"],
                c0=[0.0, 1e-12, 1e-4],
            )
        )
        with pytest.raises(ValueError, match="concentrations length"):
            validate(model)

    def test_rejects_unknown_species(self):
        model = _minimal_model(
            electrolyte=Electrolyte(
                species=["O2", "H2", "Xenon"],
                c0=[0.0, 0.0, 0.0],
            )
        )
        with pytest.raises(ValueError, match="unrecognized species"):
            validate(model)

    def test_rejects_invalid_electrolyte_mode(self):
        model = _minimal_model(
            electrolyte=Electrolyte(
                species=["O2", "H2", "Hp", "OHm", "H2O"],
                c0=[0.0, 1.45e-12, 1e-4, 6000.0, 55e3],
                mode="PEM",
            )
        )
        with pytest.raises(ValueError, match="electrolyte_mode"):
            validate(model)

    def test_rejects_wrong_setup(self):
        model = _minimal_model(setup="batch_mode")
        with pytest.raises(ValueError, match="setup"):
            validate(model)

    def test_accepts_continuous_setup(self):
        model = _minimal_model(setup="continuous_0D_alkaline")
        validate(model)  # should not raise

    def test_accepts_batch_setup(self):
        model = _minimal_model(setup="batch_0D_alkaline")
        validate(model)  # should not raise


# ===========================================================================
# CONTINUOUS 0D SIMPLE
# ===========================================================================

class TestContiSimple:

    def test_parser_populates_name(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.name == "MyAWE"

    def test_parser_populates_setup(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.setup == "continuous_0D_alkaline"

    def test_parser_populates_voltage(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.conditions.voltage == pytest.approx(-2.5)

    def test_parser_populates_species(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.electrolyte.species == ["O2", "H2", "Hp", "OHm", "H2O"]

    def test_parser_populates_electrolyte_mode(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.electrolyte.mode == "simple"

    def test_parser_populates_anode_reaction(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.anode.reaction == "OERdummy"

    def test_parser_populates_cathode_reaction(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.cathode.reaction == "HERdummy"

    def test_parser_populates_separator_kappa(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.separator.kappa == pytest.approx(38.0)

    def test_transformer_sets_user_input_record_name(self):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        assert ctx["user_input_record_name"] == "MyAWE_UserInput"

    def test_transformer_resolves_species_fqns(self):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        fqns = ctx["species_fqns"]
        assert len(fqns) == 5
        assert "GaseousSpecies.O2" in fqns[0]
        assert "LiquidSpecies.H2O" in fqns[-1]

    def test_transformer_not_koh(self):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        assert ctx["use_koh_conductivity"] is False
        assert ctx["is_batch"] is False

    def test_transformer_contains_expected_keys(self):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        required = {
            "name", "user_input_record_name", "electrolyte_mode",
            "species_fqns", "use_koh_conductivity", "is_batch",
            "anode_reaction_fqn", "cathode_reaction_fqn",
            "voltage", "kappa_anode", "kappa_cathode",
            "diaphragm_kappa", "sim_stop_time", "inflow_scale",
        }
        assert required <= ctx.keys()

    def test_full_pipeline_produces_output_files(self, tmp_path):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        assert (tmp_path / "UserInput.mo").exists()
        assert (tmp_path / "Model.mo").exists()

    def test_full_pipeline_output_files_nonempty(self, tmp_path):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        assert (tmp_path / "UserInput.mo").stat().st_size > 0
        assert (tmp_path / "Model.mo").stat().st_size > 0

    def test_generated_model_contains_separator(self, tmp_path):
        model = parse(CONTI_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "Diaphragm_Hydroxide" in text
        assert "AnodeInflow" in text
        assert "kappa_const" in text


# ===========================================================================
# CONTINUOUS 0D KOH
# ===========================================================================

class TestContiKOH:

    def test_parser_populates_setup(self):
        model = parse(CONTI_KOH_DSL)
        assert model.setup == "continuous_0D_alkaline"

    def test_parser_populates_koh_mode(self):
        model = parse(CONTI_KOH_DSL)
        assert model.electrolyte.mode == "KOH"

    def test_parser_populates_koh_species(self):
        model = parse(CONTI_KOH_DSL)
        assert "Kp" in model.electrolyte.species
        assert len(model.electrolyte.species) == 6

    def test_transformer_sets_koh_flag(self):
        model = parse(CONTI_KOH_DSL)
        ctx = transform(model)
        assert ctx["use_koh_conductivity"] is True
        assert ctx["is_batch"] is False

    def test_transformer_within_model(self):
        model = parse(CONTI_KOH_DSL)
        ctx = transform(model)
        assert ctx["within_model"] == "eCherry_Library.Examples.Continuous"

    def test_full_pipeline_produces_output_files(self, tmp_path):
        model = parse(CONTI_KOH_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        assert (tmp_path / "UserInput.mo").exists()
        assert (tmp_path / "Model.mo").exists()

    def test_generated_model_uses_koh_conductivity(self, tmp_path):
        model = parse(CONTI_KOH_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "ConductivityElectrolyteCalcKOH" in text
        assert "kappa_const" not in text


# ===========================================================================
# BATCH 0D SIMPLE
# ===========================================================================

class TestBatchSimple:

    def test_parser_populates_batch_setup(self):
        model = parse(BATCH_SIMPLE_DSL)
        assert model.setup == "batch_0D_alkaline"

    def test_parser_populates_simple_mode(self):
        model = parse(BATCH_SIMPLE_DSL)
        assert model.electrolyte.mode == "simple"

    def test_transformer_batch_flags(self):
        model = parse(BATCH_SIMPLE_DSL)
        ctx = transform(model)
        assert ctx["is_batch"] is True
        assert ctx["use_koh_conductivity"] is False
        assert ctx["within_model"] == "eCherry_Library.Examples.Batch.Batch0D"
        assert ctx["fqn_electrolyte"].endswith("Electrolyte_Batch_0D_L")

    def test_full_pipeline_produces_output_files(self, tmp_path):
        model = parse(BATCH_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        assert (tmp_path / "UserInput.mo").exists()
        assert (tmp_path / "Model.mo").exists()

    def test_generated_model_omits_flow_components(self, tmp_path):
        model = parse(BATCH_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "AnodeInflow" not in text
        assert "CathodeInflow" not in text
        assert "Material_Simple_InFlow_Fixed" not in text
        assert "Flow_anode" not in text
        assert "Flow_Cathode" not in text
        assert "env_anode" not in text
        assert "env_cathode" not in text

    def test_generated_model_uses_single_electrolyte(self, tmp_path):
        model = parse(BATCH_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "Anolyte" not in text
        assert "Catholyte" not in text
        assert "Electrolyte(" in text
        assert "Electrolyte_Batch_0D_L" in text

    def test_generated_model_omits_separator(self, tmp_path):
        model = parse(BATCH_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "Diaphragm" not in text

    def test_generated_model_within_clause(self, tmp_path):
        model = parse(BATCH_SIMPLE_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "within eCherry_Library.Examples.Batch.Batch0D" in text


# ===========================================================================
# BATCH 0D KOH
# ===========================================================================

class TestBatchKOH:

    def test_parser_populates_batch_koh_setup(self):
        model = parse(BATCH_KOH_DSL)
        assert model.setup == "batch_0D_alkaline"
        assert model.electrolyte.mode == "KOH"

    def test_parser_populates_koh_species(self):
        model = parse(BATCH_KOH_DSL)
        assert "Kp" in model.electrolyte.species
        assert len(model.electrolyte.species) == 6

    def test_transformer_batch_koh_flags(self):
        model = parse(BATCH_KOH_DSL)
        ctx = transform(model)
        assert ctx["is_batch"] is True
        assert ctx["use_koh_conductivity"] is True
        assert ctx["within_model"] == "eCherry_Library.Examples.Batch.Batch0D"

    def test_full_pipeline_produces_output_files(self, tmp_path):
        model = parse(BATCH_KOH_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        assert (tmp_path / "UserInput.mo").exists()
        assert (tmp_path / "Model.mo").exists()

    def test_generated_model_uses_koh_conductivity(self, tmp_path):
        model = parse(BATCH_KOH_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "ConductivityElectrolyteCalcKOH" in text

    def test_generated_model_omits_flow_components(self, tmp_path):
        model = parse(BATCH_KOH_DSL)
        ctx = transform(model)
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "AnodeInflow" not in text
        assert "Diaphragm" not in text
        assert "Electrolyte_Batch_0D_L" in text