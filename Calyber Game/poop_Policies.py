#!/usr/bin/env python
# coding: utf-8

# # Student Policies
# Now that you know how model cost, conversion, demand, and optimize price and matching, we can move on the final part of this game, **building your policies!**. Below we have set up skeleton code for you to build your policies. Make when you finish to run the last code cell to upload your policy.

# In[1]:


# Load in all your libraries and packages here!
# NOTE: you are allowed to use packages loaded below ONLY. If you want to use any other packages, please contact the TA.
import pandas as pd
import numpy as np
import itertools
import math
import random
import copy
import time
import pandas as pd
import haversine
# from haversine import haversine
import unittest
import pickle
import collections

from utils import * # this imports all helper functions in utils.py

# TODO: Replace the string "TeamName" below with your own team's name in camel case. For e.g. "AwesomeTeam"
# DO NOT RENAME THE FILE, the file name should be "{TEAM_NAME}_Policies.py"
TEAM_NAME = "poop"


# # Offline Learning

# ## Pricing Policy Part

# In[2]:


import glob

# Define price bins clearly
price_bins = [(0.48,0.54),(0.54,0.6),(0.6,0.65),(0.65,0.7),(0.7,0.75),(0.75,0.8)]

# Initialize alpha-beta distributions
alpha = collections.defaultdict(lambda: 1)
beta = collections.defaultdict(lambda: 1)

global_alpha = [1] * len(price_bins)
global_beta = [1] * len(price_bins)

agg_alpha_by_pickup = collections.defaultdict(lambda: [1]*len(price_bins))
agg_beta_by_pickup = collections.defaultdict(lambda: [1]*len(price_bins))

agg_alpha_by_dropoff = collections.defaultdict(lambda: [1]*len(price_bins))
agg_beta_by_dropoff = collections.defaultdict(lambda: [1]*len(price_bins))

def assign_arm(price):
    for idx, (low, high) in enumerate(price_bins):
        if low <= price < high:
            return idx
    return len(price_bins)-1

def discretize_state_size(size):
    return '0' if size==0 else '1-4' if size<=4 else '5-10' if size<=10 else '11+'

def discretize_avg_wait(wait):
    return '0-30' if wait<=30 else '31-100' if wait<=100 else '100+'

# Load weekly files separately
weeks_converted = sorted(glob.glob('data/week_*_converted_with_state.csv'))
weeks_non_converted = sorted(glob.glob('data/week_*_convert_0.csv'))

# iterate week by week explicitly
for week_idx, (conv_file, nonconv_file) in enumerate(zip(weeks_converted, weeks_non_converted), start=1):

    df_converted = pd.read_csv(conv_file)
    df_non_converted = pd.read_csv(nonconv_file)

    df_converted['convert_or_not'] = 1
    df_non_converted['convert_or_not'] = 0

    # Concatenate and sort this week's data explicitly
    df_week = pd.concat([df_converted, df_non_converted], ignore_index=True)
    df_week = df_week.sort_values(by='arrival_time').reset_index(drop=True)

    # Step 3: Explicitly RESET STATE EACH WEEK
    state = {}  # reset here explicitly (important)

    # Iterate clearly through riders of current week
    for idx, row in df_week.iterrows():
        t_now = row['arrival_time']  # continuous time is fine
        
        # Remove riders whose patience expired explicitly
        state = {rid: (arr, pat) for rid, (arr, pat) in state.items() if (t_now - arr) < pat}

        # Define context explicitly (with reset weekly state)
        context = (
            row['pickup_area'],
            row['dropoff_area'],
            discretize_state_size(len(state)),
            discretize_avg_wait(np.mean([t_now - arr for arr, _ in state.values()]) if state else 0)
        )

        # Update alpha-beta based on observed conversions clearly
        arm = assign_arm(row['quoted_price'])
        converted = row['convert_or_not']
        
        if converted:
            alpha[(context, arm)] += 1
            global_alpha[arm] += 1
            agg_alpha_by_pickup[row['pickup_area']][arm] +=1
            agg_alpha_by_dropoff[row['dropoff_area']][arm] +=1
            if row['waiting_time'] > 0:
                state[row['rider_id']] = (t_now, row['waiting_time'])
        else:
            beta[(context, arm)] += 1
            global_beta[arm] += 1
            agg_beta_by_pickup[row['pickup_area']][arm] +=1
            agg_beta_by_dropoff[row['dropoff_area']][arm] += 1


