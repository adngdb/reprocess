#!/usr/bin/env python

import click
import requests


URLS = {
    'stage': 'https://crash-stats.allizom.org',
    'prod': 'https://crash-stats.mozilla.com',
}


def search_crash_ids(params, env, batch_size):
    '''Returns all crash IDs resulting from a search defined by `params`.
    '''
    url = '{}/api/SuperSearch/'.format(URLS[env])
    payload = dict(params)
    payload.update({
        '_facets_size': 0,
        '_results_number': batch_size,
        '_columns': ['uuid'],
    })
    crash_ids = []
    total_results = 1

    while len(crash_ids) < total_results:
        payload['_results_offset'] = len(crash_ids)
        r = requests.get(url, params=payload)
        results = r.json()
        total_results = results['total']
        for hit in results['hits']:
            crash_ids.append(hit['uuid'])

        click.echo('Pulled {} results'.format(len(results['hits'])))

    assert len(crash_ids) == total_results
    click.echo('Received {} results from SuperSearch'.format(len(crash_ids)))
    return crash_ids


def send_for_reprocessing(crash_ids, env, batch_size, auth_token):
    '''Send a list of crash IDs to be reprocessed.
    '''
    url = '{}/api/Reprocessing/'.format(URLS[env])

    click.echo('Starting reprocessing')

    for i in range(0, len(crash_ids), batch_size):
        payload = {
            'crash_ids': crash_ids[i:i + batch_size]
        }
        headers = {
            'Auth-Token': auth_token,
        }
        r = requests.post(url, data=payload, headers=headers)
        assert r.status_code in (201, 200), r.status_code
        click.echo('Reprocessed {} crash reports'.format(
            len(payload['crash_ids'])
        ))


def build_params(arguments):
    '''Return a dictionary of arguments built from a list of values formatted
    like this: {key}={value}.

    For example:
    input: ['foo=bar', 'foo=baz', 'q=>42']
    output: { 'foo': ['bar', 'baz'], 'q': ['>42'] }
    '''
    params = {}
    for value in arguments:
        key, val = value.split('=', 1)
        if key not in params:
            params[key] = []
        params[key].append(val)
    return params


@click.command()
@click.option(
    '-t', '--auth-token',
    prompt='Auth token',
    help=(
        'An Auth Token that has the "Reprocess Crashes" permission on target '
        'environment'
    )
)
@click.option(
    '-s', '--batch-size',
    default=500,
    help='Number of documents to query or send at once'
)
@click.option(
    '-e', '--env',
    type=click.Choice(['prod', 'stage']),
    default='prod',
    help='Target crash-stats environment (stage or prod)'
)
@click.argument('params', nargs=-1)
def reprocess(auth_token, batch_size, env, params):
    '''Reprocess a list of crashes from a Super Search query.

    Accepts querystring-like arguments, for example:
    ./reprocess.py product=Firefox version=4.0 'date=>2010-10-10'
    '''
    params = build_params(params)
    click.echo(params)

    crash_ids = search_crash_ids(params, env, batch_size)
    send_for_reprocessing(crash_ids, env, batch_size, auth_token)

    click.echo(
        'Successfully sent {} crash reports for reprocessing'.format(
            len(crash_ids)
        )
    )


if __name__ == '__main__':
    reprocess()
