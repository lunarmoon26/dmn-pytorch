import torch
import argparse
import pickle
import pprint
import numpy as np
import os
from dataset import Dataset, Config
from model import DMN
from run import run_epoch
from config import get_default_args
import datetime
from tensorboardX import SummaryWriter

args = get_default_args()

def run_experiment(model, dataset, set_num):
    writer = SummaryWriter('tensorboard')

    best_metric = np.zeros(2)
    early_stop = False
    if model.config.train:
        if model.config.resume:
            model.load_checkpoint()

        for ep in range(model.config.epoch):
            if early_stop:
                break
            print('- Training Epoch %d' % (ep+1))
            tr_met,_ = run_epoch(model, dataset, ep, 'tr', set_num)
            writer.add_scalar('Train/Loss', tr_met[0], ep+1) 
            writer.add_scalar('Train/Accuracy', tr_met[1], ep+1) 
            if model.config.valid:
                print('- Validation')
                val_met,_ = run_epoch(model, dataset, ep, 'va', set_num, False)
                writer.add_scalar('Validation/Loss', val_met[0], ep+1) 
                writer.add_scalar('Validation/Accuracy', val_met[1], ep+1) 
                if best_metric[1] < val_met[1]:
                    best_metric = val_met
                    model.save_checkpoint({
                        'config': model.config,
                        'state_dict': model.state_dict(),
                        'optimizer': model.optimizer.state_dict()})
                    if best_metric[1] == 100:
                        break
                else:
                    # model.decay_lr()
                    if model.config.early_stop:
                        early_stop = True
                        print('\tearly stop applied')
                print('\tbest metrics:\t%s' % ('\t'.join(['{:.2f}'.format(k)
                    for k in best_metric])))

            if model.config.test:
                print('- Testing')
                test_met,_ = run_epoch(model, dataset, ep, 'te', set_num, False)
                writer.add_scalar('Test/Loss', test_met[0], ep+1) 
                writer.add_scalar('Test/Accuracy', test_met[1], ep+1) 
            print()
    
    if model.config.test:
        print('- Load Validation/Testing')
        if model.config.resume or model.config.train:
            model.load_checkpoint()
        run_epoch(model, dataset, 0, 'va', set_num, False)
        run_epoch(model, dataset, 0, 'te', set_num, False)
        print()

    return best_metric


def main():
    if not os.path.exists('./results'):
        os.makedirs('./results')

    print('### load dataset')
    dataset = pickle.load(open(args.data_path, 'rb'))
    
    USE_CUDA = torch.cuda.is_available()
    device = torch.device("cuda" if USE_CUDA else "cpu")

    # update args
    dataset.config.__dict__.update(args.__dict__)
    args.__dict__.update(dataset.config.__dict__)
    pp = lambda x: pprint.PrettyPrinter().pprint(x)
    pp(args.__dict__)

    # new model experiment
    for set_num in range(args.set_num, args.set_num+1):
        print('\n[QA set %d]' % (set_num))
        model = DMN(args, dataset.idx2vec, set_num).to(device)
        results = run_experiment(model, dataset, set_num)

    print('### end of experiment')

if __name__ == '__main__':
    main()

