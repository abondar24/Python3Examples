from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from db_setup import Base, Restaurant, MenuItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('mysql://root:alex24@172.17.0.2/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Make a new restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name = 'newRestaurantName' type='text' placeholder='New Restaurant Name'>"
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output.encode("utf-8"))
                return

            if self.path.endswith("/edit"):
                restaurant_id_path = self.path.split("/")[2]
                restaurant_query = session.query(Restaurant).filter_by(id=restaurant_id_path).one()

                if restaurant_query:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += restaurant_query.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" \
                              % restaurant_id_path
                    output += "<input name = 'newRestaurantName' type='text' placeholder='%s'>" % restaurant_query.name
                    output += "<input type='submit' value='Rename'>"
                    output += "</form></body></html>"
                    self.wfile.write(output.encode("utf-8"))

            if self.path.endswith("/delete"):
                restaurant_id_path = self.path.split("/")[2]
                restaurant_query = session.query(Restaurant).filter_by(id=restaurant_id_path).one()

                if restaurant_query:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?" % restaurant_query.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" \
                              % restaurant_id_path
                    output += "<input type='submit' value='Delete'>"
                    output += "</form></body></html>"
                    self.wfile.write(output.encode("utf-8"))

            if self.path.endswith("/restaurants"):
                restraunts = session.query(Restaurant).all()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                for restaurant in restraunts:
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href ='/restaurants/%s/edit'>Edit</a>" % restaurant.id
                    output += "</br>"
                    output += "<a href ='/restaurants/%s/delete'>Delete</a>" % restaurant.id
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output.encode("utf-8"))
                return
        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                restaurant_id_path = self.path.split("/")[2]
                restaurant_query = session.query(Restaurant).filter_by(id=restaurant_id_path).one()

                if restaurant_query:
                    session.delete(restaurant_query)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers['Content-type'])
                if ctype == 'multipart/form-data':
                    pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    message_content = fields.get('newRestaurantName')[0].decode('utf-8')
                    restaurant_id_path = self.path.split("/")[2]
                    restaurant_query = session.query(Restaurant).filter_by(id=restaurant_id_path).one()

                    if restaurant_query:
                        restaurant_query.name = message_content
                        session.add(restaurant_query)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers['Content-type'])
                if ctype == 'multipart/form-data':
                    pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    message_content = fields.get('newRestaurantName')[0].decode('utf-8')
                    new_restaurant = Restaurant(name=message_content)
                    session.add(new_restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('location', '/restaurants')
                    self.end_headers()
        except:
            pass


def main():
    try:
        port = 8024
        server = HTTPServer(('', port), WebServerHandler)
        print("Web server is running on port %s" % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered,stopping server...")
        server.socket.close()


if __name__ == '__main__':
    main()
