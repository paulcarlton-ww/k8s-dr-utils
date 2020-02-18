"""
This module contains DR classes
"""
import os
import logging
import boto3
import boto3.s3
from botocore.config import Config
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import utilslib.library as lib

class Base(object):
    """Base class that provides a logger

    Arguments:
        logname (str) -- the name of the logger to use, defaults to __name__
        log_level (str) -- the level of logging, defaults to CRITICAL
    """
    log = None

    @lib.retry_wrapper
    def __init__(self, **kwargs):
        """
        Constructor

        Args:
        args     -- posistional arguments
        kwargs   -- Named arguments

        Returns:
        Base object
        """
        super(Base, self).__init__()

        log_name = kwargs["logname"] if "logname" in kwargs else __name__
        self.log = logging.getLogger(log_name)
        log_level = kwargs["log_level"] if "log_level" in kwargs else "CRITICAL"
        self.log.setLevel(log_level)


class S3(Base):
    """Base class for S3
    """
    @lib.retry_wrapper
    def __init__(self, *args, **kwargs):
        """
        Constructor

        Args:
        args     -- posistional arguments
        kwargs   -- Named arguments

        Returns:
        K8s object
        """
        super(S3, self).__init__(*args, **kwargs)
        self.log.debug("S3 init", extra=dict(**kwargs))

        if 'client' in kwargs:
            self.client = kwargs.get("client")
        else:
            kube_config = Config(connect_timeout=5, retries={'max_attempts': 0})
            self.client = boto3.client('s3', config=kube_config)

        self.bucket_name = kwargs.get("bucket_name", None)

    @staticmethod
    def parse_key(key):
        """
        parses the S3 bucket key returning component parts

        Args:
        key   -- the key

        Returns:
        tuble containing the fields in the key based on '/' seperator.
        """
        fields = key.split('/')
        if len(fields) == 6:
            return fields[0], fields[1], fields[2], fields[3], fields[5]
        else:
            raise Exception(
                "key should comprise set/cluster/namespace/kind/name")


class Store(S3):
    """Class to store or remove items from S3
    """
    @lib.retry_wrapper
    def __init__(self, *args, **kwargs):
        """
        Constructor

        Args:
        args     -- posistional arguments
        kwargs   -- Named arguments

        Returns:
        Store object
        """
        super(Store, self).__init__(*args, **kwargs)
        self.log.debug("Store init", extra=dict(**kwargs))

    @lib.timing_wrapper
    @lib.retry_wrapper
    def store_in_bucket(self, key, data):
        """
        store data in an S3 bucket with the provided key.

        :param key: The key.
        :param data: The dictionary to store
        """
        return self.client.put_object(Bucket=self.bucket_name, Key=key, Body=data.encode())

    @lib.timing_wrapper
    @lib.retry_wrapper
    def delete_from_bucket(self, key):
        """
        delete object in s3 with the provided key.

        :param key: the s3 key of the object to delete
        """
        return self.client.delete_object(Bucket=self.bucket_name, Key=key)



class Retrieve(S3):
    """Retrieve keys and items from S3
    """
    @lib.retry_wrapper
    def __init__(self, *args, **kwargs):
        """
        Constructor

        Args:
        args     -- posistional arguments
        kwargs   -- Named arguments

        Returns:
        Retrieve object
        """
        super(Retrieve, self).__init__(*args, **kwargs)
        self.log.debug("Retrieve init", extra=dict(**kwargs))

    @lib.timing_wrapper
    @lib.retry_wrapper
    def get_s3_namespaces(self, clusterset, clustername):
        """
        retrieve namespace names for provided cluster name prefix.

        :param clustername: the name of the cluster to get the namespaces for
        """
        keys = self.get_bucket_keys("{}/{}".format(clusterset, clustername))
        namespaces = list(map(lambda k: k.split('/')[2], keys))
        return list(dict.fromkeys(namespaces))

    @lib.timing_wrapper
    @lib.retry_wrapper
    def get_bucket_keys(self, prefix):
        """
        retrieve items in an S3 bucket with the provided prefix.

        :param prefix: The key prefix .
        """
        response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return list(map(lambda i: i['Key'], response['Contents']))

    @lib.timing_wrapper
    @lib.retry_wrapper
    def get_bucket_item(self, key):
        """
        retrieve an item from s3 for a particular key

        :param key: they key of the item to get
        """
        response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        return response['Body'].read()

