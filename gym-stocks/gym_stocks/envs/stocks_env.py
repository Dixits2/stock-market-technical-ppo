import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import pandas as pd
import requests
from io import StringIO

class StocksEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    # constants
    self.STARTING_BALANCE = 10000.0
    self.VISIBLE_PAST_DAYS = 7


    self.balance = self.STARTING_BALANCE
    self.owned_shares = 0
    self.all_data = self.get_new_data()
    self.obs_data = self.all_data.drop(["Open", "Close"], axis=1)
    # last value in range of values
    self.current_pos = self.VISIBLE_PAST_DAYS
    # observations: OCHLV values of last 30 days, owned_shares, and balance
    self.action_space = spaces.Box(low=-1, high=1, shape=(1, ), dtype=np.float32)
    self.observation_space = spaces.Box(low=0, high=np.finfo(np.float32).max, shape=(self.VISIBLE_PAST_DAYS + 1, 3), dtype=np.float32) #OCHLV Values
      # spaces.Box(low=0, high=np.iinfo(np.int16).max, shape=(1, ), dtype=np.int16),  #owned_shares
      # spaces.Box(low=0, high=np.finfo(np.float32).max, shape=(1, ), dtype=np.float32))) #balance
    self.previous_profit = self.get_profit()

  def reset(self):
    self.balance = self.STARTING_BALANCE
    self.owned_shares = 0
    self.all_data = self.get_new_data()
    self.obs_data = self.all_data.drop(["Open", "Close"], axis=1)
    self.current_pos = self.VISIBLE_PAST_DAYS
    self.previous_profit = 0

    return self._next_observation()

  def get_new_data(self):
    return pd.read_csv(StringIO(requests.get(url="http://127.0.0.1:5000/").json()), sep=",").drop(["Date", "OpenInt"], axis=1)

  def get_max_sell(self):
    return self.owned_shares

  def get_max_buy(self):
    max_buy = int(self.balance/self.all_data['Close'][self.current_pos - 1])
    if max_buy < 0:
      return 0
    return max_buy

  def get_net_worth(self):
    return self.balance + (self.owned_shares * self.all_data["Open"][self.current_pos])

  def get_profit(self):
    return (self.balance + (self.owned_shares * self.all_data["Open"][self.current_pos])) - self.STARTING_BALANCE

  def _next_observation(self):
    # Get the data points for the last 30 days
    data = self.obs_data[(self.current_pos - self.VISIBLE_PAST_DAYS):self.current_pos].to_numpy().astype('float32')
    return np.append(data, [[self.balance, self.owned_shares, self.get_max_buy()]], axis=0)

  def is_actionless(self):
    return -self.get_max_sell() == 0 and self.get_max_buy() == 0

  def get_reward(self):
    new_profit = self.get_profit()
    reward = new_profit - self.previous_profit
    self.previous_profit = new_profit
    return reward

  # https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
  def translate(self, value, leftMin, leftMax, rightMin, rightMax):
      # Figure out how 'wide' each range is
      leftSpan = leftMax - leftMin
      rightSpan = rightMax - rightMin

      # Convert the left range into a 0-1 range (float)
      valueScaled = float(value - leftMin) / float(leftSpan)

      # Convert the 0-1 range into a value in the right range.
      return rightMin + (valueScaled * rightSpan)


  def step(self, action):
    # print(action[0])
    # print("~`~`~`~`Market has just Closed~`~`~`~`")
    self.current_pos += 1
    action = int(self.translate(action[0], -1, 1, -self.get_max_sell(), self.get_max_buy()))
    if self.balance >= action * self.all_data["Open"][self.current_pos]:
      self.balance = self.balance - action * self.all_data["Open"][self.current_pos]
      self.owned_shares = self.owned_shares + action

    reward = self.get_reward()
    done = self.current_pos >= len(self.all_data) - 1 or self.is_actionless() or self.balance < 0

    # if self.balance < 0:
    #   print("bal has dropped to less than 0")

    # if self.get_net_worth() <= 0:
    #   print(str(action_space.low) + ", " + str(action_space.high))

    # if self.is_actionless():
    # if action > 0:
    #   print(str(-self.get_max_sell()) + ", " + str(self.get_max_buy()) + "| Action: " + str(action) + "| Shares Owned: " + str(self.owned_shares) + "| Balance: " + str(self.balance) + '| Net Worth: ' + str(self.get_net_worth()))
    # if self.balance < self.all_data['Open'][self.current_pos]:
      # print(self.balance)
      # print(str(self.action_space.low) + ", " + str(self.action_space.high))

    obs = self._next_observation()

    return obs, reward, done, {}

  def render(self, mode='human'):
    print('Step: %d / %d' % (self.current_pos, len(self.all_data)))
    print('Balance: %g' % (self.balance))
    print('Shares held: %d' % (self.owned_shares))
    print('Current Buy Price: %g' % (self.all_data['Open'][self.current_pos]))
    print('Net worth: %g' % self.get_net_worth())
    print('Profit: %g' % self.get_profit())
  
  def close(self):
    a = 0