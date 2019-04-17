import numpy as np
import sys
import pprint
import copy
import pickle
import nltk
# import string
import sys, os, ssl
import gzip
from os.path import expanduser

# To bypass ssl issue 
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and 
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt')


class Dataset(object):
    def __init__(self, config):
        self.config = config
        self.init_settings()
        self.init_dict()
        self.build_word_dict(self.config.data_dir)
        self.get_pretrained_word(self.config.word2vec_path)
        self.process_data(self.config.data_dir)

    def init_settings(self):
        self.dataset = {}
        self.train_ptr = 0
        self.valid_ptr = 0
        self.test_ptr = 0

    def init_dict(self):
        self.PAD = '<PAD>'
        self.UNK = '<UNK>'
        self.word2idx = {}
        self.idx2word = {}
        self.idx2vec = []  # pretrained
        self.word2idx[self.PAD] = 0
        self.idx2word[0] = self.PAD
        self.word2idx[self.UNK] = 1
        self.idx2word[1] = self.UNK
        self.init_word_dict = {}
    
    def update_word_dict(self, key):
        self.word2idx[key] = len(self.word2idx)
        self.idx2word[len(self.idx2word)] = key

    def map_dict(self, key_list, dictionary):
        output = []
        for key in key_list:
            # assert key in dictionary
            if key in dictionary:
                output.append(dictionary[key])
            else:
                output.append(dictionary[self.UNK])
        return output
    
    def build_word_dict(self, dir):
        print('### building word dict %s' % dir)
        for subdir, _, files, in os.walk(dir):
            for file in sorted(files):
                set_type = file.split('_')[-1][:-4]
                if self.config.allow_unk and (set_type == 'test' or set_type == 'valid'):
                    continue
                with open(os.path.join(subdir, file)) as f:
                    for line_idx, line in enumerate(f):
                        line = line[:-1]
                        story_idx = int(line.split(' ')[0])

                        def update_init_dict(split):
                            for word in split:
                                if word not in self.init_word_dict:
                                    self.init_word_dict[word] = (
                                            len(self.init_word_dict), 1)
                                else:
                                    self.init_word_dict[word] = (
                                            self.init_word_dict[word][0],
                                            self.init_word_dict[word][1] + 1)

                        if '\t' in line: # question
                            question, answer, _ = line.split('\t')
                            question = ' '.join(question.split(' ')[1:])
                            q_split = nltk.word_tokenize(question)
                            if self.config.word2vec_type == 6:
                                q_split = [w.lower() for w in q_split]
                            update_init_dict(q_split)

                            answer = answer.split(',') if ',' in answer else [answer]
                            if self.config.word2vec_type == 6:
                                answer = [w.lower() for w in answer]
                            update_init_dict(answer)
                            # TODO: check vocab
                            """
                            for a in answer: 
                                if a not in self.init_word_dict:
                                    print(a)
                            """
                        else: # story
                            story_line = ' '.join(line.split(' ')[1:])
                            s_split = nltk.word_tokenize(story_line)
                            if self.config.word2vec_type == 6:
                                s_split = [w.lower() for w in s_split]
                            update_init_dict(s_split)

        print('init dict size', len(self.init_word_dict))
        # print(self.init_word_dict)

    def get_pretrained_word(self, path):
        print('\n### loading pretrained %s' % path)
        word_cnt = 0
        self.idx2vec.append([0.0] * self.config.word_embed_dim) # PAD
        self.idx2vec.append(np.random.uniform(-0.25, 0.25, size=self.config.word_embed_dim).tolist()) # UNK

        with gzip.open(path, 'rt', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    line = line.strip()
                    first_space_pos = line.find(' ', 1)   
                    word = line[:first_space_pos]
                    if self.config.word2vec_type == 6:
                        word = word.lower()
                    if word not in self.init_word_dict:    
                        continue
                    word_cnt += 1
                    vec = [float(l) for l in line.split()[1:]]
                    if word not in self.word2idx:
                        self.update_word_dict(word)
                        self.idx2vec.append(vec)                 
                except ValueError as e:
                    print(e)
        
        print('apple:', self.word2idx['apple'])
        print('apple:', self.idx2vec[self.word2idx['apple']][:5])
        print('pretrained vectors', np.asarray(self.idx2vec).shape, 'unk', len(self.init_word_dict) - word_cnt)
        print('dictionary change', len(self.init_word_dict), 
                'to', len(self.word2idx), len(self.idx2word))

    def process_data(self, dir):
        print('\n### processing %s' % dir)
        for subdir, _, files, in os.walk(dir):
            for file in sorted(files):
                with open(os.path.join(subdir, file)) as f:
                    max_sentnum = max_slen = max_qlen = 0
                    qa_num = file.split('_')[0][2:]
                    set_type = file.split('_')[-1][:-4]
                    story_list = []
                    sf_cnt = 1
                    si2sf = {}
                    total_data = []

                    for line_idx, line in enumerate(f):
                        line = line[:-1]
                        story_idx = int(line.split(' ')[0])
                        if story_idx == 1: 
                            story_list = []
                            sf_cnt = 1
                            si2sf = {}

                        if '\t' in line: # question
                            question, answer, sup_fact = line.split('\t')
                            question = ' '.join(question.split(' ')[1:])
                            q_split = nltk.word_tokenize(question)
                            if self.config.word2vec_type == 6:
                                q_split = [w.lower() for w in q_split]
                            q_split = self.map_dict(q_split, self.word2idx)

                            answer = answer.split(',') if ',' in answer else [answer]
                            if self.config.word2vec_type == 6:
                                answer = [w.lower() for w in answer]
                            answer = self.map_dict(answer, self.word2idx)
                            sup_fact = [si2sf[int(sf)] for sf in sup_fact.split()]

                            sentnum = story_list.count(self.word2idx['.'])
                            max_sentnum = max(max_sentnum, sentnum)
                            max_slen = max(max_slen, len(story_list))
                            max_qlen = max(max_qlen, len(q_split))

                            story_tmp = story_list[:]
                            total_data.append([story_tmp, q_split, answer, sup_fact])

                        else: # story
                            story_line = ' '.join(line.split(' ')[1:])
                            s_split = nltk.word_tokenize(story_line)
                            if self.config.word2vec_type == 6:
                                s_split = [w.lower() for w in s_split]
                            s_split = self.map_dict(s_split, self.word2idx)
                            story_list += s_split
                            si2sf[story_idx] = sf_cnt
                            sf_cnt += 1

                    self.dataset[str(qa_num) + '_' + set_type] = total_data
                    def check_update(d, k, v):
                        d[k] = max(v, d[k]) if k in d else v
                    check_update(self.config.max_sentnum, int(qa_num), max_sentnum)
                    check_update(self.config.max_slen, int(qa_num), max_slen)
                    check_update(self.config.max_qlen, int(qa_num), max_qlen)
                    self.config.word_vocab_size = len(self.word2idx)

        print('data size', len(total_data))
        print('max sentnum', max_sentnum)
        print('max slen', max_slen)
        print('max qlen', max_qlen, end='\n\n')

    def process_input(self, lines):
        print('\n### processing input')
        self.config.max_sentnum[0] = self.config.max_slen[0] = self.config.max_qlen[0] = 0
        max_sentnum = max_slen = max_qlen = 0
        qa_num = 0
        set_type = 'test'
        story_list = []
        sf_cnt = 1
        si2sf = {}
        total_data = []

        for line_idx, line in enumerate(lines):
            story_idx = line_idx + 1
            if '?' in line: # question
                question = line
                answer = []
                sup_fact = []
                q_split = nltk.word_tokenize(question)
                if self.config.word2vec_type == 6:
                    q_split = [w.lower() for w in q_split]
                q_split = self.map_dict(q_split, self.word2idx)

                sentnum = story_list.count(self.word2idx['.'])
                max_sentnum = max(max_sentnum, sentnum)
                max_slen = max(max_slen, len(story_list))
                max_qlen = max(max_qlen, len(q_split))

                story_tmp = story_list[:]
                total_data.append([story_tmp, q_split, answer, sup_fact])

            else: # story
                story_line = line
                s_split = nltk.word_tokenize(story_line)
                if self.config.word2vec_type == 6:
                    s_split = [w.lower() for w in s_split]
                s_split = self.map_dict(s_split, self.word2idx)
                story_list += s_split
                si2sf[story_idx] = sf_cnt
                sf_cnt += 1

        self.dataset[str(qa_num) + '_' + set_type] = total_data
        def check_update(d, k, v):
            d[k] = max(v, d[k]) if k in d else v
        check_update(self.config.max_sentnum, int(qa_num), max_sentnum)
        check_update(self.config.max_slen, int(qa_num), max_slen)
        check_update(self.config.max_qlen, int(qa_num), max_qlen)

        print('data size', len(total_data))
        print('max sentnum', max_sentnum)
        print('max slen', max_slen)
        print('max qlen', max_qlen, end='\n\n')

    def pad_sent_word(self, sentword, maxlen):
        while len(sentword) != maxlen:
            sentword.append(self.word2idx[self.PAD])

    def pad_data(self, dataset, set_num):
        for data in dataset:
            story, question, _, _ = data
            self.pad_sent_word(story, self.config.max_slen[set_num])
            self.pad_sent_word(question, self.config.max_qlen[set_num])

        return dataset
    
    def get_next_batch(self, mode='tr', set_num=1, batch_size=None):
        if batch_size is None:
            batch_size = self.config.batch_size
        
        if mode == 'tr':
            ptr = self.train_ptr
            data = self.dataset[str(set_num) + '_train']
        elif mode == 'va':
            ptr = self.valid_ptr
            data = self.dataset[str(set_num) + '_valid']
        elif mode == 'te':
            ptr = self.test_ptr
            data = self.dataset[str(set_num) + '_test']
        
        batch_size = (batch_size if ptr+batch_size<=len(data) else len(data)-ptr)
        padded_data = self.pad_data(copy.deepcopy(data[ptr:ptr+batch_size]), set_num)
        stories = [d[0] for d in padded_data]
        questions = [d[1] for d in padded_data]
        answers = [d[2] for d in padded_data]
        if len(np.array(answers).shape) < 2:
            for answer in answers:
                while len(answer) != self.config.max_alen:
                    answer.append(-100)
        sup_facts = [d[3] for d in padded_data]
        for sup_fact in sup_facts:
            while len(sup_fact) < self.config.max_episode:
                sup_fact.append(self.config.max_sentnum[set_num]+1)
        s_lengths = [[idx+1 for idx, val in enumerate(d[0]) 
            if val == self.word2idx['.']] for d in padded_data]
        e_lengths = []
        for s_len in s_lengths:
            e_lengths.append(len(s_len))
            while len(s_len) != self.config.max_sentnum[set_num]:
                s_len.append(0)
        q_lengths = [[idx+1 for idx, val in enumerate(d[1]) 
            if val == self.word2idx['?']][0] for d in padded_data]
        
        if mode == 'tr':
            self.train_ptr = (ptr + batch_size) % len(data)
        elif mode == 'va':
            self.valid_ptr = (ptr + batch_size) % len(data)
        elif mode == 'te':
            self.test_ptr = (ptr + batch_size) % len(data)

        return (stories, questions, answers, sup_facts, 
                s_lengths, q_lengths, e_lengths)
    
    def get_batch_ptr(self, mode):
        if mode == 'tr':
            return self.train_ptr
        elif mode == 'va':
            return self.valid_ptr
        elif mode == 'te':
            return self.test_ptr

    def get_dataset_len(self, mode, set_num):
        if mode == 'tr':
            return len(self.dataset[str(set_num) + '_train'])
        elif mode == 'va':
            return len(self.dataset[str(set_num) + '_valid'])
        elif mode == 'te':
            return len(self.dataset[str(set_num) + '_test'])

    def init_batch_ptr(self, mode=None):
        if mode is None:
            self.train_ptr = 0
            self.valid_ptr = 0
            self.test_ptr = 0
        elif mode == 'tr':
            self.train_ptr = 0
        elif mode == 'va':
            self.valid_ptr = 0
        elif mode == 'te':
            self.test_ptr = 0

    def shuffle_data(self, mode='tr', set_num=1, seed=None):
        if seed is not None:
            np.random.seed(seed)
        if mode == 'tr':
            np.random.shuffle(self.dataset[str(set_num) + '_train'])
        elif mode == 'va':
            np.random.shuffle(self.dataset[str(set_num) + '_train'])
        elif mode == 'te':
            np.random.shuffle(self.dataset[str(set_num) + '_test'])

    def decode_data(self, s, q, a, sf, l):
        print(l)
        print('story:', 
                ' '.join(self.map_dict(s[:l[-1]], self.idx2word)))
        print('question:', ' '.join(self.map_dict(q, self.idx2word)))
        print('answer:', self.map_dict(a, self.idx2word))
        print('supporting fact:', sf)
        print('length of sentences:', l)

    
class Config(object):
    def __init__(self):
        user_home = expanduser('~')
        self.data_dir = os.path.join(user_home, 'datasets/babi/en-valid-10k')
        self.word2vec_type = 840  # 6 or 840 (B)
        self.word2vec_path = os.path.join(user_home, 
            'datasets/glove/glove.%dB.300d.txt.gz' % self.word2vec_type)
        self.word_embed_dim = 300
        self.batch_size = 32
        self.max_sentnum = {}
        self.max_slen = {}
        self.max_qlen = {}
        self.max_episode = 5
        self.word_vocab_size = 0
        self.save_preprocess = True
        self.preprocess_save_path = './data/babi(tmp).pkl'
        self.preprocess_load_path = './data/babi(10k).pkl'
        self.allow_unk = True # won't index words in test and valid dataset


"""
[Version Note]
    v0.1: single max lengths
    v0.2: max length per type, supporting fact index fix

"""

if __name__ == '__main__':
    if not os.path.exists('./data'):
        os.makedirs('./data')
    
    config = Config()
    if config.save_preprocess:
        dataset = Dataset(config)
        pickle.dump(dataset, open(config.preprocess_save_path, 'wb'))
    else:
        print('## load preprocess %s' % config.preprocess_load_path)
        dataset = pickle.load(open(config.preprocess_load_path, 'rb'))
   
    # dataset config must be valid
    pp = lambda x: pprint.PrettyPrinter().pprint(x)
    pp(([(k,v) for k, v in vars(dataset.config).items() if '__' not in k]))
    print()
   
    for set_num in range(1):
        """
        mode = 'tr'
        while True:
            i, t, l = dataset.get_next_batch(mode, set_num+1, batch_size=1000)
            print(dataset.get_batch_ptr(mode), len(i))
            if dataset.get_batch_ptr(mode) == 0:
                print('iteration test pass!', mode)
                break

        mode = 'va'
        while True:
            i, t, l = dataset.get_next_batch(mode, set_num+1, batch_size=100)
            print(dataset.get_batch_ptr(mode), len(i))
            if dataset.get_batch_ptr(mode) == 0:
                print('iteration test pass!', mode)
                break
        """

        mode = 'te'
        dataset.shuffle_data(mode, set_num+1)
        while True:
            s, q, a, sf, sl, ql, el = dataset.get_next_batch(
                    mode, set_num+1, batch_size=100)
            print(dataset.get_batch_ptr(mode), len(s))
            if dataset.get_batch_ptr(mode) == 0:
                print(s[0], q[0], a[0], sf[0], sl[0], ql[0], el[0])
                dataset.decode_data(s[0], q[0], a[0], sf[0], sl[0][:el[0]])
                print('iteration test pass!', mode)
                break

