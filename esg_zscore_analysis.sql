-- esg_zscore_analysis.sql
-- Computes z-scores per industry per ESG dimension, then ranks
-- industries by imbalance (variance of their 3 z-scores).
SELECT AVG(environment_score) AS env_avg, AVG(social_score) AS soc_avg, AVG(governance_score) AS gov_avg FROM esg_clean;
SELECT AVG((environment_score - 408.19) * (environment_score - 408.19)) AS env_var, AVG((social_score - 288.72) * (social_score - 288.72)) AS soc_var, AVG((governance_score - 275.97) * (governance_score - 275.97)) AS gov_var FROM esg_clean;
DROP TABLE IF EXISTS esg_zscores;
CREATE TABLE esg_zscores AS SELECT industry, environment_score, social_score, governance_score, total_esg_score, (environment_score - 408.19) / 73.89 AS env_z, (social_score - 288.72) / 25.70 AS soc_z, (governance_score - 275.97) / 20.90 AS gov_z FROM esg_clean;
SELECT industry, ROUND(env_z,2) AS env_z, ROUND(soc_z,2) AS soc_z, ROUND(gov_z,2) AS gov_z FROM esg_zscores ORDER BY (env_z*env_z + soc_z*soc_z + gov_z*gov_z) DESC LIMIT 5;
