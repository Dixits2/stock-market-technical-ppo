import gym
import json
import datetime as dt
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common import make_vec_env
from stable_baselines.common.vec_env.base_vec_env import VecEnvWrapper
from stable_baselines import PPO2
import gym_stocks
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

test_days = 260 #365 accounting for weekends
scenario_count = 7
tests_per_model = 10
model_count = 5
# this main tests for compotence of model based on good testing data
# over a period of one year for 7 different scenarios, returns the
# average profit per scenario after the 7 scenarios, as well as the
# average profit per day after the 7 scenarios.

# The algorithms require a vectorized environment to run

def min_max(val, c_min, c_max):
	if val > c_max:
		c_max = val
	if val < c_min:
		c_min = val
	return (val, c_min, c_max)


model = PPO2.load('SavedModels/model_5')

stats = []

# model
for l in range(model_count):
	model_profit = 0
	model_min = 0
	model_max = 0
	model_avg_profit = 0


	# run(multiple test for a model)
	for k in range(tests_per_model):
		run_profit = 0
		run_min = 0
		run_max = 0

		env = gym.make('Stocks-Testing-v0')
		obs = env._next_observation()

		#scene(scenario)
		for j in range(scenario_count):
			if j != 0:
				obs = env.reset()
			scene_profit = 0
			scene_min = 0
			scene_max = 0

			for i in range(test_days):
				action, _states = model.predict(obs)
				obs, rewards, done, info = env.step(action)

				if i == test_days - 1: # if reaches end, add cumulative profit
					vals = min_max(env.get_profit(), scene_min, scene_max)
					scene_profit += vals[0]
					scene_min = vals[1]
					scene_max = vals[2]
				else: # if it is not at the end
					if done: # if it goes bankrupt midway, add cumulative profit and move on to next scenario
						vals = min_max(env.get_profit(), scene_min, scene_max)
						scene_profit += vals[0]
						scene_min = vals[1]
						scene_max = vals[2]
						break
			vals = min_max(scene_profit, scene_min, scene_max)
			run_profit += vals[0]
			run_min = vals[1]
			run_max = vals[2]
		vals = min_max(run_profit/scenario_count, run_min, run_max)
		model_profit += vals[0]
		model_min = vals[1]
		model_max = vals[2]
	model_avg_profit = model_profit/tests_per_model
	stats.append([model_min, model_max, model_avg_profit])

df = pd.DataFrame.from_records(stats, columns=["Minimum Profit", "Maximum Profit", "Average Profit"])

print(df)

print("Averages for this modelset:")
print(df.mean(axis=0))

print("Model with highest minimum profit: model_" + str(df[['Minimum Profit']].idxmax()  + 1))
print("Model with highest maximum profit: model_" + str(df[['Maximum Profit']].idxmax()  + 1))
print("Model with highest average profit: model_" + str(df[['Average Profit']].idxmax()  + 1))

# print the profits stats for each model: min profit, max profit, profit range, avg profit


# print model with:
# highest min_profit, highest max_profit, lowest profit range, highest avg profit