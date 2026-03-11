FROM n8nio/n8n:2.0.1

USER root

# Instalujemy globalnie potrzebne pakiety npm
RUN npm install --location=global papaparse slugify xmlbuilder2 pdf-lib csv-parse cheerio fast-xml-parser

# Ustawiamy NODE_PATH na katalog globalnych modułów
ENV NODE_PATH=/usr/local/lib/node_modules

USER node
