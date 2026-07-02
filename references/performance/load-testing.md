# Load Testing Reference

> **Scope**: Ready-to-use load test scripts (k6, Locust, JMeter).  
> For test strategy, thresholds, and when to run load tests see [performance-engineer-guide.md](performance-engineer-guide.md).

## k6 Test Script

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 500 },
    { duration: '5m', target: 1000 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/users', {
    params: {
      headers: { 'Content-Type': 'application/json' },
    },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response has users': (r) => r.json('data').length > 0,
  }) || errorRate.add(1);
  
  responseTime.add(res.timings.duration);
  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', colors: true }),
    'performance-report.json': JSON.stringify(data),
  };
}
```

## Locust Test

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
    
    @task(10)
    def view_products(self):
        self.client.get("/api/products", name="View Products")
    
    @task(5)
    def view_product_detail(self):
        self.client.get("/api/products/1", name="Product Detail")
    
    @task(2)
    def add_to_cart(self):
        self.client.post("/api/cart", json={
            "product_id": 1,
            "quantity": 1
        }, name="Add to Cart")
```

## JMeter Test Plan

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testname="API Load Test">
      <elementProp name="TestPlan.user_defined_variables">
        <stringProp name="VariableNames">BASE_URL</stringProp>
      </elementProp>
    </TestPlan>
    
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testname="Users">
        <elementProp name="ThreadGroup.main_controller">
          <stringProp name="ThreadGroup.num_threads">100</stringProp>
          <stringProp name="ThreadGroup.ramp_time">60</stringProp>
        </elementProp>
      </ThreadGroup>
      
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testname="GET /users">
          <stringProp name="HTTPSampler.domain">${BASE_URL}</stringProp>
          <stringProp name="HTTPSampler.path">/api/users</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
        </HTTPSamplerProxy>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```