class K8s(Base):
    """A class to perform actions against Kubernetes
    """
    v1 = None
    v1App = None
    v1ext = None
    rbac = None
    auto_scaler = None
    custom = None
    
    cluster_name = None
    kube_config = None

    supported_kinds = {'ConfigMap': ('v1', 'config_map'),
                       'LimitRange': ('v1', 'limit_range'),
                       'ResourceQuota': ('v1', 'resource_quota'),
                       'Secret': ('v1', 'secret'),
                       'Service': ('v1', 'service'),
                       'ServiceAccount': ('v1', 'service_account'),
                       'PodTemplate': ('v1', 'pod_template'),
                       'Deployment': ('v1App', 'deployment'),
                       'Role': ('rbac', 'role'),
                       'RoleBinding': ('rbac', 'role_binding'),
                       'HorizontalPodAutoscaler': ('auto_scaler', 'horizontal_pod_autoscaler')}
    
    supported_custom_kinds = {'VirtualService': ('networking.istio.io', 'v1alpha3', 'virtualservices'),
                              'Gateway': ('networking.istio.io', 'v1alpha3', 'gateways')}
    
    @lib.retry_wrapper
    def __init__(self, *args, **kwargs):
        """
        Constructor

        Args:
        args     -- posistional arguments
        kwargs   -- Named arguments

        Returns:
        K8s object
        """
        super(K8s, self).__init__(*args, **kwargs)

        self.log.debug("K8s init", extra=dict(**kwargs))

        kube_config = kwargs["kube_config"] if "kube_config" in kwargs else ""
        if kube_config and len(kube_config) > 0:
            self.log.info("using kube_config=%s", kube_config)
            config.load_kube_config(config_file=kube_config)
        else:
            self.log.info("no kube_config, running in-cluster")
            config.load_incluster_config()

        self.v1 = client.CoreV1Api()
        self.v1App = client.AppsV1Api()
        self.v1ext = client.ExtensionsV1beta1Api()
        self.v1beta1 = client.ApiextensionsV1beta1Api()
        self.custom = client.CustomObjectsApi()
        self.auto_scaler = client.AutoscalingV1Api()
        self.rbac = client.RbacAuthorizationV1Api()

        if 'cluster_name' in kwargs:
            self.log.info("using explicit cluster_set= %s, cluster_name=%s",  kwargs.get('cluster_set'), kwargs.get('cluster_name'))
            self.cluster_info = { "cluster.name": kwargs.get('cluster_name'), "cluster.set": kwargs.get('cluster_set')}  
        else:
            self.log.info("getting cluster info")
            self.cluster_info = self.get_cluster_info()

    @staticmethod
    def strip_nulls(data):
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def strip_underscores(data):
        return {k: v for k, v in data.items() if not k.startswith("_")} 

    @staticmethod
    def process_dict(d):
        [d.pop(x, None) for x in ['clusterName',
                                  'creationTimestamp', 
                                  'deletionTimestamp',
                                  'finalizers',
                                  'stringData',
                                  'generation',
                                  'initializers',
                                  'managedFields', 
                                  'ownerReferences',
                                  'resourceVersion',
                                  'uid',
                                  'selfLink',
                                  'status']]
        d = K8s.strip_nulls(d)
        d = K8s.strip_underscores(d)
        return d

    @staticmethod
    def object_to_dict(data):
        if isinstance(data, object) and hasattr(data, "attribute_map"):
            d = {}
            for k, v in data.attribute_map.items():
                d[v] = getattr(data, k)
        else:
            if not isinstance(data, dict):
                return data
            if "attribute_map" in data:
                d = {}
                attr_map = data.get("attribute_map", {})
                for k, v in attr_map.items():
                    value = data.pop(k, None)
                    if value:
                        d[v] = value
            else:
                d = data
        return K8s.process_dict(d)

    @staticmethod
    def process_data(data):
        d = K8s.object_to_dict(data)
        if isinstance(d, dict):
            for k, v in d.items():
                d[k] = K8s.process_data(v)
        if isinstance(d, list):
            l = []
            for i in d:
                l.append(K8s.process_data(i))
            d = l
        return d

    def get_api_method(self, kind):
        try:
            api_name = K8s.supported_kinds.get(kind)[0]
            method = K8s.supported_kinds.get(kind)[1]
            api = getattr(self, api_name)
        except Exception as e:
            raise e
        return api, method

    @lib.timing_wrapper
    @lib.retry_wrapper
    def list_custom_kind(self, namespace, group, version, kinds):
        resources = self.custom.list_namespaced_custom_object(group, version, namespace, kinds)
        return resources['items']
 
    @lib.timing_wrapper
    @lib.retry_wrapper
    def read_custom_kind(self, namespace, group, version, kind, name):
        return self.custom.get_namespaced_custom_object(group, version, namespace, kind, name)
    
    @lib.timing_wrapper
    @lib.k8s_chunk_wrapper
    @lib.retry_wrapper
    def list_custom_resource_definitions(self, limit=100, next=next):
        return self.v1beta1.list_custom_resource_definition(limit=limit, _continue=next)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def read_resource_definition(self, name):
        return self.v1beta1.read_custom_resource_definition(name=name)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def get_custom_resource_definitions(self, limit=100, next=''):
        for resource in self.list_custom_resource_definitions(limit=limit, next=next):
            yield self.v1beta1.read_custom_resource_definition(resource.metadata.name)

    @lib.timing_wrapper
    @lib.k8s_chunk_wrapper
    @lib.retry_wrapper
    def list_namespaces(self, limit=100, next='', label_selector=''):
        return self.v1.list_namespace(limit=limit, _continue=next, 
                                      label_selector=label_selector)


    @lib.timing_wrapper
    @lib.retry_wrapper
    def read_namespace(self, namespace):
        return self.v1.read_namespace(namespace)

    @lib.timing_wrapper
    @lib.k8s_chunk_wrapper
    @lib.retry_wrapper
    def list_kind(self, namespace, kind, limit=100, next=''):
        api, method = self.get_api_method(kind)
        return lib.dynamic_method_call(namespace, limit=limit, _continue=next,
                                       method_text=method,
                                       method_prefix="list_namespaced_",
                                       method_object=api)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def read_kind(self, namespace, kind, name):
        api, method = self.get_api_method(kind)
        return lib.dynamic_method_call(name, namespace,
                                       method_text=method,
                                       method_prefix="read_namespaced_",
                                       method_object=api)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def delete_kind(self, namespace, kind, name):
        api, method = self.get_api_method(kind)
        return lib.dynamic_method_call(name, namespace,
                                       method_text=method,
                                       method_prefix="delete_namespaced_",
                                       method_object=api)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def create_kind(self, namespace, kind, data):
        api, method = self.get_api_method(kind)
        return lib.dynamic_method_call(namespace, data,
                                       method_text=method,
                                       method_prefix="create_namespaced_",
                                       method_object=api)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def replace_kind(self, namespace, kind, name, data):
        api, method = self.get_api_method(kind)
        return lib.dynamic_method_call(name, namespace, data,
                                       method_text=method,
                                       method_prefix="replace_namespaced_",
                                       method_object=api)

    @lib.timing_wrapper
    @lib.retry_wrapper
    def get_cluster_info(self):
        data = self.read_kind("kube-system", "ConfigMap", "cluster-data")
        api, method = self.get_api_method("ConfigMap")
        return K8s.process_data(data)["data"]
        