# ## Matching Policy Part

# In[3]:


MAX_POOL = 180 # 3-mins pairs
COST_PM = 0.7
BASE_PRICE_FALLBACK = 0.65
base_price = pd.read_csv('base_price_table.csv')

def pair_profit(r1, r2, cache):
    key = (r1._uid, r2._uid) if r1._uid < r2._uid else (r2._uid, r1._uid)
    if key not in cache:
        trip, *_ = populate_shared_ride_lengths(
            (r1.pickup_lat,  r1.pickup_lon), (r1.dropoff_lat, r1.dropoff_lon),
            (r2.pickup_lat,  r2.pickup_lon), (r2.dropoff_lat, r2.dropoff_lon)
        )
        cache[key] = trip
    else:
        trip = cache[key]

    if trip == 0:
        return -math.inf
    
    match1 = base_price.loc[(base_price["pickup_area"] == r1.pickup_area) &
                            (base_price["dropoff_area"] == r1.dropoff_area),
                            "base_price"]
    match2 = base_price.loc[(base_price["pickup_area"] == r2.pickup_area) &
                            (base_price["dropoff_area"] == r2.dropoff_area),
                            "base_price"]

    # if the pair exists, take the scalar; otherwise fall back (e.g. 0.65)
    quoted_price_1 = match1.iat[0] if len(match1) else BASE_PRICE_FALLBACK
    quoted_price_2 = match2.iat[0] if len(match2) else BASE_PRICE_FALLBACK

    rev  = quoted_price_1 * r1.solo_length + quoted_price_2 * r2.solo_length
    return rev - COST_PM * trip


# # Pricing Policy

# Feel free to add more functions to `StudentPricingPolicy` but **DO NOT** modify the initalization and static methods. Your code will only be graded based on the output of your pricing function.

# In[4]:


class StudentPricingPolicy:
    # DO NOT MODIFY
    def __init__(self, c = 0.70):
        self.c = c

    # DO NOT MODIFY
    @staticmethod
    def get_name():
        return TEAM_NAME

    def pricing_function(self, state, rider):
        """
        Returns the price of the given rider in the given state

        Parameters
        ----------
        state: list
            list of rider(s) (object) waiting in the state
        rider: object
            An incoming rider

        Returns
        -------
        float
            The price of the rider: must be in [0, 1]
        """
        pickup_area = rider.pickup_area
        dropoff_area = rider.dropoff_area
        state_size = discretize_state_size(len(state))
        avg_wait = np.mean([getattr(r, 'waiting_time', 0) or 0 for r in state]) if state else 0
        
        exact_context = (pickup_area, dropoff_area, state_size, avg_wait)
        context_seen = any((exact_context, arm) in alpha for arm in range(len(price_bins)))
        
        # If exact context seen before, use it explicitly
        if context_seen:
            context_to_use = exact_context
            samples = [
                (np.random.beta(alpha[(context_to_use, arm)], beta[(context_to_use, arm)]), arm)
                for arm in range(len(price_bins))
            ]

            # Sort samples descending by value
            top_k = sorted(samples, reverse=True)[:2]
            # Take the average of the prices of top-k arms
            top_prices = [np.mean(price_bins[arm]) for _, arm in top_k]

            return np.mean(top_prices)

        else:
            if pickup_area in agg_alpha_by_pickup:
                a_pick = agg_alpha_by_pickup[pickup_area]
                b_pick = agg_beta_by_pickup[pickup_area]
            else:
                a_pick = [1] * len(price_bins)
                b_pick = [1] * len(price_bins)

            if dropoff_area in agg_alpha_by_dropoff:
                a_drop = agg_alpha_by_dropoff[dropoff_area]
                b_drop = agg_beta_by_dropoff[dropoff_area]
            else:
                a_drop = [1] * len(price_bins)
                b_drop = [1] * len(price_bins)

            a_combined = [(a1 + a2)/2 for a1, a2 in zip(a_pick, a_drop)]
            b_combined = [(b1 + b2)/2 for b1, b2 in zip(b_pick, b_drop)]

            # Thompson Sampling
            samples = [np.random.beta(a, b) for a, b in zip(a_combined, b_combined)]
            best_arm = np.argmax(samples)
                            
            return np.mean(price_bins[best_arm])


