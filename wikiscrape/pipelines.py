import oursql

class SaveToMySQL(object):
    def __init__(self):
        self.conn = oursql.connect(host='localhost', user='root', db='artchart_0', port=3307)

    def process_item(self, item, spider):
        cursor = self.conn.cursor()

        cursor.execute('INSERT INTO artists (`name`) VALUES (?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)', (item['artist'],))
        artist_id = cursor.lastrowid

        cursor.execute('INSERT INTO locations (`name`) VALUES (?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)', (item['location'],))
        location_id = cursor.lastrowid

        cursor.execute('INSERT INTO works (`name`, `artist_id`, `location_id`) VALUES (?, ?, ?)', (item['name'], artist_id, location_id))
        return item
