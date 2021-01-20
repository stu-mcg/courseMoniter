FROM node:15
ENV NODE_ENV=production
WORKDIR /nodeFrontEnd
COPY . .
RUN npm install --production
CMD [ "node", "index.js" ]