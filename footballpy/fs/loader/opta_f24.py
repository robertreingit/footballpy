# -*- encoding: utf-8 -*-

from lxml import etree
import pandas as pd

def parse_pass(el):
    """ Parsing passe element from F24
    """
    basic_info = get_basic_info(el)
    x0 = float(el.get('x'))
    y0 = float(el.get('y'))
    x1 = float(get_q_value(el, 140))
    y1 = float(get_q_value(el, 141))
    outcome = el.get('outcome')
    return {**{
            'evt_type': 'pass',
            'outcome': outcome,
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
    return { **{
        'x': x,
        'y': y,
        'outcome': outcome
        }, **basic_info }


def get_q_value(el, id):
    """
    """
    return el.xpath('./Q[@qualifier_id="{0}"]'.format(id))[0].get('value')

def get_basic_info(el):
    """
    """
    period = int(el.get('period_id'))
    minute = int(el.get('min'))
    second = int(el.get('sec'))
    timestamp = el.get('timestamp')
    player_id = el.get('player_id')
    team_id = el.get('team_id')
    return {
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
    passes = root.xpath('//Event[@type_id="1"]')
    passes_parsed = [parse_pass(ev) for ev in passes]
    print(passes_parsed[0])
    #df = pd.DataFrame(passes_parsed)
    misses = get_events(root, 13)
    misses_parsed = [parse_miss(ev) for ev in misses]
    posts = get_events(root, 14)
    attempts = get_events(root, 15)
    goals = get_events(root, 16)
