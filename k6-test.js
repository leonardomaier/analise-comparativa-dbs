import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
  cloud: {
    // Project: analise-comparativa-dbs
    projectID: 3739994,
    // Test runs with the same name groups test runs together.
    name: 'Test (18/01/2025-09:35:28)'
  }
};

export default function() {
  http.get('https://test.k6.io');
  sleep(1);
}