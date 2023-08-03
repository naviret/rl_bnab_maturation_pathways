import os
import torch 
import torch.nn.functional as F
import torch.nn as nn
import torch.optim as optim
from torch.distributions.normal import Normal

class ActorNetwork(nn.Module):
    def __init__(self, alpha, input_dims, max_action, fc1_dims = 256,
                 fc2_dims=256, num_actions=2, name="actor", checkpoint_dir="checkpoint") -> None:

        # I don't understand why there's num_actions, why do you output two actions 
        # [ANSWER] think of robot example with two motors and each eaction is how you move that motor

        super(ActorNetwork).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.num_actions = num_actions
        self.name = name
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_file = os.path.join(self.checkpoint_dir, name + "_sac")
        self.max_action = max_action
        self.reparam_noise = 1e-6

        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.mu = nn.Linear(self.fc2_dims, self.num_actions)
        self.sigma = nn.Linear(self.fc2_dims, self.num_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=alpha)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        self.to(self.device)

    def forward(self, state):
        prob = self.fc1(state)
        prob = F.relu(prob)
        prob = self.fc2(prob)
        prob = F.relu(prob)

        mu = self.mum(prob)
        sigma = self.sigma(prob)

        ####### make a distribution that isn't arbitrarily large
        sigma = torch.clamp(sigma, min=self.reparam_noise, max = 1)

        return mu, sigma
    
    def sample_normal(self, state, reparametrize=True):
        mu, sigma = self.forward(state)
        probabilites = Normal(mu, sigma)

        if reparametrize:
            unbounded_action = probabilites.rsample()
        else:
            unbounded_action = probabilites .sample()

        bounded_action = torch.tanh(unbounded_action) * torch.tensor(self.max_action).to(self.device)
        # for continous action space, the action is defined by a single scalar
        # using the max_action makes it so that the action is in the range of the action
        # space. note that the tanh is used to bound the sample from -1 to 1
        
        # used for calculating the loss function 
        log_probs = probabilites.log_prob(unbounded_action)
        log_probs -= torch.log(1 - bounded_action.pow(2) + self.reparam_noise)

        # scalar quantity for loss calculation
        log_probs = log_probs.sum(1, keepdim=True)

        return bounded_action, log_probs

    def save_checkpoint(self):
        torch.save(self.state_dict(), self.checkpoint_file)
    
    def load_checkpoint(self):
        self.load_state_dict(torch.load(self.checkpoint_file))