class Backup(Base):

    custom_resources = []

    @lib.retry_wrapper
    def __init__(self, *args, **kwargs):
        super(Backup, self).__init__(*args, **kwargs)

        self.log.debug("Backup init", extra=dict(**kwargs))

        self.k8s = K8s(*args, **kwargs)
        self.store = Store(*args, **kwargs)
        self.retrieve = Retrieve(*args, **kwargs)
            
    def create_key_yaml(self, data):
        d = K8s.process_data(data)
        y = yaml.dump(d)
        key = "{}/{}/{}/{}/{}/{}.yaml".format(self.k8s.cluster_info["cluster.set"],self.k8s.cluster_info["cluster.name"],
                                d['metadata']['namespace'] if d["kind"] != "Namespace" else d['metadata']['name'],
                                d["kind"], d["apiVersion"].replace("/", "_"),
                                d['metadata']['name'])
        self.log.debug("key: %s, yaml...\n %s", key, y)
        return key, y

    @lib.timing_wrapper
    def get_custom_resources(self):
        resources = []
        for resource in self.k8s.get_custom_resource_definitions():
            resources.append(resource)
        return resources

    @lib.timing_wrapper
    def save_namespace(self, namespace):
        """Save a namespace to S3

        This method will enumerate all resources in a namespace
        and then backup the yaml to S3. It will also delete
        any yaml in S3 for resources that no longer exist in
        the namespace.

        Arguments:
            namespace {str} -- the kubernetes namespace to backup

        Returns:
            [int] -- number of resources backuped to S3
            [int] -- number of resources deleted from s3
        """
        if not isinstance(namespace, str):
            raise Exception("namespace must be a string")

        if namespace == "":
            raise Exception("you must supply a namespace, empty string supplied")

        self.log.info("saving namespace %s", namespace)

        keys_stored = self._save_to_s3(namespace)
        keys_deleted = self._handle_deleted_resources(keys_stored, namespace)

        self.log.info("saved %d resources to S3 and deleted %d resources from S3", len(keys_stored), len(keys_deleted))
        return len(keys_stored), len(keys_deleted)

    @lib.timing_wrapper
    def _save_to_s3(self, namespace):
        """Save Kubernetes resources for a namespace to S3

        Arguments:
            namespace {str} -- the kubernetes namespace to backup

        Returns:
            [str[]] -- an array of keys for the objects stored
        """
        keys = []

        # Save the namespace first
        self.log.debug("reading namespace %s", namespace)
        ns = self.k8s.read_namespace(namespace)
        key, data = self.create_key_yaml(ns)
        self.log.debug("storing namespace in S3 with key %s", key)
        self.store.store_in_bucket(key, data)
        keys.append(key)

        # Save the kinds that are supported
        for kind in K8s.supported_kinds.keys():
            for item in self.k8s.list_kind(namespace, kind):
                self.log.debug("reading kind %s with name %s in namespace %s", kind, item.metadata.name, namespace)
                read_data = self.k8s.read_kind(namespace, kind, item.metadata.name)
                key, data = self.create_key_yaml(read_data)
                self.log.debug("storing %s in S3 with key %s", kind, key)
                self.store.store_in_bucket(key, data)
                keys.append(key)
        # Save custom kinds
        for kind in self.k8s.supported_custom_kinds.keys():
            group, version, kinds = self.k8s.supported_custom_kinds[kind]
            for item in self.k8s.list_custom_kind(namespace, group, version, kinds):
                self.log.debug("reading kind %s with name %s in namespace %s", kind, item['metadata']['name'], namespace)
                read_data = self.k8s.read_custom_kind(namespace, group, version, kinds, item['metadata']['name'])
                key, data = self.create_key_yaml(read_data)
                self.log.debug("storing %s in S3 with key %s", kind, key)
                self.store.store_in_bucket(key, data)
                keys.append(key)         
        return keys

    @lib.timing_wrapper
    def _handle_deleted_resources(self, existing_keys, namespace):
        """Delete any artefacts from S3 for non-existent resources
        
        Arguments:
            existing_keys {str[]} -- an array of the keys for resources that exist in the namespace
            namespace {str} -- the kubernetes namespace to backup

        Returns:
            [str[]] -- an array of the keys deleted from the s3 bucket
        """
        keys_deleted = []

        prefix = "{}/{}/{}".format(self.k8s.cluster_info["cluster.set"],self.k8s.cluster_info["cluster.name"], namespace)
        for key in self.retrieve.get_bucket_keys(prefix):
            if key not in existing_keys:
                self.log.info("key %s doesn't exist in k8s, deleting from s3", key)
                self.store.delete_from_bucket(key)
                keys_deleted.append(key)
            else:
                self.log.debug("key %s exists in k8s, no action")
        return keys_deleted


