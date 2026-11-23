# cmpsc463-project2-healthcare
Authors: Noam Abraham, Stevens Blantrice, Yony Rober

Deliverables: Source code, project report, demo video

Due 12/6/2026

This project's goal is to model a solution to a real-world issue related to healthcare affordability and access, using concepts from Penn State Abington's CMPSC 463.

Our chosen application is a Fair Appointment Scheduler and Policy Simulator. A simulated clinic network has patients, each with an urgency weight, visit length, arrival time, and insurance/income group, and providers with limited capacity. The app schedules patients under several policies and then measures how efficient and how fair each policy is. 

Algorithms used

        Component	                                Algorithm / structure
Scheduling policies	            Greedy by weight/length ratio, plus FIFO, shortest-visit-first, urgency-first as baselines
Dispatch to providers	          Min-heap keyed on provider's next free time	
Patient lookup	                Hash table (id → record)	
Open appointment slots	        BST with insert, delete, and "earliest slot ≥ t" queries	
Ranking disagreement	          Inversion counting (O(n log n)), normalized by n(n-1)/2, computed overall and per group	
Wait-time statistics	          Rselect/Dselect for median, 90th percentile, and top-k longest waits, benchmarked against sort-based versions

Division of responsibilities

Noam: Scheduling engine

Patient and provider data model
All scheduling policies, heap-based dispatch, BST slot manager, hash table
Simulation loop that takes a dataset and a policy and returns a full schedule
Brute-force optimal solver for small instances
Cancellations and rebooking using a BST

Yony: Fairness and analytics

Synthetic dataset generator with configurable size, group mix, and urgency distribution
Inversion counter, used to compare each policy's service order against a reference ranking (arrival order and urgency order)
Dselect/Rselect statistics module and per-group metrics (average wait, max wait, 90th percentile, rank disagreement)
Runtime benchmarks (Dselect vs. sorting, inversion counting vs. O(n²)) and correctness tests for every module

Stevens: Web app

UI for loading or generating a dataset, picking policies, and running simulations
Visualizations: timeline or Gantt view per provider, side-by-side policy comparison, per-group wait charts, a fairness summary
Controls for the dataset parameters and for the weight function
Integration with A's and B's modules, and the final demo flow

Project report: https://docs.google.com/document/d/1waoYEy05nz-PUNVFp-cla_bti6NIjoBVk1uNddRxCd4/edit?usp=sharing

Demo: TODO
