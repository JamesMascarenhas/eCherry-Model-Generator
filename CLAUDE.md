# CLAUDE.md — eCherry DSL Generator (CISC 844 Project)

## Project Summary

Build a lightweight model-driven pipeline:

```
.reactor (DSL file) → parser → metamodel → transformer → generator → .mo (Modelica)
```

**Target**: Generate eCherry-compatible Modelica artifacts across multiple reactor families.

**Language**: Python only. No Xtext, EMF, MPS, or heavy tooling.

**Status**: Core pipeline complete. Six configurations implemented. Interactive wizard complete.

---

## Current Implementation Status

### Reactor Families — Implemented ✅
| Setup | Simple | KOH | Ammonia |
|---|---|---|---|
| `continuous_0D_alkaline` | ✅ | ✅ | ✅ |
| `batch_0D_alkaline` | ✅ | ✅ | — |
| `continuous_1D_alkaline` | ✅ | — | — |

### Pipeline — All stages complete ✅
- `src/parser/parser.py` — hand-written line-by-line parser
- `src/metamodel/metamodel.py` — Python dataclasses
- `src/validator.py` — nine semantic checks
- `src/transform/transformer.py` — ReactorModel → GeneratorContext dict
- `src/generator/generator.py` + two Jinja2 templates
- `run.py` — CLI entry point with clean error handling
- `reactor_builder.py` — interactive wizard: guided DSL authoring + automatic generation
- `tests/test_pipeline.py` — **84 passing pytest tests**

---

## Directory Layout

```
project/
├── CLAUDE.md                         # this file (git-ignored, present locally)
├── README.md
├── requirements.txt                  # jinja2, pytest
├── .gitignore
├── run.py                            # CLI: python run.py dsl/example_conti_simple.reactor
├── reactor_builder.py                # interactive wizard: python reactor_builder.py
├── dsl/
│   ├── example_conti_simple.reactor  # continuous 0D simple
│   ├── example_conti_koh.reactor     # continuous 0D KOH
│   ├── example_batch_simple.reactor  # batch 0D simple
│   ├── example_batch_koh.reactor     # batch 0D KOH
│   ├── example_conti_ammonia.reactor # continuous 0D ammonia
│   └── example_conti_1d_simple.reactor  # continuous 1D simple
├── src/
│   ├── parser/
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── metamodel/
│   │   ├── __init__.py
│   │   └── metamodel.py
│   ├── transform/
│   │   ├── __init__.py
│   │   └── transformer.py
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── templates/
│   │       ├── top_model.mo.j2
│   │       └── user_input.mo.j2
│   └── validator.py
├── results/
│   ├── generated/
│   │   ├── example_conti_simple/
│   │   │   ├── Model.mo
│   │   │   └── UserInput.mo
│   │   ├── example_conti_koh/
│   │   │   ├── Model.mo
│   │   │   └── UserInput.mo
│   │   ├── example_batch_simple/
│   │   │   ├── Model.mo
│   │   │   └── UserInput.mo
│   │   ├── example_batch_koh/
│   │   │   ├── Model.mo
│   │   │   └── UserInput.mo
│   │   ├── example_conti_ammonia/
│   │   │   ├── Model.mo
│   │   │   └── UserInput.mo
│   │   └── example_conti_1d_simple/
│   │       ├── Model.mo
│   │       └── UserInput.mo
│   └── manual/                       # reference .mo files from eCherry
├── tests/
│   └── test_pipeline.py
└── docs/
    ├── Project Plan.pdf
    ├── Project Proposal.pdf
    └── Proposal Plan.pdf
```

### Output naming convention
- `run.py dsl/example_conti_simple.reactor` → `results/generated/example_conti_simple/Model.mo` and `UserInput.mo`
- The subfolder name comes from the DSL filename (without `.reactor`)
- The files inside are always just `Model.mo` and `UserInput.mo`
- The reactor `name` field inside the DSL drives the Modelica record/model names (e.g. `AWE_Conti_Simple_UserInput`)

---

## DSL Files and Their Reactor Names

| DSL file | `reactor` name inside | Setup | Mode |
|---|---|---|---|
| `example_conti_simple.reactor` | `AWE_Conti_Simple` | `continuous_0D_alkaline` | `simple` |
| `example_conti_koh.reactor` | `AWE_Conti_KOH` | `continuous_0D_alkaline` | `KOH` |
| `example_batch_simple.reactor` | `AWE_Batch_Simple` | `batch_0D_alkaline` | `simple` |
| `example_batch_koh.reactor` | `AWE_Batch_KOH` | `batch_0D_alkaline` | `KOH` |
| `example_conti_ammonia.reactor` | `AAE_Conti_Ammonia` | `continuous_0D_ammonia` | — |
| `example_conti_1d_simple.reactor` | `AWE_Conti_1D_Simple` | `continuous_1D_alkaline` | `simple` |

