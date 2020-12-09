import axios from 'axios';

const BASE_URI = 'http://localhost:5000';

const client = axios.create({
 baseURL: BASE_URI,
 json: true
});

class APIClient {
  constructor(accessToken) {
    this.accessToken = accessToken;
  }

  createBook(book) {
    return this.perform('push', '/book', book);
  }

  deleteBook(book) {
    return this.perform('delete', `/book/${book.id}`);
  }

  getBooks() {
    return this.perform('get', '/books');
  }

  async perform (method, resource, data) {
    return client({
      method,
      url: resource,
      data,
      headers: {
        Authorization: `Bearer ${this.accessToken}`
      }
    }).then(resp => {
      return resp.data ? resp.data : [];
    })
  }
}

export default APIClient;