FROM node:15
ENV NODE_ENV=production
WORKDIR /node
COPY . .
RUN npm install --production
CMD [ "node", "index.js" ]