---

## Current Metamodel (`src/metamodel/metamodel.py`)

```python
@dataclass
class GeometryParams:
    X: float = 0.01
    X_membrane: float = 0.0005
    Y: float = 1.0
    Z: float = 1.0
    cond0: float = 1.0
    dX: float = 1e-6
    X_electrode: float = 0.005   # ammonia only — GeoRecElec.X; ignored by AWE

@dataclass
class OperatingConditions:
    T0: float = 300.0
    Tenvironment: float = 293.15
    p: float = 1.0
    voltage: float = -2.5
    inflow_scale: float = 0.005  # 1D uses 0.05; read from DSL conditions block

@dataclass
class Electrode:
    reaction: str
    kappa: float
    kind: str = "planar"
    extra_reactions: list[str] | None = None  # ammonia cathode only

@dataclass
class Separator:
    kind: str = "hydroxide_diaphragm"
    kappa: float = 38.0

@dataclass
class Electrolyte:
    species: list[str]
    c0: list[float]
    mode: str = "simple"       # "simple" or "KOH" — not used for ammonia

@dataclass
class FlowChannel:
    mode: str = "simple_fixed"

@dataclass
class GasChannelParams:
    """Ammonia-specific. None for all AWE families."""
    mol_vec_frac0: list[float]
    c0_gas_channel: list[float]
    slices: int = 10
    t: float = 5.0

@dataclass
class DiffusionLayerParams:
    """1D diffusion boundary layer — None for all 0D families."""
    X_difflayer: float = 1e-6    # total thickness of diffusion layer
    kappa_anode: float = 85.0    # conductivity of anode diffusion layer
    kappa_cathode: float = 74.0  # conductivity of cathode diffusion layer
    n_slices: int = 10           # discretization slices (min 2)

@dataclass
class ReactorModel:
    name: str
    geometry: GeometryParams
    conditions: OperatingConditions
    anode: Electrode
    cathode: Electrode
    separator: Separator
    electrolyte: Electrolyte
    flow_channel: FlowChannel
    sim_stop_time: float = 50.0
    setup: str = "continuous_0D_alkaline"
    gas_channel_params: GasChannelParams | None = None    # ammonia only
    diffusion_layer: DiffusionLayerParams | None = None   # 1D families only
```

---

## Current Validator (`src/validator.py`)

Nine checks — fail fast with clear messages:

1. `len(c0) == len(species)` — electrolyte concentration array matches species count
2. `voltage < 0` — voltage must be negative
3. `setup in _VALID_SETUPS` — `{"continuous_0D_alkaline", "batch_0D_alkaline", "continuous_0D_ammonia", "continuous_1D_alkaline"}`
4. `electrolyte.mode in {"simple", "KOH"}` — skipped for ammonia setup
5. All species names recognized against `_KNOWN_SPECIES`
6. Both `anode.reaction` and `cathode.reaction` in `_KNOWN_REACTIONS`
7. All `cathode.extra_reactions` in `_KNOWN_REACTIONS`
8. Ammonia-specific block (only runs when `setup == "continuous_0D_ammonia"`):
   - `gas_channel_params` must not be None
   - `len(c0_gas_channel) == len(species)`
   - `len(mol_vec_frac0) == len(species)`
   - `cathode.kind == "gas_diffusion"`
9. 1D-specific block (only runs when `setup == "continuous_1D_alkaline"`):
   - `diffusion_layer` must not be None
   - `diffusion_layer.n_slices >= 2`

When adding new families: update `_VALID_SETUPS`, `_KNOWN_SPECIES`, and `_KNOWN_REACTIONS`.

---

## Current Transformer (`src/transform/transformer.py`)

Key context flags:
- `is_batch` — True when `setup == "batch_0D_alkaline"`
- `is_ammonia` — True when `setup == "continuous_0D_ammonia"`
- `is_1d_conti` — True when `setup == "continuous_1D_alkaline"`
- `use_koh_conductivity` — True when `(not is_ammonia) and (not is_1d_conti) and (mode == "KOH")`

Key context keys used by templates:
- `within_model` — package placement
- `fqn_electrolyte` — `Electrolyte_Conti_0D_L` vs `Electrolyte_Batch_0D_L`
- `user_input_record_name` — `<ReactorModel.name>_UserInput`
- `is_batch`, `is_ammonia`, `is_1d_conti` — drive template branching
- `use_koh_conductivity` — drives conductivity model selection
- `fqn_activation_overpotential` — full FQN

1D-specific context keys (None for 0D families):
- `fqn_diff_layer` — `Electrolyte_Batch_1D_L_nLayers` FQN
- `fqn_conn_layer` — `ConnectionLayer_Diffusive` FQN
- `X_difflayer` — diffusion layer thickness
- `kappa_anode_diff`, `kappa_cathode_diff` — conductivities
- `n_slices` — discretization count
- `diff_dX` — connection layer dX (hardcoded `1e-7` from gold standard)

