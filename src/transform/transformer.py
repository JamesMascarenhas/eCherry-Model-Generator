from src.metamodel.metamodel import ReactorModel
from src.validator import validate

_LIB   = "eCherry_Library"
_ALIAS = "Echery_library"  # spelling used in eCherry examples

_SPECIES_FQN: dict[str, str] = {
    "O2":  f"{_LIB}.Data.DataRecords.Species.GaseousSpecies.O2",
    "H2":  f"{_LIB}.Data.DataRecords.Species.GaseousSpecies.H2",
    "Hp":  f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.Hp",
    "OHm": f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.OHm",
    "Kp":  f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.Kp",
    "H2O": f"{_LIB}.Data.DataRecords.Species.LiquidSpecies.H2O",
    # ammonia species
    "N2":  f"{_LIB}.Data.DataRecords.Species.GaseousSpecies.N2",
    "NH3": f"{_LIB}.Data.DataRecords.Species.DissolvedSpecies.NH3",
}

_REACTION_FQN: dict[str, str] = {
    "OERdummy": f"{_LIB}.Data.DataRecords.ElecReaction.List_Of_Reactions.OERdummy",
    "HERdummy": f"{_LIB}.Data.DataRecords.ElecReaction.List_Of_Reactions.HERdummy",
    "NRRdummy": f"{_LIB}.Data.DataRecords.ElecReaction.List_Of_Reactions.NRRdummy",
}

_USER_INPUT_RECORD: dict[str, str] = {
    "simple": "Example_AlkalineWaterElectrolysis",
    "KOH":    "Example_AlkalineWaterElectrolysis_KOH",
}


def _fmt_array(values: list) -> str:
    """Format a Python list as a Modelica array literal string for context."""
    def _n(v):
        return str(v) if isinstance(v, int) else f"{v:.6g}"
    return "{" + ", ".join(_n(v) for v in values) + "}"


