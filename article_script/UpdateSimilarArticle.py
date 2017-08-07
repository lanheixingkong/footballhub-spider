# -*- coding: utf-8 -*-

from imp import reload
import sys
#sys.path.append("/Users/Lei/Documents/pyspace/mymodule")
sys.path.append("/root/python-space/mymodule")
import mysqldao
# reload(mysqlapi)
import numpy as np
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

#mysqlDao = mysqldao.MysqlDao()
mysqlDao = mysqldao.MysqlDao(host = "localhost", user = "root", password = "root123")

def queryArticleWords(total = 1000, maxId=0):
    corpus = []
    ids = []
    num = 100 if total > 100 else total
    while True:
#         news = queryNews(num, offset)
        if maxId == 0:
            sql = "select id, content_words from article order by id desc limit ?"
            news = mysqlDao.select(sql, (num,))
        else:
            sql = "select id, content_words from article where id < ? order by id desc limit ?"
            news = mysqlDao.select(sql, args = (maxId, num))

        nlen = len(news)
#         print('query news num: %d' % nlen)

        for (id, contentWords) in news:
    #         print('cut id: %d' % id)
            if contentWords != None and contentWords != '' and len(ids) < total:
                corpus.append(contentWords)
                ids.append(id)


#         print('corpus num: %d' % len(corpus))
        if nlen == 0 or len(ids) >= total or nlen < num:
            break

        maxId = news[-1][0]

    # print(corpus)
    print('corpus len: %d, corpus query end...' % len(ids))
    return (corpus, ids)

# 计算范数
def calNorm(weight):
    norms = []
    for i in range(len(weight)):
        norms.append(np.linalg.norm(weight[i]))
    return norms

# 合并相似文章
def mergeSet(i, j, sets=[]):
    hasIn = False
    for s in sets:
        if i in s or j in s:
            s.update([i,j])
            hasIn = True
            break

    if not hasIn:
        sets.append(set([i, j]))

# 计算文章相似度
# simList 文章两两之间相似度集合
# notSimList 没有相似文章的集合
# 合并后的相似文章集合
def calSim(weight, sim=0.5):
    simList = []
    simSet = set()
    sets = []
    notSimList = []
    norms = calNorm(weight)
    for i in range(len(weight)):
        for j in range(i+1, len(weight)):
            if i != j:
                n = weight[i].dot(weight[j])
                d = norms[i] * norms[j]
                cos = n / d
                if cos > sim:
#                     print('cos: %f, i: %d, j: %d' % (cos, i, j))
                    simList.append((i, j, cos))
                    mergeSet(i, j, sets)
                    simSet.update([i,j])

        if i not in simSet:
            notSimList.append(i)

    return (simList, notSimList, sets)


# 整理需标记的文章，在同一个相似度集合中不是最大序号的值
def sign(sets):
    signList = []
    signTupleList = []
    for s in sets:
        ss = sorted(s)
#         print(ss)
        signList.extend(ss[1:])
        signTupleList.append((ss[0], ss[1:]))

    return (signList, signTupleList)


def updateSign(sets, ids):
    idsStr = np.array(ids, dtype=str)

    (signList, signTupleList) = sign(sets)
    # 更新需要标记的文章
    idsstr = ','.join(idsStr[signList])
#     print(idsstr)
    signSql = 'update article set sim_sign = 1 where id in (%s)' % idsstr
    mysqlDao.execute(signSql, ())
#     print(signSql)

    # 插入相似文章
    for (maxIdIdx, simIdsIdx) in signTupleList:
        maxId = ids[maxIdIdx]
        simIds = ','.join(idsStr[simIdsIdx])

        countSql = 'select count(1) from similar_article where max_id = ?'
#         print(countSql, maxId)
        simCount = mysqlDao.select(countSql, (maxId,))

        if simCount[0][0] > 0:
            sql = 'update similar_article set sim_ids = ? where max_id = ?'
#             print(sql, (simIds, maxId))
            mysqlDao.execute(sql, (simIds, maxId))
        else:
            sql = 'insert into similar_article(max_id, sim_ids) values(?, ?)'
#             print(sql, (maxId, simIds))
            mysqlDao.execute(sql, (maxId, simIds))


def updateSimilarArticle(unit=1500):
    # 更新所有文章相似度，以1000篇文章未单位

    maxId = 0
    while True:
        print("------------start query maxId: %d-----------------" % maxId)
        (corpus, ids) = queryArticleWords(total = unit, maxId = maxId)
        maxId = ids[-1]
        print('ids from %d to %d' % (ids[-1], ids[0]))

        vectorizer = CountVectorizer()  #该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
        transformer = TfidfTransformer() #该类会统计每个词语的tf-idf权值
        tfidf=transformer.fit_transform(vectorizer.fit_transform(corpus))

        word=vectorizer.get_feature_names()#获取词袋模型中的所有词语
        print('word len: %d' % len(word))

        weight=tfidf.toarray()#将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
        print('weight shape: %s' % str(weight.shape))

        (simList, notSimList, sets) = calSim(weight)
        print('simList len: %d, notSimList len: %d, sets len: %d' % (len(simList), len(notSimList), len(sets)))
        #print(sets)
        updateSign(sets, ids)
        break
        if len(ids) < unit:
            break

    print("update similar article end...")


updateSimilarArticle()
