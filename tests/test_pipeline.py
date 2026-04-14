import pytest

from src.parser.parser import parse
from src.transform.transformer import transform
from src.validator import validate
from src.generator.generator import generate
from src.metamodel.metamodel import (
    ReactorModel, GeometryParams, OperatingConditions,
    Electrode, Separator, Electrolyte, FlowChannel,
    DiffusionLayerParams
)

CONTI_SIMPLE_DSL = "dsl/example_conti_simple.reactor"
CONTI_KOH_DSL    = "dsl/example_conti_koh.reactor"
BATCH_SIMPLE_DSL = "dsl/example_batch_simple.reactor"
BATCH_KOH_DSL    = "dsl/example_batch_koh.reactor"
AMMONIA_DSL = "dsl/example_conti_ammonia.reactor"
CONTI_1D_DSL = "dsl/example_conti_1d_simple.reactor"


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
    
    def test_rejects_1d_without_diffusion_layer(self):
        model = _minimal_model(setup="continuous_1D_alkaline")
        with pytest.raises(ValueError, match="diffusion_layer"):
            validate(model)

    def test_rejects_1d_with_invalid_n_slices(self):
        model = _minimal_model(
            setup="continuous_1D_alkaline",
            diffusion_layer=DiffusionLayerParams(
                X_difflayer=1e-6,
                kappa_anode=85.0,
                kappa_cathode=74.0,
                n_slices=1,
            ),
        )
        with pytest.raises(ValueError, match="n_slices must be at least 2"):
            validate(model)


# ===========================================================================
# CONTINUOUS 0D SIMPLE
# ===========================================================================

class TestContiSimple:

    def test_parser_populates_name(self):
        model = parse(CONTI_SIMPLE_DSL)
        assert model.name == "AWE_Conti_Simple"

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
        assert ctx["user_input_record_name"] == "AWE_Conti_Simple_UserInput"

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


# ===========================================================================
# AMMONIA 0D CONTINUOUS
# ===========================================================================

