<!--
Copyright (c) 2019 Matthias Tafelmeier.

This file is part of godon

godon is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

godon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this godon. If not, see <http://www.gnu.org/licenses/>.
-->
# Godon CLI

## breeder

**OPTIONS**
* hostname
    * flags: --hostname
    * type: string
    * desc: godon hostname
* port
    * flags: --port
    * type: number
    * desc: godon port

### breeder list

> List all configured breeders

~~~bash
set -eEux

curl --request GET http://${hostname}:${port}/breeders
~~~

### breeder create

**OPTIONS**
* definition
    * flags: --file
    * type: string
    * desc: definition file of breeder to be created

> Create a breeder

~~~bash
set -eEux

curl --request POST \
     -H 'Content-Type: application/json' \
     --data @"${file}" \
     http://${hostname}:${port}/breeders
~~~

### breeder purge

**OPTIONS**
* name
    * flags: --name
    * type: string
    * desc: name of breeder to be purged

> Purge a breeder

~~~bash
set -eEux

curl --request DELETE \
     -H 'Content-Type: application/json' \
     --data "{ \"name\": \"${name}\" }" \
     http://${hostname}:${port}/breeders
~~~

### breeder update

**OPTIONS**
* definition
    * flags: --file
    * type: string
    * desc: definition file of breeder to be updated

> Update a breeder

~~~bash
set -eEux

curl --request PUT \
     -H 'Content-Type: application/json' \
     --data @"${file}" \
     http://${hostname}:${port}/breeders
~~~

### breeder show

**OPTIONS**
* name
    * flags: --name
    * type: string
    * desc: name of breeder to get details from

> Show a breeder

~~~bash
set -eEux

curl --request GET \
     -H 'Content-Type: application/json' \
     --data "{ \"name\": \"${name}\" }" \
     "http://${hostname}:${port}/breeders/${name}"
~~~