# eCherry Reactor Model Generator

A model-driven prototype for generating eCherry-compatible Modelica simulation models from high-level electrochemical reactor specifications.

## Overview
Electrochemical reactor simulations built with eCherry typically require manual assembly of low-level Modelica components and configuration of simulation parameters. This project explores a model-driven approach that raises the level of abstraction by allowing users to define reactor configurations in a domain-specific language (DSL), then automatically transforms those models into eCherry-compatible Modelica code.

The project is designed to demonstrate core model-driven software development concepts, including:
- metamodeling
- domain-specific language design
- model transformation
- automated artifact generation

## Problem
Constructing electrochemical reactor simulations manually can be complex and time-consuming, especially for researchers and engineers with domain expertise in electrochemistry rather than in Modelica or simulation tooling.

This project addresses that problem by providing a higher-level modeling workflow for electrochemical reactor design.

## Proposed Pipeline
The system follows a four-stage model-driven pipeline:

1. DSL Reactor Model
2. Metamodel-Based Representation
3. Model Transformation
4. Automated Code Generation for the eCherry library

At a high level, the workflow is:

DSL model  
→ parser  
→ internal metamodel-based representation  
→ transformation rules  
→ generated eCherry-compatible Modelica model

## Domain Scope
The project focuses on electrochemical reactor modeling, including systems such as:
- electrolyzers
- fuel cells
- electrochemical reactors

Core domain concepts represented in the metamodel include:
- Reactor
- Electrode
- Electrolyte
- Separator
- FlowChannel
- OperatingConditions

Operating conditions may include parameters such as:
- temperature
- pressure
- flow rate

## Example DSL
```txt
reactor Electrolyzer {
  electrode_area = 10 cm^2
  electrolyte = KOH
  temperature = 298K
}