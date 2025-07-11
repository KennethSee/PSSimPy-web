# PSSimPy-web
PSSimPy-Web is a web-based simulator built on the [PSSimPy Python library](https://github.com/KennethSee/PSSimPy) (version 0.1.4). It provides a simulation framework for modeling and analyzing Large-Value Payment Systems (LVPS) with agent-based modeling. This tool is designed for researchers, policymakers, and financial institutions to evaluate the implications of design decisions.

## Citation

We would appreciate it if you cited [our paper](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p3047.pdf) if you have used PSSimPy web or any of its core ideas in your research:

>See, K., Garcia, N. M., & Li, X. (2025). Simulating Blockchain Applications in Large-Value Payment Systems through Agent-Based Modeling. _Proceedings of the 24th International Conference on Autonomous Agents and Multiagent Systems (AAMAS '25)_. International Conference on Autonomous Agents and Multiagent Systems (pp. 3047-3049), Detroit, Michigan, USA.

```BibTeX
% BibTeX citation
@inproceedings{See2025-blockchain_lvps_sim,
  title={Simulating Blockchain Applications in Large-Value Payment Systems through Agent-Based Modeling},
  author={See, Kenneth and Garcia, Nicholas MacGregor and Li, Xiaofan},
  booktitle={Proceedings of the 24th International Conference on Autonomous Agents and Multiagent Systems},
  series={AAMAS '25},
  pages={3047–-3049},
  numpages={3},
  year={2025},
  publisher={International Foundation for Autonomous Agents and Multiagent Systems},
  address={Detroit, Michigan, USA}
}
```

## Usage
### Clone the Repository
```bash
git clone https://github.com/KennethSee/PSSimPy-web.git
cd PSSimPy-web
```

### Installation
```bash
pip install -r requirements.txt
```

### Launch App
```bash
streamlit run app.py
```

The application will open in your default web browser. Follow the navigation bar to configure scenarios, run simulations, and view results.

## Workflow Overview
![image](https://github.com/user-attachments/assets/b8af4f60-64a7-42f1-a4ca-358fc0b14d26)

### Setting Up Simulation Parameters
The "Simulation Parameters" page allows you to define the static parameters in your simulation scenario. Use the expandable "Help?" section for more information on each parameter.
![image](https://github.com/user-attachments/assets/6045c163-aa44-4ed7-9d9d-b3fd645b79a4)

### Input Simulation Data
The "Input Data" page allows you to define the data that will be used in the simulation. There are three types of data - Banks, Accounts, and Transactions. Transaction data is optional; check the "Random system-generated transactions?" checkbox to enable the simulation system to generate transactions randomly.

![image](https://github.com/user-attachments/assets/1dea69ab-0193-4ea4-98dc-ab535ac10994)
The data should be uploaded as csv files. Templates can be found in the _file_templates_ folder in this repository.
### Configuring the Agents
Each of the agents can be configured to have customized policies and behaviors. For each type of agent, users can either utilize out-of-the-box templates or create custom agents. Where applicable, custom parameters can be defined to allow the agent to track additional data points. Each agent configuration page will include a code box which displays Python code that implements the policy of the agent. The code implementation of the functions defined can be modified but the function headers should not be changed.
![image](https://github.com/user-attachments/assets/613cc7b4-98b2-4b6d-a624-212aad2c0fcb)

### Preview and Run Simulation
The "Preview" page presents an overview of the simulation inputs that have been defined in the workflow.
![image](https://github.com/user-attachments/assets/2e5ccd4f-036f-46de-b491-9d92554c21e5)
![image](https://github.com/user-attachments/assets/297140a6-6a46-46ca-b249-0ca4ad7bd4f2)
Once satisfied, you can click on the "Begin Simulation" button to run the simulation scenario.

### Access Simulation Results
The Results section allows you to access the results from a simulation run. Raw data is displayed and can be downloaded as .csv files for further analysis.
![image](https://github.com/user-attachments/assets/6d4604ca-fbb9-47f1-af74-0365ebe546c1)
Some charts that track liquidity and credit usage over the period of the simulation have also been provided.

## Export and Import Simulation Settings
### Export
Simulation settings can be exported at the bottom of the "Preview" page. A unique name should be given for each export. The export can either include just the settings (which include the static parameters and the agents' configurations) or with the input data as well.
![image](https://github.com/user-attachments/assets/eca01a1e-36c4-462f-a160-ee2d02e91c2e)
Upon a successful export, you should be able to locate the exported settings as a .zip file within the _saved_settings_ folder in your local directory.

### Import
Exported .zip files can be imported at the bottom of the Landing page.
![image](https://github.com/user-attachments/assets/b33417ff-2d14-4675-9ff9-1297a9a18d5d)
Upon successful import, you should see all the settings in the workflow populated with the contents from the imported settings.


