import json
import numpy as np
import tensorflow as tf
from ActorNetwork import ActorNetwork
from CriticNetwork import CriticNetwork
from OU import OU
from ReplayBuffer import ReplayBuffer
from gym_torcs import TorcsEnv
import time
import os
import math
from PrioritizedReplayBuffer import PrioritizedReplayBuff

OU = OU()  # Ornstein-Uhlenbeck Process

BUFFER_SIZE = math.pow(2, 17)
BATCH_SIZE = 32
GAMMA = 0.99
TAU = 0.001  # Target Network HyperParameters
LRA = 0.0001  # Learning rate for Actor
LRC = 0.001  # Lerning rate for Critic
EXPLORE = 100000.


def play_game(train_indicator=1, usePrioReplayBuff=False):
    """
    :param train_indicator: 1 means Train, 0 means simply Run
    :param usePrioReplayBuff: 1 means use prioritized replay buffer, 0 means use normal replay buffer
    :return:
    """
    action_dim = 3  # Steering/Acceleration/Brake
    state_dim = 29  # of sensors input

    np.random.seed(1337)

    vision = False

    episode_count = 2000
    max_steps = 100000
    step = 0
    epsilon = 1

    # Tensorflow GPU optimization
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    from keras import backend as K
    K.set_session(sess)

    actor = ActorNetwork(sess, state_dim, action_dim, BATCH_SIZE, TAU, LRA)
    critic = CriticNetwork(sess, state_dim, action_dim, BATCH_SIZE, TAU, LRC)
    if not usePrioReplayBuff:
        buff = ReplayBuffer(BUFFER_SIZE)  # Create replay buffer
    else:
        buff = PrioritizedReplayBuff(BUFFER_SIZE)  # Create prioritized replay buffer

    # Generate a Torcs environment
    env = TorcsEnv(vision=vision, throttle=True, gear_change=False)

    # csv file to record the average reward of every episode
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    dir_name = 'avg_rwd_data'
    filename = 'avg_reward_episode_' + time_str + '.csv'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    filename = os.path.join(dir_name, filename)
    with open(filename, mode='w') as csv_file:
        # Now load the weight
        print("Now we load the weight")
        try:
            actor.model.load_weights("actormodel.h5")
            critic.model.load_weights("criticmodel.h5")
            actor.target_model.load_weights("actormodel.h5")
            critic.target_model.load_weights("criticmodel.h5")
            print("Weight load successfully")
        except:
            print("Cannot find the weight")

        print("TORCS Experiment Start...")
        for i in range(episode_count):

            print("Episode : " + str(i) + " Replay Buffer " + str(buff.count()))

            if np.mod(i, 3) == 0:
                ob = env.reset(relaunch=True)  # relaunch TORCS every 3 episode because of the memory leak error
            else:
                ob = env.reset()
            s_t = np.hstack((ob.angle, ob.track, ob.trackPos, ob.speedX, ob.speedY, ob.speedZ,
                             ob.wheelSpinVel / 100.0, ob.rpm))

            total_reward = 0.
            for j in range(max_steps):
                loss = 0
                epsilon -= 1.0 / EXPLORE
                a_t = np.zeros([1, action_dim])
                noise_t = np.zeros([1, action_dim])

                a_t_original = actor.model.predict(s_t.reshape(1, s_t.shape[0]))
                # shape: [s_t.shape[0]] --> [[s_t.shape[0]]
                noise_t[0][0] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][0], 0.0, 0.60, 0.30)
                noise_t[0][1] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][1], 0.5, 1.00, 0.10)
                noise_t[0][2] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][2], -0.1, 1.00, 0.05)

                # The following code do the stochastic brake
                # if random.random() <= 0.1:
                #    print("********Now we apply the brake***********")
                #    noise_t[0][2] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][2],  0.2 , 1.00, 0.10)

                a_t[0][0] = a_t_original[0][0] + noise_t[0][0]
                a_t[0][1] = a_t_original[0][1] + noise_t[0][1]
                a_t[0][2] = a_t_original[0][2] + noise_t[0][2]

                ob, r_t, done, info = env.step(a_t[0])
                s_t1 = np.hstack((ob.angle, ob.track, ob.trackPos, ob.speedX, ob.speedY, ob.speedZ,
                                  ob.wheelSpinVel / 100.0, ob.rpm))

                batch_index = []
                if usePrioReplayBuff:
                    # Add transition to replay buffer: (state_t, action_t, reward_t, state_t+1, end_or_not)
                    transition = np.hstack(s_t, a_t[0], r_t, s_t1, done)
                    buff.store(transition)

                    # Do the batch update
                    batch_index, batch, batch_ISWeight = buff.sample(BATCH_SIZE)

                else:
                    # Add transition to replay buffer: (state_t, action_t, reward_t, state_t+1, end_or_not)
                    buff.add(s_t, a_t[0], r_t, s_t1, done)

                    # Do the batch update
                    batch = buff.getBatch(BATCH_SIZE)

                states = np.asarray([e[0] for e in batch])
                actions = np.asarray([e[1] for e in batch])
                rewards = np.asarray([e[2] for e in batch])
                new_states = np.asarray([e[3] for e in batch])
                dones = np.asarray([e[4] for e in batch])
                y_t = np.asarray([e[1] for e in batch])

                target_q_values_t_plus_one = critic.target_model.predict([new_states, actor.target_model.predict(new_states)])

                for k in range(len(batch)):
                    if dones[k]:
                        y_t[k] = rewards[k]
                    else:
                        y_t[k] = rewards[k] + GAMMA * target_q_values_t_plus_one[k]

                if train_indicator:
                    loss += critic.model.train_on_batch([states, actions], y_t)
                    action_for_grad = actor.model.predict(states)
                    grads = critic.gradients(states, action_for_grad)
                    grads_squared = np.square(grads)
                    if usePrioReplayBuff:
                        target_q_values_t = critic.target_model.predict([states, actions])
                        td_errs_squared = np.square(y_t - target_q_values_t)
                        buff.update(batch_index, td_errs_squared, grads_squared)

                    actor.train(states, grads)
                    actor.target_train()
                    critic.target_train()

                total_reward += r_t
                s_t = s_t1

                print("Episode", i, "Step", step, "Action", a_t, "Reward", r_t, "Loss", loss)
                step += 1
                if done:
                    break

            if np.mod(i, 3) == 0:
                if train_indicator:
                    print("Now we save model")
                    actor.model.save_weights("actormodel.h5", overwrite=True)
                    with open("actormodel.json", "w") as outfile:
                        json.dump(actor.model.to_json(), outfile)

                    critic.model.save_weights("criticmodel.h5", overwrite=True)
                    with open("criticmodel.json", "w") as outfile:
                        json.dump(critic.model.to_json(), outfile)

            print("TOTAL REWARD @ " + str(i) + "-th Episode  : Reward " + str(total_reward))
            csv_file.write(str(total_reward / step))
            csv_file.write(",")
            print("Total Step: " + str(step))
            print("")
        csv_file.close()
        env.end()  # This is for shutting down TORCS
        print("Finish.")


if __name__ == "__main__":
    play_game(usePrioReplayBuff=True)
