import numpy as np

class ReplayBuffer():
    
    def __init__(self, max_size, input_shape, num_actions) -> None:
        
        self.memory_size = max_size
        
        # keeps track of position of first available memory
        self.memory_counter = 0 
        
        self.state_memory = np.zeros((self.memory_size, *input_shape))
        self.next_state_memory = np.zeros((self.memory_size, *input_shape))
        self.action_memory = np.zeros(self.memory_size, num_actions)
        self.reward_memory = np.zeros(self.memory_size)
        self.terminal_memory = np.zeros(self.memory_size, dtype=np.bool)


        ### currently storing in np.zeros but that might not be feasible since 

    def store_transition(self, state, action, reward, next_state, done):

        index = self.memory_counter

        self.state_memory[index] = state
        self.next_state_memory[index] = next_state
        self.action_memory[index] = action
        self.reward_memory[index] = reward
        self.terminal_memory[index] = done

        self.memory_counter += 1

        ####### Need to check if memory is full, then restart counter and rewrite 

    
    def sample_buffer(self, batch_size):
        
        ###### memory_counter is the current idx, memory_size is the max idx
        max_memory = min(self.memory_counter, self.memory_size)

        batch = np.random.choice(max_memory, batch_size)
        np.random.choice(max_memory, size=batch_size)

        states = self.state_memory[batch]
        next_states = self.next_state_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        dones = self.terminal_memory[batch]