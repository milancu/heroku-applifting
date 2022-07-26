import os

from aiohttp import web
import aiohttp_jinja2
import jinja2

from databases import Database

database = Database(os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///example.db'))
async def on_startup(app):
    await database.connect()

    backend = database._get_backend()

    if backend == 'databases.backends.postgres:PostgresBackend':
        query = """CREATE TABLE IF NOT EXISTS books (id SERIAL, name VARCHAR(100))"""
    elif backend == 'databases.backends.sqlite:SQLiteBackend':
        query = """CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, name VARCHAR(100))"""
    else:
        raise Exception(f'Unknown database backend {backend}')
    await database.execute(query=query)

@aiohttp_jinja2.template('index.jinja2')
async def handler(request):
    return {'books': await database.fetch_all("SELECT * FROM books;")}

async def handler_books(request):
    data = await request.post()
    name = data['name']

    await database.execute("INSERT INTO books (name) VALUES (:name)", {'name': name})

    raise web.HTTPFound('/')

async def handler_books_delete(request):
    await database.execute("DELETE FROM books WHERE id = :id", {'id': int(request.match_info['id'])})

    raise web.HTTPFound('/')

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

app.on_startup.append(on_startup)

app.add_routes([
    web.get('/', handler),
    web.post('/books', handler_books),
    web.get('/books/delete/{id}', handler_books_delete),
])

if __name__ == '__main__':
    web.run_app(app, port=os.getenv('PORT', 8080))