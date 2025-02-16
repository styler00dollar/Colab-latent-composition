import torch, torchvision, os
from utils import proggan, customnet

def proggan_setting(domain):
    # default: 256 resolution, 512 z dimension, resnet 18 encoder
    outdim = 256
    nz = 512
    resnet_depth = 18
    if domain == 'celebahq-small':
        outdim = 128
    if domain == 'celebahq':
        outdim = 1024
    return dict(outdim=outdim, nz=nz, resnet_depth=resnet_depth)

def load_proggan(domain):
    # Automatically download and cache progressive GAN model
    # (From Karras, converted from Tensorflow to Pytorch.)

    if os.path.isfile('pretrained_models/pgans/%s/generator.pth' % domain):
        # these are pgans we trained ourselves
        sd = torch.load('pretrained_models/pgans/%s/generator.pth' % domain)
    else:
        weights_filename = dict(
            bedroom='proggan_bedroom-d8a89ff1.pth',
            church='proggan_churchoutdoor-7e701dd5.pth',
            conferenceroom='proggan_conferenceroom-21e85882.pth',
            diningroom='proggan_diningroom-3aa0ab80.pth',
            kitchen='proggan_kitchen-67f1e16c.pth',
            livingroom='proggan_livingroom-5ef336dd.pth',
            restaurant='proggan_restaurant-b8578299.pth',
            celebahq='proggan_celebhq-620d161c.pth')[domain]
        # Posted here.
        url = 'http://gandissect.csail.mit.edu/models/' + weights_filename
        try:
            sd = torch.hub.load_state_dict_from_url(url) # pytorch 1.1
        except:
            sd = torch.hub.model_zoo.load_url(url) # pytorch 1.0
    model = proggan.from_state_dict(sd)
    model = model.eval()
    return model


def load_proggan_encoder(domain, nz=512, outdim=256, use_RGBM=True, use_VAE=False,
                         resnet_depth=18, ckpt_path=None):
    assert not(use_RGBM and use_VAE),'specify one of use_RGBM, use_VAE'
    if use_VAE:
        nz = nz*2
    channels_in = 4 if use_RGBM or use_VAE else 3
    print(f"Using halfsize?: {outdim<150}")
    print(f"Input channels: {channels_in}")
    netE = customnet.CustomResNet(size=18, num_classes=nz,
                                  halfsize=outdim<150,
                                  modify_sequence=customnet.modify_layers,
                                  channels_in=channels_in)
    if ckpt_path is None:
        if use_RGBM:
            suffix = 'RGBM'
        elif use_VAE:
            suffix = 'VAE'
        else:
            suffix = 'RGB'
        ckpt_path = f'pretrained_models/pgan_encoders/{domain}_{suffix}/model_final.pth'
        print(f"Using default checkpoint path: {ckpt_path}")
    ckpt = torch.load(ckpt_path)
    netE.load_state_dict(ckpt['state_dict'])
    netE = netE.eval()
    return netE

