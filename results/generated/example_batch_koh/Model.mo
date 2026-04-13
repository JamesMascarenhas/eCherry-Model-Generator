within eCherry_Library.Examples.Batch.Batch0D;
model MyAWE_Batch
  import Echery_library = eCherry_Library;
  extends Modelica.Icons.Example;

  parameter Real Ufixed = -2.5;

  // Electrical ground and voltage source
  Modelica.Electrical.Analog.Basic.Ground Ground;

  Echery_library.ElectrochemicalReactor.ElectricalDomain.Source.Potential_Source.Voltage_Fixed Source(
    Ufixed = Ufixed,
    GeoRec = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.GeoRec,
    Y = 1,
    Z = 1);

  // Electrodes
  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Anode(
    specRec   = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.MyAWE_Batch_UserInput.OERdummy},
    CathodeEl = false,
    P         = 100000,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  Echery_library.ElectrochemicalReactor.Electrodes.Electrode_Planar Cathode(
    specRec   = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.AWEspec,
    GeoRec    = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.GeoRec,
    CondRec   = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.CondRec,
    reac      = {Echery_library.Data.UserInput.MyAWE_Batch_UserInput.HERdummy},
    CathodeEl = true,
    P         = 100000,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

  // Electrolyte compartment(s)
  Echery_library.ElectrochemicalReactor.Electrolytes.Liquid.Electrolyte_Batch_0D_L Electrolyte(
    specRec = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.AWEspec,
    GeoRec  = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.GeoRec,
    CondRec = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.CondRec,
    c0      = Echery_library.Data.UserInput.MyAWE_Batch_UserInput.c0,
    redeclare model ConductivityModel = eCherry_Library.ElectrochemicalReactor.Properties.ConductivityModels.ConductivityElectrolyteCalcKOH,
    redeclare model TemperatureModel = Properties.TemperatureModels.TemperatureConstant);

equation
  // Electrical
  connect(Ground.p,  Source.p);
  connect(Anode.p,   Source.n);
  connect(Source.p,  Cathode.n);

  // Single shared electrolyte — electrode coupling
  connect(Anode.n,                    Electrolyte.p);
  connect(Electrolyte.n,              Cathode.p);
  connect(Cathode.flowFromElectrolyte, Electrolyte.rightFlow);
  connect(Electrolyte.leftFlow,        Anode.flowFromElectrolyte);


  annotation(experiment(StopTime = 50));

end MyAWE_Batch;