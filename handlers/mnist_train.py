import os
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from handlers import mnist_cnn as mnist_interence
import numpy as np
BATCH_SIZE = 100
#学习率
LEARNING_RATE_BASE = 0.8
#学习指数衰减率
LEARNING_RATE_DECAY = 0.99
#损失函数正则化系数
REGULARIZATION_TATE = 0.0001
#滑动平均系数
MOVING_AVERAGE_DECAY = 0.99
#迭代次数
TRAIN_STEP = 300000
#模型路径
MODEL_PATH = 'model'
#模型名称
MODEL_NAME = 'model'

def train(mnist):
    #定义用于输入图片数据的张量占位符，输入样本的尺寸
    x = tf.placeholder(tf.float32, shape=[None,
                                          mnist_interence.IMAGE_SIZE,
                                          mnist_interence.IMAGE_SIZE,
                                          mnist_interence.NUM_CHANNEL], name='x-input')
    #定义用于输入图片标签数据的张量占位符，输入样本的尺寸
    y_ = tf.placeholder(tf.float32, shape=[None, mnist_interence.OUTPUT_NODE], name='y-input')
    #定义采用方差的正则化函数
    regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_TATE)
    #通过interence函数获得计算结果张量
    y = mnist_interence.interence(x,True,regularizer)
    global_step = tf.Variable(0, trainable=False)
    #定义平均滑动
    variable_average = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    #对所有可以训练的变量采用平均滑动
    variable_average_ops = variable_average.apply(tf.trainable_variables())
    #对预测数据y和实际数据y_计算他们概率的交叉值
    cross_entroy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=tf.argmax(y_, 1))
    #对各对交叉值求平均，其实是计算y和y_两个随机变量概率分布的交叉熵，交叉熵值越小则表明两种概率分布越接近
    cross_entroy_mean = tf.reduce_mean(cross_entroy)
    #采用交叉熵和正则化参数作为最后的损失函数
    loss = cross_entroy_mean + tf.add_n(tf.get_collection('loss'))
    #设置学习率递减方式
    learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE, global_step,
                                               mnist.train.num_examples / BATCH_SIZE, LEARNING_RATE_DECAY)
    #采用梯度下降的方式计算损失函数的最小值
    train_step = tf.train.GradientDescentOptimizer(0.01).minimize(loss, global_step=global_step)
    #定义学习操作：采用梯度下降求一次模型训练参数，并对求得的模型参数计算滑动平均值
    train_op = tf.group(train_step, variable_average_ops)
    saver = tf.train.Saver()
    number = getNumber() #初始化number为最后一次写入number.txt的i值，以防循环从0再次开始
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        ckpt = tf.train.get_checkpoint_state(MODEL_PATH)  # 获取checkpoints对象
        if ckpt and ckpt.model_checkpoint_path:  ##判断ckpt是否为空，若不为空，才进行模型的加载，否则从头开始训练
            saver.restore(sess, ckpt.model_checkpoint_path)  # 恢复保存的神经网络结构，实现断点续训
        for i in range(number,TRAIN_STEP+1):
            # 由于神经网络的输入大小为[BATCH_SIZE,IMAGE_SIZE,IMAGE_SIZE,CHANNEL]，因此需要reshape输入。
            xs,ys = mnist.train.next_batch(BATCH_SIZE)
            reshape_xs = np.reshape(xs,(BATCH_SIZE, mnist_interence.IMAGE_SIZE,
                                        mnist_interence.IMAGE_SIZE,
                                        mnist_interence.NUM_CHANNEL))
            #通过计算图，计算模型损失张量和学习张量的当前值
            _,loss_value,step,learn_rate = sess.run([train_op,loss,global_step,learning_rate],feed_dict={x:reshape_xs,y_:ys})
            if i % 100 == 0:
                print('After %d step, loss on train is %g,and learn rate is %g'%(step,loss_value,learn_rate))
                with open('../docs/number.txt', 'w') as f:  # 打开test.txt   如果文件不存在，创建该文件。
                    number = str(i)
                    f.write(number)  # 把变量i写入number.txt。这里number必须是str格式，如果不是，则可以转一下。
                saver.save(sess,os.path.join(MODEL_PATH,MODEL_NAME),global_step=global_step)

def getNumber():
    '''
    从number.txt得到最后一次写入的i值
    :return: number
    '''
    with open('../docs/number.txt', 'r') as up:
        lineLst = up.readlines()
        lastNumber = lineLst[len(lineLst) - 1]
        up.close()
    number = int(lastNumber)
    return number

if __name__ == '__main__':
    mnist = input_data.read_data_sets('./mni_data', one_hot=True)
    #ys = mnist.validation.labels
    #print(ys)
    train(mnist)
