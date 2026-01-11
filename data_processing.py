import re
import csv
import yaml
import os

DATA_DIR = "data"

def save_data(rows):
  with open("dataset.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in rows:
      writer.writerow(row)

def process_game(file_name):
  # Load YAML File
  with open(file_name, "r", encoding="utf-8") as f:
    match = yaml.safe_load(f)

  date_str = str(match["info"]["dates"][0])
  year = int(re.search(r"20(\d{2})", date_str).group(1))
  innings = match["innings"]

  data = []

  for inning in innings:
    inning_name, inning_data = next(iter(inning.items()))
    deliveries = inning_data["deliveries"]

    run_count = 0
    wicket_count = 0
    batsman_runs = {}

    over_rows = {}

    # Process Balls
    for delivery in deliveries:
      ball_key, ball_data = next(iter(delivery.items()))
      # Floor the Over Count
      over_number = int(float(ball_key))

      # Update Batsman Runs
      batsman = ball_data["batsman"]
      runs_batsman = ball_data["runs"]["batsman"]
      batsman_runs[batsman] = batsman_runs.get(batsman, 0) + runs_batsman

      # Update Totals
      run_count += ball_data["runs"]["total"]
      if "wicket" in ball_data:
          wicket_count += 1

      striker = batsman
      non_striker = ball_data["non_striker"]

      # Update Feature Row -> Overwritten Until Final Ball of Over
      over_rows[over_number] = {
          "over": over_number + 1,
          "run_count": run_count,
          "wicket_count": wicket_count,
          "batsman1_runs": batsman_runs.get(striker, 0),
          "batsman2_runs": batsman_runs.get(non_striker, 0),
      }

    # Total Innings Runs
    total_runs = run_count

    # Append Row to Data
    for row in over_rows.values():
        row["year"] = year
        row["total_runs"] = total_runs
        data.append([
            row["over"],
            row["run_count"],
            row["wicket_count"],
            row["batsman1_runs"],
            row["batsman2_runs"],
            row["year"],
            row["total_runs"],
        ])

    # Write Data to CSV
    save_data(data)

  return data

# Iterate Through All Previous Matches
for filename in os.listdir(DATA_DIR):
  if filename.endswith(".yaml") or filename.endswith(".yml"):
    file_path = os.path.join(DATA_DIR, filename)
    print(f"Processing {file_path}")

    process_game(file_path)