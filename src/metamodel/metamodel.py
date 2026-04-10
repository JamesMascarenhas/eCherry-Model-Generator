from dataclasses import dataclass


@dataclass
class GeometryParams:
    X: float = 0.01
    X_membrane: float = 0.0005
    Y: float = 1.0
    Z: float = 1.0
    cond0: float = 1.0
    dX: float = 1e-6


@dataclass
class OperatingConditions:
    T0: float = 300.0
    Tenvironment: float = 293.15
    p: float = 1.0
    voltage: float = -2.5
    inflow_scale: float = 0.005


@dataclass
class Electrode:
    reaction: str
    kappa: float
    kind: str = "planar"


@dataclass
class Separator:
    kind: str = "hydroxide_diaphragm"
    kappa: float = 38.0


@dataclass
class Electrolyte:
    species: list[str]
    c0: list[float]
    mode: str = "simple"


@dataclass
class FlowChannel:
    mode: str = "simple_fixed"


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
