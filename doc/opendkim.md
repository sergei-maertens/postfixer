# OpenDKIM + PostgreSQL

## Additional packages

apt-get install libopendbx1-pgsql

## Checks

-> check if BEGIN/END headers are problematic for opendkim or not

## Config in /etc/opendkim.conf

SigningTable        dsn:psql://postgres@5432+127.0.0.1/opendkimtest/table=dkim_keys?keycol=domain_name?datacol=id
KeyTable        dsn:psql://postgres@5432+127.0.0.1/opendkimtest/table=dkim_keys?keycol=id?datacol=domain_name,selector,private_key
