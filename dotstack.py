#!/usr/bin/python

'''
dotstack.py -- visualization of Heat stacks.
Copyright (C) 2014 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import colorsys
import logging
import os
import sys

from keystoneclient.v2_0.client import Client as KEYSTONE
from heatclient.client import Client as HEAT
from heatclient.exc import *

LOG = logging.getLogger('dotstack')


def get_keystone_client(args):
    '''Returns a keystone client.  Other examples that need an
    authenticated keystone client can simply:

        import common
        import keystone_example
        parser = common.create_parser()
        args = parser.parse_args()
        client = keystone_example.get_keystone_client(args)
    '''

    LOG.info('authenticating to keystone server')
    return KEYSTONE(username=args.os_username,
                    password=args.os_password,
                    tenant_name=args.os_tenant_name,
                    tenant_id=args.os_tenant_id,
                    auth_url=args.os_auth_url)


def get_heat_client(ks):
    '''Iterate through the service catalog and display all endpoint
    URLs for all services.'''

    LOG.info('looking for orchestration service in service catalog')
    endpoints = ks.service_catalog.get_endpoints(service_type='orchestration',
                                                 endpoint_type='public')
    if 'orchestration' not in endpoints:
        LOG.error('no orchestration endpoint in service catalog')
        sys.exit(1)

    endpoint_url = endpoints['orchestration'][0]['publicURL']
    LOG.info('found orchestration endpoint = %s', endpoint_url)
    return HEAT('1', endpoint=endpoint_url, token=ks.auth_token)


def parse_args():
    p = argparse.ArgumentParser()

    authg = p.add_argument_group(title='Authentication options')

    authg.add_argument('--os-username',
                       default=os.environ.get('OS_USERNAME'))
    authg.add_argument('--os-password',
                       default=os.environ.get('OS_PASSWORD'))
    authg.add_argument('--os-tenant-name',
                       default=os.environ.get('OS_TENANT_NAME'))
    authg.add_argument('--os-tenant-id',
                       default=os.environ.get('OS_TENANT_ID'))
    authg.add_argument('--os-region-name',
                       default=os.environ.get('OS_REGION_NAME'))
    authg.add_argument('--os-auth-url',
                       default=os.environ.get('OS_AUTH_URL'))

    logg = p.add_mutually_exclusive_group()
    logg.add_argument('--verbose', '-v',
                      help='enable verbose logging',
                      action='store_const',
                      const=logging.INFO,
                      dest='loglevel')
    logg.add_argument('--debug',
                      help='enable debug logging',
                      action='store_const',
                      const=logging.DEBUG,
                      dest='loglevel')

    outg = p.add_argument_group(title='Output options')
    outg.add_argument('--colors', '-C',
                      action='store_true',
                      help='colorize graph nodes')
    outg.add_argument('--detailed', '-D',
                      action='store_true',
                      help='produce detailed nodes in graph')

    p.add_argument('--recursive', '-r',
                   action='store_true',
                   help='descend into nested stacks')
    p.add_argument('stack',
                   help='name or id of heat stack')

    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()


def get_stack_data(client, stack, nodelist, nodemap, edges, recurse=False):
    for rsrc in client.resources.list(stack.id):
        rname = rsrc.resource_name
        rqual = '%s:%s' % (stack.id, rname)
        rid = rsrc.physical_resource_id
        nodelist.append((rqual, rname))
        nodemap[rqual] = rsrc

        for req in rsrc.required_by:
            edges.append((rqual, '%s:%s' % (stack.id, req)))

        if recurse:
            try:
                nested = client.stacks.get(rid)
                get_stack_data(client, nested, nodelist, nodemap, edges,
                               recurse=recurse)
            except HTTPNotFound:
                pass


def main():
    global args
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    if args.loglevel != logging.DEBUG:
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARN)

    ks = get_keystone_client(args)
    heat = get_heat_client(ks)

    # Find the named stack.
    try:
        stack = heat.stacks.get(args.stack)
    except HTTPNotFound:
        for stack in heat.stacks.list():
            if stack.stack_name == args.stack:
                break
        else:
            LOG.error('unable to find stack named %s' % args.stack)
            sys.exit(1)

    nodelist = []
    nodemap = {}
    edges = []

    get_stack_data(heat, stack, nodelist, nodemap, edges,
                   recurse=args.recursive)

    # This builds a color palette for coloring the graph nodes by
    # resource type.
    rsrc_types = set([node.resource_type for node in nodemap.values()])
    HSV_tuples = [(x*1.0/len(rsrc_types), 0.3, 1.0)
                  for x in range(len(rsrc_types))]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    rsrc_colors = dict(zip(rsrc_types, RGB_tuples))

    print 'digraph heat_stack_%s {' % stack.stack_name
    print 'rankdir=LR'

    # First output all the nodes and appropriate formatting options.
    for node in sorted(nodelist):
        rsrc = nodemap[node[0]]
        rsrc_type = rsrc.resource_type
        rsrc_id = rsrc.physical_resource_id
        rsrc_color = '#%02X%02X%02X' % tuple(int(255*x)
                                             for x in rsrc_colors[rsrc_type])
        if args.detailed:
            print '"%s" [label="%s | %s | %s", shape="record"]' % (
                node[0], node[1], rsrc_type, rsrc_id)
        elif args.colors:
            print '"%s" [label="%s", style=filled, color="%s"]' % (
                node[0], node[1], rsrc_color)
        else:
            print '"%s" [label="%s"]' % (
                node[0], node[1])

    # Now output all the edges.
    for lhs, rhs in edges:
        print '"%s" -> "%s"' % (lhs, rhs)
    print '}'

if __name__ == '__main__':
    main()