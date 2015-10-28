# DeepDive Tools

Standardizing inputs, outputs, and processing steps of DeepDive for a cloud deployment/tool

[will eventually be here](https://pypi.python.org/pypi/deepdive)

## Overview of Project
I first tried setting up DeepDive in a standard way, to perform extractions of mentions and features by way of the deepdive executable, to the database. This operation did not give me the amount of control that would be desired, as infrastructure does not extend well to a SLURM environment with a launch setup. It was also frustrating to be using DeepDive as a "black box." I realized very quickly that I was using the DeepDive command simply as a wrapper to write to the data base, and given that I had to write my own scripts anyway, it would be easiest to break apart the initial steps for extractions, build more "container-ized" methods to do initial steps, and then use DeepDive for the training and inference (where I see it's strength). It was also apparent that with the current setup, users would be doing different versions of the same thing, over again, and this is not efficient. I wanted to start from scratch with a modified infrastructure, and this gives me an opportunity to think about how I want to do this, because it needs to be a lot easier than it currently is. My first goal is to standardize the process, and build a set of python tools that can work with simple inputs and outputs for (what will eventually be) a cloud-based or VM-based deployment. I am going to think about this in the context of Neuroimaging / Psychology analysis, and that all steps should come from data structures (and not manually doing things).

### Mention Extraction
Ways to identify mentions can come from several places:
- a structured language (ontologies), typically an owl (extended version of rdf) file
- labels for an atlas or brain map (also structured, an XML file and nifti image)
- a subset of "normal word" terms deemed important by way of relationships in wordnet

I will start with the second - using labels from at atlas or brain map, as this seems like the quickest way to connect terms with actual data. For all three of the above approaches, I want to generate a standard data structure for "putting" the data into. The idea will be that my DeepDive prep tool will be able to handle anything coming in this format. 
