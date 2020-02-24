# -*- encoding: utf-8 -*-

from lxml import etree
import pandas as pd


detailed_position_key = {
        0: 'NA',
        1: 'goalkeeper',
        2: 'wing_back',
        3: 'full_back',
        4: 'central_defender',
        5: 'defensive_midfielder',
        6: 'attacking_midfielder',
        7: 'central_midfielder',
        8: 'winger',
        9: 'striker',
        10: 'second_striker'
        }

def get_game_info(el):
    """Return a dictionary with the match infos.

        Args:
            el: etree._Element of game tag
        Returns:
            a list with the information about the game.
    """
    return dict(list(map(lambda key: (key, el.get(key)), el.keys())))

def parse_pass(el):
    """ Parsing passe element from F24
    """
    basic_info = get_basic_info(el)
    x0 = float(el.get('x'))
    y0 = float(el.get('y'))
    x1 = float(get_q_value(el, 140))
    y1 = float(get_q_value(el, 141))
    outcome = el.get('outcome')
    cross = check_q_element_present(el, 2)
    free_kick = check_q_element_present(el, 5)
    corner = check_q_element_present(el, 6)
    return {**{
            'evt_type': 'pass',
            'outcome': outcome,
            'cross': cross,
            'free_kick': free_kick,
            'corner': corner,
            'x0': x0,
            'y0': y0,
            'x1': x1,
            'y1': y1
            }, **basic_info }

def get_events(root, evt_type):
    """Get a list of events of type evt_type.

        Args:
        root: root of f24 xml tree
        evt_type: string identifier of type
        Returns:
            a list containing the events.
    """
    return root.xpath('//Event[@type_id="{0}"]'.format(evt_type))

def parse_miss(el):
    """Parsing function for a missed shot.

        Args:
            el: lxml-element
        Returns:
            A dictionary with the according entries.
    """
    evt_type = 'miss'
    basic_info = get_basic_info(el)
    x = float(el.get('x'))
    y = float(el.get('y'))
    outcome = el.get('outcome')
    return { **{
        'x': x,
        'y': y,
        'outcome': outcome
        }, **basic_info }

def parse_post(el):
    """
    """
    evt_type = 'post'
    basic_info = get_basic_info(el)
    x = float(el.get('x'))
    y = float(el.get('y'))
    outcome = el.get('outcome')
    return { **{
        'x': x,
        'y': y,
        'outcome': outcome
        }, **basic_info }


def parse_attempt(el):
    """
    """
    evt_type = 'attempt'
    basic_info = get_basic_info(el)
    x = float(el.get('x'))
    y = float(el.get('y'))
    outcome = el.get('outcome')
    header = check_q_element_present(el, 15)
    return { **{
        'x': x,
        'y': y,
        'header': header,
        'outcome': outcome
        }, **basic_info }


def parse_goal(el):
    """
    """
    evt_type = 'goal'
    basic_info = get_basic_info(el)
    x = float(el.get('x'))
    y = float(el.get('y'))
    outcome = el.get('outcome')
    open_play = check_q_element_present(el, 22)
    set_play = check_q_element_present(el, 24)
    penalty = check_q_element_present(el, 9)
    own_goal = check_q_element_present(el, 28)
    header = check_q_element_present(el, 15)
    assist_id = get_q_value_safe(el, 55)
    return { **{
        'evt_type': evt_type,
        'open_play': open_play,
        'set_play': set_play,
        'penalty': penalty,
        'own_goal': own_goal,
        'header': header,
        'assist_id': assist_id,
        'x': x,
        'y': y,
        'outcome': outcome
        }, **basic_info }

def parse_sub(el):
    """
    """
    evt_type = 'substitution'
    type_id = int(el.get('type_id'))
    if type_id == 18:
        evt_type_qualified = 'player_off'
    elif type_id == 19:
        evt_type_qualified = 'player_on'
    elif type_id == 20:
        evt_type_qualified = 'player_retired'
    else:
        evt_type_qualified = 'NA'
    basic_info = get_basic_info(el)
    position = get_q_value(el, 44)
    connected_sub = get_q_value(el, 55)
    detailed_position = detailed_position_key[int(get_q_value_safe(el, 292, 0))]
    return { **{
        'evt_type': evt_type,
        'evt_type_qualified': evt_type_qualified,
        'position': position,
        'connected_sub': connected_sub,
        'detailed_position': detailed_position
        }, **basic_info }

def get_q_value(el, id):
    """Returns the q value from el children.

        Warning: Assumes that the qualifier is present. Therefore, doesn't
        do any checking throws an error checking and return the first entry
        from the list returned by xpath.

        Args:
            el: etree._Element of event
            id: number of q element to obtain. Can be string or integer
        Returns:
            the according value as a string.
    """
    return el.xpath('./Q[@qualifier_id="{0}"]'.format(id))[0].get('value')

def get_q_value_safe(el, id, default = 'NA'):
    """
    """
    entry = el.xpath('./Q[@qualifier_id="{0}"]'.format(id))
    if entry:
        return entry[0].get('value')
    else:
        return default 
            

def check_q_element_present(el, id):
    """
    """
    return len(el.xpath('./Q[@qualifier_id="{0}"]'.format(id))) > 0

def get_basic_info(el):
    """
    """
    evt_id = int(el.get('event_id'))
    period = int(el.get('period_id'))
    minute = int(el.get('min'))
    second = int(el.get('sec'))
    timestamp = el.get('timestamp')
    player_id = el.get('player_id')
    team_id = el.get('team_id')
    return {
            'evt_id': evt_id,
            'period': period,
            'minute': minute,
            'second': second,
            'player_id': player_id,
            'team_id': team_id,
            'timestamp': timestamp
            }


if __name__ == '__main__':
    fname = 'f24-22-2016-861478-eventdetails.xml'
    tree = etree.parse(fname)
    root = tree.getroot()
    game_info = get_game_info(root[0])
    whistle_on = get_events(root, 32)
    passes = get_events(root, 1) 
    passes_parsed = [parse_pass(ev) for ev in passes]
    misses = get_events(root, 13)
    misses_parsed = [parse_miss(ev) for ev in misses]
    posts = get_events(root, 14)
    attempts = get_events(root, 15)
    goals = get_events(root, 16)
    goals_parsed = [parse_goal(ev) for ev in goals]
    players_off = get_events(root, 18)
    players_off_parsed = [parse_sub(ev) for ev in players_off]
    players_on = get_events(root, 19)
    players_on_parsed = [parse_sub(ev) for ev in players_on]
    players_retired = get_events(root, 20)
    players_retired_parsed = [parse_sub(ev) for ev in players_retired]