Ammonia-specific context keys (None for AWE families):
- `fqn_gde` — `Electrode_GasDiffusion` FQN
- `fqn_gas_channel_compartment` — `GasChannel` FQN
- `fqn_liquid_inflow` — `Material_L_InFlow_ResTime` FQN
- `fqn_gas_inflow` — `Material_G_InFlow_ResTime` FQN
- `fqn_simple_outflow` — `Material_Simple_OutFlow` FQN
- `geo_X_mem`, `geo_X_elec` — membrane and electrode geometry X values
- `gas_channel_slices`, `gas_channel_t`, `gas_channel_mol_vec_frac0`, `c0_gas_channel`
- `cathode_extra_reaction` — the NRRdummy reaction name

---

## Template Logic (`src/generator/templates/top_model.mo.j2`)

### Branch order (five-way)
```
{% if is_1d_conti %}
    → Same electrodes as 0D simple (Electrode_Planar, P=100000, Pi)
    → Same Anolyte + Catholyte (Electrolyte_Conti_0D_L)
    → Same Diaphragm, same inflow/outflow components
    → ADDITION: Electrolyte_Batch_1D_L_nLayers × 2 (Diff_Anolyte, Diff_Catholyte)
    → ADDITION: ConnectionLayer_Diffusive × 2
    → 1D connect topology (diffusion layers inserted between electrodes and bulk)
{% elif is_ammonia %}
    → Electrode_Planar anode (no P, no Pi)
    → Electrode_GasDiffusion cathode (splitFactor=0, two reactions)
    → Anolyte + Catholyte (Electrolyte_Conti_0D_L, GeoRecElec)
    → Diaphragm_Hydroxide (GeoRecMem, explicit X and kappa)
    → GasChannel compartment
    → Material_L_InFlow_ResTime × 2 + Material_G_InFlow_ResTime × 1
    → Material_Simple_OutFlow × 3
    → ammonia connect topology
{% elif is_batch %}
    → single Electrolyte (Electrolyte_Batch_0D_L)
    → no Separator, no flow components
    → 4 connect statements only
{% elif use_koh_conductivity %}
    → Anolyte + Catholyte with redeclare ConductivityModel
{% else %}
    → Anolyte + Catholyte with kappa_const
{% endif %}
```

### Electrode block — AWE families only
Both electrodes include:
- `Pi(each displayUnit="bar")`
- `redeclare model ActivationOverpotentialModel`
- `redeclare model TemperatureModel`
- `CathodeEl = false/true`
- `P = 100000`

Ammonia electrodes do NOT include `P` or `Pi`.

### Connect topology — continuous 1D
```
// Electrical (extends 0D simple chain with diffusion layers)
Ground.p → Source.p
Anode.p  → Source.n
Source.p → Diff_Catholyte.n

// Ionic chain: Anode → Diff_Anolyte → Anolyte → Diaphragm → Catholyte → Diff_Catholyte → Cathode
Anode.n → Diff_Anolyte.p → Anolyte.p → Diaphragm.p → Catholyte.p → Diff_Catholyte.p → Cathode.p

// Anode material
Anode.flowFromElectrolyte → Diff_Anolyte.leftFlow
Diff_Anolyte.rightFlow    → ConnLayer_Anode.leftFlow
ConnLayer_Anode.rightFlow → Anolyte.leftFlow
AnodeInflow → Anolyte.inFlow
Anolyte.outFlow → Flow_anode → env_anode
Anolyte.rightFlow → Diaphragm.anCon

// Catholyte material
Diaphragm.catCon  → Catholyte.leftFlow
CathodeInflow → Catholyte.inFlow
Catholyte.outFlow → Flow_Cathode → env_cathode
Catholyte.rightFlow    → ConnLayer_Cathode.leftFlow
ConnLayer_Cathode.rightFlow → Diff_Catholyte.leftFlow
Diff_Catholyte.rightFlow   → Cathode.flowFromElectrolyte
```

### Connect topology — ammonia
```
// Electrical
Ground.p → Source.p
Anode.p  → Source.n
GasDiffusionCathode.n → Source.p   // note: GDE.n, not GDE.p

// Liquid chain
Anode.n → Anolyte.p → Diaphragm.p → Catholyte.p → GasDiffusionCathode.p

// Separator exchange
Anolyte.rightFlow → Diaphragm.anCon
Diaphragm.catCon  → Catholyte.leftFlow

// GDE
Catholyte.rightFlow → GasDiffusionCathode.flowFromElectrolyte
GasDiffusionCathode.flowFromGas → GasChannel.flowFromElectrode

// Anode material
Anode.flowFromElectrolyte → Anolyte.leftFlow

// Inflows / outflows
InflowAnolyte → Anolyte.inFlow
InflowCatholyte → Catholyte.inFlow
InflowGasChannel → GasChannel.flowIn
Anolyte.outFlow → OutflowAnolyte
Catholyte.outFlow → OutflowCatholyte
GasChannel.flowOut → OutflowGasChannel
```

