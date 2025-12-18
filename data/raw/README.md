# Raw Data Directory

## Expected File Structure

Place your raw mission data file here:
- `raw_mission_data_final.csv` (10,000 rows)

## Data Schema

| Column | Type | Description |
|--------|------|-------------|
| Report_ID | int | Unique identifier |
| Source_Date | datetime | Report timestamp |
| Reporter_ID | string | Reporter identifier |
| Unit_Name | string | Reporting unit |
| Sector | string | Geographic sector |
| Report_Urgency | string | Urgency level |
| Reliability_Score | string | Source reliability (A1-D4, F) |
| Content_Body | string | Report text (Hebrew) |

## Note
Data files are not included in the repository due to size and sensitivity.