def transform(model: ReactorModel) -> dict:
    validate(model)

    is_ammonia   = model.setup == "continuous_0D_ammonia"
    is_batch     = model.setup == "batch_0D_alkaline"
    is_1d_conti  = model.setup == "continuous_1D_alkaline"
    mode         = model.electrolyte.mode
    c0           = model.electrolyte.c0
    inflow_scale = model.conditions.inflow_scale

    # --- package placement and baseline record ---
    if is_ammonia:
        within_model        = f"{_LIB}.Examples.AlkalineAmmoniaElectrolyzer"
        baseline_record_name = "Example_AlkalineAmmoniaElectrolyzer"
    elif is_batch:
        within_model        = f"{_LIB}.Examples.Batch.Batch0D"
        baseline_record_name = _USER_INPUT_RECORD[mode]
    else:
        within_model        = f"{_LIB}.Examples.Continuous"
        baseline_record_name = _USER_INPUT_RECORD[mode]

    # --- ammonia-specific context (None for AWE families) ---
    if is_ammonia:
        gcp = model.gas_channel_params
        ammonia_ctx = {
            # geometry record values
            "geo_X_mem":  model.geometry.X_membrane,   # GeoRecMem.X
            "geo_X_elec": model.geometry.X_electrode,  # GeoRecElec.X
            # gas channel params
            "gas_channel_slices":       gcp.slices,
            "gas_channel_t":            gcp.t,
            "gas_channel_mol_vec_frac0": _fmt_array(gcp.mol_vec_frac0),
            "c0_gas_channel":            _fmt_array(gcp.c0_gas_channel),
            # species record name (AESspec vs AWEspec)
            "spec_record_name": "AESspec",
            # extra cathode reaction (NRRdummy)
            "cathode_extra_reaction": (
                model.cathode.extra_reactions[0]
                if model.cathode.extra_reactions else None
            ),
            # FQNs for new component types
            "fqn_gde": (
                f"{_ALIAS}.ElectrochemicalReactor.Electrodes.Electrode_GasDiffusion"
            ),
            "fqn_gas_channel_compartment": (
                f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain"
                ".Compartments.Gas.GasChannel"
            ),
            "fqn_liquid_inflow": (
                f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain"
                ".Flows.Material_L_InFlow_ResTime"
            ),
            "fqn_gas_inflow": (
                f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain"
                ".Flows.Material_G_InFlow_ResTime"
            ),
            "fqn_simple_outflow": (
                f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain"
                ".Flows.Material_Simple_OutFlow"
            ),
        }
    else:
        ammonia_ctx = {
            "geo_X_mem": None, "geo_X_elec": None,
            "gas_channel_slices": None, "gas_channel_t": None,
            "gas_channel_mol_vec_frac0": None, "c0_gas_channel": None,
            "spec_record_name": "AWEspec",
            "cathode_extra_reaction": None,
            "fqn_gde": None, "fqn_gas_channel_compartment": None,
            "fqn_liquid_inflow": None, "fqn_gas_inflow": None,
            "fqn_simple_outflow": None,
        }

    # --- 1D diffusion layer context (None for 0D families) ---
    if is_1d_conti:
        dl = model.diffusion_layer
        diff_ctx = {
            "X_difflayer":       dl.X_difflayer,
            "kappa_anode_diff":  dl.kappa_anode,
            "kappa_cathode_diff": dl.kappa_cathode,
            "diff_dX":           1e-7,   # hardcoded from gold standard
            "fqn_diff_layer": (
                f"{_ALIAS}.ElectrochemicalReactor.Electrolytes.Liquid"
                ".Electrolyte_Batch_1D_L_nLayers"
            ),
            "fqn_conn_layer": (
                f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain"
                ".ConnectionLayers.ConnectionLayer_Diffusive"
            ),
        }
    else:
        diff_ctx = {
            "X_difflayer": None, "kappa_anode_diff": None,
            "kappa_cathode_diff": None, "diff_dX": None,
            "fqn_diff_layer": None, "fqn_conn_layer": None,
        }

    return {
        # --- identity ---
        "name":                   model.name,
        "electrolyte_mode":       mode,
        "user_input_record_name": model.name + "_UserInput",
        "baseline_record_name":   baseline_record_name,

        # --- Modelica package placement ---
        "within_user_input": f"{_LIB}.Data.UserInput",
        "within_model":      within_model,

        # --- import alias ---
        "import_alias":  _ALIAS,
        "import_target": _LIB,

        # --- family flags ---
        "is_ammonia":  is_ammonia,
        "is_batch":    is_batch,
        "is_1d_conti": is_1d_conti,

        # --- KOH conductivity (AWE only) ---
        "use_koh_conductivity": (not is_ammonia) and (not is_1d_conti) and (mode == "KOH"),
        "fqn_koh_conductivity": (
            f"{_LIB}.ElectrochemicalReactor.Properties.ConductivityModels"
            ".ConductivityElectrolyteCalcKOH"
        ),

        # --- activation overpotential ---
        "fqn_activation_overpotential": (
            f"{_LIB}.ElectrochemicalReactor.Electrodes.Electrochemistry"
            ".Activation_Overpotential.ActivationOverpotential"
        ),

        # --- shared component FQNs (via import alias) ---
        "fqn_voltage_source":  f"{_ALIAS}.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed",
        "fqn_electrode":       f"{_ALIAS}.ElectrochemicalReactor.Electrodes.Electrode_Planar",
        "fqn_electrolyte": (
            f"{_ALIAS}.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_0D_L"
            if is_batch else
            f"{_ALIAS}.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L"
        ),
        "fqn_separator":       f"{_ALIAS}.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide",
        "fqn_inflow":          f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed",
        "fqn_connecting_flow": f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow",
        "fqn_environment":     f"{_ALIAS}.ElectrochemicalReactor.MaterialDomain.Flows.Environment",
        "fqn_ground":          "Modelica.Electrical.Analog.Basic.Ground",

        # --- data record FQNs (UserInput template) ---
        "fqn_species_record":  f"{_LIB}.Data.DataRecords.Species.SpeciesRecord",
        "fqn_reaction_record": f"{_LIB}.Data.DataRecords.ElecReaction.Reaction",
        "fqn_geometry":        f"{_LIB}.Data.DataRecords.Geometry",
        "fqn_conditions":      f"{_LIB}.Data.DataRecords.Conditions",

        # --- species ---
        "species":      model.electrolyte.species,
        "species_fqns": [_SPECIES_FQN[s] for s in model.electrolyte.species],

        # --- reactions ---
        "anode_reaction":       model.anode.reaction,
        "cathode_reaction":     model.cathode.reaction,
        "anode_reaction_fqn":   _REACTION_FQN[model.anode.reaction],
        "cathode_reaction_fqn": _REACTION_FQN[model.cathode.reaction],

        # --- electrical ---
        "voltage": model.conditions.voltage,

        # --- geometry (flat, AWE use) ---
        "geo_X":          model.geometry.X,
        "geo_X_membrane": model.geometry.X_membrane,
        "geo_Y":          model.geometry.Y,
        "geo_Z":          model.geometry.Z,
        "geo_cond0":      model.geometry.cond0,
        "geo_dX":         model.geometry.dX,

        # --- operating conditions ---
        "T0":           model.conditions.T0,
        "Tenvironment": model.conditions.Tenvironment,
        "p":            model.conditions.p,

        # --- concentrations (AWE use) ---
        "c0":             c0,
        "pi":             [100000] * len(model.electrolyte.species),
        "inflow_molflow": [c * inflow_scale for c in c0],

        # --- conductivity (AWE use) ---
        "kappa_anode":   model.anode.kappa,
        "kappa_cathode": model.cathode.kappa,

        # --- separator (AWE use) ---
        "diaphragm_kappa": model.separator.kappa,
        "diaphragm_X":     model.geometry.X_membrane,

        # --- flow scaling (AWE use) ---
        "inflow_scale": inflow_scale,

        # --- simulation ---
        "sim_stop_time": model.sim_stop_time,

        # --- ammonia-specific (None for AWE) ---
        **ammonia_ctx,

        # --- 1D diffusion layer (None for 0D families) ---
        **diff_ctx,
    }