---

## DSL Syntax

File extension: `.reactor`

### AWE families (continuous/batch, simple/KOH)
```
reactor AWE_Conti_Simple {
  setup: continuous_0D_alkaline    // or: batch_0D_alkaline
  electrolyte_mode: simple         // or: KOH
  voltage: -2.5

  species: [O2, H2, Hp, OHm, H2O]

  reactions {
    anode:   OERdummy
    cathode: HERdummy
  }

  geometry {
    X:          0.01
    X_membrane: 0.0005
    Y:          1.0
    Z:          1.0
    cond0:      1.0
    dX:         1e-6
  }

  conditions {
    T0:           300
    Tenvironment: 293.15
    p:            1
  }

  concentrations: [0, 1.45e-12, 1e-4, 6000, 55e3]

  electrolyte {
    kappa_anode:   75
    kappa_cathode: 85
  }

  diaphragm {
    kappa: 38
  }

  simulation {
    stop_time: 50
  }
}
```

### 1D continuous alkaline
```
reactor AWE_Conti_1D_Simple {
  setup:            continuous_1D_alkaline
  electrolyte_mode: simple
  voltage:          -2.3

  species: [O2, H2, Hp, OHm, H2O]

  reactions {
    anode:   OERdummy
    cathode: HERdummy
  }

  geometry {
    X:          0.01
    X_membrane: 5e-6
    Y:          1.0
    Z:          1.0
    cond0:      1.0
    dX:         1e-6
  }

  conditions {
    T0:           300
    Tenvironment: 293.15
    p:            1
    inflow_scale: 0.05    // 1D uses 0.05; 0D default is 0.005
  }

  concentrations: [0, 1.45e-12, 1e-4, 6000, 55e3]

  electrolyte {
    kappa_anode:   75
    kappa_cathode: 85
  }

  diaphragm {
    kappa: 38
  }

  diffusion_layer {
    X_difflayer:   1e-6
    kappa_anode:   85
    kappa_cathode: 74
    n_slices:      10
  }

  simulation {
    stop_time: 5
  }
}
```

Parser notes for 1D:
- `diffusion_layer { ... }` block populates `DiffusionLayerParams`. If absent, `diffusion_layer` is `None` and the 0D topology is used.
- `inflow_scale` is read from the `conditions` block. For 1D use `0.05` (matches gold standard). All 0D families default to `0.005`.

### Ammonia family
```
reactor AAE_Conti_Ammonia {
  setup:   continuous_0D_ammonia
  voltage: -2.0

  species: [O2, H2, N2, NH3, OHm, Kp, H2O]

  reactions {
    anode:        OERdummy
    cathode:      [HERdummy, NRRdummy]   // list form — ammonia only
    cathode_type: gas_diffusion          // required for ammonia
  }

  geometry {
    X:           0.001
    X_membrane:  115e-6
    X_electrode: 0.005    // GeoRecElec.X — ammonia only
    Y:           0.5
    Z:           1.0
    cond0:       1.0
    dX:          0.01
  }

  conditions {
    T0:           333.15
    Tenvironment: 288.15
    p:            100000
  }

  concentrations {             // block form — ammonia only
    electrolyte: [0, 1.45e-12, 0, 0, 6000, 6000, 55e3]
    gas_channel: [0, 0, 1, 0, 0, 0, 0]
  }

  gas_channel {
    mol_vec_frac0: [0, 0, 1, 0, 0, 0, 0]
    slices: 10
    t: 5
  }

  diaphragm {
    kappa: 38
  }

  simulation {
    stop_time: 30
  }
}
```

Parser differences for ammonia vs AWE:
- `cathode:` accepts a bracketed list `[HERdummy, NRRdummy]` — first item → `reaction`, rest → `extra_reactions`
- `concentrations` can be a block with `electrolyte:` and `gas_channel:` sub-keys instead of a flat list
- `cathode_type:` key inside `reactions {}` sets `Electrode.kind`
- `X_electrode:` inside `geometry {}` sets `GeometryParams.X_electrode`
- `gas_channel {}` block populates `GasChannelParams`

---

## reactor_builder.py — Interactive Wizard

Run with: `python reactor_builder.py`

### What it does
1. Asks for DSL filename (validated: alphanumeric + underscores only)
2. Checks for existing file collision — prompts before overwriting
3. Asks for reactor name
4. Shows available setups as a numbered menu
5. Based on setup, asks setup-specific questions with correct defaults shown in brackets
6. Writes the `.reactor` file using string formatting
7. Automatically runs `run.py` and reports generated file paths