class Restore(Base):
    kind_order = ['Namespace',
                  'LimitRange',
                  'ResourceQuota',
                  'ConfigMap',
                  'Secret',
                  'Service',
                  'Role',
                  'ServiceAccount',
                  'RoleBinding',
                  'HorizontalPodAutoscaler',
                  'Deployment',
                  'Gateway',
                  'VirtualService']

    exclude_list = [("default", "Service", "kubernetes"),
                    ("default", "Endpoints", "kubernetes")]

    def __init__(self, bucket_name, strategy, *args, **kwargs):
        super(Restore, self).__init__(*args, **kwargs)

        self.log.debug("Restore init", extra=dict(**kwargs))

        self.k8s = K8s(*args, **kwargs)
        self.retrieve = Retrieve(bucket_name=bucket_name, *args, **kwargs)

        self.bucket_name = bucket_name
        self.strategy = strategy

    @staticmethod
    def exclude_check(namespace, kind, name):
        if (namespace, kind, name) in Restore.exclude_list:
            return True
        if kind == "Secret" and "default" in name:
            return True
        if kind == "SerivceAccount" and "default" in name:
            return True
        return False

    @lib.timing_wrapper
    def remove_if_exists(self, namespace, kind, name):
        try:
            self.k8s.read_kind(namespace, kind, name)
        except Exception:
            return
        self.k8s.delete_kind(namespace, kind, name)

    @lib.timing_wrapper
    def restore_namespaces(self, clusterSet, clusterName, namespacesToRestore="*"):
        namespace = []
        num_processed = 0
        for namespace in self.retrieve.get_s3_namespaces(clusterSet, clusterName):
            if namespacesToRestore != "*" and namespace not in namespacesToRestore:
                self.log.info("skipping namespace: %s", namespace)
                continue

            self.log.info("restoring namespace: %s", namespace)
            self.strategy.start_namespace(namespace)

            try:
                for kind in Restore.kind_order:
                    prefix = "{}/{}/{}/{}".format(clusterSet, clusterName, namespace, kind)

                    for key in self.retrieve.get_bucket_keys(prefix):
                        _, _, _, _, name = S3.parse_key(key)
                        if Restore.exclude_check(namespace, kind, name):
                            self.log.info("skipping: %s/%s in namespace %s", kind, name, namespace)
                            continue
                        data = self.retrieve.get_bucket_item(key)
                        self.log.info("processing %s", key)
                        self.log.debug("%s", data.decode("utf-8"))
                        self.strategy.process_resource(data)
                        num_processed += 1
            except ApiException as err:
                if err.status == 409:
                    self.log.warning("resource already exists, skipping")
                else:
                    raise
            self.strategy.finish_namespace()
        return num_processed
