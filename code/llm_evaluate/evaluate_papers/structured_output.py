#!/usr/bin/env python

from pydantic import BaseModel

class SubElement(BaseModel):
    result: int
    paper_text: str

class StructuredOutput(BaseModel):
    research_type: SubElement
    result_outcome: SubElement
    affiliation: SubElement
    problem_description: SubElement
    goal_objective: SubElement
    research_method: SubElement
    research_question: SubElement
    hypothesis: SubElement
    prediction: SubElement
    contribution: SubElement
    pseudocode: SubElement
    open_source_code: SubElement
    open_experiment_code: SubElement
    train: SubElement
    validation: SubElement
    test: SubElement
    results: SubElement
    hardware_specification: SubElement
    software_dependencies: SubElement
    experiment_setup: SubElement
