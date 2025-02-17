import pathlib
import plotly.express as px
file = pathlib.Path(f'./temp.txt')
content = file.read_text()
contents = content.split('/')
content = ''.join(contents)
types=[0,1]
counts = {}
for type_ in types:
    count_ = content.count(str(type_))
    counts[type_] = count_
_count = [counts[0],counts[1]]
fig = px.bar(_count)
fig.show()