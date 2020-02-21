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

# this main tests for compotence of model based on good testing data
# over a period of one year for 7 different scenarios, returns the
# average profit per scenario after the 7 scenarios, as well as the
# average profit per day after the 7 scenarios.

# The algorithms require a vectorized environment to run
p_sum = 0
model_timesteps = 2000000 #14000000
test_days = 260 #365 accounting for weekends
scenario_count = 7
ovr_prof = 0
# env = make_vec_env('Stocks-v0', n_envs=16)
# #https://stable-baselines.readthedocs.io/en/master/_modules/stable_baselines/ppo2/ppo2.html
# # default hyperparams: n_steps, gamma, ent_coef, learning_rate, vf_coef, max_grad_norm, lam, nminibatches(mult of n_envs), cliprange, etc.
# # need to add hyperparams: viewable previous data
# #setup server where i can push configs, every time this loops it pulls the next config in the queue
# #every time it finishes it pushes various data such as reward_variance, reward_slope, avg_reward, final_reward, etc. from that run
# 	#build a nn to optimize hyper params
# model = PPO2(MlpPolicy, env, verbose=1, n_cpu_tf_sess=16, gamma=0.9997, learning_rate=2.0e-4)
# model.learn(total_timesteps=model_timesteps)
# model.save('SavedModels/testing_model')

model = PPO2.load('SavedModels/model_5')

env = gym.make('Stocks-Testing-v0')
obs = env._next_observation()

for j in range(scenario_count):
	if j != 0:
		obs = env.reset()
	cum_profit = 0
	arr_vals_run = []

	for i in range(test_days):
	  # inp = input("Enter an action: ")
	  action, _states = model.predict(obs)
	  obs, rewards, done, info = env.step(action)
	  arr_vals_run.append(env.get_profit())
	  # print(env.action_space.low)
	  # print(env.action_space.high)
	  # print(env.action_space.sample())
	  # print(rewards)

	  # env.render()
	  # print("Reward: %g" % rewards)
	  # print("----------")

	  if i == test_days - 1: # if reaches end, add cumulative profit
	  	cum_profit += env.get_profit()
	  else: # if it is not at the end
	    if done: # if it goes bankrupt midway, add cumulative profit and move on to next scenario
	  	  cum_profit += env.get_profit()
	  	  # obs = env.reset()
	  	  break
	  	  # print("--------------Env Reset------------")
	# add cumulative profit of this run to overrall profit of all runs
	ovr_prof += cum_profit
	# add avg profit to overall average profit per day sum
	p_sum += cum_profit/test_days
	#cumulative profit for this run
	print('total profit after ' + str(test_days) + ' days for scenario ' + str(j + 1) + ': $' + str(cum_profit))
	plt.plot(arr_vals_run, label="scenario " + str(j + 1))

# average overall profit after 260 days of trading for this model
print(ovr_prof/scenario_count)
# average profit per day for this model
print(p_sum/scenario_count)

# plt.plot(arr_vals)
plt.legend()
plt.show()