import sqlite3

class DBAdapter():

    connection = None

    format = [
        {
            'name': 'instances',
            'fields': ['uid integer', 'id text']
        },
        {
            'name': 'groups',
            'fields': ['uid integer', 'type integer']
        }
    ]

    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname)
        self.__initTables()

    def __initTables(self):
        c = self.connection.cursor()
        for table in self.format:
            fields = ','.join(table['fields'])
            query = 'create table if not exists {0} ({1})'.format(table['name'], fields)

            c.execute(query)

        self.connection.commit()

