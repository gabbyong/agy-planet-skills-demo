---
name: visualize-dataset
description: Use this when the user asks you to help download and use a dataset to help him understand what it looks like.
---

# Workflow

When helping a user understand a new dataset, you should aim to start go from low-fidelity to high fidelity information. 

In general, always write your response using paragraphs that are 2-3 sentences long which are entity dense and succint. Prefer the style of writers like Martin Kleppman and the Elements Of Style. 

Do not use horizontal rules (`---`) or visual dividers between sections.

Here's a workflow

1. **Break Down the Dataset** First, explain what the dataset is about. This includes the data it contains ( sample counts, resolutions, splits ), other related benchmarks and dataset along with current SOTA figures.  This should be around 2 paragraphs

You should also explain what are some of the reasons why this specific benchmark is difficult (Eg. noise, spatial distractions, task makeup). You must always provide citations for comparisons for this so the user can verify your work if needed. 

2. **Provide Samples**: Then, you should explore a small slice of the dataset ( and confirm with the user before downloading the entire whole dataset ) and provide the samples to the user using the most appropriate format for the modality.

When writing scripts or downloading/inspecting data in Python, always use `uv`. Check if a `.venv` exists in the local environment; if it does not exist, initialize one (e.g. `uv venv`). Execute all scripts and install necessary packages using `uv` (e.g. `uv run`, `uv pip install`).

3. **Follow Ups**: Once you've done this, you should then provide the user a few potential follow ups that he can explore to explore the data, current solutions for the benchmark etc.