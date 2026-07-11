# ESG Industry Performance Analysis

An analysis of Environmental, Social, and Governance (ESG) scores across 43 industries.

## Files
- esg_raw.csv - original data with duplicate industries
- esg_clean.csv - cleaned, deduplicated data (43 industries)
- esg_cleaning.sql - SQL used to normalize names and merge duplicates
- esg_zscore_analysis.sql - SQL computing z-scores and an imbalance ranking
- esg_clustering.py - k-means clustering script (scikit-learn)
- esg_clusters.csv, cluster_scatter.png, elbow_plot.png - clustering outputs

## Dashboard
[View the Tableau dashboard](https://public.tableau.com/views/Book1_17838017222860/Dashboard1?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) *(interactive, opens in browser)*

Or download `esg_dashboard.twbx` from this repo and open in Tableau Desktop.
