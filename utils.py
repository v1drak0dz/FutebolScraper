import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

def normalize_name(name: str) -> str:
    """Normaliza nomes (remove espaços duplos, acentos e caixa)."""
    if not name:
        return ''
    return re.sub(r'\s+', ' ', name).strip()

def prettify_xml(elem: ET.Element) -> str:
    """Retorna XML formatado bonito."""
    rough = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
