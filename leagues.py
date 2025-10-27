import xml.dom.minidom as minidom

leagues = [
    'Brasileirão Série A',
    'Brasileirão Série B',
    'Brasileirão Série C',
    'Brasileirão Série D',
    'Paulista A1-2025',
    'Paulista A2-2025',
    'Paulista A4-2025',
    'Libertadores',
    'Copa do Brasil',
    'Sul-Americana',
    'Copa Paulista'
]

doc = minidom.Document()
ligas = doc.createElement("ligas")
doc.appendChild(ligas)

for league in leagues:
    liga = doc.createElement("liga")
    nome = doc.createElement("nome")
    text = doc.createTextNode(league)
    nome.appendChild(text)
    liga.appendChild(nome)
    ligas.appendChild(liga)

with open('ligas.xml', 'w', encoding='utf-8') as f:
    f.write(doc.toprettyxml(indent="  "))