class TestAmmoniaConti:
    """Parser, transformer, and generator tests for continuous_0D_ammonia."""

    # ── parser ──────────────────────────────────────────────────────────────────

    def test_parser_name(self):
        m = parse(AMMONIA_DSL)
        assert m.name == "AAE_Conti_Ammonia"

    def test_parser_setup(self):
        m = parse(AMMONIA_DSL)
        assert m.setup == "continuous_0D_ammonia"

    def test_parser_species(self):
        m = parse(AMMONIA_DSL)
        assert m.electrolyte.species == ["O2", "H2", "N2", "NH3", "OHm", "Kp", "H2O"]

    def test_parser_cathode_reaction(self):
        m = parse(AMMONIA_DSL)
        assert m.cathode.reaction == "HERdummy"
        assert m.cathode.extra_reactions == ["NRRdummy"]

    def test_parser_cathode_kind(self):
        m = parse(AMMONIA_DSL)
        assert m.cathode.kind == "gas_diffusion"

    def test_parser_anode_reaction(self):
        m = parse(AMMONIA_DSL)
        assert m.anode.reaction == "OERdummy"

    def test_parser_c0_electrolyte(self):
        m = parse(AMMONIA_DSL)
        assert len(m.electrolyte.c0) == 7
        assert m.electrolyte.c0[2] == 0.0       # N2 dissolved = 0
        assert m.electrolyte.c0[4] == 6000.0    # OHm

    def test_parser_gas_channel_params(self):
        m = parse(AMMONIA_DSL)
        gcp = m.gas_channel_params
        assert gcp is not None
        assert gcp.slices == 10
        assert gcp.t == 5.0
        assert gcp.mol_vec_frac0[2] == 1.0      # N2 fraction = 1
        assert gcp.c0_gas_channel[2] == 1.0     # N2 in gas channel = 1

    def test_parser_x_electrode(self):
        m = parse(AMMONIA_DSL)
        assert m.geometry.X_electrode == 0.005

    # ── transformer ─────────────────────────────────────────────────────────────

    def test_transformer_is_ammonia_flag(self):
        ctx = transform(parse(AMMONIA_DSL))
        assert ctx["is_ammonia"] is True
        assert ctx["is_batch"] is False

    def test_transformer_within_model(self):
        ctx = transform(parse(AMMONIA_DSL))
        assert ctx["within_model"] == "eCherry_Library.Examples.AlkalineAmmoniaElectrolyzer"

    def test_transformer_baseline_record(self):
        ctx = transform(parse(AMMONIA_DSL))
        assert ctx["baseline_record_name"] == "Example_AlkalineAmmoniaElectrolyzer"

    def test_transformer_species_fqns(self):
        ctx = transform(parse(AMMONIA_DSL))
        fqns = ctx["species_fqns"]
        assert any("N2" in f for f in fqns)
        assert any("NH3" in f for f in fqns)

    def test_transformer_fqn_gde(self):
        ctx = transform(parse(AMMONIA_DSL))
        assert "Electrode_GasDiffusion" in ctx["fqn_gde"]

    def test_transformer_cathode_extra_reaction(self):
        ctx = transform(parse(AMMONIA_DSL))
        assert ctx["cathode_extra_reaction"] == "NRRdummy"

    def test_transformer_koh_conductivity_false(self):
        # ammonia never uses KOH conductivity redeclare
        ctx = transform(parse(AMMONIA_DSL))
        assert ctx["use_koh_conductivity"] is False

    # ── generator ───────────────────────────────────────────────────────────────

    def test_generator_model_contains_gde(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text()
        assert "Electrode_GasDiffusion" in text

    def test_generator_model_contains_gas_channel(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text()
        assert "GasChannel" in text

    def test_generator_model_within(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text()
        assert "within eCherry_Library.Examples.AlkalineAmmoniaElectrolyzer" in text

    def test_generator_model_no_pi_array(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text()
        # ammonia electrodes do not emit Pi(each displayUnit="bar")
        assert 'Pi(each displayUnit="bar")' not in text

    def test_generator_userinput_aesspec(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text()
        assert "AESspec" in text

    def test_generator_userinput_three_georecs(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text()
        assert "GeoRec(" in text
        assert "GeoRecMem(" in text
        assert "GeoRecElec(" in text

    def test_generator_userinput_c0_electrolyte(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text()
        assert "c0_Electrolyte" in text
        assert "c0_GasChannel" in text

    def test_generator_userinput_slices(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text()
        assert "slices" in text
        assert "1/slices" in text

    def test_generator_model_diaphragm_has_kappa_and_X(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text()
        assert "Diaphragm(" in text
        assert "kappa" in text
        assert "X       =" in text or "X=" in text

    def test_generator_userinput_slices_before_georec(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text()
        # slices must be declared before GeoRec which uses 1/slices
        assert text.index("slices") < text.index("GeoRec(")

    def test_generator_userinput_no_molflow(self, tmp_path):
        ctx = transform(parse(AMMONIA_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text()
        assert "molFlow_vec" not in text
        assert "Pi[" not in text
    

# ===========================================================================
# CONTINUOUS 1D ALKALINE
# ===========================================================================

    class TestConti1D:
        """Parser, transformer, and generator tests for continuous_1D_alkaline."""

    def test_parser_populates_1d_setup(self):
        model = parse(CONTI_1D_DSL)
        assert model.setup == "continuous_1D_alkaline"

    def test_parser_populates_diffusion_layer(self):
        model = parse(CONTI_1D_DSL)
        assert model.diffusion_layer is not None
        assert model.diffusion_layer.X_difflayer == pytest.approx(1e-6)
        assert model.diffusion_layer.kappa_anode == pytest.approx(85.0)
        assert model.diffusion_layer.kappa_cathode == pytest.approx(74.0)

    def test_parser_populates_diffusion_layer_n_slices(self):
        model = parse(CONTI_1D_DSL)
        assert model.diffusion_layer is not None
        assert model.diffusion_layer.n_slices == 10

    def test_transformer_sets_1d_flag(self):
        ctx = transform(parse(CONTI_1D_DSL))
        assert ctx["is_1d_conti"] is True
        assert ctx["is_batch"] is False
        assert ctx["is_ammonia"] is False

    def test_transformer_within_model(self):
        ctx = transform(parse(CONTI_1D_DSL))
        assert ctx["within_model"] == "eCherry_Library.Examples.Continuous"

    def test_transformer_disables_koh_for_1d_simple(self):
        ctx = transform(parse(CONTI_1D_DSL))
        assert ctx["use_koh_conductivity"] is False

    def test_transformer_sets_diffusion_layer_context(self):
        ctx = transform(parse(CONTI_1D_DSL))
        assert ctx["X_difflayer"] == pytest.approx(1e-6)
        assert ctx["kappa_anode_diff"] == pytest.approx(85.0)
        assert ctx["kappa_cathode_diff"] == pytest.approx(74.0)
        assert ctx["n_slices"] == 10
        assert "Electrolyte_Batch_1D_L_nLayers" in ctx["fqn_diff_layer"]
        assert "ConnectionLayer_Diffusive" in ctx["fqn_conn_layer"]

    def test_generator_model_contains_diffusion_layers(self, tmp_path):
        ctx = transform(parse(CONTI_1D_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "Diff_Anolyte" in text
        assert "Diff_Catholyte" in text
        assert "Electrolyte_Batch_1D_L_nLayers" in text

    def test_generator_model_contains_connection_layers(self, tmp_path):
        ctx = transform(parse(CONTI_1D_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "ConnLayer_Anode" in text
        assert "ConnLayer_Cathode" in text
        assert "ConnectionLayer_Diffusive" in text

    def test_generator_model_contains_n_slices(self, tmp_path):
        ctx = transform(parse(CONTI_1D_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "n_slices" in text

    def test_generator_model_contains_1d_connect_pattern(self, tmp_path):
        ctx = transform(parse(CONTI_1D_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "Model.mo").read_text(encoding="utf-8")
        assert "Anode.flowFromElectrolyte" in text
        assert "Diff_Anolyte.leftFlow" in text
        assert "ConnLayer_Anode.leftFlow" in text
        assert "Diff_Catholyte.leftFlow" in text
        assert "Cathode.flowFromElectrolyte" in text

    def test_generator_userinput_contains_x_difflayer(self, tmp_path):
        ctx = transform(parse(CONTI_1D_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text(encoding="utf-8")
        assert "X_difflayer" in text

    def test_generator_userinput_still_uses_awe_spec(self, tmp_path):
        ctx = transform(parse(CONTI_1D_DSL))
        generate(ctx, str(tmp_path))
        text = (tmp_path / "UserInput.mo").read_text(encoding="utf-8")
        assert "AWEspec" in text
        assert "AESspec" not in text