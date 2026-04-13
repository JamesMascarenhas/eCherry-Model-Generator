within eCherry_Library.Examples.AlkalineAmmoniaElectrolyzer;
model AAE_Conti_Ammonia
  import Echery_library = eCherry_Library;
  extends Modelica.Icons.Example;

  parameter Real Ufixed = -2;

  // ── Electrical ──────────────────────────────────────────────────────────────
  Modelica.Electrical.Analog.Basic.Ground Ground;
  Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed Source(
    Ufixed = Ufixed,
    GeoRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRec);

  // ── Anode (planar) ──────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Anode(
    specRec   = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec    = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.OERdummy},
    CathodeEl = false,
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Cathode (gas diffusion electrode) ───────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_GasDiffusion GasDiffusionCathode(
    specRec     = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec      = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRecElec,
    CondRec     = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    reac        = {Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.HERdummy, Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.NRRdummy},
    CathodeEl   = true,
    splitFactor = 0,
    redeclare model ActivationOverpotentialModel = eCherry_Library.ElectrochemicalReactor.Electrodes.Electrochemistry.Activation_Overpotential.ActivationOverpotential,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Electrolyte compartments ─────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Anolyte(
    specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec  = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRecElec,
    CondRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.c0_Electrolyte,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Catholyte(
    specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec  = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRecElec,
    CondRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.c0_Electrolyte,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Separator ────────────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide Diaphragm(
    specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec  = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRecMem,
    CondRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    X       = 0.000115,
    kappa   = 38,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // ── Gas channel compartment ──────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.MaterialDomain.Compartments.Gas.GasChannel GasChannel(
    specRec       = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec        = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRec,
    CondRec       = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    mol_vec_frac0 = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.mol_vec_frac0);

  // ── Liquid inflows ───────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_L_InFlow_ResTime InflowAnolyte(
    specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec  = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRecElec,
    CondRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.c0_Electrolyte,
    t       = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.t);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_L_InFlow_ResTime InflowCatholyte(
    specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec  = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRecElec,
    CondRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.c0_Electrolyte,
    t       = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.t);

  // ── Gas inflow ───────────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_G_InFlow_ResTime InflowGasChannel(
    specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec,
    GeoRec  = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.GeoRec,
    CondRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.c0_GasChannel,
    t       = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.t);

  // ── Outflows ─────────────────────────────────────────────────────────────────
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_OutFlow OutflowAnolyte(specRec   = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec);
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_OutFlow OutflowCatholyte(specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec);
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_OutFlow OutflowGasChannel(specRec = Echery_library.Data.UserInput.AAE_Conti_Ammonia_UserInput.AESspec);

equation
  // Electrical
  connect(Ground.p,              Source.p);
  connect(Anode.p,               Source.n);
  connect(GasDiffusionCathode.n, Source.p);

  // Liquid flow chain: Anode → Anolyte → Diaphragm → Catholyte → GDE
  connect(Anode.n,     Anolyte.p);
  connect(Anolyte.n,   Diaphragm.p);
  connect(Diaphragm.n, Catholyte.p);
  connect(Catholyte.n, GasDiffusionCathode.p);

  // Separator material exchange
  connect(Anolyte.rightFlow,  Diaphragm.anCon);
  connect(Diaphragm.catCon,   Catholyte.leftFlow);

  // GDE connections
  connect(Catholyte.rightFlow,              GasDiffusionCathode.flowFromElectrolyte);
  connect(GasDiffusionCathode.flowFromGas,  GasChannel.flowFromElectrode);

  // Anode material flow
  connect(Anode.flowFromElectrolyte, Anolyte.leftFlow);

  // Inflows
  connect(InflowAnolyte.convFlow,    Anolyte.inFlow);
  connect(InflowCatholyte.convFlow,  Catholyte.inFlow);
  connect(InflowGasChannel.convFlow, GasChannel.flowIn);

  // Outflows
  connect(Anolyte.outFlow,    OutflowAnolyte.convFlow);
  connect(Catholyte.outFlow,  OutflowCatholyte.convFlow);
  connect(GasChannel.flowOut, OutflowGasChannel.convFlow);

  annotation(experiment(StopTime = 30));

end AAE_Conti_Ammonia;
