# -*- coding: utf-8 -*-

from nltk.corpus import PlaintextCorpusReader
import jieba
jieba.load_userdict("/root/python-space/mymodule/football_dict.txt")

def getStopWords():
    corpus_root = '/root/python-space/mymodule'
    stoplists = PlaintextCorpusReader(corpus_root, 'stopwords.txt')
    stopwords = stoplists.words()
    return stopwords

def fenci(content, stopwords = []):
    seg_list = jieba.cut(content)
    result = []
    print 'fenci content:', content
    for word in seg_list:
        if word.isalpha() and not word in stopwords:
            result.append(word)
    
    #print 'result:', result
    #print 'result len:', len(result)     
    #ret = ' '.join(result)
    #print 'ret:', ret
    return result
