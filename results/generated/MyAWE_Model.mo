within eCherry_Library.Examples.Continuous;

model MyAWE
  import Echery_library = eCherry_Library;

  parameter Real Ufixed = -2.5;

  // UserInput record — holds all species, geometry, conditions, concentrations
  eCherry_Library.Data.UserInput.Example_AlkalineWaterElectrolysis UI;

  // Electrical ground and voltage source
  Modelica.Electrical.Analog.Basic.Ground Ground;

  Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed Source(
    Ufixed = Ufixed);

  // Electrodes
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Anode(
    SpecRec = UI.SpecRec,
    GeoRec  = UI.GeoRec,
    CondRec = UI.CondRec,
    ReacRec = UI.AnodeReac);

  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Cathode(
    SpecRec = UI.SpecRec,
    GeoRec  = UI.GeoRec,
    CondRec = UI.CondRec,
    ReacRec = UI.CathodeReac);

  // Electrolyte compartments
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Anolyte(
    SpecRec     = UI.SpecRec,
    GeoRec      = UI.GeoRec,
    CondRec     = UI.CondRec,
    c0          = UI.c0,
    kappa_const = 75);

  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Conti_0D_L Catholyte(
    SpecRec     = UI.SpecRec,
    GeoRec      = UI.GeoRec,
    CondRec     = UI.CondRec,
    c0          = UI.c0,
    kappa_const = 85);

  // Separator
  Echery_library.ElectrochemicalReactor.Separators.Diaphragm_Hydroxide Diaphragm(
    SpecRec = UI.SpecRec,
    GeoRec  = UI.GeoRec,
    kappa   = 38,
    X       = 0.0005);

  // Anode-side material flows
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed AnodeInflow(
    SpecRec     = UI.SpecRec,
    c0          = UI.c0,
    molFlow_vec = UI.molFlow_vec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow Flow_anode(
    SpecRec = UI.SpecRec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment env_anode(
    SpecRec = UI.SpecRec,
    CondRec = UI.CondRec);

  // Cathode-side material flows
  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_InFlow_Fixed CathodeInflow(
    SpecRec     = UI.SpecRec,
    c0          = UI.c0,
    molFlow_vec = UI.molFlow_vec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Material_Simple_ConnectingFlow Flow_Cathode(
    SpecRec = UI.SpecRec);

  Echery_library.ElectrochemicalReactor.MaterialDomain.Flows.Environment env_cathode(
    SpecRec = UI.SpecRec,
    CondRec = UI.CondRec);

equation
  // Electrical
  connect(Ground.p,  Source.p);
  connect(Anode.p,   Source.n);
  connect(Source.p,  Cathode.n);

  // Anode side — material flow
  connect(AnodeInflow.convFlow,    Anolyte.inFlow);
  connect(Anolyte.outFlow,         Flow_anode.convinFlow);
  connect(Flow_anode.convoutFlow,  env_anode.convFlow);
  // Anode side — electrode coupling and separator
  connect(Anolyte.leftFlow,  Anode.flowFromElectrolyte);
  connect(Anode.n,           Anolyte.p);
  connect(Anolyte.rightFlow, Diaphragm.anCon);
  connect(Anolyte.n,         Diaphragm.p);

  // Cathode side — material flow
  connect(CathodeInflow.convFlow,     Catholyte.inFlow);
  connect(Catholyte.outFlow,          Flow_Cathode.convinFlow);
  connect(Flow_Cathode.convoutFlow,   env_cathode.convFlow);
  // Cathode side — electrode coupling and separator
  connect(Catholyte.rightFlow, Cathode.flowFromElectrolyte);
  connect(Cathode.n,    Catholyte.p);
  connect(Catholyte.leftFlow, Diaphragm.catCon);
  connect(Catholyte.n,  Diaphragm.n);

  annotation(experiment(StopTime = 50));

end MyAWE;
