within eCherry_Library.Data.UserInput;

record Example_AlkalineWaterElectrolysis

  parameter Integer nS = 5 "Number of species";

  parameter eCherry_Library.Data.DataRecords.Species.SpeciesRecord SpecRec[nS] = {
    eCherry_Library.Data.DataRecords.Species.GaseousSpecies.O2(),
    eCherry_Library.Data.DataRecords.Species.GaseousSpecies.H2(),
    eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.Hp(),
    eCherry_Library.Data.DataRecords.Species.DissolvedSpecies.OHm(),
    eCherry_Library.Data.DataRecords.Species.LiquidSpecies.H2O()
  };

  parameter eCherry_Library.Data.DataRecords.ElecReaction.Reaction AnodeReac =
    eCherry_Library.Data.DataRecords.ElecReaction.List_Of_Reactions.OERdummy();

  parameter eCherry_Library.Data.DataRecords.ElecReaction.Reaction CathodeReac =
    eCherry_Library.Data.DataRecords.ElecReaction.List_Of_Reactions.HERdummy();

  parameter eCherry_Library.Data.DataRecords.Geometry GeoRec = eCherry_Library.Data.DataRecords.Geometry(
    X           = 0.01,
    X_membrane  = 0.0005,
    Y           = 1,
    Z           = 1,
    cond0       = 1,
    dX          = 1e-06);

  parameter eCherry_Library.Data.DataRecords.Conditions CondRec = eCherry_Library.Data.DataRecords.Conditions(
    T0          = 300,
    Tenvironment = 293.15,
    p           = 1);

  parameter Real c0[nS]          = {0, 1.45e-12, 0.0001, 6000, 55000};
  parameter Real Pi[nS]          = {100000, 100000, 100000, 100000, 100000};
  parameter Real molFlow_vec[nS] = {0, 7.25e-15, 5e-07, 30, 275};

end Example_AlkalineWaterElectrolysis;
