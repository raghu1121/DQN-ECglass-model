#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import ray

from ray.rllib.agents.registry import get_agent_class
from ray.rllib.utils import try_import_tf

tf = try_import_tf()

ray.init(num_cpus=6)


def train_and_export( num_steps, model_dir, ckpt_dir, prefix):
    config = {
        "num_workers": 0
    }
    cls = get_agent_class('DQN')
    alg = cls(env='ECglass-v2', config=config)
    alg.restore('/home/raghu/Documents/ray/python/ray/rllib/examples/serving/checkpoint_93/checkpoint-93')
    for _ in range(num_steps):
        alg.train()

    # Export tensorflow checkpoint for fine-tuning
    alg.export_policy_checkpoint(ckpt_dir, filename_prefix=prefix)
    # Export tensorflow SavedModel for online serving
    alg.export_policy_model(model_dir)


def restore_saved_model(export_dir):
    signature_key = \
        tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
    g = tf.Graph()
    with g.as_default():
        with tf.Session(graph=g) as sess:
            meta_graph_def = \
                tf.saved_model.load(sess,
                                    [tf.saved_model.tag_constants.SERVING],
                                    export_dir)
            print("Model restored!")
            print("Signature Def Information:")
            print(meta_graph_def.signature_def[signature_key])
            print("You can inspect the model using TensorFlow SavedModel CLI.")
            print("https://www.tensorflow.org/guide/saved_model")


def restore_checkpoint(export_dir, prefix):
    sess = tf.Session()
    meta_file = "%s.meta" % prefix
    saver = tf.train.import_meta_graph(os.path.join(export_dir, meta_file))
    saver.restore(sess, os.path.join(export_dir, prefix))
    print("Checkpoint restored!")
    print("Variables Information:")
    for v in tf.trainable_variables():
        value = sess.run(v)
        print(v.name, value)


if __name__ == "__main__":
    algo = "DQN"
    model_dir = "/media/raghu/6A3A-B7CD/ray_results/policy_model/model_export_dir1/2/"
    ckpt_dir = "/media/raghu/6A3A-B7CD/ray_results/policy_model/ckpt_export_dir1/"
    prefix = "model1.ckpt"
    num_steps = 3
    train_and_export( num_steps,model_dir, ckpt_dir, prefix)
    restore_saved_model(model_dir)
    restore_checkpoint(ckpt_dir, prefix)
