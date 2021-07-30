import json
import numpy as np
from collections import Counter
from sklearn.manifold import TSNE

with open("data/united_kingdom.json", "r") as fin:
    uk = json.loads(fin.readline())

uk = [party for party in uk if len(party['colors']) > 0 and len(party['ideology'])]

ideologies = Counter(sum([party['ideology'] for party in uk],[]))
ideologies = [k for k, v in ideologies.most_common() if v > 1]
mapping = dict(zip(ideologies, range(len(ideologies))))

party_vectors = dict()
for party in uk:
    idx = [mapping[ideology] for ideology in party['ideology'] if ideology in mapping]
    vec = np.zeros(len(mapping))
    vec[idx] = 1
    if len(vec) > 0:
        party_vectors[party['id']] = vec

X = np.vstack(list(party_vectors.values()))
embedding = TSNE(n_components=2).fit_transform(X)
print(embedding)
