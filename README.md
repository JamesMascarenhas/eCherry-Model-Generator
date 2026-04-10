# eCherry Reactor Model Generator

A model-driven prototype that lets users describe an electrochemical reactor in a small external textual DSL and automatically generates eCherry-compatible Modelica simulation models.

Built for CISC 844 — Model-Driven Software Development, Queen's University.

---

## Overview

Electrochemical reactor simulations built with [eCherry](https://git.rwth-aachen.de/avt-svt/public/echerry) require manually assembling low-level Modelica components, configuring simulation parameters, and understanding the internal structure of the library. This is time-consuming and error-prone, especially for domain experts in electrochemistry who are not Modelica specialists.

This project addresses that problem by introducing a model-driven workflow:

```
.reactor (DSL file)
    → parser
    → internal metamodel
    → transformer
    → generator
    → eCherry-compatible .mo files
```

Users describe their reactor in a concise domain-specific language. The tool handles all the Modelica boilerplate — component instantiation, parameter wiring, and connection topology.

---

## Model-Driven Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Metamodeling | Python dataclasses representing the reactor domain |
| DSL design | Hand-written external textual DSL (`.reactor` files) |
| Model transformation | `ReactorModel` → `GeneratorContext` with eCherry-specific mappings |
| Artifact generation | Jinja2 templates targeting eCherry Modelica components |

---

## Target Scope (v1)

The prototype targets a single well-understood example family: the **continuous 0D alkaline water electrolyzer** (`Electrolyzer_Conti_0D_L`). This is the simplest non-trivial eCherry configuration and provides a clear gold standard for evaluating the generated output.

Two electrolyte modes are supported:

- `simple` — constant conductivity, 5-species system (O₂, H₂, H⁺, OH⁻, H₂O)
- `KOH` — concentration-dependent conductivity, 6-species system (adds K⁺)

---

## DSL Example

```text
reactor MyAWE {
  electrolyte_mode: simple
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

---

## Project Structure

```
.
├── CLAUDE.md                   # Context file for Claude Code (git-ignored)
├── README.md
├── requirements.txt
├── run.py                      # CLI entry point
├── dsl/
│   └── example_awe.reactor     # Example DSL input
├── src/
│   ├── parser/                 # DSL parser → ReactorModel
│   ├── metamodel/              # Python dataclasses (domain representation)
│   ├── transform/              # ReactorModel → GeneratorContext
│   ├── generator/              # GeneratorContext → .mo files (Jinja2 templates)
│   └── validator.py            # Structural and semantic validation
├── results/
│   ├── generated/              # .mo files produced by the generator
│   └── manual/                 # Reference .mo files from eCherry (for comparison)
└── tests/
    └── test_pipeline.py
```

---

## Getting Started

### Requirements

- Python 3.10+
- [Jinja2](https://jinja.palletsprojects.com/)

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Generator

```bash
python run.py dsl/example_awe.reactor
```

This produces two files in `results/generated/`:

- `MyAWE_UserInput.mo` — the eCherry `UserInput` data record (species, reactions, geometry, conditions, concentrations)
- `MyAWE_Model.mo` — the assembled top-level Modelica model with all component instantiations and connections

### Evaluating the Output

Reference models from eCherry are stored in `results/manual/`. Compare the generated output against these to verify correctness:

```bash
diff results/generated/MyAWE_Model.mo results/manual/Electrolyzer_Conti_0D_L.mo
```

Generated models can be simulated in [Dymola](https://www.3ds.com/products-services/catia/products/dymola/) or [OpenModelica](https://openmodelica.org/).

---

## Domain Model

The metamodel captures the following core domain entities, each mapping to one or more eCherry constructs:

| Domain Entity | eCherry Mapping |
|---|---|
| `Reactor` | Top-level assembled `model` |
| `Electrode` | `Electrode_Planar` (anode + cathode) |
| `Electrolyte` | `Electrolyte_Conti_0D_L` (anolyte + catholyte) |
| `Separator` | `Diaphragm_Hydroxide` |
| `FlowChannel` | `Material_Simple_InFlow_Fixed`, `Material_Simple_ConnectingFlow`, `Environment` |
| `OperatingConditions` | `DataRecords.Conditions`, `DataRecords.Geometry` |

---

## Evaluation

The project is evaluated by comparing manually-constructed eCherry models against DSL-generated ones across three dimensions:

- **Correctness** — do the generated models simulate identically to the reference?
- **Effort** — how many lines does the DSL description require vs. the raw Modelica?
- **Iteration speed** — how quickly can a user modify and regenerate a configuration?

---

## References

- Pyschik et al. (2025). *eCherry: A Modelica Library for Modular Dynamic Modelling of Electrochemical Reactors.* Electrochemical Science Advances. [doi:10.1002/elsa.202400030](https://doi.org/10.1002/elsa.202400030)
- Fowler, M. (2010). *Domain-Specific Languages.* Addison-Wesley.
- Kelly, S. & Tolvanen, J.-P. (2008). *Domain-Specific Modeling: Enabling Full Code Generation.* Wiley.