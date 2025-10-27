from xml.dom import minidom

# Carrega o XML a partir de um arquivo ou string
xml_file = "ligas.xml"  # ou o caminho do seu arquivo
dom = minidom.parse(xml_file)

# Pega todos os elementos <liga>
ligas = dom.getElementsByTagName("liga")

# Itera pelas ligas e pega o conteúdo de <nome>
for liga in ligas:
    nome_element = liga.getElementsByTagName("nome")[0]
    nome_text = nome_element.firstChild.nodeValue
    print(nome_text)
