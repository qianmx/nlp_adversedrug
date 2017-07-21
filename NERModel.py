import untangle
import glob
from mitie import *


class NERModel:
    def __init__(self):
        '''
        initiate class object
        '''
        self.trainer = ner_trainer("MITIE/MITIE-models/english/total_word_feature_extractor.dat")
        self.ner = None

    def parse_train_xml(self, filename):
        """
        @input a filename string
        @return:
        For training data: both a dictionary (key is the section) for X (text strings)
        and a list of dictionary for y (keys: id (not for task 1), section, type, start, len)
        """
        X = {}
        Y = []

        obj = untangle.parse(filename)
        for text in obj.Label.Text.Section:
            X[text['id']] = text.cdata

        if obj.Label.Mentions.Mention:
            for mention in obj.Label.Mentions.Mention:
                entity = {}
                entity['id'] = mention['id']
                entity['section'] = mention['section']
                entity['type'] = mention['type']
                entity['start'] = mention['start']
                entity['len'] = mention['len']
                Y.append(entity)

        return X, Y

    def parse_test_xml(self, filename):
        """
        @input a filename string
        @return: directory X
        """
        X = {}

        obj = untangle.parse(filename)
        for text in obj.Label.Text.Section:
            X[text['id']] = text.cdata

        return X

    def fit(self, folder_path):
        '''
        # train ner model on training files

        :param folder:  dictionary of training files
        '''

        url_base = os.getcwd() + '/' + folder_path + '/'
        train_text_ls = glob.glob(url_base + '*.xml')

        for doc in train_text_ls:
            train_x, train_y = self.parse_train_xml(doc)

            # convert train_y into {s1: [(start,len, type),...], s2: [(),...],...}
            train_y_dir = {}
            for item in train_y:
                key = item['section']
                val_tuple = (item['start'], item['len'], item['type'])
                if key not in train_y_dir:
                    train_y_dir[key] = [val_tuple]
                else:
                    train_y_dir[key].append(val_tuple)

            # add entities into trainer
            for section, tuples in train_y_dir.iteritems():
                tokens = tokenize(train_x[section])
                trainer_instance = ner_training_instance(tokens)
                for t in tuples:
                        try:
                            trainer_instance.add_entity(xrange(int(t[0]), int(t[0]) + int(t[1])), t[2])
                        except:
                            continue
                self.trainer.add(trainer_instance)

            self.ner = self.trainer.train()


if __name__=='__main__':
    ner = NERModel()
    ner.fit("train_xml")