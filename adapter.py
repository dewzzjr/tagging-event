from nltk.tag import CRFTagger
from nltk.tokenize import word_tokenize


class DataAdapter(object):
    def __init__(self, data=[]):
        self.tagger = CRFTagger()
        self.tagger.set_model_file('model.crf.tagger')

        if data.count(True) > 0:
            self.data_tagging, self.data_testing = self.for_tagging_testing(
                data)
            # print('TAGGING', self.data_tagging)
            # print('TESTING', self.data_testing)

    def tokenize_tag(self, text):
        text = text.replace('\r', ' | ').replace('\n', ' | ')
        tokens = word_tokenize(text, preserve_line=True)
        labels = []
        for label in self.tag(tokens):
            labels.append(label[1])
        return tokens, labels

    def for_tagging_testing(self, data):
        # self.data = data
        array_tagging = []
        array_testing = []
        for d in data:
            all_tags = []
            all_test = []
            for index, t in enumerate(d['text']):
                one_tag = [t, d['label'][index]]
                all_test.append(one_tag)
                all_tags.append(t)
            array_tagging.append(all_tags)
            array_testing.append(all_test)
            # print(all_tags)
        return array_tagging, array_testing

    def for_testing(self, data):
        # self.data = data
        array = []
        # print('TEST', data.count())
        for d in data:
            all_tags = []
            for index, t in enumerate(d['text']):
                # one_tag = [t, (d['label'][index] if is_ascii(d['label'][index]) else 'O')]
                one_tag = [t, d['label'][index]]
                all_tags.append(one_tag)
            array.append(all_tags)
            # print(all_tags)
        return array

    def for_tagging(self, data):
        # self.data = data
        array = []
        for d in data:
            all_tags = []
            for t in d['text']:
                all_tags.append(t)
            array.append(all_tags)
            # print(all_tags)
        return array

    def tag_sents(self):
        if self.data_tagging is not None:
            return self.tagger.tag_sents(self.data_tagging)
        else:
            return 'NoData'

    def tag(self, data):
        return self.tagger.tag(data)

    def evaluate(self):
        if self.data_testing is not None:
            return self.tagger.evaluate(self.data_testing)
        else:
            return 'NoData'

    def train(self, data):
        data = self.for_testing(data)
        self.tagger.train(data, 'model.crf.tagger')
        print('ACCURACY:', self.tagger.evaluate(data))
