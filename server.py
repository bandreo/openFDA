import http.server
import http.client
import socketserver
import json 

PORT = 8000  

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    NOMBRE_SERVIDOR = "api.fda.gov"
    NOMBRE_RECURSO = "/drug/label.json"
    MEDIC_openfda = '&search=active_ingredient:'
    COMP_openfda = '&search=openfda.manufacturer_name:'

    def pangina_inicio(self):  
      # el html contiene la estructura de nuestra pantalla de inicio.
        html = """   
            <html>
                <head>
                    <title> OpenFDA</title>
                </head>
                <body align=center>

                    <h1>Drug product labelling OpenFDA </h1>
                    <form method="get" action="listDrugs">
                        <input type = "submit" value="Drug List">
                        </input>
                    </form>

                    <br>
                    <br>
                    <form method="get" action="searchDrug">
                        <input type = "submit" value="Drug Search">
                        <input type = "text" name="drug"></input>
                        </input>
                    </form>
                    <br>
                    <br>

                    <form method="get" action="listCompanies">
                        <input type = "submit" value="Company List">
                        </input>
                    </form>
                    <br>
                    <br>

                    <form method="get" action="searchCompany">
                        <input type = "submit" value="Company Search">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    <br>
                    <br>

                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Warnings List">
                        </input>
                    </form>
                </body>
            </html>
                """
        return html

    def pagina_2(self, lista):
        datos_html = """
                                <html>
                                    <head>
                                        <title>Blanca´s App</title>   
                                    </head>
                                    <body style='background-color: lightgreen'>
                                        <ul>
                            """
        for i in lista:  # iteramos los datos y almacenamos
            datos_html += "<li>" + i + "</li>"

        datos_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return datos_html

    def results(self, limit=10): #obtenemos los resultados y establecemos límite en 10
        connec = http.client.HTTPSConnection(self.NOMBRE_SERVIDOR) 
        connec.request("GET", self.NOMBRE_RECURSO + "?limit=" + str(limit)) 
        print(self.NOMBRE_RECURSO + "?limit=" + str(limit))
        r1 = connec.getresponse()  
        datos_raw = r1.read().decode("utf8") 
        datos = json.loads(datos_raw)  # procesamos el contenido json
        results = datos['results']
        return results

    def do_GET(self):
        lista_recursos = self.path.split("?")
        if len(lista_recursos) > 1:
            paramet = lista_recursos[1]
        else:
            paramet = ""

        limit = 1

        if paramet:
            partes = paramet.split("=")
            if partes[0] == "limit":
                limit = int(partes[1])
                print("Limit: {}".format(limit))
        else:
            print("NO HAY PARAMETROS")
            
        if self.path == '/':

            self.send_response(200)  # envia respuesta 
            self.send_header('Content-type', 'text/html')  # envia los headers
            self.end_headers()
            html = self.pagina_inicio()
            self.wfile.write(bytes(html, "utf8"))

        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            lista_medics = []
            results = self.results(limit)
            for resultado in results:
                if ('generic_name' in resultado['openfda']):
                    lista_medics.append(resultado['openfda']['generic_name'][0])
                else:
                    lista_medics.append('Desconocido')
            resultado_html = self.pagina_2(lista_medics)

            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'listCompanies' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            comps = []
            results = self.results(limit)
            for resultado in results:
                if ('manufacturer_name' in resultado['openfda']):
                    comps.append(resultado['openfda']['manufacturer_name'][0])
                else:
                    comps.append('El nombre es desconocido')
            resultado_html = self.pagina_2(comps)

            self.wfile.write(bytes(resultado_html, "utf8"))
        elif 'listWarnings' in self.path:

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            warnings = []
            results = self.results(limit)
            for resultado in results:  # introducimos nuestros resultados en una lista
                if ('warnings' in resultado):
                    warnings.append(resultado['warnings'][0])
                else:
                    warnings.append('Advertencia desconocida')
            resultado_html = self.pagina_2(warnings)

            self.wfile.write(bytes(resultado_html, "utf8"))

        elif 'searchDrug' in self.path:  # Buscamos un medicamento en el buscador
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            limit = 10
            drug = self.path.split('=')[1]

            medicamentos = []
            connec = http.client.HTTPSConnection(self.NOMBRE_SERVIDOR)  # establecemos conexion con el servidor
            connec.request("GET", self.NOMBRE_RECURSO + "?limit=" + str(limit) + self.MEDIC_openfda + drug)
            r1 = connec.getresponse()
            datos1 = r1.read()
            datos = datos1.decode("utf8")
            datos_almacenados = json.loads(datos)
            events_search_drug = datos_almacenados['results']
            for resultado in events_search_drug:
                if ('generic_name' in resultado['openfda']):
                    medicamentos.append(resultado['openfda']['generic_name'][0])
                else:
                    medicamentos.append('El medicamento es desconocido')

            resultado_html = self.pagina_2(medicamentos)
            self.wfile.write(bytes(resultado_html, "utf8"))


        elif 'searchCompany' in self.path:  # Buscamos la compañía

            self.send_response(200) 
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            limit = 10
            company = self.path.split('=')[1]
            companies = []
            connec = http.client.HTTPSConnection(self.NOMBRE_SERVIDOR)
            connec.request("GET", self.NOMBRE_RECURSO + "?limit=" + str(limit) + self.COMP_openfda + company)
            r1 = connec.getresponse()
            datos1 = r1.read()
            datos = datos1.decode("utf8")
            almacen_company = json.loads(datos)
            search_company = almacen_company['results']

            for search in search_company:
                companies.append(search['openfda']['manufacturer_name'][0])
            resultado_html = self.pagina_2(companies)
            self.wfile.write(bytes(resultado_html, "utf8"))
            
            #Extensiones

        elif 'redirect' in self.path:
            print('Redirección  a  página principal')
            self.send_response(301)
            self.send_header('Location', 'http://localhost:' + str(PORT))
            self.end_headers()

        elif 'secret' in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()

        else: 
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("ERROR 404, NOT FOUND '{}'.".format(self.path).encode())
        return


socketserver.TCPServer.allow_reuse_address = True 
Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)

httpd.serve_forever()
