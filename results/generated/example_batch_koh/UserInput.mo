within eCherry_Library.Data.UserInput;

record AWE_Batch_KOH_UserInput
  import DataRecords = eCherry_Library.Data.DataRecords;

  constant eCherry_Library.Data.DataRecords.Species.SpeciesRecord AWEspec(
    species = {
      eCherry_Library.Data.DataRecords.Species.GaseousSpecies.O2,
      eCherry_Library.Data.DataRecords.Species.GaseousSpecies.H2,
      eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.Hp,
      eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.OHm,
      eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.Kp,
      eCherry_Library.Data.DataRecords.Species.LiquidSpecies.H2O
    });

  constant DataRecords.ElecReaction.Reaction OERdummy = DataRecords.ElecReaction.List_Of_Reactions.OERdummy;
  constant DataRecords.ElecReaction.Reaction HERdummy = DataRecords.ElecReaction.List_Of_Reactions.HERdummy;

  constant DataRecords.Geometry GeoRec = DataRecords.Geometry(
    X           = 0.01,
    X_membrane  = 0.0005,
    Y           = 1,
    Z           = 1,
    cond0       = 1,
    dX          = 1e-06);

  constant DataRecords.Conditions CondRec = DataRecords.Conditions(
    T0           = 300,
    Tenvironment = 293.15,
    p            = 1);

  constant Modelica.Units.SI.Concentration c0[AWEspec.nSpec]          = {0, 1.45e-12, 0.0001, 6000, 6000, 55000};
  constant Modelica.Units.SI.Pressure       Pi[AWEspec.nSpec]           = {100000, 100000, 100000, 100000, 100000, 100000};
  constant Modelica.Units.SI.MolarFlowRate molFlow_vec[AWEspec.nSpec]  = {0, 1.45e-12, 0.0001, 6000, 6000, 55000};

end AWE_Batch_KOH_UserInput;
