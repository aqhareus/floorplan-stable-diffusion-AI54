# 🟦 Moroccan Zellige Pattern Generation  
### Stable Diffusion LoRA Fine-Tuning Project (UTBM — AI54)

This project aims to fine-tune **Stable Diffusion v1.5** using **LoRA (Low-Rank Adaptation)** in order to generate high-quality **Moroccan Zellige patterns** — including 8-point stars, cross patterns, octagonal structures, and full mosaic layouts.

The model learns:
- Zellige geometric symmetry  
- Ceramic texture  
- Moroccan color palettes  
- Complex interlaced mosaic structures  

This repository contains the full code for dataset loading, preprocessing, LoRA training, and inference.

---

## 📌 Project Overview

Zellige is a traditional Moroccan art form based on:
- the **Sceau** (8-point star),
- the **Saft** tile,
- and four geometric base tiles described in mathematical literature.

The objective of this project is to reproduce these geometric arrangements using generative AI.

We fine-tune Stable Diffusion on a curated dataset of real Zellige patterns using **LoRA**, which allows:
- lightweight training (only training attention layers),
- fast convergence,
- shareable model weights.

---

## 📁 Repository Structure