### Validation enforced in wizard
- Filename: alphanumeric + underscores only, non-empty
- Voltage: must be negative (reprompts if not)
- Concentration arrays: must match expected species count for the setup (5/6/7 values)
- `n_slices`: must be >= 2

### Setup-specific defaults

| Parameter | continuous_0D simple | continuous_0D KOH | batch_0D simple | batch_0D KOH | ammonia | 1D simple |
|---|---|---|---|---|---|---|
| voltage | -2.5 | -2.5 | -2.5 | -2.5 | -2.0 | -2.3 |
| Y | 1.0 | 0.05 | 1.0 | 0.05 | 0.5 | 1.0 |
| Z | 1.0 | 0.05 | 1.0 | 0.05 | 1.0 | 1.0 |
| X_membrane | 0.0005 | 0.0005 | 0.0005 | 0.0005 | 115e-6 | 5e-6 |
| T0 | 300 | 300 | 300 | 300 | 333.15 | 300 |
| p | 1 | 1 | 1 | 1 | 100000 | 1 |
| stop_time | 50 | 50 | 50 | 50 | 30 | 5 |

### What the wizard abstracts away
- Species are fixed per setup/mode — not asked
- Reactions are fixed per setup — not asked
- `inflow_scale` is set automatically (0.05 for 1D, 0.005 for all others) — not asked

### Semantic verification
All six canonical DSL files were verified to be exact semantic matches to wizard-generated output using `dataclasses.asdict(parse(...))` comparison. Cosmetic formatting differences (e.g. `1e-4` vs `0.0001`) are intentional — the parser produces identical `ReactorModel` objects from both forms.

---

## eCherry Component FQNs

### Import alias (copy exactly — note the misspelling)
```modelica
import Echery_library = eCherry_Library;
```

### AWE component FQNs via alias
```
Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed
Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar
Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L
Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_0D_L
Echery_library.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide
Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed
Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow
Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment
Modelica.Electrical.Analog.Basic.Ground
```

### 1D-only component FQNs via alias
```
Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_1D_L_nLayers
Echery_library.ElectrochemicalReactor.MaterialDomain.ConnectionLayers.ConnectionLayer_Diffusive
```

### Ammonia-only component FQNs via alias
```
Echery_library.ElectrochemicalReactor.Electrodes.Electrode_GasDiffusion
Echery_library.ElectrochemicalReactor.MaterialDomain.Compartments.Gas.GasChannel
Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_L_InFlow_ResTime
Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_G_InFlow_ResTime
Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_OutFlow
```

### Redeclare options
```
Properties.TemperatureModels.TemperatureConstant
eCherry_Library.ElectrochemicalReactor.Properties.ConductivityModels.ConductivityElectrolyteCalcKOH
eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential
```

### DataRecord FQNs (full path, used in UserInput template)
```
eCherry_Library.Data.DataRecords.Species.SpeciesRecord
eCherry_Library.Data.DataRecords.Species.GaseousSpecies.O2
eCherry_Library.Data.DataRecords.Species.GaseousSpecies.H2
eCherry_Library.Data.DataRecords.Species.GaseousSpecies.N2        // ammonia
eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.Hp
eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.OHm
eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.Kp
eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.NH3     // ammonia
eCherry_Library.Data.DataRecords.Species.LiquidSpecies.H2O
eCherry_Library.Data.DataRecords.Geometry
eCherry_Library.Data.DataRecords.Conditions
eCherry_Library.Data.DataRecords.ElecReaction.Reaction
eCherry_Library.Data.DataRecords.ElecReaction.List_Of_Reactions.HERdummy
eCherry_Library.Data.DataRecords.ElecReaction.List_Of_Reactions.OERdummy
eCherry_Library.Data.DataRecords.ElecReaction.List_Of_Reactions.NRRdummy  // ammonia
```

---

## Known Species (DSL → eCherry)

| DSL name | eCherry FQN | Notes |
|---|---|---|
| `O2` | `GaseousSpecies.O2` | all families |
| `H2` | `GaseousSpecies.H2` | all families |
| `N2` | `GaseousSpecies.N2` | ammonia only |
| `Hp` | `DissolvedSpecies.Hp` | AWE families |
| `OHm` | `DissolvedSpecies.OHm` | all families |
| `Kp` | `DissolvedSpecies.Kp` | KOH and ammonia |
| `NH3` | `DissolvedSpecies.NH3` | ammonia only |
| `H2O` | `LiquidSpecies.H2O` | all families |

Standard AWE species: `[O2, H2, Hp, OHm, H2O]`
KOH AWE species: `[O2, H2, Hp, OHm, Kp, H2O]`
Ammonia species: `[O2, H2, N2, NH3, OHm, Kp, H2O]`

