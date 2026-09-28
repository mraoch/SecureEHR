CREATE DATABASE dbfde;
CREATE USER fde with password 'dbfde';
ALTER ROLE fde SET client_encoding TO 'utf-8';
ALTER ROLE fde SET default_transaction_isolation TO 'read committed';
ALTER ROLE fde SET timezone TO 'UTC';
grant all PRIVILEGES ON DATABASE dbfde TO fde;