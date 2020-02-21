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

# this main tests for best profit per day for various paramsets,
# prints the average overall profit after 260 days of trading for 
# this paramset, as well as average profit per day for this paramset

# The algorithms require a vectorized environment to run
p_sum = 0
model_timesteps = 14000000
iterations = 5
test_days = 500 #365 accounting for weekends
ovr_prof = 0
prints = []
for j in range(iterations):
	env = make_vec_env('Stocks-v0', n_envs=32)
	#https://stable-baselines.readthedocs.io/en/master/_modules/stable_baselines/ppo2/ppo2.html
	# default hyperparams: n_steps, gamma, ent_coef, learning_rate, vf_coef, max_grad_norm, lam, nminibatches(mult of n_envs), cliprange, etc.
	# need to add hyperparams: viewable previous data
	#setup server where i can push configs, every time this loops it pulls the next config in the queue
	#every time it finishes it pushes various data such as reward_variance, reward_slope, avg_reward, final_reward, etc. from that run
		#build a nn to optimize hyper params
	model = PPO2(MlpPolicy, env, verbose=1, tensorboard_log="./ppo2_stocks/", n_cpu_tf_sess=32, gamma=0.9997, learning_rate=2.0e-4)
	model.learn(total_timesteps=model_timesteps)
	model.save('SavedModels/model_' + str(j + 1))

	env = gym.make('Stocks-v0')
	obs = env.reset()
	cum_profit = 0
	arr_vals_run = []

	# one set of iterations
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

	  # add profit to cumulative profit after every env reset
	  if i == test_days - 1:
	  	cum_profit += env.get_profit()
	  else:
	    if done:
	  	  cum_profit += env.get_profit()
	  	  obs = env.reset()
	  	  # print("--------------Env Reset------------")
	# add cumulative profit of run to overrall profit of all runs
	ovr_prof += cum_profit
	# add avg profit to overall average profit per day sum
	p_sum += cum_profit/test_days
	#cumulative profit for this run
	prints.append('total profit after '+ str(test_days) + ' days for model ' + str(j + 1) + ': $' + str(cum_profit))
	plt.plot(arr_vals_run, label="model " + str(j + 1))


[print(i) for i in prints]
# average overall profit after 260 days of trading for this paramset
print(ovr_prof/iterations)
# average profit per day for this paramset
print(p_sum/iterations)



plt.legend()
plt.show()







# import os
# import pandas as pd
# import numpy as np
# import requests
# from io import StringIO
# import time
# import gym_stocks

# call sequence:
# step


# import gym
# env = gym.make('Stocks-v0')
# print(env.reset())
# print(len(env.all_data))
# # print(np.finfo(np.float32).max)
# # print(env.all_data[(env.current_pos - env.VISIBLE_PAST_DAYS):env.current_pos])
# # print(env.current_pos)
# # a = time.time()
# # b = env.get_high()
# # c = time.time()
# # d = env.action_space.high
# # e = time.time()
# # f = env.action_space.sample()
# # g = time.time()
# # print(str(b) + " " + str(c - a))
# # print(str(d) + " " + str(e - c))
# # print(str(f) + " " + str(g - e))
# env.close()


# # start = time.time()
# # df = pd.read_csv(StringIO(requests.get('http://127.0.0.1:5000/').json()), sep=",").drop(["OpenInt"], axis=1)
# # end = time.time()

# # print(df)
# # # print(end-start)
# # # print(df.at[0, 'Close'])
# # print(df[0:30].to_numpy())

# # x = 0


# files = [i for i in os.listdir("Stocks") if i.endswith("txt")]

# P_CNT = 7

# total_lines = 0

# for file in files:
# 	content = open('Stocks/' + file)
# 	num_lines = sum(1 for line in content)
# 	total_lines += num_lines - P_CNT

# print(total_lines)
# print(len(files))
# print(total_lines/len(files))