---

## Known Reactions (DSL → eCherry)

| DSL name | eCherry name | Side |
|---|---|---|
| `HER` or `HERdummy` | `List_Of_Reactions.HERdummy` | cathode |
| `OER` or `OERdummy` | `List_Of_Reactions.OERdummy` | anode |
| `NRR` or `NRRdummy` | `List_Of_Reactions.NRRdummy` | cathode (ammonia, extra) |

---

## Setup × Mode Matrix

| Setup value | within_model | fqn_electrolyte | has_separator | has_flows | cathode_type |
|---|---|---|---|---|---|
| `continuous_0D_alkaline` | `Examples.Continuous` | `Electrolyte_Conti_0D_L` | yes | yes (simple) | planar |
| `batch_0D_alkaline` | `Examples.Batch.Batch0D` | `Electrolyte_Batch_0D_L` | no | no | planar |
| `continuous_0D_ammonia` | `Examples.AlkalineAmmoniaElectrolyzer` | `Electrolyte_Conti_0D_L` | yes | yes (ResTime) | gas_diffusion |
| `continuous_1D_alkaline` | `Examples.Continuous` | `Electrolyte_Conti_0D_L` (bulk) + `Electrolyte_Batch_1D_L_nLayers` (diff layers) | yes | yes (simple) | planar |

KOH mode adds `redeclare ConductivityModel` to electrolytes for AWE 0D families.
Batch mode adds explicit `X`, `Y`, `Z` to the single `Electrolyte` component.
Ammonia uses three geometry records (GeoRec, GeoRecMem, GeoRecElec) and two concentration arrays.
1D adds two diffusion layer components and two connection layers; bulk electrolytes remain `Electrolyte_Conti_0D_L`.

---

## Adding a New Reactor Family — Checklist

When adding a new family (follow this order every time):

