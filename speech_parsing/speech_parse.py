import pandas as pd
import json

data = pd.read_csv('RickAndMortyScripts.csv')

data['se_ep'] = data.apply(lambda row: f'{row["season no."]}_{row["episode no."]}', axis=1)

episodes = pd.DataFrame(data['se_ep'].drop_duplicates().reset_index(drop=True))

scripts = []
for e in range(0, len(episodes['se_ep'])):
    script = []
    ep = episodes['se_ep'][e]

    for i in range(0, len(data['line'])):
        if data['se_ep'][i] == ep:
            script.append(data['line'][i])

    scripts.append(script)

scripts = ['\n'.join(s) for s in scripts]
eps = episodes['se_ep'].to_list()
se_ep = [{'se_ep': e, 'script': s} for e, s in zip(eps, scripts)]

for el in se_ep:
    with open(f'{el.get("se_ep")}.json', 'w', encoding='utf-8') as f:
        json.dump(el, f, ensure_ascii=False, indent=4)


"""import hashlib

for s in scripts:
    block_string = s.encode()
    print(hashlib.sha3_256(block_string).hexdigest())"""