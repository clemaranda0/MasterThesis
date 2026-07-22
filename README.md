````md
# Master Thesis – Prospective LCA of Agri-Food Products

This repository contains the code, input data, Scenario Difference Files (SDFs), and post-processing scripts developed for my Master's thesis on **prospective Life Cycle Assessment (LCA)** of agri-food products using **Brightway**, **Activity Browser**, and **premise**.

---

# Prerequisites

Before running the project, make sure you have:

- A Python virtual environment with:
  - `premise`
  - `Brightway`
  - `Activity Browser`
- An Activity Browser project already created (e.g. **Master Thesis**).
- An initialized Brightway project with the required databases.

## Activity Browser structure

The project should follow a structure similar to the one below.

<img width="342" height="529" alt="image" src="https://github.com/user-attachments/assets/f1e4d58c-148b-4961-b2fc-37768d7b6c59" />

<img width="1077" height="355" alt="image" src="https://github.com/user-attachments/assets/b0c14af3-68db-459a-8dfe-e3a29eb4e61f" />

The foreground databases contain the two case-study products (**cheese** and **potato**) together with additional activities created for the mitigation scenarios (e.g. **3-NOP feed supplementation** for reducing enteric methane emissions).

---

# Repository structure

| File | Description |
|------|-------------|
| `config.py` | Global configuration parameters and user-specific settings. |
| `helpers.py` | Collection of helper functions used throughout the project. |
| `main_run_premise.py` | Generates prospective ecoinvent databases for selected years and IAM scenarios using *premise*. |
| `main_generate_sdf.py` | Generates Scenario Difference Files (SDFs) for scenario-based LCAs in Activity Browser. |
| `main_process_results.py` | Formats and processes Activity Browser outputs for analysis and visualization. |
| `main_learning_curve.py` | Estimates empirical environmental learning rates and generates learning curve figures. |

---

# Input data

The `inputs` folder contains the datasets required by the scripts.

| File | Description |
|------|-------------|
| `cereals_emissions_Europe_ts` | Historical emission intensity and annual production of cereals (excluding rice) in Europe since 1968 (FAOSTAT). |
| `milk_emissions_World_ts` | Historical emission intensity and annual milk production worldwide since 1968 (FAOSTAT). |
| `cow_feeding` | List of activities identified as feed inputs for dairy cows (author's compilation). |
| `exclusions_yield` | List of activities excluded from yield scaling (author's compilation). |

---

# Scenario Difference Files (SDFs)

The `SDF` folder contains all generated Scenario Difference Files used in Activity Browser.

Files are organized by simulation year, from **2030** to **2050**.

---

# Results

The `results` folder contains the formatted outputs used for the analyses presented in the thesis.

If you want to process your own Activity Browser results using `main_process_results.py`, follow these steps:

1. In Activity Browser, export the LCA results from:
   - **Process Contributions**
   - **Absolute results**
   - **Aggregated by "Reference product"**
2. Save each exported file using the following naming convention:

   ```
   impact-assessment-method_scenario_year_product_impact-category
   ```

   Example:

   ```
   EF v3.1_remind-SSP1-PkBudg650+agricultural-practices_2030_potato_climate change
   ```

3. Update the input/output paths in `main_process_results.py` to match your local folder structure.

---

# Additional information

This repository contains the code and datasets used for the analyses presented in the accompanying Master's thesis.

For a detailed description of the methodology, assumptions, scenario implementation, and results, please refer to the thesis manuscript.
````
