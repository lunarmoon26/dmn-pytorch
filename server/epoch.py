import sys
import numpy as np
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable

def progress(_progress):
    bar_length = 5  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(_progress, int):
        _progress = float(_progress)
    if not isinstance(_progress, float):
        _progress = 0
        status = "error: progress var must be float\r\n"
    if _progress < 0:
        _progress = 0
        status = "Halt...\r\n"
    if _progress >= 1:
        _progress = 1
        status = ""
    block = int(round(bar_length * _progress))
    text = "\r\t[%s]\t%.2f%% %s" % (
            "#" * block + " " * (bar_length-block), _progress * 100, status)

    return text

def run_epoch(model, dataset, ep, mode='tr', set_num=1, is_train=True):
    total_metrics = np.zeros(2)
    total_step = 0.0
    print_step = model.config.print_step
    start_time = datetime.now()
    dataset.shuffle_data(seed=None, mode='tr')

    USE_CUDA = torch.cuda.is_available()
    device = torch.device("cuda" if USE_CUDA else "cpu")

    total_outputs = []

    while True:
        model.optimizer.zero_grad()
        stories, questions, answers, sup_facts, s_lens, q_lens, e_lens = \
            dataset.get_next_batch(mode, set_num)
        # dataset.decode_data(stories[0], questions[0], answers[0], sup_facts[0], s_lens[0])
        wrap_tensor = lambda x: torch.LongTensor(np.array(x))
        wrap_var = lambda x: Variable(wrap_tensor(x)).to(device)
        stories = wrap_var(stories)
        questions = wrap_var(questions)
        answers = wrap_var(answers)
        sup_facts = wrap_var(sup_facts) - 1
        s_lens = wrap_tensor(s_lens)
        q_lens = wrap_tensor(q_lens)
        e_lens = wrap_tensor(e_lens)

        if is_train:
            model.train()
        else:
            model.eval()
        outputs, gates = model(stories, questions, s_lens, q_lens, e_lens)
        if set_num > 0:
            a_loss = model.criterion(outputs[:, 0, :], answers[:, 0])
            if answers.size(1) > 1:  # multiple answer
                for ans_idx in range(model.config.max_alen):
                    a_loss += model.criterion(outputs[:, ans_idx, :], answers[:, ans_idx])
            for episode in range(model.config.max_episode):
                if episode == 0:
                    g_loss = model.criterion(gates[:, episode, :], sup_facts[:, episode])
                else:
                    g_loss += model.criterion(gates[:, episode, :], sup_facts[:, episode])
            beta = 0 if ep < model.config.beta_cnt and mode == 'tr' else 1
            alpha = 1
            metrics = model.get_metrics(outputs, answers, multiple=answers.size(1) > 1)
            total_loss = alpha * g_loss + beta * a_loss

            if is_train:
                total_loss.backward()
                nn.utils.clip_grad_norm(model.parameters(), model.config.grad_max_norm)
                model.optimizer.step()

            total_metrics[0] += total_loss.item()
            total_metrics[1] += metrics
        else:
            # max_idx = torch.max(outputs[:,0,:], 1)[1].data.cpu().numpy()
            outputs_topk = torch.topk(outputs[:,0,:], 3)[1].data.cpu().numpy()
            total_outputs += [tk[0] for tk in outputs_topk]

        total_step += 1.0

        # print step
        if dataset.get_batch_ptr(mode) % print_step == 0 or total_step == 1:
            et = int((datetime.now() - start_time).total_seconds())
            _progress = progress(
                dataset.get_batch_ptr(mode) / dataset.get_dataset_len(mode, set_num))
            if dataset.get_batch_ptr(mode) == 0:
                _progress = progress(1)
            _progress += '[%s] time: %s' % (
                '\t'.join(['{:.2f}'.format(k)
                           for k in total_metrics / total_step]),
                '{:2d}:{:2d}:{:2d}'.format(et // 3600, et % 3600 // 60, et % 60))
            sys.stdout.write(_progress)
            sys.stdout.flush()

            # end of an epoch
            if dataset.get_batch_ptr(mode) == 0:
                et = (datetime.now() - start_time).total_seconds()
                print('\n\ttotal metrics:\t%s' % ('\t'.join(['{:.2f}'.format(k)
                                                             for k in total_metrics / total_step])))
                break

    return total_metrics / total_step, total_outputs
