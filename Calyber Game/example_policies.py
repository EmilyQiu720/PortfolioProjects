# Description: This file contains the example pricing and matching policies used to generate the training data in the simulation.

import numpy as np
import itertools
import unittest
import pickle
import time
from utils import populate_shared_ride_lengths


# Pricing policy
class ExamplePricingPolicy(object):

    def __init__(self, c=0.7):
        self.c = c

    @staticmethod
    def get_name():
        return "Example"

    def pricing_function(self, state, rider):

        # the prices vector (pasted from the result in `example_pricing_policy_calculation.ipynb`) is the price for each pickup area. Riders from the same pickup area are charged the same base price plus an error term.
        prices = [0.57685655, 0.53056563, 0.51467013, 0.60836117, 0.55640752,
                0.41337777, 0.39378596, 0.35      , 0.89838252, 0.70604205,
                0.74354604, 0.75589718, 0.6986384 , 0.56606807, 0.59584261,
                0.54766121, 0.70604205, 0.70226617, 0.57220752, 0.59821444,
                0.54628065, 0.43348996, 0.51038933, 0.35016429, 0.49153274,
                0.58378463, 0.56111173, 0.39208874, 0.51814224, 0.52605272,
                0.46332601, 0.47555747, 0.50366752, 0.59467912, 0.47979966,
                0.64997678, 0.75589718, 0.49344785, 0.52716047, 0.54492038,
                0.54160475, 0.52716047, 0.48530292, 0.54492038, 0.68236918,
                0.58276257, 0.77015554, 0.66353705, 0.55951693, 0.73793849,
                0.67114376, 0.73265155, 0.60189027, 0.71409027, 0.74354604,
                0.57685655, 0.70604205, 0.56522335, 0.63103407, 0.52771937,
                0.55872973, 0.64789812, 0.58798973, 0.80765953, 0.63276302,
                0.55717513, 0.57130511, 0.56522335, 0.51418458, 0.63276302,
                0.53350226, 0.75589718, 0.59467912, 1.        , 0.673825  ,
                0.57311882]

        # generate a random error term between -0.1 and 0.1
        error = np.random.uniform(-0.1, 0.1)

        # the price is the base price of the pickup area plus the error term
        price = prices[rider.pickup_area-1] + error

        # bound the price to be between c/2 and 1
        price = np.minimum(np.maximum(price, self.c/2), 1)

        return price


# Matching policy
class ExampleMatchingPolicy(object):

    def __init__(self, c=0.7):
        self.c = c

    @staticmethod
    def get_name():
        return "Example"

    def matching_function(self, state, rider):
        """ Greedy matching: match the arriving rider with the waiting rider who shares the longest trip with the arriving rider. If there is no waiting rider, or the maximal shared trip length with the waiting riders is 0, then don't match the arriving rider with any one and let her wait in the system. """

        # list of the shared trip lengths of the arrving rider with all waiting riders
        shared_lengths = list()

        # OD pairs of the arriving rider
        origin0 = (rider.pickup_lat, rider.pickup_lon)
        destination0 = (rider.dropoff_lat, rider.dropoff_lon)

        for waiting_rider in state:

            # OD pairs of the waiting riders
            origin1 = (waiting_rider.pickup_lat, waiting_rider.pickup_lon)
            destination1 = (waiting_rider.dropoff_lat, waiting_rider.dropoff_lon)

            # use the helper function to calculate the shortest trip length shared by the arriving rider and the waiting rider
            _, shared_length, _, _, _ = populate_shared_ride_lengths(origin0, destination0, origin1, destination1)
            shared_lengths.append(shared_length)

        # match the arriving rider with the waiting rider who shares the longest trip with the arriving rider
        if len(shared_lengths) > 0 and np.max(shared_lengths) > 0:
            best_waiting_rider = state[np.argmax(shared_lengths)]
        else:
            best_waiting_rider = None

        return best_waiting_rider