from simple_dqn_keras import Agent
from Neat import Neat
import numpy as np
from Shooter import Game
import pygame

def player_1_inout():
    keys = pygame.key.get_pressed()
    Forward = 0
    Side = 0
    rotate = 0
    fire = 0
    for key in keys:
        if keys[pygame.K_w]:
            Forward = 1
        elif keys[pygame.K_s]:
            Forward = -1
        if keys[pygame.K_d]:
            rotate = 1
        elif keys[pygame.K_a]:
            rotate = -1
        if keys[pygame.K_q]:
            Side = -1
        elif keys[pygame.K_e]:
            Side = 1
        if keys[pygame.K_z]:
            fire = 1
    return Forward, rotate, Side, fire


def player_2_inout():
    keys = pygame.key.get_pressed()
    Forward = 0
    Side = 0
    rotate = 0
    fire = 0
    for key in keys:
        if keys[pygame.K_t]:
            Forward = 1
        elif keys[pygame.K_g]:
            Forward = -1
        if keys[pygame.K_h]:
            rotate = 1
        elif keys[pygame.K_f]:
            rotate = -1
        if keys[pygame.K_r]:
            Side = -1
        elif keys[pygame.K_y]:
            Side = 1
        if keys[pygame.K_b]:
            fire = 1
    return Forward, rotate, Side, fire

def convert(action):
    forward = 0
    side = 0
    rotate = 0
    fire = 0
    if action == 0:
        pass
    elif action == 1:
        forward = 1
    elif action == 2:
        forward = -1
    elif action == 3:
        side = 1
    elif action == 4:
        side = -1
    elif action == 5:
        rotate = 1
    elif action == 6:
        rotate = -1
    elif action == 7:
        fire = 1

    elif action == 8:
        forward = 1
        fire = 1
    elif action == 9:
        forward = -1
        fire = 1
    elif action == 10:
        side = 1
        fire = 1
    elif action == 11:
        side = -1
        fire = 1
    elif action == 12:
        rotate = 1
        fire = 1
    elif action == 13:
        rotate = -1
        fire = 1

    elif action == 14:
        forward = 1
        rotate = 1
    elif action == 15:
        forward = -1
        rotate = 1
    elif action == 16:
        side = 1
        rotate = 1
    elif action == 17:
        side = -1
        rotate = 1

    elif action == 18:
        forward = 1
        rotate = -1
    elif action == 19:
        forward = -1
        rotate = -1
    elif action == 20:
        side = 1
        rotate = -1
    elif action == 21:
        side = -1
        rotate = -1
    return [forward, side, rotate, fire]




if __name__ == '__main__':
    env = Game()
    env.create()
    fps = 30
    clock = pygame.time.Clock()

    '''
    while True:
        forward_1, rotate_1, side_1, fire_1 = player_1_inout()
        forward_2, rotate_2, side_2, fire_2 = player_2_inout()
        env.step_player_1([forward_1, side_1, rotate_1, fire_1])
        env.step_player_2([forward_2, side_2, rotate_2, fire_2])
        observation_Q_, reward_Q, observation_N, reward_N, done = env.step()
        env.render()   
        clock.tick(fps)
        if done == True:
            env.reset()
    '''

    n_generations = 1000
    Neat_population = 70
    max_game_length = 5000  # steps

    # to be changed, inputs
    agent = Agent(gamma=0.99, epsilon=1.0, alpha=0.0005, input_dims=17,
                  n_actions=22, mem_size=1000000, batch_size=64, epsilon_end=0.01)
    agent_eval = Agent(gamma=0.99, epsilon=0, alpha=0.0005, input_dims=17,
                  n_actions=22, mem_size=1000000, batch_size=64, epsilon_end=0.01)

    neat = Neat(population_size=Neat_population, generations_to_extinct=10, c1=1, c2=1, c3=0.4, delta_species=0.4, input_size=17,
                output_size=4)
    neat.initial_population()
    scores_Q = []
    eps_history = []
    last_score = 0
    
    for i in range(n_generations):
        for j in range(1, Neat_population):
            moves = 0
            done = False
            score_Q = 0
            score_N = 0
            DQ = 70
            observation_Q, observation_N = env.reset()
            if j == 2:
                agent_eval.load_model()

            while not done:

                if j < DQ:
                    action_Q_ = agent.choose_action(np.array(observation_Q))
                else:
                    action_Q_ = agent_eval.choose_action(np.array(observation_Q))

                action_Q = convert(action_Q_)
                env.step_player_1(action_Q)
                action_N = neat.evaluate(network_nr=j, net_input=observation_N, recursion=3)
                fire_N = 0
                if action_N[3] > 0.6:
                    fire_N = 1

                env.step_player_2([action_N[0]*2-1, action_N[1]*2-1, action_N[2]*2-1, fire_N])

                observation_Q_, reward_Q, observation_N, reward_N, done = env.step()

                score_N += reward_N
                score_Q += reward_Q
                moves += 1
                if moves > max_game_length:
                    done = True
                    reward = 0

                if j < DQ:
                    agent.remember(np.array(observation_Q), action_Q_, reward_Q, np.array(observation_Q_), done)
                    observation_Q = observation_Q_
                    agent.learn()

                env.render()

            neat.update_fitness(j, score_N)

            if j == 1:
                eps_history.append(agent.epsilon)
                scores_Q.append(score_Q)
                avg_score = np.mean(scores_Q[max(0, i-100):(i+1)])
                print('episode ', i, 'score %.2f' % score_Q, 'average score %.2f' % avg_score)
                agent.save_model()

        neat.train(0.2, 0.26, 0.5)
        print('gen',i,'fitness', neat.species_fitness)
