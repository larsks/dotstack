This is a quick hack that produces [dot][] output from a Heat stack.

[dot]: http://en.wikipedia.org/wiki/DOT_(graph_description_language)

## Usage

    usage: dotstack.py [-h] [--os-username OS_USERNAME]
                       [--os-password OS_PASSWORD]
                       [--os-tenant-name OS_TENANT_NAME]
                       [--os-tenant-id OS_TENANT_ID]
                       [--os-region-name OS_REGION_NAME]
                       [--os-auth-url OS_AUTH_URL] [--verbose | --debug]
                       [--colors] [--detailed] [--recursive]
                       stack

    positional arguments:
      stack                 name or id of heat stack

    optional arguments:
      -h, --help            show this help message and exit
      --verbose, -v         enable verbose logging
      --debug               enable debug logging
      --recursive, -r       descend into nested stacks

    Authentication options:
      --os-username OS_USERNAME
      --os-password OS_PASSWORD
      --os-tenant-name OS_TENANT_NAME
      --os-tenant-id OS_TENANT_ID
      --os-region-name OS_REGION_NAME
      --os-auth-url OS_AUTH_URL

    Output options:
      --colors, -C          colorize graph nodes
      --detailed, -D        produce detailed nodes in graph

## Example

Running:

    python dotstack.py --recursive --color mystack > mystack.dot

Produces dot output like [this](sample.dot) and results in a graph
like [this](sample.png).

Running:

    python dotstack.py --recursive --detailed mystack > mystack.dot

Produces dot output like [this](sample-detailed.dot) and results in a
graph like [this](sample-detailed.png).  You will need to process the
dot output with the `dot` tool from [graphviz][]:

[graphviz]: http://www.graphviz.org/

    dot -Tsvg -o mystack.svg mystack.dot

You can generate output in a variety of other formats if `svg` just
isn't your bag, baby.

## License

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

