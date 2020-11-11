class ModelShape:
    class AlexNet:
        FLOW_PATH = ['conv11_96', 'maxpool', 'conv5_256', 'maxpool', 'conv3_384', 'conv5_256', 'maxpool', 'FC_1024',
                     'FC_1024', 'softmax']
        LAYER_NUMS = {
            'conv11_96': 1,
            'conv5_256': 1,
            'conv3_384': 2,
            'FC_1024': 1,
            'maxpool': 1,
            'softmax': 1
        }

    class VGG16:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'conv3_512', 'maxpool', 'FC_4096', 'FC_4096', 'softmax']
        LAYER_NUMS = {
            'conv3_64': 2,
            'conv3_128': 2,
            'conv3_256': 3,
            'conv3_512': 3,
            'maxpool': 1,
            'FC_4096': 1,
            'softmax': 1
        }

    class VGG19:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'conv3_512', 'maxpool', 'FC_4096', 'FC_4096', 'softmax']
        LAYER_NUMS = {
            'conv3_64': 2,
            'conv3_128': 2,
            'conv3_256': 4,
            'conv3_512': 4,
            'maxpool': 1,
            'FC_4096': 1,
            'softmax': 1
        }

    class VGG11:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool',
                     'conv3_512', 'maxpool', 'FC_4096', 'FC_4096', 'softmax']
        LAYER_NUMS = {
            'conv3_64': 1,
            'conv3_128': 1,
            'conv3_256': 2,
            'conv3_512': 2,
            'maxpool': 1,
            'FC_4096': 1,
            'softmax': 1
        }

    class SimpleNet:
        FLOW_PATH = ['conv3_64', 'maxpool', 'conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'FC_1024', 'FC_1024',
                     'softmax']
        LAYER_NUMS = {
            'conv3_64': 1,
            'conv3_128': 1,
            'conv3_256': 1,
            'maxpool': 1,
            'FC_1024': 1,
            'softmax': 1
        }

    class TestNet:
        FLOW_PATH = ['conv3_128', 'maxpool', 'conv3_256', 'maxpool', 'conv3_512', 'maxpool', 'FC_2048', 'FC_2048',
                     'softmax']
        LAYER_NUMS = {
            'conv3_64': 1,
            'conv3_128': 1,
            'conv3_256': 1,
            'conv3_512': 1,
            'maxpool': 1,
            'FC_1024': 1,
            'FC_2048': 1,
            'softmax': 1
        }

