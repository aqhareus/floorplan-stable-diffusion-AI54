# AI54 – Floor Plan Image Generation with Stable Diffusion
## Project Overview

This project is developed as part of the AI54 course.
The objective is to fine-tune a pre-trained Stable Diffusion model for image generation using a structured dataset of architectural floor plans.

The project focuses on adapting an existing generative model (fine-tuning), not training a model from scratch, in accordance with the course requirements.

We chose the floor plan domain because it provides structured visual data with available textual descriptions, enabling a cleaner and more reliable fine-tuning process compared to unannotated image datasets.

## Motivation

Initial experimentation with artistic pattern datasets revealed a major limitation: the absence of ground truth or textual annotations (captions).
Since Stable Diffusion relies on text–image alignment, the lack of captions makes effective fine-tuning unreliable.

The floor plan dataset solves this issue by providing:

- Structured visual content

- Existing captions

- High interpretability of generated results

- Strong alignment with the methods studied in class (TDs)

## Dataset

We use the following dataset from Hugging Face:

https://huggingface.co/datasets/zimhe/pseudo-floor-plan-12k

or also, we can use the dataset from CubiCasa5k :

https://gts.ai/dataset-download/cubicasa5k/#wpcf7-f47097-o1

### Dataset characteristics:

- Approximately 12,000 floor plan images

- Paired with textual captions

- Synthetic but consistent architectural layouts

- Suitable for text-to-image generation tasks

Optional caption enrichment can be performed using models such as BLIP or CLIP if needed.

## Methodology

- Dataset preparation

- Load images and captions

- Clean and normalize text descriptions

- Resize images to Stable Diffusion-compatible resolution

## Model selection

- Pre-trained Stable Diffusion model

- Fine-tuning using LoRA to reduce computational cost

- Fine-tuning

- Train LoRA adapters on the floor plan dataset

- Keep base model frozen

- Optimize text–image alignment

- Evaluation

- Visual inspection of generated floor plans

- Comparison between base model outputs and fine-tuned outputs

- Analysis of layout consistency and caption adherence

## Tools and Libraries

- Python

- PyTorch

- Hugging Face Diffusers

- Transformers

- Accelerate

- Stable Diffusion

- LoRA

Experiments are designed to be compatible with Google Colab.

## Project Structure
.
├── data/
│   └── floor_plan_dataset/
├── notebooks/
│   ├── data_exploration.ipynb
│   ├── caption_analysis.ipynb
│   └── fine_tuning_lora.ipynb
├── models/
│   └── lora_weights/
├── results/
│   └── generated_images/
├── README.md

## Expected Results

- Generation of realistic and coherent floor plan images

- Improved alignment between textual prompts and generated layouts

- Clear visual difference between the base Stable Diffusion model and the fine-tuned version

## Team Organization

This is a group project. Tasks are distributed as follows:

- Dataset analysis and preprocessing

- Model fine-tuning and training

- Evaluation and visualization

- Report writing and presentation