# # Matching Policy

# Again, feel free to add more functions to `StudentMatchingPolicy` but **DO NOT** modify the initalization and static methods. Your code will only be graded based on the output of your matching function.

# In[5]:


class StudentMatchingPolicy:
    # DO NOT MODIFY
    def __init__(self, c = 0.70):
        self.c = c

    # DO NOT MODIFY
    @staticmethod
    def get_name():
        return TEAM_NAME
    
    def _ensure_uid(self, r):
        if not hasattr(r, "_uid"):
            r._uid = self._uid_seq
            self._uid_seq += 1

    def matching_function(self, state, rider):
        """
        Returns the matched rider or None is there is no match

        Parameters
        ----------
        state: list
            list of rider(s) (object) waiting in the state
        rider: object
            An incoming rider

        Returns
        -------
        rider or None:
            Returns a matched rider (object) or None
        """
        """
        O(n) system‑aware greedy; uses a persistent distance cache
        and updates best_alt incrementally.
        """
        if not hasattr(self, "_dist_cache"):
            self._dist_cache = {}
            self._best_alt   = {}
            self._uid_seq    = 0

        if not state:
            return None
        
        # give uids to everyone
        for r in state + [rider]:
            self._ensure_uid(r)

        # --- newest ≤ MAX_POOL riders ---
        pool = state[-MAX_POOL:] if len(state) > MAX_POOL else state

        # --- ensure best_alt entries exist ---
        for w in pool:
            self._best_alt.setdefault(w._uid, -1.0)

        best_partner, best_gain = None, 0

        for w in pool:
            pf = pair_profit(rider, w, self._dist_cache)        
            gain = pf - self._best_alt[w._uid]

            # update w's alternative if this new profit is better
            if pf > self._best_alt[w._uid]:
                self._best_alt[w._uid] = pf

            if gain > best_gain:
                best_gain, best_partner = gain, w

        self._best_alt[rider._uid] = 0        # register rider for future
        return best_partner if best_gain > 0 else None


# # Testing your Code

# Use the function below to test your policies. This output will only tell you the price and matching result from your policies.
# 
# The test examples consist of 4 states and 1 incoming rider:
# - Four States: These represent states with 0, 8, 35, and 77 waiting requests, respectively. Each state is created by aggregating all arriving riders within random time windows of 0 seconds, 15 seconds, 1 minute, and 2 minutes from the training data.
# - Incoming Rider: This rider is randomly sampled from the training data.

# In[6]:


from utils import test_policies
test_policies(StudentPricingPolicy, StudentMatchingPolicy)


# ## Congrats! You finished!

# Once you have completed this notebook, you can run the following command to export your notebook to a python script. Make sure to submit only `{TEAM_NAME}_Policies.py` file. Please do not edit anything!

# In[7]:


# DO NOT MODIFY
from utils import export_notebook
# export the notebook as a .py file with name of "{TEAM_NAME}_Policies.py"
export_notebook(TEAM_NAME)

