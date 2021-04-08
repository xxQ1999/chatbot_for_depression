import demo
from model import train_model, valid_model
import tensorflow.compat.v1 as tf
from demo import demo

flags = tf.app.flags
flags.DEFINE_string('MODE', 'demo', 
                    'Set program to run in different mode, include train, valid and demo.')
flags.DEFINE_string('checkpoint_dir', './ckpt', 
                    'Path to model file.')
flags.DEFINE_string('train_data', './data/fer2013/fer2013.csv',
                    'Path to training data.')
flags.DEFINE_string('valid_data', './valid_sets/',
                    'Path to training data.')
flags.DEFINE_boolean('show_box', False, 
                    'If true, the results will show detection box')
FLAGS = flags.FLAGS


def face_expression(image_path):
  assert FLAGS.MODE in ('train', 'valid', 'demo')
  
  if FLAGS.MODE == 'demo':
    return demo(FLAGS.checkpoint_dir, FLAGS.show_box, image_path)
  elif FLAGS.MODE == 'train':
    train_model(FLAGS.train_data)
  elif FLAGS.MODE == 'valid':
    valid_model(FLAGS.checkpoint_dir, FLAGS.valid_data)


if __name__ == '__main__':
  print (face_expression("img/悲伤2.jpg"))