1. **Read the gold standard** `.mo` files from the eCherry repo first
2. **metamodel.py** — add optional fields only; do not break existing dataclass defaults
3. **validator.py** — add new `setup` to `_VALID_SETUPS`, new species to `_KNOWN_SPECIES`, new reactions to `_KNOWN_REACTIONS`; add family-specific check block if needed
4. **transformer.py** — add new branch for `within_model`, `fqn_electrolyte`, family flags, and new context keys; add new species/reaction FQNs
5. **top_model.mo.j2** — add `{% if %}` branch for new topology
6. **user_input.mo.j2** — add `{% if %}` branch for new UserInput structure
7. **dsl/** — add `example_<family>.reactor` with descriptive `reactor <n> {`
8. **results/manual/** — copy gold standard `.mo` files from eCherry repo
9. **tests/test_pipeline.py** — add `FAMILY_DSL` constant at top; add `class Test<Family>:` at bottom
10. **reactor_builder.py** — add setup to menu, add defaults branch in geometry/conditions/concentrations, add any new DSL blocks to the writing section
11. **CLAUDE.md** — update status matrix, directory layout, DSL table, metrics

---

## Test Structure (`tests/test_pipeline.py`)

Tests organized into classes by family — **84 tests total**:

- `TestValidator` — 9 tests (rejection + acceptance, including 1D checks)
- `TestContiSimple` — 12 tests
- `TestContiKOH` — 7 tests
- `TestBatchSimple` — 8 tests
- `TestBatchKOH` — 6 tests
- `TestAmmoniaConti` — 22 tests (parser × 9, transformer × 7, generator × 6 + diaphragm/slices checks)
- `TestConti1D` — 20 tests (parser × 3, transformer × 4, generator × 13)

DSL file constants at the top of the test file:
```python
CONTI_SIMPLE_DSL = "dsl/example_conti_simple.reactor"
CONTI_KOH_DSL    = "dsl/example_conti_koh.reactor"
BATCH_SIMPLE_DSL = "dsl/example_batch_simple.reactor"
BATCH_KOH_DSL    = "dsl/example_batch_koh.reactor"
AMMONIA_DSL      = "dsl/example_conti_ammonia.reactor"
CONTI_1D_DSL     = "dsl/example_conti_1d_simple.reactor"
```

---

## Evaluation Metrics (calculated)

| | DSL lines | Generated Model.mo lines | Generated UserInput.mo lines | Manual lines | Reduction |
|---|---|---|---|---|---|
| Continuous AWE simple | 41 | 95 | 22 | 213 | 73% |
| Continuous AWE KOH | 41 | 95 | 20 | 180 | 70% |
| Batch AWE simple | 41 | 45 | 22 | ~100 | ~60% |
| Batch AWE KOH | 41 | 45 | 20 | n/a | ~60% |
| Continuous ammonia | 48 | 100 | 32 | ~180 | ~70% |
| Continuous 1D simple | 50 | 110 | 23 | ~175 | ~71% |

Note: "Reduction" measures (manual lines − DSL lines) / manual lines. The more meaningful claim is that a user writes ~41–50 lines of DSL and the generator produces ~117–143 lines of correct eCherry Modelica automatically.

Key findings:
- Changing one line (`electrolyte_mode: simple` → `electrolyte_mode: KOH`) switches the entire generated output automatically
- Changing one field (`setup: continuous_0D_alkaline` → `setup: batch_0D_alkaline`) switches topology automatically
- Ammonia and 1D are structurally distinct families expressible in ~48–50 DSL lines
- The `reactor_builder.py` wizard further reduces user effort to zero manual DSL authoring — users answer prompted questions and generation happens automatically

---

## Gold Standard Reference Files (`results/manual/`)

| File | Family |
|---|---|
| `Electrolyzer_Conti_0D_L.mo` | Continuous 0D simple model |
| `Example_AlkalineWaterElectrolysis.mo` | Continuous 0D simple + 1D UserInput |
| `Electrolyzer_Conti_0D_L_KOH.mo` | Continuous 0D KOH model |
| `Example_AlkalineWaterElectrolysis_KOH.mo` | Continuous 0D KOH UserInput |
| `Electrolyzer_Conti_1D_L.mo` | Continuous 1D model |
| `AlkalineAmmoniaElectrolyzer.mo` | Ammonia (AAE_0D model) |
| `Example_AlkalineAmmoniaElectrolyzer.mo` | Ammonia UserInput |

Note: No explicit KOH batch gold standard exists in eCherry — batch KOH is a novel combination this tool supports. `Example_AlkalineWaterElectrolysis.mo` is shared by both 0D simple and 1D families (1D adds only `X_difflayer` to our generated UserInput).

---

## Scope

### Implemented ✅
- Continuous 0D alkaline simple
- Continuous 0D alkaline KOH
- Batch 0D alkaline simple
- Batch 0D alkaline KOH
- Continuous 0D ammonia (GDE cathode, gas channel, ResTime inflows)
- Continuous 1D alkaline simple (diffusion boundary layers, ConnectionLayer_Diffusive)
- External textual DSL with hand-written parser
- Metamodel with first-class domain entities
- Semantic validation with clear error messages (9 checks)
- Jinja2 template-based code generation
- CLI (`run.py`) with subfolder output structure
- Interactive wizard (`reactor_builder.py`) with validation and auto-generation
- 84-test pytest suite organized by family

### Out of scope
- Thermal domain
- Gas-liquid variants
- Cyclic voltammetry / CV mode
- PhotoVoltaics coupling
- Automated Dymola simulation execution
- Round-trip parsing of generated `.mo` files
- Batch ammonia
- KOH 1D

---

## Running the Pipeline

```bash
source .venv/bin/activate

# interactive wizard (recommended for new reactors)
python reactor_builder.py

# generate a specific family directly
python run.py dsl/example_conti_simple.reactor
python run.py dsl/example_conti_koh.reactor
python run.py dsl/example_batch_simple.reactor
python run.py dsl/example_batch_koh.reactor
python run.py dsl/example_conti_ammonia.reactor
python run.py dsl/example_conti_1d_simple.reactor

# run all tests
python -m pytest tests/ -v
```

---

## Academic Framing

- **DSL**: External textual DSL; hand-written line-by-line parser; two syntax forms (flat concentrations vs block concentrations for ammonia)
- **Metamodel**: Python dataclasses = M1 level; grammar + validator = implicit M2; nine validation checks enforce structural and semantic constraints
- **Transformation**: Model-to-model; `ReactorModel` → `GeneratorContext` dict with resolved FQNs; family flags drive branching
- **Code generation**: Model-to-text; Jinja2 templates with five-way branching targeting eCherry Modelica component API
- **Abstraction claim**: User writes ~41–50 lines of DSL; generator produces ~117–143 lines of correct eCherry Modelica automatically
- **Wizard**: Further abstraction layer — user answers CLI prompts, no DSL authoring required; `reactor_builder.py` writes the DSL and triggers generation
- **Compositionality**: `setup` × `electrolyte_mode` flags are orthogonal — new modes don't require rewriting existing branches
- **Extensibility**: Each new family is a pure additive branch — zero changes to existing code paths

---

## Known Limitations

1. **`X_difflayer` hardcoded in 1D model** — the generated `Model.mo` emits `X_difflayer = 1e-06` as a literal value rather than referencing `UI.X_difflayer`. The UserInput record carries the value but the model doesn't reference it. Both values come from the same DSL source so they are always consistent, but it breaks the clean UserInput-reference pattern used elsewhere.

2. **Float formatting** — `fmt()` uses `:.6g` which produces `0.0001` instead of `1e-4` and `55000` instead of `55e3`. The generated `.reactor` files are semantically identical to hand-written ones (parser produces the same `ReactorModel`) but differ in notation. Scientific notation is preserved where Python's `:.6g` naturally produces it (e.g. `1.45e-12`).

3. **`n_slices` explicitly emitted** — the gold standard `Electrolyzer_Conti_1D_L.mo` does not pass `n_slices` explicitly to `Electrolyte_Batch_1D_L_nLayers` (relies on the default of 10). Our generator always emits it explicitly. This is intentional — it makes the DSL-to-model mapping traceable — but it is a deviation from the gold standard style.

4. **Batch ammonia not supported** — batch topology and ammonia chemistry have not been combined. No gold standard exists for this combination in eCherry.

---

## Design Decisions

1. **Batch KOH uses `Y=0.05, Z=0.05`** — consistent with `Example_AlkalineWaterElectrolysis_KOH` UserInput record. Cell geometry is a property of the KOH chemistry choice, not the batch/continuous topology. All KOH variants use this geometry regardless of setup.

2. **1D `inflow_scale = 0.05`** — the gold standard `Electrolyzer_Conti_1D_L.mo` uses `molFlow_vec = c0 * 0.05`. This is specified in the DSL `conditions` block as `inflow_scale: 0.05`. All 0D families use the default `0.005`.

3. **Species and reactions are fixed per family** — the wizard does not ask users to specify species or reactions. These are determined entirely by setup and electrolyte mode. This is correct — the user cannot meaningfully change chemistry without also changing the eCherry component topology.

4. **`reactor_builder.py` does not import from `src/`** — the wizard uses only string formatting and `subprocess`. All validation is handled by the existing pipeline when `run.py` is called. This keeps the wizard simple and avoids coupling it to the internal module structure.

---

## Common Mistakes to Avoid

1. Import alias is `Echery_library` not `eCherry_Library` — misspelling matches eCherry source exactly
2. `c0` array length must match species count — validator catches this
3. `within` clauses must match package hierarchy exactly
4. Voltage must be negative — validator enforces this
5. Batch mode uses single `Electrolyte` not `Anolyte`/`Catholyte`
6. Batch mode has no `Diaphragm` and no flow components
7. `env_anode`/`env_cathode` only take `specRec` — no `CondRec`
8. `Electrolyte_Batch_0D_L` uses `c0` parameter not `mol_vec0`
9. `Pi` array in UserInput uses `Modelica.Units.SI.Pressure` type (AWE only)
10. `molFlow_vec` in UserInput uses `Modelica.Units.SI.MolarFlowRate` type (AWE only)
11. AWE electrodes always get `Pi(each displayUnit="bar")` and `P = 100000` — ammonia electrodes do not
12. Batch electrolyte gets explicit `X`, `Y`, `Z` parameters — continuous electrolytes do not
13. Output goes to `results/generated/<dsl_stem>/Model.mo` and `UserInput.mo` — subfolder named after DSL file, files always named `Model.mo` and `UserInput.mo`
14. Reactor `name` field inside DSL drives Modelica record names, DSL filename drives output subfolder — these are independent
15. Ammonia uses three geometry records — `GeoRec` (bulk/gas), `GeoRecMem` (membrane), `GeoRecElec` (electrode/electrolyte)
16. Ammonia Diaphragm requires explicit `X` and `kappa` parameters in the model template
17. Ammonia UserInput has no `Pi` and no `molFlow_vec` — those are AWE-only
18. `slices` must be declared before the geometry records that use `Z = 1/slices` in ammonia UserInput
19. Ammonia spec record is named `AESspec` not `AWEspec`
20. `use_koh_conductivity` guard includes `not is_ammonia` and `not is_1d_conti` — prevents KOH conductivity redeclare in families where it doesn't apply
21. 1D model: diffusion layers (`Electrolyte_Batch_1D_L_nLayers`) go between electrodes and bulk electrolyte — NOT between bulk and diaphragm
22. 1D model: `ConnectionLayer_Diffusive` has `dX=1e-7` (hardcoded from gold standard) — not the same as `GeoRec.dX`
23. 1D model: bulk `Anolyte`/`Catholyte` are still `Electrolyte_Conti_0D_L` — only the boundary layers are 1D
24. 1D UserInput: `X_difflayer` constant uses type `Modelica.Units.SI.Length`
25. 1D electrical chain: `Source.p` connects to `Diff_Catholyte.n` — the cathode diffusion layer is in the electrical chain, not `Catholyte.n` directly
26. KOH geometry: both continuous and batch KOH use `Y=0.05, Z=0.05` — this is a chemistry property, not a topology property
27. `inflow_scale` is DSL-readable from the `conditions` block — 1D must set it explicitly to `0.05`