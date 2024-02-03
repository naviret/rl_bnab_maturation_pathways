import numpy as np
from agent import Agent

if __name__ == '__main__':
    
    # Generate environment
    env = None

    # Create Agent
    agent = Agent(input_dims=env.observation_space.shape,
                  num_actions=env.action_space.shape[0])
    
    # Define number of episodes
    episodes = 250
    
    # Track scores
    best_score = env.min_score()
    score_history = list()
    
    # Train or load checkpoint model
    load_checkpoint = False

    # Load models
    if load_checkpoint:
        agent.load_models()
        ##### [FUTURE DEV] ##### env.render() --> some UI for human
    
    # Play all episodes
    for e in range(episodes):

        # Extract starting state (environment dependent)
        observation = env.reset() 
        
        # Ends episode, starts as False
        done = False

        # Initial score
        score = 0

        # Play one episode
        while not done:
            
            # Extract some action and play that action
            action = agent.choose_action(observation=observation)
            next_observation, reward, done, _ = env.step(action=action)
            
            # Keep reward
            score += reward

            # Store MDP variables 
            agent.remember(state=observation, action=action, reward=reward, 
                           new_state=next_observation, done=done)
    
            # Train neural networks
            if not load_checkpoint:
                learning = agent.learn()
            
            # Transition to next state
            observation = next_observation
        
        # Keep track of scores
        score_history.append(score)
        avg_score = np.mean(score_history[-100])

        if avg_score > best_score:
            best_score = avg_score

            # Save model after episode
            if not load_checkpoint:
                agent.save_models()


        print(f"Episode {e}: Score {score:.2f} | Average score {avg_score:.2f}")


        
    

    #