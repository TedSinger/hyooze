import sqlite3

INIT = '''
create table if not exists __color (
    red unsigned int1 not null,
    green unsigned int1 not null,
    blue unsigned int1 not null,
    chroma unsigned int2 not null,
    brightness unsigned int2 not null,
    hue signed int2 not null,
    primary key(red asc, green asc, blue asc)
) without rowid;
'''
VIEW = '''
create view if not exists color as
select red, green, blue, chroma / 619.0, brightness / 375.0, hue / 100.0, printf('#%02X%02X%02X', red, green, blue) as "hexcode" from color;
'''
INDEX = '''
create index rgb on color(red, green, blue);
'''
def get_conn():
    conn = sqlite3.connect('/home/ted/Sync/code/python/hyooze/cache.db')
    conn.execute(INIT)
    conn.execute(VIEW)
    # conn.execute(INDEX)
    conn.commit()
    return conn

def insert_many(conn, rows):
    conn.executemany('''insert into colors (red, green, blue, chroma, brightness, hue) values (?,?,?,?,?,?)''', rows)
    conn.commit()

def get_starting_point(conn):
    sql = '''with max_red as (select max(red) as "red" from colors),
            max_green as (select max(green) as "green" from colors, max_red where colors.red = max_red.red)
       select max_red.red, max_green.green, max(blue) as "blue" from colors, max_red, max_green where colors.green = max_green.green and colors.red = max_red.red'''
    cursor = conn.execute(sql)
    return cursor.fetchone()


if __name__ == '__main__':
    from hyooze.perception import BRIGHT_OFFICE
    conn = get_conn()

    colors = [(r, g, b) for r in range(256) for g in range(256) for b in range(256)]
    start = get_starting_point(conn)
    if start == (None, None, None):
        start_idx = 0
    else:
        start_idx = colors.index(start) + 1

    CHUNK_SIZE = 2000
    while True:
        chunk = []
        for i in range(start_idx, min(start_idx + CHUNK_SIZE, len(colors))):
            r,g,b = colors[i]
            chunk.append([r,g,b,*BRIGHT_OFFICE.rgb_to_cbh(r,g,b)]) # need to divide and round!!
        if len(chunk) == 0:
            break
        else:
            print(f'inserting from {colors[start_idx]}) {len(chunk)}')
            insert_many(conn, chunk)
            start_idx += CHUNK_SIZE