# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Uses watch to print the stream of events from list namespaces and list pods.
The script will wait for 10 events related to namespaces to occur within
the `timeout_seconds` threshold and then move on to wait for another 10 events
related to pods to occur within the `timeout_seconds` threshold.

---

[INFO] Timeout settings

There are two inputs available in the client, that could be used to set connection timeouts:
1. timeout_seconds
2. _request_timeout

a) Sever-side timeout ("kwargs['timeout_seconds'] = n")

    - The value of the argument `timeout_seconds`, n (which is time duration in seconds) is consumed at the server side, and is included in the request URL to the server. For eg. ~
      "https://localhost:6443/api/v1/namespaces/default/pods?labelSelector=app%3Ddemo&timeoutSeconds=100&watch=True."

    - If the `timeout_seconds` value is set, for ex: "kwargs['timeout_seconds'] = 3600", then the server timeout will be equal to 1 hour, as determined by the following expression ~
      "timeout = time.Duration(3600) * time.seconds" -> "timeout = 1 hour"

      Refer: https://github.com/kubernetes/apiserver/blob/92392ef22153d75b3645b0ae339f89c12767fb52/pkg/endpoints/handlers/get.go#L255

    - If the `timeout_seconds` value is not set, then the connection timeout will be a randomized value (in seconds) between 0 and `minRequestTimeout`, to spread out load. It is determined by the following expression ~
      "timeout = time.Duration(float64(minRequestTimeout) * (rand.Float64() + 1.0))",

      Where `minRequestTimeout` indicates the minimum number of seconds a handler must keep a request open before timing it out. The default value of `minRequestTimeout` is 1800 seconds.

      Refer: https://github.com/kubernetes/apiserver/blob/92392ef22153d75b3645b0ae339f89c12767fb52/pkg/endpoints/handlers/get.go#L258
             https://github.com/kubernetes/kubernetes/blob/release-1.1/docs/admin/kube-apiserver.md

    - In case of a network outage, the timeout value will have no effect & the client will hang indefinitely without raising any exception. It is recommended to set this timeout value to a higher number such as 3600 seconds (1 hour).

b) Client-side timeout ("kwargs['_request_timeout'] = n")

    - The value of the argument `_request_timeout`, n (which is time duration in seconds) is set to the socket used for the connection.

    - The argument `_request_timeout` can accept 2 types of input values, i.e. either in integer (int) type, or a tuple with a length of 2. In case of the tuple input type, the first value will be ignored. 

    - In case of network outage, leading to dropping all packets with no RST/FIN, the timeout value (in seconds) determined by the `request_timeout` argument, would be the time duration for how long the client will wait before realizing & dropping the connection.

    - When the timeout happens, an exception will be raised, for ex ~
      "urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='localhost', port=6443): Read timed out."

    - It is recommended to set this timeout value to a low number (for ex ~ maybe 60 seconds)
"""

from kubernetes import client, config, watch


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    v1 = client.CoreV1Api()
    count = 10
    w = watch.Watch()
    for event in w.stream(v1.list_namespace, timeout_seconds=10):
        print("Event: %s %s" % (event['type'], event['object'].metadata.name))
        count -= 1
        if not count:
            w.stop()
    print("Finished namespace stream.")

    for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=10):
        print("Event: %s %s %s" % (
            event['type'],
            event['object'].kind,
            event['object'].metadata.name)
        )
        count -= 1
        if not count:
            w.stop()
    print("Finished pod stream.")


if __name__ == '__main__':
    main()
