import keras.backend as K
import tensorflow as tf
from keras.layers import Dense, Input, merge
from keras.models import Model
from keras.optimizers import Adam

HIDDEN1_UNITS = 300
HIDDEN2_UNITS = 600


class CriticNetwork(object):
    """
    Create two network to predict the value (gradually changing to represent the long-term reward)
    from the a series of actions and states.
    """
    def __init__(self, sess, state_size, action_size, batch_size, tau, learning_rate):
        self.sess = sess
        self.BATCH_SIZE = batch_size
        self.TAU = tau
        self.LEARNING_RATE = learning_rate
        self.action_size = action_size

        K.set_session(sess)

        # Now create the model
        self.model, self.action, self.state = self.create_critic_network(state_size, action_size)
        self.target_model, self.target_action, self.target_state = self.create_critic_network(state_size, action_size)
        self.action_grads = tf.gradients(self.model.output, self.action)  # GRADIENTS for policy update
        self.sess.run(tf.initialize_all_variables())

    def gradients(self, states, actions):
        """
        :param states
        :param actions
        :return: gradient in terms of actions
        """
        return self.sess.run(self.action_grads, feed_dict={
            self.state: states,
            self.action: actions
        })[0]

    def target_train(self):
        """
        Renew the target network (slowly converge, represent the long-term target)
        """
        critic_weights = self.model.get_weights()
        critic_target_weights = self.target_model.get_weights()
        for i in xrange(len(critic_weights)):
            critic_target_weights[i] = self.TAU * critic_weights[i] + (1 - self.TAU) * critic_target_weights[i]
        self.target_model.set_weights(critic_target_weights)

    def create_critic_network(self, state_size, action_dim):
        """
        Critic network, map the state and the action to the current value.
        :param state_size: shape of the state space vector
        :param action_dim: shape of the action space vector
        :return: target value.
        """
        print("Now we build the critic model")
        S = Input(shape=[state_size])
        A = Input(shape=[action_dim], name='action2')
        w1 = Dense(HIDDEN1_UNITS, activation='relu')(S)
        h1 = Dense(HIDDEN2_UNITS, activation='linear')(w1)
        a1 = Dense(HIDDEN2_UNITS, activation='linear')(A)
        h2 = merge([h1, a1], mode='sum')
        h3 = Dense(HIDDEN2_UNITS, activation='relu')(h2)
        V = Dense(action_dim, activation='linear')(h3)
        model = Model(input=[S, A], output=V)
        adam = Adam(lr=self.LEARNING_RATE)
        model.compile(loss='mse', optimizer=adam)
        return model, A, S
