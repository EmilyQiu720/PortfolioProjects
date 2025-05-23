[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=19025025&assignment_repo_type=AssignmentRepo)
# Calyber: A Shared Rides Pricing and Matching Game

<p align="center">
  <img src="images/logo_new.png" width="280" />
</p>

This repository contains code for a project to design pricing and matching policies for the ridesharing company Calyber. The training data (`data/training_data.csv`) includes historical rider arrivals and requests under the default policies (`example_policies.py`). Your task is to develop new policies in `student_policies.ipynb` to maximize company profits. Policies will be evaluated on an unrevealed test dataset. For more details, refer to the accompanying PDF and the descriptions below.


## Files description:
- `student_policies.ipynb`: The main file to complete.
- `example_policies.py`: Contains example pricing and matching policies.
- `example_pricing_policy_calculation.ipynb`: Code for calculating the example pricing policy, with results pasted into `example_policies.py`.
- `rider.py`: Defines the `rider` class for managing rider-related data.
- `helper_functions_demonstration.ipynb`: Demonstrates the use of `populate_shared_ride_lengths()` to calculate the shortest path of a shared ride, and plots the route.
### Files in `data` folder:
- `training_data.csv`: contains the training data. Each row represents an arriving rider. Columns include:
    - `rider_id`: Rider’s unique ID (integer, 0–11787).
    - `arrival_week`: Week of rider arrival (integer, 1–6).
    - `arrival_time`: Arrival time within the hour (in seconds, 0–3600).
    - `pickup_area`: Index of the rider’s pickup area (1–76).
    - `dropoff_area`: Index of the rider’s dropoff area (1–76).
    - `pickup_lat` and `pickup_lon`: Latitude and longitude of the pickup area’s centroid.
    - `dropoff_lat` and `dropoff_lon`: Latitude and longitude of the dropoff area’s centroid.
    - `solo_length`: Solo ride distance (in miles), which is the haversine distance between the pickup and dropoff locations of the rider.
    - `quoted_price`:  Quoted price per mile ($/mile) under the example policy (float, 0–1).
    - `convert_or_not`: Whether the rider converts (1 for yes, 0 for no) under the example policy.
    - `waiting_time`: Rider's waiting time (in seconds), the time difference between the arrival time and the dispatching time of the rider. `nan` if the rider does not convert.
    - `matching_outcome`: Matched rider’s ID if matched, otherwise nan.
- `area_lat_lon.csv`: Contains latitude and longitude of centroids for Chicago’s 76 community areas. The columns include:
    - `area`: Community area index (1–76).
    - `lat` and `lon`: Latitude and longitude of the area’s centroid.
- `test_examples.pickle`: contains examples for testing your policies, including one incoming rider object and four states of different sizes. It is used in the testing code of `test_policies()` in `student_policies.ipynb`.
    - Loading Instructions: Use `data = pickle.load(open('data/test_examples.pickle', 'rb'))`.
    - Contents:
        - `data['rider']`: A rider object (instance of the `rider` class from `rider.py`), sampled randomly from the training data, representing an incoming rider.
        - `data['states']`: A list containing four states. Each state is a list of rider objects representing the waiting requests. The four states have 0/8/35/77 waiting requests, respectively. Each state is generated by accumulating all arriving riders over random time windows of 0s/15s/1min/2min in the training data.
