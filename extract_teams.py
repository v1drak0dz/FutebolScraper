from typing import Dict

def add_team(teams: Dict, league: str, team_name: str, brasao: str, group: str):
    """Adiciona ou atualiza informações de um time no dicionário global."""
    if league not in teams:
        teams[league] = {}

    if team_name not in teams[league]:
        teams[league][team_name] = {
            'brasao': brasao or '',
            'liga': league,
            'group': group or ''
        }
    else:
        # atualiza campos faltantes
        if not teams[league][team_name].get('brasao') and brasao:
            teams[league][team_name]['brasao'] = brasao
        if not teams[league][team_name].get('group') and group:
            teams[league][team_name]['group'] = group
