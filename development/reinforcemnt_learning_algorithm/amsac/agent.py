import os
import sys
import torch as torch
import torch.nn.functional as F
import numpy as np
from buffer import ReplayBuffer
from actor import ActorNetwork
from critic import CriticNetwork
from value import ValueNetwork

class Agent():
    def __init__(self, alpha=0.0003, beta=0.0003, input_dims=[8],
                    env=None, gamma=0.99, num_actions=2, max_size=1000000, tau=0.005,
                    layer1_size=256, layer2_size=256, batch_size=256, reward_scale=2) -> None:
        
        # alpha: learning rate for actor
        # beta: learning rate for critic
        # gamma: 
        # tau: modulate parameters of target_value network --> soft copy 
        # reward_scale:

        self.gamma = gamma
        self.tau = tau
        self.memory = ReplayBuffer(max_size=max_size, input_shape=input_dims, num_actions=num_actions)

        self.batch_size = batch_size
        self.num_actions = num_actions

        self.actor = ActorNetwork(alpha, input_dims, num_actions=num_actions, max_action=env.action_space.high)
        self.critic_1 = CriticNetwork(beta, input_dims, num_actions=num_actions, name="critic_1")
        self.critic_2 = CriticNetwork(beta, input_dims, num_actions=num_actions, name="critic_2")
        self.value = ValueNetwork(beta, input_dims, name="value")
        self.target_value = ValueNetwork(beta, input_dims, name="target_value")

        self.scale = reward_scale
        self.update_network_paramaters(tau=1) 
        # set parameters of value network exactly (tau = 1) equal to parameters of target value network
        # tau < 1 is a soft update 
        
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


    def choose_action(self, observation):
        state = torch.tensor([observation]).to(self.device)
        actions, _ = self.actor.sample_normal(state, reparametrize=False)
        ### no reparam since no training is happening here

        return actions.cpu().detach().numpy()[0]
    

    def remember(self, state, action, reward, new_state, done):
        self.memory.store_transition(state, action, reward, new_state, done)


    def update_network_parameters(self, tau):
        
        target_value_params = self.target_value.named_parameters()
        value_params = self.value.named_parameters()

        target_value_state_dict = dict(target_value_params)
        value_state_dict = dict(value_params)

        for name in value_state_dict:
            value_state_dict[name] = tau*value_state_dict[name].clone() + \
                                 (1 - tau)*target_value_state_dict[name].clone()
                            ## soft update occurs here to get value network
                            ## kind of equal to targe value network


    def save_models(self):
        print(".........saving models........." + "\n")
        self.actor.save_checkpoint()
        self.value.save_checkpoint()
        self.target_value.save_checkpoint()
        self.critic_1.save_checkpoint()
        self.critic_2.save_checkpoint()


    def load_models(self):
        print(".........saving models........." + "\n")
        self.actor.load_checkpoint()
        self.value.load_checkpoint()
        self.target_value.load_checkpoint()
        self.critic_1.load_checkpoint()
        self.critic_2.load_checkpoint()


    def learn(self):
        ####### make a get memory counter method
        if self.memory.memory_counter < self.batch_size:
            return ####### only learn when batch_size is filled up
        
        state, action, reward, next_state, done = self.memory.sample_buffer(self.batch_size)
        
        state = torch.tensor(state, dtype=torch.float).to(self.device)
        action = torch.tensor(action, dtype=torch.float).to(self.device)
        reward = torch.tensor(reward, dtype=torch.float).to(self.device)
        next_state = torch.tensor(next_state, dtype=torch.float).to(self.device)
        done = torch.tensor(done).to(self.device)

        value = self.value(state).view(-1) #### creates a tensor of tensors when converting to numpy array
        next_value = self.target_value(next_state).view(-1) #### that wouldn't make sense for a scalar
        next_value[done] = 0.0 ### terminal states have a value of 0


        ### TRAIN VALUE NETWORK
        ### actions and log_prob according to the new policy ie why we do sample_normal
        #### to calculate loss of value and actor networks you want loss according to new policy
        action, log_probs = self.actor.sample_normal(state, reparametrize=False)
        log_probs = log_probs.view(-1)

        #### q values from each critic under new policy (ie new action)
        q1_new_policy = self.critic_1.forward(state, action)
        q2_new_policy = self.critic_2.forward(state, action)
        critic_value = torch.min(q1_new_policy, q2_new_policy) # taking minimum to 
                                                               # to reduce over-estimation bias
                                                               # ie takes worse q value

        critic_value = critic_value.view(-1)

        self.value.optimizer.zero_grad()
        value_target = critic_value - log_probs
        value_loss = 0.5 * F.mse_loss(value, value_target)
        
        value_loss.backward(retain_graph=True)
        self.value.optimizer.step()

        #### TRAIN ACTOR NETWORK
        ### have to reparametrize since loss will be propagated back on the actor network 
        action, log_probs = self.actor.sample_normal(state, reparametrize=True)
        log_probs = log_probs.view(-1)

        ####### REPEATING CODE, MAKE A FUNCTION ###############
        #### q values from each critic under new policy (ie new action)
        q1_new_policy = self.critic_1.forward(state, action)
        q2_new_policy = self.critic_2.forward(state, action)
        critic_value = torch.min(q1_new_policy, q2_new_policy) 
        critic_value = critic_value.view(-1)

        actor_loss = log_probs - critic_value
        actor_loss = torch.mean(actor_loss) ### across the different types of action within the same action
        self.actor.optimizer.zero_grad() ### reset gradient
        actor_loss.backward(retain_graph=True)
        self.actor.optimizer.step()

        #### TRAIN CRITIC NETWORK
        self.critic_1.optimizer.zero_grad()
        self.critic_2.optimizer.zero_grad()
        q_hat = self.scale * reward + self.gamma * next_value
        #### self.scale includes entropy, 
        # gamma times the value of the state resulting from the action means less reward as more
        # actions are taken (for gamma less than 1)
        q1_old_policy = self.critic_1.forward(state, action).view(-1)
        q2_old_policy = self.critic_1.forward(state, action).view(-1)
        critic_1_loss = 0.5 * F.mse_loss(q1_old_policy, q_hat)
        critic_2_loss = 0.5 * F.mse_loss(q2_old_policy, q_hat)

        critic_loss = critic_1_loss + critic_2_loss
        critic_loss.backward()
        self.critic_1.optimizer.step()
        self.critic_2.optimizer.step()

        self.update_network_parameters(tau=self.tau)
