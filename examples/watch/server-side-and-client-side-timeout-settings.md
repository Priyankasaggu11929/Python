
**This documentation briefly provides information about the `server side` & `client side` connection timeout settings, in the watch request handler.**

---

There are two inputs available in the client, that could be used to set connection timeouts:

- `timeout_seconds`
- `_request_timeout`

---

#### Sever-side timeout (`kwargs['timeout_seconds'] = n`)

- The value of the argument `timeout_seconds`, **n**, (which is time duration in seconds) is consumed at the server side. It is included in the request URL to the server. 
  
  *For eg.* ~ `https://localhost:6443/api/v1/namespaces/default/pods?labelSelector=app%3Ddemo&timeoutSeconds=100&watch=True`

- In case, if the `timeout_seconds` value is set, the value `n` would determine the server-side connection timeout duration.

  *For eg.* ~ if `kwargs['timeout_seconds'] = 3600`, then the server-side connection timeout will be equal to 1 hour.
  
  This timeout duration is determined by the expression ~ `timeout = time.Duration(3600) * time.seconds`, *i.e.* `timeout = 1 hour`

  ***Refer:*** 
  - *[kubernetes/apiserver/pkg/endpoints/handlers/get.go#L255](https://github.com/kubernetes/apiserver/blob/92392ef22153d75b3645b0ae339f89c12767fb52/pkg/endpoints/handlers/get.go#L255)*

- In case, if the `timeout_seconds` value is not set, then the connection timeout will be a randomized value (in seconds) between 0 and `minRequestTimeout`, to spread out load.

  It is determined using the expression ~ `timeout = time.Duration(float64(minRequestTimeout) * (rand.Float64() + 1.0))`

  Where `minRequestTimeout` indicates the minimum number of seconds a handler must keep a request open before timing it out.
  
  The default value of `minRequestTimeout` is 1800 seconds.

  ***Refer:***
  - *[kubernetes/apiserver/pkg/endpoints/handlers/get.go#L258](https://github.com/kubernetes/apiserver/blob/92392ef22153d75b3645b0ae339f89c12767fb52/pkg/endpoints/handlers/get.go#L258)*
  - *[kubernetes/release-1.1/docs/admin/kube-apiserver.md](https://github.com/kubernetes/kubernetes/blob/release-1.1/docs/admin/kube-apiserver.md)*

- In case of a network outage, this timeout value will have no effect & the client will hang indefinitely without raising any exception.

- It is recommended to set this timeout value to a higher number such as 3600 seconds (1 hour).

---

#### Client-side timeout (`kwargs['_request_timeout'] = n`)

- The value of the argument `_request_timeout`, **n** (which is time duration in seconds) is set to the socket used for the connection.

- In case, if the `_request_timeout` value is set, this argument can accept 2 types of input values ~
    - integer (int), 
    - a tuple (with a length of 2)
 
  If it is tuple input type, the first value will be ignored. 

- In case of network outage, leading to dropping all packets with no RST/FIN, the timeout value (in seconds) determined by the `request_timeout` argument, would be the time duration for how long the client will wait before realizing & dropping the connection.

- When the timeout happens, an exception will be raised, for eg. ~
  
  `urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='localhost', port=6443): Read timed out.`
  
- In case, if the `_request_timeout` value is not set, then the default value is **`None`** & socket will have no timeout.

  ***Refer:***
  - [https://docs.python.org/2/library/socket.html#socket.getdefaulttimeout](https://docs.python.org/2/library/socket.html#socket.getdefaulttimeout)

- It is recommended to set this timeout value to a lower number (for eg. ~ maybe 60 seconds)
